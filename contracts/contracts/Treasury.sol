// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.24;

/// @title Treasury — общественная казна Public Trust DAO (СКЕЛЕТ, TESTNET-ONLY)
/// @author Public Trust DAO (автор/инициатор — Федор Григорьев; авторство ≠ владение)
/// @notice Базовый слой казны. Хранит ТЕСТОВЫЕ средства и отдаёт их ТОЛЬКО через
///         уполномоченного исполнителя (`executor`), которым по конституции должен
///         быть мультисиг хранителей 3-из-5 / Timelock управления — НЕ один человек.
///         Это реализует ядро конституции: «никто не владеет казной единолично»
///         (ст. 1–2), «ничего не скрывать» (ст. 3 — события на каждое движение),
///         поэтапность и лимиты (ANTI-ABUSE §1 — потолок одной выплаты),
///         аварийная пауза (circuit breaker).
/// @dev    РЕЛЬС БЕЗОПАСНОСТИ: это скелет для testnet/локали. Реальные средства —
///         ТОЛЬКО после независимого аудита + Safe 3-из-5 + отдельного одобрения
///         оператора (CONSTITUTION ст. 4.4). Деплойер НЕ получает власти над
///         средствами: после конструктора у него нет привилегий.
contract Treasury {
    // --- Роли (адреса; задаются при деплое, меняются только через executor) ---

    /// @notice Кто может отправлять средства из казны. Предназначен быть мультисигом
    ///         3-из-5 / Timelock управления, а НЕ отдельным человеком.
    address public executor;

    /// @notice Кто может включить аварийную паузу. Может ТОЛЬКО остановить выплаты,
    ///         НЕ может двигать средства (безопасность ≠ власть).
    address public guardian;

    // --- Параметры антизлоупотребления -----------------------------------------

    /// @notice Потолок одной выплаты (поэтапные выплаты / лимиты, ANTI-ABUSE §1).
    ///         Крупнее лимита — дробить на транши, каждый под коллективным контролем.
    uint256 public maxRelease;

    /// @notice Аварийная пауза. Когда true — выплаты запрещены, депозиты разрешены.
    bool public paused;

    // --- Защита от повторного входа (reentrancy) --------------------------------
    uint256 private _lock = 1;

    // --- События (прозрачность: ст. 3, каждое движение публично) ---------------

    event Deposited(address indexed from, uint256 amount, uint256 newBalance);
    event Released(address indexed recipient, uint256 amount, bytes32 indexed registryRef, address indexed by);
    event Paused(address indexed by);
    event Unpaused(address indexed by);
    event ExecutorChanged(address indexed previous, address indexed next);
    event GuardianChanged(address indexed previous, address indexed next);
    event MaxReleaseChanged(uint256 previous, uint256 next);

    // --- Модификаторы ----------------------------------------------------------

    modifier onlyExecutor() {
        require(msg.sender == executor, "Treasury: not executor");
        _;
    }

    modifier onlyGuardian() {
        require(msg.sender == guardian, "Treasury: not guardian");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "Treasury: paused");
        _;
    }

    modifier nonReentrant() {
        require(_lock == 1, "Treasury: reentrant");
        _lock = 2;
        _;
        _lock = 1;
    }

    /// @param executor_ Уполномоченный исполнитель выплат (мультисиг/Timelock).
    /// @param guardian_ Хранитель аварийной паузы (может только останавливать).
    /// @param maxRelease_ Потолок одной выплаты в wei тестовой монеты (0 = без лимита,
    ///        допускается только для локальных тестов; на testnet задавать явно).
    constructor(address executor_, address guardian_, uint256 maxRelease_) {
        require(executor_ != address(0), "Treasury: executor=0");
        require(guardian_ != address(0), "Treasury: guardian=0");
        executor = executor_;
        guardian = guardian_;
        maxRelease = maxRelease_;
        emit ExecutorChanged(address(0), executor_);
        emit GuardianChanged(address(0), guardian_);
        emit MaxReleaseChanged(0, maxRelease_);
    }

    // --- Депозиты (поддержка через саму систему, SUPPORT-MODEL) -----------------

    /// @notice Принять средства в казну. Открыто для всех — поддержка идёт через
    ///         саму прозрачную систему, а не отдельной кнопкой сбоку.
    receive() external payable {
        emit Deposited(msg.sender, msg.value, address(this).balance);
    }

    /// @notice Явный депозит (то же, что receive, но вызывается данными).
    function deposit() external payable {
        emit Deposited(msg.sender, msg.value, address(this).balance);
    }

    // --- Выплаты (только executor, под лимитом, с публичным событием) ----------

    /// @notice Отправить средства получателю. Может вызвать ТОЛЬКО `executor`
    ///         (мультисиг/Timelock), не на паузе, в пределах лимита и баланса.
    /// @param recipient Кому уходят средства (на слое escrow — поставщик услуги).
    /// @param amount Сумма в wei.
    /// @param registryRef Псевдонимная ссылка на решение/кейс в публичном реестре
    ///        (`governance/registry/`) — связывает on-chain движение с записью PTD.
    function release(address payable recipient, uint256 amount, bytes32 registryRef)
        external
        onlyExecutor
        whenNotPaused
        nonReentrant
    {
        require(recipient != address(0), "Treasury: recipient=0");
        require(amount > 0, "Treasury: amount=0");
        require(amount <= address(this).balance, "Treasury: insufficient");
        if (maxRelease != 0) {
            require(amount <= maxRelease, "Treasury: over limit");
        }

        emit Released(recipient, amount, registryRef, msg.sender);

        (bool ok, ) = recipient.call{value: amount}("");
        require(ok, "Treasury: transfer failed");
    }

    // --- Аварийная пауза (circuit breaker; останавливает, не направляет) -------

    function pause() external onlyGuardian {
        require(!paused, "Treasury: already paused");
        paused = true;
        emit Paused(msg.sender);
    }

    function unpause() external onlyGuardian {
        require(paused, "Treasury: not paused");
        paused = false;
        emit Unpaused(msg.sender);
    }

    // --- Передача ролей (путь децентрализации: GOVERNANCE.md, фазы A→D) ---------

    /// @notice Сменить исполнителя. Только текущий executor — это и есть путь
    ///         передачи власти от bootstrap-мультисига к голосуемому Timelock.
    function setExecutor(address next) external onlyExecutor {
        require(next != address(0), "Treasury: executor=0");
        emit ExecutorChanged(executor, next);
        executor = next;
    }

    /// @notice Сменить хранителя аварийной паузы. Только executor (коллективно).
    function setGuardian(address next) external onlyExecutor {
        require(next != address(0), "Treasury: guardian=0");
        emit GuardianChanged(guardian, next);
        guardian = next;
    }

    /// @notice Изменить потолок одной выплаты. Только executor (коллективно).
    function setMaxRelease(uint256 next) external onlyExecutor {
        emit MaxReleaseChanged(maxRelease, next);
        maxRelease = next;
    }

    // --- Просмотр --------------------------------------------------------------

    /// @notice Текущий баланс казны (wei тестовой монеты).
    function balance() external view returns (uint256) {
        return address(this).balance;
    }
}
