// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.24;

/// @title Reputation — непередаваемый бейдж участника Public Trust DAO (СКЕЛЕТ, TESTNET-ONLY)
/// @author Public Trust DAO (автор/инициатор — Федор Григорьев; авторство ≠ владение)
/// @notice Право голоса = верифицированная уникальность ЧЕЛОВЕКА, а не количество денег
///         (docs/GOVERNANCE.md §2 «один человек — один голос»). Бейдж:
///           • непередаваем (soulbound) — нет ни одной функции перевода: иначе возник бы
///             рынок голосов и обход «1 человек = 1 голос»;
///           • без денежной ценности — это не токен-актив и не доля в прибыли (ст. 1.2),
///             а технический признак «верифицированный человек = 1 голос»;
///           • базовый вес = 1; допустим ОГРАНИЧЕННЫЙ прозрачный множитель за проверяемый
///             вклад, но с ЖЁСТКИМ потолком (`reputationCap`), чтобы не возникла новая
///             элита (GOVERNANCE.md §2, запрет №5).
/// @dev    РАЗГРАНИЧЕНИЕ «уникальность ≠ власть» (GOVERNANCE.md §3): `verifier` лишь
///         подтверждает уникальность человека (mint/revoke бейджа) и НЕ распоряжается
///         средствами. Параметры репутации/потолок меняет `governor` (мультисиг→Timelock,
///         меняется только голосованием). Никакая роль здесь не двигает казну.
///         РЕЛЬС: скелет для testnet/локали; деплойер не получает привилегий после
///         конструктора. Реальное включение — только после аудита (CONSTITUTION ст. 4.4).
contract Reputation {
    // --- Роли -------------------------------------------------------------------

    /// @notice Кто подтверждает уникальность человека: выдаёт/отзывает бейдж.
    ///         По GOVERNANCE.md §3 — слой proof-of-personhood / поручительство /
    ///         временная ревью-комиссия. НЕ распоряжается средствами.
    address public verifier;

    /// @notice Кто меняет параметры управления (потолок множителя, репутацию, роли).
    ///         Предназначен быть Governor/Timelock (меняется только голосованием),
    ///         а НЕ отдельным человеком. Тоже НЕ двигает казну.
    address public governor;

    // --- Параметры голоса -------------------------------------------------------

    /// @notice Жёсткий потолок бонусного веса за вклад (поверх базовой 1).
    ///         Гарантирует, что вес голоса остаётся в коридоре [1 .. 1+cap] —
    ///         никакой участник не получает непропорциональную власть.
    uint256 public reputationCap;

    /// @notice Текущее число верифицированных участников (для кворума и статистики).
    uint256 public memberCount;

    // --- Состояние бейджей ------------------------------------------------------

    /// @notice Верифицирован ли адрес как уникальный человек (имеет бейдж).
    mapping(address => bool) public isMember;

    /// @notice Бонусные очки репутации за проверяемый вклад (до применения потолка).
    ///         Учитываются в весе голоса только пока адрес — участник.
    mapping(address => uint256) public reputationPoints;

    // --- События (прозрачность ст. 3; registryRef связывает с реестром PTD) -----

    event BadgeMinted(address indexed account, bytes32 indexed registryRef, address indexed by);
    event BadgeRevoked(address indexed account, bytes32 indexed registryRef, address indexed by);
    event ReputationSet(address indexed account, uint256 previous, uint256 next, bytes32 indexed registryRef);
    event ReputationCapChanged(uint256 previous, uint256 next);
    event VerifierChanged(address indexed previous, address indexed next);
    event GovernorChanged(address indexed previous, address indexed next);

    // --- Модификаторы -----------------------------------------------------------

    modifier onlyVerifier() {
        require(msg.sender == verifier, "Rep: not verifier");
        _;
    }

    modifier onlyGovernor() {
        require(msg.sender == governor, "Rep: not governor");
        _;
    }

    /// @param verifier_ Кто выдаёт/отзывает бейдж (подтверждает уникальность).
    /// @param governor_ Кто меняет параметры/роли (Governor/Timelock, не человек).
    /// @param reputationCap_ Жёсткий потолок бонусного веса (0 = «1 человек = 1 голос»
    ///        без множителя; включать множитель — отдельным решением управления).
    constructor(address verifier_, address governor_, uint256 reputationCap_) {
        require(verifier_ != address(0), "Rep: verifier=0");
        require(governor_ != address(0), "Rep: governor=0");
        verifier = verifier_;
        governor = governor_;
        reputationCap = reputationCap_;
        emit VerifierChanged(address(0), verifier_);
        emit GovernorChanged(address(0), governor_);
        emit ReputationCapChanged(0, reputationCap_);
    }

    // --- Выдача/отзыв бейджа (только verifier; уникальность, не власть) ----------

    /// @notice Выдать бейдж участника (подтверждена уникальность живого человека).
    /// @param account Адрес верифицированного уникального участника.
    /// @param registryRef Псевдонимная ссылка на решение/кейс в публичном реестре.
    function mint(address account, bytes32 registryRef) external onlyVerifier {
        require(account != address(0), "Rep: account=0");
        require(!isMember[account], "Rep: already member");
        isMember[account] = true;
        memberCount += 1;
        emit BadgeMinted(account, registryRef, msg.sender);
    }

    /// @notice Отозвать бейдж (например, выявлена Сивилла/двойник или по апелляции).
    ///         Сбрасывает и бонусную репутацию, чтобы отозванный адрес имел вес 0.
    function revoke(address account, bytes32 registryRef) external onlyVerifier {
        require(isMember[account], "Rep: not member");
        isMember[account] = false;
        memberCount -= 1;
        if (reputationPoints[account] != 0) {
            emit ReputationSet(account, reputationPoints[account], 0, registryRef);
            reputationPoints[account] = 0;
        }
        emit BadgeRevoked(account, registryRef, msg.sender);
    }

    // --- Репутация и потолок (только governor; параметр управления) -------------

    /// @notice Назначить бонусные очки репутации участнику (поверх базовой 1).
    ///         Только governor (голосованием). Применяется к весу через потолок.
    function setReputation(address account, uint256 points, bytes32 registryRef)
        external
        onlyGovernor
    {
        require(isMember[account], "Rep: not member");
        emit ReputationSet(account, reputationPoints[account], points, registryRef);
        reputationPoints[account] = points;
    }

    /// @notice Изменить жёсткий потолок бонусного веса. Только governor (голосованием).
    function setReputationCap(uint256 next) external onlyGovernor {
        emit ReputationCapChanged(reputationCap, next);
        reputationCap = next;
    }

    // --- Передача ролей (путь децентрализации: GOVERNANCE.md фазы A→D) -----------

    /// @notice Сменить верификатора уникальности. Только governor (коллективно).
    function setVerifier(address next) external onlyGovernor {
        require(next != address(0), "Rep: verifier=0");
        emit VerifierChanged(verifier, next);
        verifier = next;
    }

    /// @notice Сменить governor — путь передачи параметров к голосуемому Timelock.
    ///         Только текущий governor.
    function setGovernor(address next) external onlyGovernor {
        require(next != address(0), "Rep: governor=0");
        emit GovernorChanged(governor, next);
        governor = next;
    }

    // --- Просмотр: вес голоса ---------------------------------------------------

    /// @notice Вес голоса адреса. Не участник → 0. Участник → 1 + min(points, cap).
    ///         Так реализуется «1 человек = 1 голос» с жёстко ограниченным множителем:
    ///         вес всегда в коридоре [1 .. 1+reputationCap], власть денег невозможна.
    function votingUnits(address account) external view returns (uint256) {
        if (!isMember[account]) {
            return 0;
        }
        uint256 bonus = reputationPoints[account];
        if (bonus > reputationCap) {
            bonus = reputationCap;
        }
        return 1 + bonus;
    }

    /// @notice Краткая проверка членства (синоним isMember для читаемости вызовов).
    function isVerified(address account) external view returns (bool) {
        return isMember[account];
    }

    // --- Soulbound: переводы невозможны по построению ----------------------------
    // У контракта НЕТ функций transfer/approve/transferFrom — бейдж непередаваем
    // by design. Право голоса нельзя продать, подарить или сосредоточить скупкой
    // (GOVERNANCE.md §2 «НЕ продаваемое право»). Изменить членство может только
    // verifier через mint/revoke, и только по подтверждённой уникальности.
}
