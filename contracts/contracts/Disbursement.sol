// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.24;

/// @title Disbursement — целевой escrow помощи (СКЕЛЕТ, TESTNET-ONLY)
/// @author Public Trust DAO (автор/инициатор — Федор Григорьев; авторство ≠ владение)
/// @notice Слой целевого расхода помощи поверх казны. Реализует главный принцип
///         модели целевого расхода ([`docs/ESCROW-TARGETED-DISBURSEMENT.md`]):
///         **помощь не выдаётся на руки — она оплачивается напрямую поставщику
///         услуги** (арендодателю, аптеке, поставщику еды). Средства блокируются
///         в escrow по конкретному кейсу и могут уйти ТОЛЬКО на заранее
///         зафиксированный адрес поставщика — получатель помощи физически не может
///         перенаправить их себе в кэш. «Подтверждение целевого расхода» встроено
///         в саму транзакцию и навсегда видно в открытом реестре.
/// @dev    Конституционные свойства заложены В КОД:
///         — двигать средства может ТОЛЬКО `executor` (мультисиг/Timelock, не один
///           человек) — «никто не владеет казной единолично» (CONSTITUTION ст. 1–2);
///         — `release` уходит СТРОГО на адрес поставщика из кейса (целевой расход,
///           ст. 5, ANTI-ABUSE §7) — задать получателя нельзя, он фиксируется в `open`;
///         — потолок одного транша `maxRelease` (поэтапные выплаты/лимиты,
///           ANTI-ABUSE §1–§2) — крупное дробится на транши;
///         — `refund` возвращает остаток В КАЗНУ (`treasury`), НЕ получателю
///           (услуга не оказана → деньги не теряются, ст. 7);
///         — `guardian` только ставит аварийную паузу, средства НЕ двигает
///           («безопасность ≠ власть»);
///         — события на каждую ветвь (`open`/`release`/`refund`/`pause`) + `registryRef`
///           (прозрачность ст. 3, связь on-chain ↔ реестр PTD).
///         РЕЛЬС БЕЗОПАСНОСТИ: скелет для testnet/локали. Реальные средства — ТОЛЬКО
///         после независимого аудита + Safe 3-из-5 + одобрения оператора (ст. 4.4).
///         Деплойер НЕ получает власти над средствами.
contract Disbursement {
    // --- Роли (адреса; задаются при деплое, меняются только через executor) -----

    /// @notice Кто открывает кейсы, шлёт транши и делает refund. Предназначен быть
    ///         мультисигом 3-из-5 / Timelock управления, а НЕ отдельным человеком.
    address public executor;

    /// @notice Кто может включить аварийную паузу. Может ТОЛЬКО остановить выплаты,
    ///         НЕ может двигать средства (безопасность ≠ власть).
    address public guardian;

    /// @notice Адрес казны — куда возвращается остаток при `refund` (НЕ получателю).
    ///         По конституции это контракт-казна `Treasury` под коллективным контролем.
    address payable public treasury;

    // --- Параметры антизлоупотребления -----------------------------------------

    /// @notice Потолок одного транша (поэтапные выплаты / лимиты, ANTI-ABUSE §1–§2).
    ///         Крупнее лимита — дробить на несколько `release`, каждый публичен.
    uint256 public maxRelease;

    /// @notice Аварийная пауза. Когда true — `open`/`release` запрещены; депозиты и
    ///         `refund` (возврат в казну) разрешены, чтобы средства не зависали.
    bool public paused;

    // --- Учёт escrow ------------------------------------------------------------

    /// @notice Статусы кейса целевой выплаты (on-chain часть жизненного цикла).
    ///         Богатые состояния (UNDER_REVIEW/APPROVED/DISPUTED/APPEAL) — офф-чейн
    ///         governance + реестр; on-chain закрепляем escrow/release/refund.
    enum Status { NONE, OPEN, RELEASED, REFUNDED }

    struct Case {
        bytes32 caseId;          // псевдонимная ссылка на заявку (без перс. данных)
        uint8 priorityLevel;     // уровень приоритета нужды (PRIORITIES.md)
        address payable provider; // поставщик услуги — ЕДИНСТВЕННЫЙ возможный получатель
        uint256 amount;          // целевая сумма (earmarked)
        uint256 released;        // сколько уже ушло поставщику (траншами)
        bytes32 registryRef;     // ссылка на запись решения в реестре (PTD-xxxx)
        Status status;
    }

    /// @notice Кейсы по id (id = порядковый номер, начиная с 1).
    mapping(uint256 => Case) public cases;

    /// @notice Сколько кейсов открыто всего (последний id).
    uint256 public caseCount;

    /// @notice Суммарно заблокировано в активных кейсах (amount - released по OPEN).
    ///         Инвариант: `escrowedTotal <= address(this).balance`.
    uint256 public escrowedTotal;

    // --- Защита от повторного входа (reentrancy) --------------------------------
    uint256 private _lock = 1;

    // --- События (прозрачность ст. 3: каждая ветвь публична) -------------------

    event Deposited(address indexed from, uint256 amount, uint256 newBalance);
    event Opened(
        uint256 indexed id,
        bytes32 indexed caseId,
        address indexed provider,
        uint256 amount,
        uint8 priorityLevel,
        bytes32 registryRef
    );
    event Released(uint256 indexed id, address indexed provider, uint256 amount, uint256 released, address by);
    event FullyReleased(uint256 indexed id, address indexed provider, uint256 total);
    event Refunded(uint256 indexed id, address indexed treasury, uint256 amount, address by);
    event Paused(address indexed by);
    event Unpaused(address indexed by);
    event ExecutorChanged(address indexed previous, address indexed next);
    event GuardianChanged(address indexed previous, address indexed next);
    event TreasuryChanged(address indexed previous, address indexed next);
    event MaxReleaseChanged(uint256 previous, uint256 next);

    // --- Модификаторы ----------------------------------------------------------

    modifier onlyExecutor() {
        require(msg.sender == executor, "Disb: not executor");
        _;
    }

    modifier onlyGuardian() {
        require(msg.sender == guardian, "Disb: not guardian");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "Disb: paused");
        _;
    }

    modifier nonReentrant() {
        require(_lock == 1, "Disb: reentrant");
        _lock = 2;
        _;
        _lock = 1;
    }

    /// @param executor_ Уполномоченный исполнитель (мультисиг/Timelock).
    /// @param guardian_ Хранитель аварийной паузы (может только останавливать).
    /// @param treasury_ Казна — адрес возврата при refund (НЕ получателю помощи).
    /// @param maxRelease_ Потолок одного транша в wei (0 = без лимита, только для
    ///        локальных тестов; на testnet задавать явно).
    constructor(address executor_, address guardian_, address payable treasury_, uint256 maxRelease_) {
        require(executor_ != address(0), "Disb: executor=0");
        require(guardian_ != address(0), "Disb: guardian=0");
        require(treasury_ != address(0), "Disb: treasury=0");
        executor = executor_;
        guardian = guardian_;
        treasury = treasury_;
        maxRelease = maxRelease_;
        emit ExecutorChanged(address(0), executor_);
        emit GuardianChanged(address(0), guardian_);
        emit TreasuryChanged(address(0), treasury_);
        emit MaxReleaseChanged(0, maxRelease_);
    }

    // --- Финансирование escrow --------------------------------------------------

    /// @notice Принять средства в escrow. Фондируется из казны (`Treasury.release`
    ///         на адрес этого контракта) либо напрямую — поддержка идёт через саму
    ///         прозрачную систему.
    receive() external payable {
        emit Deposited(msg.sender, msg.value, address(this).balance);
    }

    /// @notice Явный депозит (то же, что receive).
    function deposit() external payable {
        emit Deposited(msg.sender, msg.value, address(this).balance);
    }

    /// @notice Свободный (незаблокированный) баланс — можно направить в новый кейс.
    function available() public view returns (uint256) {
        return address(this).balance - escrowedTotal;
    }

    // --- Открытие целевого escrow (ESCROWED) -----------------------------------

    /// @notice Открыть целевой escrow: заблокировать `amount` под поставщика
    ///         `provider`. Средства смогут уйти ТОЛЬКО ему — получатель помощи их
    ///         не контролирует. Может вызвать ТОЛЬКО `executor`, не на паузе.
    /// @param caseId Псевдонимная ссылка на заявку (без персональных данных).
    /// @param priorityLevel Уровень приоритета нужды (PRIORITIES.md).
    /// @param provider Поставщик услуги — единственный возможный получатель транша.
    /// @param amount Целевая сумма в wei (должна быть обеспечена свободным балансом).
    /// @param registryRef Ссылка на запись решения в публичном реестре (PTD-xxxx).
    /// @return id Идентификатор созданного кейса.
    function open(
        bytes32 caseId,
        uint8 priorityLevel,
        address payable provider,
        uint256 amount,
        bytes32 registryRef
    ) external onlyExecutor whenNotPaused returns (uint256 id) {
        require(provider != address(0), "Disb: provider=0");
        require(provider != address(this), "Disb: provider=self");
        require(amount > 0, "Disb: amount=0");
        require(amount <= available(), "Disb: not funded");

        id = ++caseCount;
        cases[id] = Case({
            caseId: caseId,
            priorityLevel: priorityLevel,
            provider: provider,
            amount: amount,
            released: 0,
            registryRef: registryRef,
            status: Status.OPEN
        });
        escrowedTotal += amount;

        emit Opened(id, caseId, provider, amount, priorityLevel, registryRef);
    }

    // --- Транш поставщику (RELEASED; целевой расход, поэтапность) ---------------

    /// @notice Отправить транш поставщику кейса. Получатель НЕ задаётся вызовом —
    ///         средства уходят строго на `provider` из кейса (целевой расход).
    ///         Только `executor`, не на паузе, в пределах остатка и лимита транша.
    /// @param id Идентификатор кейса.
    /// @param amount Сумма транша в wei (<= остаток кейса и <= maxRelease).
    function release(uint256 id, uint256 amount)
        external
        onlyExecutor
        whenNotPaused
        nonReentrant
    {
        Case storage c = cases[id];
        require(c.status == Status.OPEN, "Disb: not open");
        require(amount > 0, "Disb: amount=0");
        uint256 remaining = c.amount - c.released;
        require(amount <= remaining, "Disb: over remaining");
        if (maxRelease != 0) {
            require(amount <= maxRelease, "Disb: over limit");
        }

        c.released += amount;
        escrowedTotal -= amount;
        bool fully = (c.released == c.amount);
        if (fully) {
            c.status = Status.RELEASED;
        }

        emit Released(id, c.provider, amount, c.released, msg.sender);
        if (fully) {
            emit FullyReleased(id, c.provider, c.amount);
        }

        (bool ok, ) = c.provider.call{value: amount}("");
        require(ok, "Disb: transfer failed");
    }

    // --- Возврат в казну (REFUNDED; услуга не оказана) -------------------------

    /// @notice Вернуть остаток кейса В КАЗНУ (НЕ получателю помощи), если услуга не
    ///         оказана/сделка сорвалась. Только `executor`. Разрешено и на паузе —
    ///         чтобы средства не зависали при инциденте. Возврат идёт на `treasury`.
    /// @param id Идентификатор кейса.
    function refund(uint256 id) external onlyExecutor nonReentrant {
        Case storage c = cases[id];
        require(c.status == Status.OPEN, "Disb: not open");
        uint256 remaining = c.amount - c.released;
        require(remaining > 0, "Disb: nothing to refund");

        c.status = Status.REFUNDED;
        escrowedTotal -= remaining;

        emit Refunded(id, treasury, remaining, msg.sender);

        (bool ok, ) = treasury.call{value: remaining}("");
        require(ok, "Disb: refund failed");
    }

    // --- Аварийная пауза (circuit breaker; останавливает, не направляет) -------

    function pause() external onlyGuardian {
        require(!paused, "Disb: already paused");
        paused = true;
        emit Paused(msg.sender);
    }

    function unpause() external onlyGuardian {
        require(paused, "Disb: not paused");
        paused = false;
        emit Unpaused(msg.sender);
    }

    // --- Передача ролей (путь децентрализации: GOVERNANCE.md, фазы A→D) ---------

    /// @notice Сменить исполнителя. Только текущий executor — путь передачи власти
    ///         от bootstrap-мультисига к голосуемому Timelock.
    function setExecutor(address next) external onlyExecutor {
        require(next != address(0), "Disb: executor=0");
        emit ExecutorChanged(executor, next);
        executor = next;
    }

    /// @notice Сменить хранителя аварийной паузы. Только executor (коллективно).
    function setGuardian(address next) external onlyExecutor {
        require(next != address(0), "Disb: guardian=0");
        emit GuardianChanged(guardian, next);
        guardian = next;
    }

    /// @notice Сменить адрес казны для возвратов. Только executor (коллективно).
    function setTreasury(address payable next) external onlyExecutor {
        require(next != address(0), "Disb: treasury=0");
        emit TreasuryChanged(treasury, next);
        treasury = next;
    }

    /// @notice Изменить потолок одного транша. Только executor (коллективно).
    function setMaxRelease(uint256 next) external onlyExecutor {
        emit MaxReleaseChanged(maxRelease, next);
        maxRelease = next;
    }

    // --- Просмотр --------------------------------------------------------------

    /// @notice Текущий полный баланс контракта (wei тестовой монеты).
    function balance() external view returns (uint256) {
        return address(this).balance;
    }

    /// @notice Остаток к выплате по кейсу (amount - released), 0 если не OPEN.
    function remainingOf(uint256 id) external view returns (uint256) {
        Case storage c = cases[id];
        if (c.status != Status.OPEN) return 0;
        return c.amount - c.released;
    }
}
