// SPDX-License-Identifier: AGPL-3.0-or-later
//
// deploy.js — сборка ВСЕГО он-чейн контура управления Public Trust DAO одним
// проходом (Этап 5, часть 3c). Связывает пять контрактов в единый механизм по
// docs/GOVERNANCE.md §4–§7:
//
//     Reputation ──(вес «1 человек = 1 голос»)──▶ Governor
//                                                    │ queue/execute
//                                                    ▼
//     guardian ──(аварийное вето)──▶ Timelock ──(executor)──▶ Treasury
//                                       ▲                     Disbursement
//                                       └ governor = Governor
//
// Итог проводки:
//   • Treasury.executor      = Timelock   (казной двигает только Timelock)
//   • Disbursement.executor  = Timelock   (escrow'ом двигает только Timelock)
//   • Timelock.governor      = Governor   (планирует/исполняет только голосование)
//   • Timelock.admin         = 0          (renounceAdmin — bootstrap снят)
//   • Reputation.governor    = Timelock   (параметры голоса меняет только голосование)
//   • Reputation.verifier    = verifier   (подтверждает уникальность; «уникальность ≠ власть»)
//   • guardian               = только аварийная пауза/вето, средствами НЕ распоряжается
//
// После проводки НИ ОДИН человек (включая деплойера) не может единолично двинуть
// средства: деплойер привилегий не сохраняет, admin снят, исполняет только
// прошедшее+отложенное голосование (CONSTITUTION ст. 1–2, GOVERNANCE.md §6).
//
// РЕЛЬС TESTNET-FIRST (CONSTITUTION ст. 4.4): реальные средства — только после
// независимого аудита и явного отдельного одобрения оператора + Safe 3-из-5.
// По умолчанию скрипт рассчитан на in-process сеть Hardhat / локальную ноду;
// на публичном testnet роли guardian/verifier берутся из переменных окружения.

const hre = require("hardhat");
const { ethers } = hre;

// Параметры по умолчанию — осмысленные для testnet/локали. На реальном
// деплое перекрываются через opts (в тестах) или через окружение (CLI).
const DEFAULTS = {
  minDelay: 100n, // сек — обязательная задержка-окно на аудит/апелляцию/вето
  reputationCap: 0n, // 0 → строго «1 человек = 1 голос» без множителя
  maxRelease: ethers.parseEther("10"), // потолок одной выплаты (поэтапность)
  votingDelay: 0n, // сек до старта голосования
  votingPeriod: 1000n, // сек — длительность открытого голосования
  quorum: 2n, // минимум голосов (за+воздержался) для кворума
  renounce: true, // снять bootstrap-admin Timelock сразу после проводки
};

// Локальные сети, где допустимо подставлять роли из доступных подписантов
// (нет реальных средств). На любой иной сети роли ОБЯЗАНЫ быть заданы явно.
const LOCAL_NETWORKS = new Set(["hardhat", "localhost"]);

/**
 * Развернуть и связать весь контур.
 * @param {object} opts
 *   - guardian {string}  адрес аварийного вето/паузы (обязателен вне локали)
 *   - verifier {string}  адрес верификатора уникальности (обязателен вне локали)
 *   - deployer {Signer}  подписант-деплойер (по умолчанию первый signer)
 *   - log {boolean}      печатать ли сводку (по умолчанию false)
 *   - + любые из DEFAULTS для перекрытия параметров.
 * @returns {Promise<object>} развёрнутые контракты, адреса и применённая конфигурация.
 */
async function deployAll(opts = {}) {
  const cfg = { ...DEFAULTS, ...opts };
  const networkName = hre.network.name;
  const isLocal = LOCAL_NETWORKS.has(networkName);

  const signers = await ethers.getSigners();
  const deployer = cfg.deployer || signers[0];

  // Роли. На локали можно подставить отдельных подписантов (удобно для тестов
  // и демо); на реальной сети — только явные адреса (рельс: без скрытых ролей).
  let guardian = cfg.guardian;
  let verifier = cfg.verifier;
  if (!guardian) {
    if (!isLocal) throw new Error("deploy: guardian address required (set GUARDIAN_ADDRESS)");
    guardian = (signers[1] || deployer).address;
  }
  if (!verifier) {
    if (!isLocal) throw new Error("deploy: verifier address required (set VERIFIER_ADDRESS)");
    verifier = (signers[2] || deployer).address;
  }

  const log = cfg.log ? (...a) => console.log(...a) : () => {};
  log(`\nPublic Trust DAO — сборка контура (network=${networkName}, TESTNET-ONLY)`);
  log(`  deployer: ${deployer.address}`);
  log(`  guardian: ${guardian}`);
  log(`  verifier: ${verifier}`);

  // 1) Timelock — задержка исполнения; admin = deployer (разовый bootstrap).
  const Timelock = await ethers.getContractFactory("Timelock", deployer);
  const timelock = await Timelock.deploy(cfg.minDelay, guardian);
  await timelock.waitForDeployment();
  const timelockAddr = await timelock.getAddress();
  log(`  Timelock      ${timelockAddr}`);

  // 2) Reputation — soulbound-вес голоса; governor = Timelock (меняется голосованием).
  const Reputation = await ethers.getContractFactory("Reputation", deployer);
  const reputation = await Reputation.deploy(verifier, timelockAddr, cfg.reputationCap);
  await reputation.waitForDeployment();
  const reputationAddr = await reputation.getAddress();
  log(`  Reputation    ${reputationAddr}`);

  // 3) Treasury — казна; executor = Timelock (двигает только голосование).
  const Treasury = await ethers.getContractFactory("Treasury", deployer);
  const treasury = await Treasury.deploy(timelockAddr, guardian, cfg.maxRelease);
  await treasury.waitForDeployment();
  const treasuryAddr = await treasury.getAddress();
  log(`  Treasury      ${treasuryAddr}`);

  // 4) Disbursement — целевой escrow; executor = Timelock, возврат остатка → Treasury.
  const Disbursement = await ethers.getContractFactory("Disbursement", deployer);
  const disbursement = await Disbursement.deploy(timelockAddr, guardian, treasuryAddr, cfg.maxRelease);
  await disbursement.waitForDeployment();
  const disbursementAddr = await disbursement.getAddress();
  log(`  Disbursement  ${disbursementAddr}`);

  // 5) Governor — прямое голосование; исполняет через Timelock.
  const Governor = await ethers.getContractFactory("Governor", deployer);
  const governor = await Governor.deploy(
    reputationAddr,
    timelockAddr,
    cfg.votingDelay,
    cfg.votingPeriod,
    cfg.quorum
  );
  await governor.waitForDeployment();
  const governorAddr = await governor.getAddress();
  log(`  Governor      ${governorAddr}`);

  // --- Проводка: Timelock доверяет планирование/исполнение только Governor'у ----
  // (адрес Governor известен лишь после его деплоя, потому bootstrap через admin).
  await (await timelock.connect(deployer).setGovernor(governorAddr)).wait();
  log(`  wired: Timelock.governor = Governor`);

  // Снять bootstrap-admin: дальше роли и задержку Timelock меняет только сам
  // Timelock (= голосованием). Никакой человек больше не правит контур в обход.
  if (cfg.renounce) {
    await (await timelock.connect(deployer).renounceAdmin()).wait();
    log(`  wired: Timelock.admin renounced → 0 (bootstrap снят)`);
  } else {
    log(`  NOTE: admin НЕ снят (renounce=false) — снять до приёма реальных средств`);
  }

  return {
    timelock,
    reputation,
    treasury,
    disbursement,
    governor,
    addresses: {
      timelock: timelockAddr,
      reputation: reputationAddr,
      treasury: treasuryAddr,
      disbursement: disbursementAddr,
      governor: governorAddr,
      guardian,
      verifier,
      deployer: deployer.address,
    },
    config: {
      network: networkName,
      minDelay: cfg.minDelay.toString(),
      reputationCap: cfg.reputationCap.toString(),
      maxRelease: cfg.maxRelease.toString(),
      votingDelay: cfg.votingDelay.toString(),
      votingPeriod: cfg.votingPeriod.toString(),
      quorum: cfg.quorum.toString(),
      adminRenounced: cfg.renounce,
    },
  };
}

// Запуск как Hardhat-скрипт: `npx hardhat run scripts/deploy.js [--network <net>]`.
async function main() {
  const result = await deployAll({
    guardian: process.env.GUARDIAN_ADDRESS,
    verifier: process.env.VERIFIER_ADDRESS,
    log: true,
  });

  console.log("\nСводка проводки (JSON):");
  console.log(JSON.stringify({ addresses: result.addresses, config: result.config }, null, 2));
  console.log(
    "\nРЕЛЬС: контур развёрнут БЕЗ реальных средств. Перед приёмом реальных " +
      "средств — независимый аудит + Safe 3-из-5 + отдельное одобрение оператора (ст. 4.4)."
  );
}

module.exports = { deployAll, DEFAULTS };

// Выполнять main() только при прямом запуске скриптом, не при require() из тестов.
if (require.main === module) {
  main().catch((err) => {
    console.error(err);
    process.exitCode = 1;
  });
}
