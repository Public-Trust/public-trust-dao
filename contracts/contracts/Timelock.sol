// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.24;

/// @title Timelock — обязательная задержка исполнения решений (СКЕЛЕТ, TESTNET-ONLY)
/// @author Public Trust DAO (автор/инициатор — Федор Григорьев; авторство ≠ владение)
/// @notice Второй слой управления по docs/GOVERNANCE.md §4: между «голосование
///         принято» и «казна исполнила» стоит обязательная пауза. Это окно, в
///         котором сообщество/аудит/аварийный механизм могут остановить явно
///         вредное или захваченное решение ДО необратимого исполнения
///         (GOVERNANCE.md §4–§5, привязка к ANTI-ABUSE: апелляция/вето-аварийка).
/// @dev    Роли строго разделены (ст. 1–2 «никто не владеет единолично»):
///           • `governor` — ЕДИНСТВЕННЫЙ, кто ставит операцию в очередь (`schedule`)
///             и исполняет её по истечении задержки (`execute`). Предназначен быть
///             контрактом Governor (прямое голосование), а НЕ человеком.
///           • `guardian` — аварийное ВЕТО: может только ОТМЕНИТЬ запланированную
///             операцию (`cancel`), но НЕ может ни создать, ни исполнить, ни
///             направить средства («пауза ≠ власть», GOVERNANCE.md §5).
///           • `admin` — РАЗОВЫЙ bootstrap-конфигуратор: назначает governor/guardian
///             на старте (т.к. адрес Governor известен только после его деплоя) и
///             ОБЯЗАН отказаться от прав (`renounceAdmin`). Не двигает средства и не
///             обходит задержку.
///         Сам параметр задержки (`minDelay`) и смена ролей после renounce меняются
///         ТОЛЬКО самим Timelock'ом (`onlySelf`) — т.е. через прошедшее+отложенное
///         голосование, не в обход (GOVERNANCE.md §6, путь децентрализации A→D).
///         РЕЛЬС: скелет для testnet/локали; реальные средства — только после аудита
///         (CONSTITUTION ст. 4.4).
contract Timelock {
    // --- Параметры --------------------------------------------------------------

    /// @notice Минимальная задержка между планированием и исполнением (в секундах).
    uint256 public minDelay;

    // --- Роли -------------------------------------------------------------------

    /// @notice Кто планирует и исполняет операции. Предназначен быть Governor
    ///         (прямое голосование), а НЕ отдельным человеком.
    address public governor;

    /// @notice Аварийное вето: может только отменить запланированную операцию.
    address public guardian;

    /// @notice Разовый bootstrap-конфигуратор. После настройки ОБЯЗАН отказаться
    ///         от прав (`renounceAdmin`) → 0. Не двигает средства, не обходит задержку.
    address public admin;

    // --- Состояние операций -----------------------------------------------------

    /// @dev Зарезервированное значение «операция исполнена».
    uint256 internal constant _DONE = 1;

    /// @notice eta операции: 0 = не запланирована, 1 = исполнена, иначе — timestamp,
    ///         начиная с которого операцию можно исполнить.
    mapping(bytes32 => uint256) public eta;

    // --- Защита от повторного входа --------------------------------------------
    uint256 private _lock = 1;

    // --- События (прозрачность ст. 3) ------------------------------------------

    event Scheduled(bytes32 indexed id, address indexed target, uint256 value, bytes data, bytes32 salt, uint256 eta);
    event Executed(bytes32 indexed id, address indexed target, uint256 value, bytes data, bytes32 salt);
    event Canceled(bytes32 indexed id, address indexed by);
    event MinDelayChanged(uint256 previous, uint256 next);
    event GovernorChanged(address indexed previous, address indexed next);
    event GuardianChanged(address indexed previous, address indexed next);
    event AdminRenounced(address indexed previous);

    // --- Модификаторы -----------------------------------------------------------

    modifier onlyGovernor() {
        require(msg.sender == governor, "Timelock: not governor");
        _;
    }

    modifier onlyGuardian() {
        require(msg.sender == guardian, "Timelock: not guardian");
        _;
    }

    /// @dev Только сам контракт (через прошедшее+отложенное голосование), не человек.
    modifier onlySelf() {
        require(msg.sender == address(this), "Timelock: only self");
        _;
    }

    modifier nonReentrant() {
        require(_lock == 1, "Timelock: reentrant");
        _lock = 2;
        _;
        _lock = 1;
    }

    /// @param minDelay_ Минимальная задержка исполнения в секундах (0 допустим только
    ///        для локальных тестов; на testnet задавать осмысленно — окно на аудит).
    /// @param guardian_ Аварийное вето (может только отменять запланированное).
    constructor(uint256 minDelay_, address guardian_) {
        require(guardian_ != address(0), "Timelock: guardian=0");
        minDelay = minDelay_;
        guardian = guardian_;
        admin = msg.sender;
        emit MinDelayChanged(0, minDelay_);
        emit GuardianChanged(address(0), guardian_);
    }

    // --- Идентификатор операции -------------------------------------------------

    /// @notice Детерминированный id операции (по цели/сумме/данным/соли).
    function hashOperation(address target, uint256 value, bytes calldata data, bytes32 salt)
        public
        pure
        returns (bytes32)
    {
        return keccak256(abi.encode(target, value, keccak256(data), salt));
    }

    // --- Просмотр состояния -----------------------------------------------------

    function isScheduled(bytes32 id) public view returns (bool) {
        return eta[id] > _DONE;
    }

    function isReady(bytes32 id) public view returns (bool) {
        uint256 when = eta[id];
        return when > _DONE && block.timestamp >= when;
    }

    function isDone(bytes32 id) public view returns (bool) {
        return eta[id] == _DONE;
    }

    // --- Планирование / исполнение (только governor) ----------------------------

    /// @notice Поставить операцию в очередь. Только `governor` (прошедшее голосование).
    ///         Исполнить можно не раньше, чем через `minDelay` (окно аудита/апелляции).
    function schedule(address target, uint256 value, bytes calldata data, bytes32 salt)
        external
        onlyGovernor
        returns (bytes32 id)
    {
        require(target != address(0), "Timelock: target=0");
        id = hashOperation(target, value, data, salt);
        require(eta[id] == 0, "Timelock: already scheduled");
        uint256 when = block.timestamp + minDelay;
        eta[id] = when;
        emit Scheduled(id, target, value, data, salt, when);
    }

    /// @notice Исполнить готовую операцию (задержка истекла). Только `governor`.
    function execute(address target, uint256 value, bytes calldata data, bytes32 salt)
        external
        payable
        onlyGovernor
        nonReentrant
        returns (bytes32 id)
    {
        id = hashOperation(target, value, data, salt);
        uint256 when = eta[id];
        require(when > _DONE, "Timelock: not scheduled");
        require(block.timestamp >= when, "Timelock: not ready");

        eta[id] = _DONE;
        emit Executed(id, target, value, data, salt);

        (bool ok, ) = target.call{value: value}(data);
        require(ok, "Timelock: call failed");
    }

    /// @notice Аварийно отменить запланированную операцию. Только `guardian` —
    ///         это вето на исполнение, НЕ распоряжение средствами (GOVERNANCE.md §5).
    function cancel(bytes32 id) external onlyGuardian {
        require(isScheduled(id), "Timelock: cannot cancel");
        delete eta[id];
        emit Canceled(id, msg.sender);
    }

    // --- Bootstrap-конфигурация ролей (admin, разово) ---------------------------

    /// @notice Назначить governor (адрес Governor известен только после его деплоя).
    ///         Доступно bootstrap-admin'у ИЛИ самому Timelock'у (через голосование) —
    ///         так governor можно заменить позже только прошедшим голосованием.
    function setGovernor(address next) external {
        require(msg.sender == admin || msg.sender == address(this), "Timelock: not admin/self");
        require(next != address(0), "Timelock: governor=0");
        emit GovernorChanged(governor, next);
        governor = next;
    }

    /// @notice Сменить аварийное вето. Admin (bootstrap) ИЛИ сам Timelock (голосование).
    function setGuardian(address next) external {
        require(msg.sender == admin || msg.sender == address(this), "Timelock: not admin/self");
        require(next != address(0), "Timelock: guardian=0");
        emit GuardianChanged(guardian, next);
        guardian = next;
    }

    /// @notice Отказаться от прав bootstrap-конфигуратора (необратимо). После этого
    ///         роли и задержку меняет только сам Timelock — т.е. голосование.
    function renounceAdmin() external {
        require(msg.sender == admin, "Timelock: not admin");
        emit AdminRenounced(admin);
        admin = address(0);
    }

    // --- Параметр задержки (только сам Timelock = только через голосование) ------

    /// @notice Изменить минимальную задержку. ТОЛЬКО через прошедшее+отложенное
    ///         голосование (цель операции = сам Timelock) — не в обход (§6).
    function updateDelay(uint256 next) external onlySelf {
        emit MinDelayChanged(minDelay, next);
        minDelay = next;
    }

    // --- Приём средств (для отложенных операций с native-переводом) -------------
    receive() external payable {}
}
