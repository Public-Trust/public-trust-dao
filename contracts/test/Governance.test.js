const { expect } = require("chai");
const { ethers } = require("hardhat");

// Тесты проверяют КОНСТИТУЦИОННЫЕ свойства прямого голосования (docs/GOVERNANCE.md §4–§7),
// а не «фичи ради фич»:
//  — «1 человек = 1 голос»: вес голоса берётся из soulbound-бейджа (Reputation),
//    не-участник голосовать/вносить предложения не может, деньги власти не дают;
//  — исполнение ТОЛЬКО через Timelock (задержка-вето): нельзя исполнить раньше срока,
//    Governor сам средства не двигает — двигает казна по приказу Timelock'а;
//  — разделение ролей: governor планирует/исполняет, guardian только аварийно отменяет
//    (вето ≠ власть), admin — разовый bootstrap и обязан отказаться от прав;
//  — параметры управления (срок/кворум/задержка) меняются ТОЛЬКО голосованием;
//  — кворум и большинство считаются детерминированно и публично.
describe("Governance: Governor + Timelock (direct voting, testnet-only)", function () {
  const REF = ethers.encodeBytes32String("PTD-0000");
  const MIN_DELAY = 100n; // секунд — окно на аудит/апелляцию/вето
  const VOTING_DELAY = 0n;
  const VOTING_PERIOD = 1000n; // секунд
  const QUORUM = 2n; // минимум голосов (за+воздержался)
  const MAX_RELEASE = ethers.parseEther("10");

  async function increase(seconds) {
    await ethers.provider.send("evm_increaseTime", [Number(seconds)]);
    await ethers.provider.send("evm_mine", []);
  }

  function saltOf(id) {
    return ethers.zeroPadValue(ethers.toBeHex(id), 32);
  }

  async function deploy() {
    const [deployer, verifier, guardian, alice, bob, carol, provider, outsider] =
      await ethers.getSigners();

    const Timelock = await ethers.getContractFactory("Timelock");
    const timelock = await Timelock.deploy(MIN_DELAY, guardian.address);
    await timelock.waitForDeployment();
    const timelockAddr = await timelock.getAddress();

    const Reputation = await ethers.getContractFactory("Reputation");
    const reputation = await Reputation.deploy(verifier.address, timelockAddr, 0); // cap=0 → строго 1 человек=1 голос
    await reputation.waitForDeployment();

    const Treasury = await ethers.getContractFactory("Treasury");
    const treasury = await Treasury.deploy(timelockAddr, guardian.address, MAX_RELEASE);
    await treasury.waitForDeployment();

    const Governor = await ethers.getContractFactory("Governor");
    const governor = await Governor.deploy(
      await reputation.getAddress(),
      timelockAddr,
      VOTING_DELAY,
      VOTING_PERIOD,
      QUORUM
    );
    await governor.waitForDeployment();

    // Bootstrap-проводка: admin (deployer) назначает governor и отказывается от прав.
    await timelock.connect(deployer).setGovernor(await governor.getAddress());
    await timelock.connect(deployer).renounceAdmin();

    // Верифицируем участников (выдаёт бейджи verifier; cap=0 → вес у каждого = 1).
    await reputation.connect(verifier).mint(alice.address, REF);
    await reputation.connect(verifier).mint(bob.address, REF);
    await reputation.connect(verifier).mint(carol.address, REF);

    // Фондируем тестовую казну.
    await deployer.sendTransaction({ to: await treasury.getAddress(), value: ethers.parseEther("5") });

    return { timelock, reputation, treasury, governor, deployer, verifier, guardian, alice, bob, carol, provider, outsider };
  }

  // Закодировать вызов казны Treasury.release(recipient, amount, ref).
  function releaseData(treasury, recipient, amount) {
    return treasury.interface.encodeFunctionData("release", [recipient, amount, REF]);
  }

  // --- Конструкторы и проводка ------------------------------------------------

  it("Timelock: конструктор задаёт задержку/guardian/admin; отвергает guardian=0", async () => {
    const [deployer, , guardian] = await ethers.getSigners();
    const Timelock = await ethers.getContractFactory("Timelock");
    await expect(Timelock.deploy(MIN_DELAY, ethers.ZeroAddress)).to.be.revertedWith("Timelock: guardian=0");
    const t = await Timelock.deploy(MIN_DELAY, guardian.address);
    expect(await t.minDelay()).to.equal(MIN_DELAY);
    expect(await t.guardian()).to.equal(guardian.address);
    expect(await t.admin()).to.equal(deployer.address);
    expect(await t.governor()).to.equal(ethers.ZeroAddress);
  });

  it("Governor: конструктор валидирует адреса и параметры", async () => {
    const [, , , alice] = await ethers.getSigners();
    const Governor = await ethers.getContractFactory("Governor");
    await expect(Governor.deploy(ethers.ZeroAddress, alice.address, 0, VOTING_PERIOD, QUORUM)).to.be.revertedWith("Gov: reputation=0");
    await expect(Governor.deploy(alice.address, ethers.ZeroAddress, 0, VOTING_PERIOD, QUORUM)).to.be.revertedWith("Gov: timelock=0");
    await expect(Governor.deploy(alice.address, alice.address, 0, 0, QUORUM)).to.be.revertedWith("Gov: period=0");
    await expect(Governor.deploy(alice.address, alice.address, 0, VOTING_PERIOD, 0)).to.be.revertedWith("Gov: quorum=0");
  });

  it("Timelock: admin проводит governor и отказывается от прав; после — только self", async () => {
    const { timelock, governor, deployer, alice } = await deploy();
    expect(await timelock.governor()).to.equal(await governor.getAddress());
    expect(await timelock.admin()).to.equal(ethers.ZeroAddress); // renounced в deploy()
    // После renounce admin не может менять роли.
    await expect(timelock.connect(deployer).setGovernor(alice.address)).to.be.revertedWith("Timelock: not admin/self");
  });

  // --- Внесение предложений (равный порог, не деньги) -------------------------

  it("propose: только верифицированный участник; не-участник отклоняется", async () => {
    const { governor, treasury, alice, outsider, provider } = await deploy();
    const data = releaseData(treasury, provider.address, ethers.parseEther("1"));
    await expect(
      governor.connect(outsider).propose(await treasury.getAddress(), 0, data, REF)
    ).to.be.revertedWith("Gov: not member");
    // Участник может; target=0 отклоняется.
    await expect(governor.connect(alice).propose(ethers.ZeroAddress, 0, data, REF)).to.be.revertedWith("Gov: target=0");
    const id = await governor.connect(alice).propose.staticCall(await treasury.getAddress(), 0, data, REF);
    expect(id).to.equal(1n);
  });

  // --- Голосование ------------------------------------------------------------

  it("castVote: вес = 1 (cap=0), не-участник не голосует, нельзя дважды/неверный support", async () => {
    const { governor, treasury, alice, bob, outsider, provider } = await deploy();
    const data = releaseData(treasury, provider.address, ethers.parseEther("1"));
    const target = await treasury.getAddress();
    const id = await governor.connect(alice).propose.staticCall(target, 0, data, REF);
    await governor.connect(alice).propose(target, 0, data, REF);

    const w = await governor.connect(alice).castVote.staticCall(id, 1);
    expect(w).to.equal(1n); // «1 человек = 1 голос»
    await governor.connect(alice).castVote(id, 1);

    await expect(governor.connect(alice).castVote(id, 1)).to.be.revertedWith("Gov: already voted");
    await expect(governor.connect(outsider).castVote(id, 1)).to.be.revertedWith("Gov: no voting weight");
    await expect(governor.connect(bob).castVote(id, 5)).to.be.revertedWith("Gov: bad support");
  });

  it("castVote: нельзя голосовать вне окна (после voteEnd → не Active)", async () => {
    const { governor, treasury, alice, provider } = await deploy();
    const data = releaseData(treasury, provider.address, ethers.parseEther("1"));
    const target = await treasury.getAddress();
    const id = await governor.connect(alice).propose.staticCall(target, 0, data, REF);
    await governor.connect(alice).propose(target, 0, data, REF);
    await increase(VOTING_PERIOD + 1n);
    await expect(governor.connect(alice).castVote(id, 1)).to.be.revertedWith("Gov: not active");
  });

  // --- Кворум и большинство ---------------------------------------------------

  it("подсчёт: кворум не набран → Defeated", async () => {
    const { governor, treasury, alice, provider } = await deploy();
    const data = releaseData(treasury, provider.address, ethers.parseEther("1"));
    const target = await treasury.getAddress();
    const id = await governor.connect(alice).propose.staticCall(target, 0, data, REF);
    await governor.connect(alice).propose(target, 0, data, REF);
    await governor.connect(alice).castVote(id, 1); // 1 голос «за», кворум=2 → не хватит
    await increase(VOTING_PERIOD + 1n);
    expect(await governor.state(id)).to.equal(2); // Defeated
  });

  it("подсчёт: против ≥ за → Defeated даже при кворуме", async () => {
    const { governor, treasury, alice, bob, carol, provider } = await deploy();
    const data = releaseData(treasury, provider.address, ethers.parseEther("1"));
    const target = await treasury.getAddress();
    const id = await governor.connect(alice).propose.staticCall(target, 0, data, REF);
    await governor.connect(alice).propose(target, 0, data, REF);
    await governor.connect(alice).castVote(id, 1); // за
    await governor.connect(bob).castVote(id, 0); // против
    await governor.connect(carol).castVote(id, 0); // против → 1 за / 2 против
    await increase(VOTING_PERIOD + 1n);
    expect(await governor.state(id)).to.equal(2); // Defeated
  });

  // --- Полный цикл: предложение → голос → Timelock → казна исполнила ----------

  it("полный цикл: успех → queue → нельзя раньше срока → execute → казна выплатила поставщику", async () => {
    const { governor, timelock, treasury, alice, bob, carol, provider } = await deploy();
    const amount = ethers.parseEther("2");
    const data = releaseData(treasury, provider.address, amount);
    const target = await treasury.getAddress();

    const id = await governor.connect(alice).propose.staticCall(target, 0, data, REF);
    await governor.connect(alice).propose(target, 0, data, REF);

    await governor.connect(alice).castVote(id, 1);
    await governor.connect(bob).castVote(id, 1);
    await governor.connect(carol).castVote(id, 2); // воздержался — идёт в кворум

    await increase(VOTING_PERIOD + 1n);
    expect(await governor.state(id)).to.equal(3); // Succeeded

    await governor.queue(id);
    expect(await governor.state(id)).to.equal(4); // Queued

    // Нельзя исполнить раньше истечения задержки Timelock'а.
    await expect(governor.execute(id)).to.be.revertedWith("Timelock: not ready");

    const before = await ethers.provider.getBalance(provider.address);
    await increase(MIN_DELAY + 1n);
    await expect(governor.execute(id))
      .to.emit(treasury, "Released")
      .withArgs(provider.address, amount, REF, await timelock.getAddress());

    expect(await governor.state(id)).to.equal(5); // Executed
    const after = await ethers.provider.getBalance(provider.address);
    expect(after - before).to.equal(amount);
    expect(await treasury.balance()).to.equal(ethers.parseEther("3"));
  });

  it("guardian: аварийное вето — cancel запланированной операции блокирует исполнение", async () => {
    const { governor, timelock, treasury, guardian, alice, bob, carol, provider } = await deploy();
    const amount = ethers.parseEther("2");
    const data = releaseData(treasury, provider.address, amount);
    const target = await treasury.getAddress();

    const id = await governor.connect(alice).propose.staticCall(target, 0, data, REF);
    await governor.connect(alice).propose(target, 0, data, REF);
    await governor.connect(alice).castVote(id, 1);
    await governor.connect(bob).castVote(id, 1);
    await increase(VOTING_PERIOD + 1n);
    await governor.queue(id);

    // guardian отменяет операцию в Timelock (вето, не распоряжение средствами).
    const opId = await timelock.hashOperation(target, 0, data, saltOf(id));
    expect(await timelock.isScheduled(opId)).to.equal(true);
    await timelock.connect(guardian).cancel(opId);
    expect(await timelock.isScheduled(opId)).to.equal(false);

    await increase(MIN_DELAY + 1n);
    await expect(governor.execute(id)).to.be.revertedWith("Timelock: not scheduled");
  });

  // --- Разделение ролей в Timelock -------------------------------------------

  it("Timelock: планировать/исполнять может только governor; cancel — только guardian", async () => {
    const { timelock, treasury, alice, provider } = await deploy();
    const data = releaseData(treasury, provider.address, ethers.parseEther("1"));
    const target = await treasury.getAddress();
    await expect(timelock.connect(alice).schedule(target, 0, data, saltOf(1))).to.be.revertedWith("Timelock: not governor");
    await expect(timelock.connect(alice).execute(target, 0, data, saltOf(1))).to.be.revertedWith("Timelock: not governor");
    await expect(timelock.connect(alice).cancel(saltOf(1))).to.be.revertedWith("Timelock: not guardian");
  });

  it("Timelock: updateDelay — только сам контракт (голосованием), не человек", async () => {
    const { timelock, deployer, guardian } = await deploy();
    await expect(timelock.connect(deployer).updateDelay(5)).to.be.revertedWith("Timelock: only self");
    await expect(timelock.connect(guardian).updateDelay(5)).to.be.revertedWith("Timelock: only self");
  });

  // --- Параметры Governor меняются только голосованием ------------------------

  it("Governor: параметры (срок/кворум/задержка) меняет только Timelock", async () => {
    const { governor, alice } = await deploy();
    await expect(governor.connect(alice).setVotingDelay(1)).to.be.revertedWith("Gov: not timelock");
    await expect(governor.connect(alice).setVotingPeriod(1)).to.be.revertedWith("Gov: not timelock");
    await expect(governor.connect(alice).setQuorumVotes(1)).to.be.revertedWith("Gov: not timelock");
  });

  it("сквозной цикл управления: голосованием меняем параметр самого Governor (quorum)", async () => {
    // Демонстрирует §6: параметры управления меняются ТОЛЬКО через прошедшее
    // голосование, исполняемое Timelock'ом — не в обход.
    const { governor, treasury, alice, bob, provider } = await deploy();
    const govAddr = await governor.getAddress();
    const newQuorum = 3n;
    const data = governor.interface.encodeFunctionData("setQuorumVotes", [newQuorum]);

    const id = await governor.connect(alice).propose.staticCall(govAddr, 0, data, REF);
    await governor.connect(alice).propose(govAddr, 0, data, REF);
    await governor.connect(alice).castVote(id, 1);
    await governor.connect(bob).castVote(id, 1);
    await increase(VOTING_PERIOD + 1n);
    await governor.queue(id);
    await increase(MIN_DELAY + 1n);
    await governor.execute(id);

    expect(await governor.quorumVotes()).to.equal(newQuorum);
  });

  // --- Отмена автором до очереди ----------------------------------------------

  it("cancel: автор может отменить до постановки в очередь; чужой — нет", async () => {
    const { governor, treasury, alice, bob, provider } = await deploy();
    const data = releaseData(treasury, provider.address, ethers.parseEther("1"));
    const target = await treasury.getAddress();
    const id = await governor.connect(alice).propose.staticCall(target, 0, data, REF);
    await governor.connect(alice).propose(target, 0, data, REF);
    await expect(governor.connect(bob).cancel(id)).to.be.revertedWith("Gov: only proposer");
    await governor.connect(alice).cancel(id);
    expect(await governor.state(id)).to.equal(6); // Canceled
  });
});
