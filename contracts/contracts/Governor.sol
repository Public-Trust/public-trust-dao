// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.24;

/// @notice Источник веса голоса: непередаваемый бейдж участника (Reputation.sol).
interface IReputationVotes {
    /// @return Вес голоса адреса: не-участник = 0, участник = 1 + ограниченный множитель.
    function votingUnits(address account) external view returns (uint256);
    function memberCount() external view returns (uint256);
}

/// @notice Минимальный интерфейс Timelock, через который исполняется воля голосования.
interface IGovTimelock {
    function schedule(address target, uint256 value, bytes calldata data, bytes32 salt) external returns (bytes32);
    function execute(address target, uint256 value, bytes calldata data, bytes32 salt) external payable returns (bytes32);
    function minDelay() external view returns (uint256);
}

/// @title Governor — прямое голосование верифицированных участников (СКЕЛЕТ, TESTNET-ONLY)
/// @author Public Trust DAO (автор/инициатор — Федор Григорьев; авторство ≠ владение)
/// @notice Сердце прямой демократии по docs/GOVERNANCE.md §4, §7: любой
///         верифицированный участник вносит предложение, идёт открытое голосование
///         с кворумом и сроком, подсчёт публичен. Принятое решение НЕ исполняется
///         сразу — оно ставится в очередь Timelock'а (окно на аудит/апелляцию) и
///         только потом исполняется казной. Так реализуется ст. 10 «изменение —
///         только через сообщество» прямо в коде.
/// @dev    Конституционные свойства заложены В КОД, не только в текст:
///           • «1 человек = 1 голос» — вес берётся из Reputation.votingUnits (soulbound,
///             деньги власти не дают, ст. 2 / запрет №5). Не-участник голосовать не может.
///           • Порог внесения предложения — РАВНЫЙ для всех (членство), не денежный
///             ценз (GOVERNANCE.md §7 «небольшой и равный порог-антиспам»).
///           • Исполнение — ТОЛЬКО через Timelock (задержка-вето), Governor сам средства
///             не двигает; казна (Treasury/Disbursement) исполняет лишь то, что прислал
///             Timelock после прошедшего голосования (GOVERNANCE.md §4).
///           • Параметры управления (срок/кворум/задержка) меняются ТОЛЬКО через сам
///             механизм — голосованием (onlyTimelock), не в обход (§6, путь A→D).
///         РЕЛЬС: скелет для testnet/локали; реальные средства — только после аудита
///         (CONSTITUTION ст. 4.4).
contract Governor {
    // --- Связанные контуры ------------------------------------------------------

    IReputationVotes public immutable reputation;
    IGovTimelock public immutable timelock;

    // --- Параметры голосования (меняются только голосованием — onlyTimelock) -----

    /// @notice Задержка (сек) между внесением предложения и началом голосования.
    uint256 public votingDelay;
    /// @notice Длительность (сек) открытого голосования.
    uint256 public votingPeriod;
    /// @notice Минимум голосов (за + воздержался) для кворума.
    uint256 public quorumVotes;

    // --- Типы -------------------------------------------------------------------

    enum State { Pending, Active, Defeated, Succeeded, Queued, Executed, Canceled }
    enum Support { Against, For, Abstain }

    struct Proposal {
        address proposer;
        address target;
        uint256 value;
        bytes data;
        bytes32 salt;
        uint64 voteStart;
        uint64 voteEnd;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 abstainVotes;
        bool queued;
        bool executed;
        bool canceled;
    }

    mapping(uint256 => Proposal) internal _proposals;
    mapping(uint256 => mapping(address => bool)) public hasVoted;

    /// @notice Сквозной счётчик предложений (id = порядковый номер, начиная с 1).
    uint256 public proposalCount;

    // --- События (прозрачность ст. 3; registryRef связывает с реестром PTD) -----

    event ProposalCreated(
        uint256 indexed id,
        address indexed proposer,
        address target,
        uint256 value,
        bytes data,
        uint64 voteStart,
        uint64 voteEnd,
        bytes32 indexed registryRef
    );
    event VoteCast(address indexed voter, uint256 indexed id, uint8 support, uint256 weight);
    event ProposalQueued(uint256 indexed id, uint256 eta);
    event ProposalExecuted(uint256 indexed id);
    event ProposalCanceled(uint256 indexed id, address indexed by);
    event VotingDelayChanged(uint256 previous, uint256 next);
    event VotingPeriodChanged(uint256 previous, uint256 next);
    event QuorumChanged(uint256 previous, uint256 next);

    modifier onlyTimelock() {
        require(msg.sender == address(timelock), "Gov: not timelock");
        _;
    }

    /// @param reputation_ Контракт веса голоса (soulbound-бейдж, «1 человек = 1 голос»).
    /// @param timelock_ Контракт задержки исполнения (через него исполняется воля).
    /// @param votingDelay_ Задержка до старта голосования (сек; 0 = сразу).
    /// @param votingPeriod_ Длительность голосования (сек; > 0).
    /// @param quorumVotes_ Минимум голосов (за+воздержался) для кворума (> 0).
    constructor(
        address reputation_,
        address timelock_,
        uint256 votingDelay_,
        uint256 votingPeriod_,
        uint256 quorumVotes_
    ) {
        require(reputation_ != address(0), "Gov: reputation=0");
        require(timelock_ != address(0), "Gov: timelock=0");
        require(votingPeriod_ > 0, "Gov: period=0");
        require(quorumVotes_ > 0, "Gov: quorum=0");
        reputation = IReputationVotes(reputation_);
        timelock = IGovTimelock(timelock_);
        votingDelay = votingDelay_;
        votingPeriod = votingPeriod_;
        quorumVotes = quorumVotes_;
        emit VotingDelayChanged(0, votingDelay_);
        emit VotingPeriodChanged(0, votingPeriod_);
        emit QuorumChanged(0, quorumVotes_);
    }

    // --- Внесение предложения (любой верифицированный участник) ------------------

    /// @notice Внести предложение «исполнить вызов `data` на `target`». Внести может
    ///         ЛЮБОЙ верифицированный участник (равный порог-антиспам, не деньги).
    /// @param target Цель исполнения (обычно Timelock-управляемая казна/параметр).
    /// @param value Сумма native для перевода при исполнении (обычно 0).
    /// @param data Кодированный вызов (напр. Treasury.release(...)).
    /// @param registryRef Псевдонимная ссылка на запись/кейс в публичном реестре.
    function propose(address target, uint256 value, bytes calldata data, bytes32 registryRef)
        external
        returns (uint256 id)
    {
        require(reputation.votingUnits(msg.sender) > 0, "Gov: not member");
        require(target != address(0), "Gov: target=0");

        id = ++proposalCount;
        uint64 start = uint64(block.timestamp + votingDelay);
        uint64 end = start + uint64(votingPeriod);

        Proposal storage p = _proposals[id];
        p.proposer = msg.sender;
        p.target = target;
        p.value = value;
        p.data = data;
        p.salt = bytes32(id);
        p.voteStart = start;
        p.voteEnd = end;

        emit ProposalCreated(id, msg.sender, target, value, data, start, end, registryRef);
    }

    // --- Голосование ------------------------------------------------------------

    /// @notice Проголосовать. Вес = Reputation.votingUnits(голосующего) («1 человек =
    ///         1 голос» + ограниченный множитель). Не-участник голосовать не может.
    /// @param support 0 = против, 1 = за, 2 = воздержался.
    function castVote(uint256 id, uint8 support) external returns (uint256 weight) {
        require(state(id) == State.Active, "Gov: not active");
        require(support <= uint8(Support.Abstain), "Gov: bad support");
        require(!hasVoted[id][msg.sender], "Gov: already voted");

        weight = reputation.votingUnits(msg.sender);
        require(weight > 0, "Gov: no voting weight");

        hasVoted[id][msg.sender] = true;
        Proposal storage p = _proposals[id];
        if (support == uint8(Support.Against)) {
            p.againstVotes += weight;
        } else if (support == uint8(Support.For)) {
            p.forVotes += weight;
        } else {
            p.abstainVotes += weight;
        }
        emit VoteCast(msg.sender, id, support, weight);
    }

    // --- Подсчёт состояния (публичен — ст. 3) -----------------------------------

    /// @notice Текущее состояние предложения. Подсчёт детерминирован и публичен.
    function state(uint256 id) public view returns (State) {
        Proposal storage p = _proposals[id];
        require(p.proposer != address(0), "Gov: unknown proposal");
        if (p.canceled) return State.Canceled;
        if (p.executed) return State.Executed;
        if (p.queued) return State.Queued;
        if (block.timestamp < p.voteStart) return State.Pending;
        if (block.timestamp <= p.voteEnd) return State.Active;
        // Голосование завершено: кворум (за+воздержался) и большинство «за».
        if (p.forVotes + p.abstainVotes >= quorumVotes && p.forVotes > p.againstVotes) {
            return State.Succeeded;
        }
        return State.Defeated;
    }

    // --- Постановка в очередь и исполнение (через Timelock) ---------------------

    /// @notice Поставить прошедшее предложение в очередь Timelock'а (старт задержки).
    function queue(uint256 id) external {
        require(state(id) == State.Succeeded, "Gov: not succeeded");
        Proposal storage p = _proposals[id];
        p.queued = true;
        timelock.schedule(p.target, p.value, p.data, p.salt);
        emit ProposalQueued(id, block.timestamp + timelock.minDelay());
    }

    /// @notice Исполнить предложение после истечения задержки Timelock'а. Само
    ///         исполнение и проверку готовности делает Timelock; Governor средства
    ///         не двигает (GOVERNANCE.md §4).
    function execute(uint256 id) external payable {
        require(state(id) == State.Queued, "Gov: not queued");
        Proposal storage p = _proposals[id];
        p.executed = true;
        timelock.execute{value: p.value}(p.target, p.value, p.data, p.salt);
        emit ProposalExecuted(id);
    }

    /// @notice Отменить предложение ДО постановки в очередь. Только автор предложения.
    ///         После постановки в очередь аварийное вето — у `guardian` Timelock'а.
    function cancel(uint256 id) external {
        State s = state(id);
        require(s == State.Pending || s == State.Active || s == State.Succeeded, "Gov: cannot cancel");
        Proposal storage p = _proposals[id];
        require(msg.sender == p.proposer, "Gov: only proposer");
        p.canceled = true;
        emit ProposalCanceled(id, msg.sender);
    }

    // --- Просмотр предложения ---------------------------------------------------

    function getProposal(uint256 id)
        external
        view
        returns (
            address proposer,
            address target,
            uint256 value,
            uint64 voteStart,
            uint64 voteEnd,
            uint256 forVotes,
            uint256 againstVotes,
            uint256 abstainVotes
        )
    {
        Proposal storage p = _proposals[id];
        require(p.proposer != address(0), "Gov: unknown proposal");
        return (p.proposer, p.target, p.value, p.voteStart, p.voteEnd, p.forVotes, p.againstVotes, p.abstainVotes);
    }

    // --- Параметры управления (меняются ТОЛЬКО голосованием = onlyTimelock) ------

    function setVotingDelay(uint256 next) external onlyTimelock {
        emit VotingDelayChanged(votingDelay, next);
        votingDelay = next;
    }

    function setVotingPeriod(uint256 next) external onlyTimelock {
        require(next > 0, "Gov: period=0");
        emit VotingPeriodChanged(votingPeriod, next);
        votingPeriod = next;
    }

    function setQuorumVotes(uint256 next) external onlyTimelock {
        require(next > 0, "Gov: quorum=0");
        emit QuorumChanged(quorumVotes, next);
        quorumVotes = next;
    }
}
