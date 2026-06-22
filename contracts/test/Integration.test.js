const { expect } = require("chai");
const { ethers } = require("hardhat");
const { deployAll } = require("../scripts/deploy");

// Интеграционный тест ВСЕГО контура (Этап 5, часть 3c): проверяет, что пять
// контрактов, собранные скриптом deploy.js, работают как единый механизм по
// docs/GOVERNANCE.md — и делает это на ГЛАВНОМ сценарии фонда:
//
//   заявка-кейс (нужда: например, аренда) → прямое голосование верифицированных
//   участников → обязательная задержка Timelock → ЦЕЛЕВАЯ выплата поставщику
//   напрямую через escrow (Disbursement), а НЕ «деньги на руки».
//
// Тест намеренно прогоняет цепочку через Disbursement (целевой escrow), тогда как
// Governance.test.js покрывает её через Treasury — вместе они показывают оба пути
// расхода из одного контура. Проверяются именно КОНСТИТУЦИОННЫЕ инварианты:
//   • средства двигает только прошедшее голосование (никакой человек единолично);
//   • получатель помощи НЕ контролирует средства — транш уходит строго поставщику;
//   • задержка-вето соблюдается (нельзя исполнить раньше срока);
//   • проводка контура верна (executor=Timelock, governor=Governor, admin снят,
//     Reputation.governor=Timelock).
describe("Integration: весь контур через deploy.js (заявка → голос → Timelock → поставщик)", function () {
  const REF = ethers.encodeBytes32String("PTD-INT-01");
  const CASE_ID = ethers.encodeBytes32String("case-rent-001");
  const MIN_DELAY = 100n;
  const VOTING_PERIOD = 1000n;
  const QUORUM = 2n;
  const PRIORITY = 1; // уровень приоритета нужды (PRIORITIES.md)

  async function increase(seconds) {
    await ethers.provider.send("evm_increaseTime", [Number(seconds)]);
    await ethers.provider.send("evm_mine", []);
  }

  // Развернуть контур скриптом и подготовить участников/фондирование escrow.
  async function setup() {
    const [deployer, verifier, guardian, alice, bob, carol, provider, outsider] =
      await ethers.getSigners();

    const dep = await deployAll({
      deployer,
      guardian: guardian.address,
      verifier: verifier.address,
      minDelay: MIN_DELAY,
      votingPeriod: VOTING_PERIOD,
      quorum: QUORUM,
      reputationCap: 0n, // строго «1 человек = 1 голос»
      maxRelease: ethers.parseEther("10"),
    });

    // Верификатор выдаёт soulbound-бейджи трём участникам (вес у каждого = 1).
    await dep.reputation.connect(verifier).mint(alice.address, REF);
    await dep.reputation.connect(verifier).mint(bob.address, REF);
    await dep.reputation.connect(verifier).mint(carol.address, REF);

    // Фондируем целевой escrow тестовой монетой (без реальных средств).
    await deployer.sendTransaction({
      to: dep.addresses.disbursement,
      value: ethers.parseEther("6"),
    });

    return { ...dep, deployer, verifier, guardian, alice, bob, carol, provider, outsider };
  }

  // Провести предложение через голосование и Timelock до исполнения.
  // Возвращает id предложения.
  async function passProposal(governor, target, data, { alice, bob, carol }) {
    const id = await governor.connect(alice).propose.staticCall(target, 0, data, REF);
    await governor.connect(alice).propose(target, 0, data, REF);
    await governor.connect(alice).castVote(id, 1); // за
    await governor.connect(bob).castVote(id, 1); // за
    if (carol) await governor.connect(carol).castVote(id, 2); // воздержался (в кворум)
    await increase(VOTING_PERIOD + 1n);
    expect(await governor.state(id)).to.equal(3); // Succeeded
    await governor.queue(id);
    expect(await governor.state(id)).to.equal(4); // Queued
    return id;
  }

  // --- Проводка контура верна -------------------------------------------------

  it("deploy.js связал контур: executor=Timelock, governor=Governor, admin снят, Reputation.governor=Timelock", async () => {
    const { timelock, reputation, treasury, disbursement, governor, addresses } = await setup();

    // Казной и escrow двигает только Timelock (= прошедшее голосование).
    expect(await treasury.executor()).to.equal(addresses.timelock);
    expect(await disbursement.executor()).to.equal(addresses.timelock);
    expect(await disbursement.treasury()).to.equal(addresses.treasury);

    // Timelock планирует/исполняет только по приказу Governor; bootstrap снят.
    expect(await timelock.governor()).to.equal(addresses.governor);
    expect(await timelock.admin()).to.equal(ethers.ZeroAddress);

    // Параметры веса голоса меняет только голосование (governor Reputation = Timelock).
    expect(await reputation.governor()).to.equal(addresses.timelock);
    // Governor смотрит на тот же Reputation для веса.
    expect(await governor.reputation()).to.equal(addresses.reputation);
    expect(await reputation.memberCount()).to.equal(3n);
  });

  it("никто единолично не двигает средства: deployer/guardian не executor escrow", async () => {
    const { disbursement, deployer, guardian, provider } = await setup();
    // Прямой вызов open в обход голосования отклоняется (не executor).
    await expect(
      disbursement.connect(deployer).open(CASE_ID, PRIORITY, provider.address, ethers.parseEther("1"), REF)
    ).to.be.revertedWith("Disb: not executor");
    await expect(
      disbursement.connect(guardian).open(CASE_ID, PRIORITY, provider.address, ethers.parseEther("1"), REF)
    ).to.be.revertedWith("Disb: not executor");
  });

  // --- Главный сквозной сценарий ----------------------------------------------

  it("сквозной путь: голосование открывает escrow и выплачивает транш напрямую поставщику", async () => {
    const { governor, timelock, disbursement, alice, bob, carol, provider } = await setup();
    const disbAddr = await disbursement.getAddress();
    const amount = ethers.parseEther("4");

    // ШАГ 1. Голосование «открыть целевой escrow под поставщика на сумму нужды».
    const openData = disbursement.interface.encodeFunctionData("open", [
      CASE_ID,
      PRIORITY,
      provider.address,
      amount,
      REF,
    ]);
    const openId = await passProposal(governor, disbAddr, openData, { alice, bob, carol });

    // Нельзя исполнить раньше истечения задержки Timelock'а (окно аудита/вето).
    await expect(governor.execute(openId)).to.be.revertedWith("Timelock: not ready");
    await increase(MIN_DELAY + 1n);
    await governor.execute(openId);
    expect(await governor.state(openId)).to.equal(5); // Executed

    // Кейс открыт; средства заблокированы под поставщика, ещё не выплачены.
    const caseId = await disbursement.caseCount();
    expect(caseId).to.equal(1n);
    const c = await disbursement.cases(caseId);
    expect(c.provider).to.equal(provider.address);
    expect(c.amount).to.equal(amount);
    expect(c.released).to.equal(0n);
    expect(await disbursement.escrowedTotal()).to.equal(amount);

    // ШАГ 2. Голосование «выплатить транш» — получатель адресата НЕ задаёт,
    // средства уйдут строго поставщику из кейса (целевой расход).
    const releaseData = disbursement.interface.encodeFunctionData("release", [caseId, amount]);
    const relId = await passProposal(governor, disbAddr, releaseData, { alice, bob, carol });

    const before = await ethers.provider.getBalance(provider.address);
    await increase(MIN_DELAY + 1n);
    await expect(governor.execute(relId))
      .to.emit(disbursement, "Released")
      .withArgs(caseId, provider.address, amount, amount, await timelock.getAddress());

    // Поставщик получил средства напрямую; escrow закрыт.
    const after = await ethers.provider.getBalance(provider.address);
    expect(after - before).to.equal(amount);
    const cAfter = await disbursement.cases(caseId);
    expect(cAfter.released).to.equal(amount);
    expect(cAfter.status).to.equal(2); // RELEASED (enum NONE=0,OPEN=1,RELEASED=2)
    expect(await disbursement.escrowedTotal()).to.equal(0n);
  });

  // --- Аварийное вето на уровне всего контура ---------------------------------

  it("guardian-вето: запланированную выплату можно остановить до исполнения", async () => {
    const { governor, timelock, disbursement, guardian, alice, bob, carol, provider } = await setup();
    const disbAddr = await disbursement.getAddress();
    const amount = ethers.parseEther("3");

    const openData = disbursement.interface.encodeFunctionData("open", [
      CASE_ID,
      PRIORITY,
      provider.address,
      amount,
      REF,
    ]);
    const openId = await passProposal(governor, disbAddr, openData, { alice, bob, carol });

    // guardian аварийно отменяет операцию в Timelock (вето ≠ распоряжение средствами).
    const salt = ethers.zeroPadValue(ethers.toBeHex(openId), 32);
    const opId = await timelock.hashOperation(disbAddr, 0, openData, salt);
    expect(await timelock.isScheduled(opId)).to.equal(true);
    await timelock.connect(guardian).cancel(opId);

    await increase(MIN_DELAY + 1n);
    await expect(governor.execute(openId)).to.be.revertedWith("Timelock: not scheduled");
    // Кейс так и не открылся — escrow пуст.
    expect(await disbursement.caseCount()).to.equal(0n);
  });
});
