const { expect } = require("chai");
const { ethers } = require("hardhat");

// Тесты проверяют не «фичи ради фич», а конституционные свойства целевого escrow
// (docs/ESCROW-TARGETED-DISBURSEMENT.md):
//  — «не даём деньги — оплачиваем нужду»: транш уходит СТРОГО поставщику кейса,
//    получателя нельзя задать вызовом, его фиксирует open;
//  — двигать средства может только executor (никто не владеет единолично);
//  — guardian только останавливает, не направляет;
//  — потолок одного транша (поэтапность / анти-злоупотребление);
//  — refund возвращает остаток В КАЗНУ, не получателю;
//  — каждое движение публично (события);
//  — escrow обеспечен балансом (нельзя открыть кейс без фондирования).
describe("Disbursement (targeted escrow, testnet-only)", function () {
  const ONE = ethers.parseEther("1");
  const FIVE = ethers.parseEther("5");
  const TEN = ethers.parseEther("10");
  const MAX = ethers.parseEther("3"); // потолок одного транша
  const CASE = ethers.encodeBytes32String("case-0001");
  const REF = ethers.encodeBytes32String("PTD-0000");
  const PRIORITY = 2; // «угроза потери жилья» — уровень 2 в PRIORITIES.md

  async function deploy() {
    const [deployer, executor, guardian, treasury, provider, applicant, outsider] =
      await ethers.getSigners();
    const Disbursement = await ethers.getContractFactory("Disbursement");
    const d = await Disbursement.deploy(
      executor.address,
      guardian.address,
      treasury.address,
      MAX
    );
    await d.waitForDeployment();
    return { d, deployer, executor, guardian, treasury, provider, applicant, outsider };
  }

  async function fund(d, who, amount) {
    await who.sendTransaction({ to: await d.getAddress(), value: amount });
  }

  it("конструктор задаёт роли/казну/лимит, деплойер без привилегий", async () => {
    const { d, deployer, executor, guardian, treasury } = await deploy();
    expect(await d.executor()).to.equal(executor.address);
    expect(await d.guardian()).to.equal(guardian.address);
    expect(await d.treasury()).to.equal(treasury.address);
    expect(await d.maxRelease()).to.equal(MAX);
    expect(await d.paused()).to.equal(false);
    expect(await d.caseCount()).to.equal(0);
    // Деплойер — обычный адрес, не executor.
    await expect(
      d.connect(deployer).open(CASE, PRIORITY, deployer.address, ONE, REF)
    ).to.be.revertedWith("Disb: not executor");
  });

  it("отвергает нулевые роли/казну в конструкторе", async () => {
    const [, executor, guardian, treasury] = await ethers.getSigners();
    const Disbursement = await ethers.getContractFactory("Disbursement");
    await expect(
      Disbursement.deploy(ethers.ZeroAddress, guardian.address, treasury.address, MAX)
    ).to.be.revertedWith("Disb: executor=0");
    await expect(
      Disbursement.deploy(executor.address, ethers.ZeroAddress, treasury.address, MAX)
    ).to.be.revertedWith("Disb: guardian=0");
    await expect(
      Disbursement.deploy(executor.address, guardian.address, ethers.ZeroAddress, MAX)
    ).to.be.revertedWith("Disb: treasury=0");
  });

  it("принимает фондирование escrow от любого и эмитит событие", async () => {
    const { d, outsider } = await deploy();
    await expect(
      outsider.sendTransaction({ to: await d.getAddress(), value: ONE })
    )
      .to.emit(d, "Deposited")
      .withArgs(outsider.address, ONE, ONE);
    expect(await d.balance()).to.equal(ONE);
    expect(await d.available()).to.equal(ONE);
  });

  it("ТОЛЬКО executor может открыть кейс; нельзя открыть без фондирования", async () => {
    const { d, executor, guardian, provider, outsider } = await deploy();
    // Нет средств — открыть нельзя.
    await expect(
      d.connect(executor).open(CASE, PRIORITY, provider.address, ONE, REF)
    ).to.be.revertedWith("Disb: not funded");

    await fund(d, outsider, FIVE);
    // Посторонний/guardian не могут открыть.
    for (const who of [outsider, guardian]) {
      await expect(
        d.connect(who).open(CASE, PRIORITY, provider.address, ONE, REF)
      ).to.be.revertedWith("Disb: not executor");
    }

    await expect(d.connect(executor).open(CASE, PRIORITY, provider.address, FIVE, REF))
      .to.emit(d, "Opened")
      .withArgs(1, CASE, provider.address, FIVE, PRIORITY, REF);
    expect(await d.caseCount()).to.equal(1);
    expect(await d.escrowedTotal()).to.equal(FIVE);
    expect(await d.available()).to.equal(0);
    expect(await d.remainingOf(1)).to.equal(FIVE);
  });

  it("open отвергает нулевого/самопровайдера и нулевую сумму", async () => {
    const { d, executor, outsider } = await deploy();
    await fund(d, outsider, FIVE);
    await expect(
      d.connect(executor).open(CASE, PRIORITY, ethers.ZeroAddress, ONE, REF)
    ).to.be.revertedWith("Disb: provider=0");
    await expect(
      d.connect(executor).open(CASE, PRIORITY, await d.getAddress(), ONE, REF)
    ).to.be.revertedWith("Disb: provider=self");
    const [, , , , provider] = await ethers.getSigners();
    await expect(
      d.connect(executor).open(CASE, PRIORITY, provider.address, 0, REF)
    ).to.be.revertedWith("Disb: amount=0");
  });

  it("транш уходит СТРОГО поставщику кейса (целевой расход: не даём деньги — оплачиваем нужду)", async () => {
    const { d, executor, provider } = await deploy();
    await fund(d, executor, FIVE);
    await d.connect(executor).open(CASE, PRIORITY, provider.address, ONE, REF);

    const before = await ethers.provider.getBalance(provider.address);
    await expect(d.connect(executor).release(1, ONE))
      .to.emit(d, "Released")
      .withArgs(1, provider.address, ONE, ONE, executor.address);
    const after = await ethers.provider.getBalance(provider.address);
    // Деньги ушли именно поставщику — задать другого получателя вызовом нельзя.
    expect(after - before).to.equal(ONE);
  });

  it("ТОЛЬКО executor шлёт транш; поэтапность по траншам, статус закрывается при полной выплате", async () => {
    const { d, executor, guardian, provider, outsider } = await deploy();
    await fund(d, executor, FIVE);
    await d.connect(executor).open(CASE, PRIORITY, provider.address, FIVE, REF);

    for (const who of [outsider, guardian, provider]) {
      await expect(d.connect(who).release(1, ONE)).to.be.revertedWith(
        "Disb: not executor"
      );
    }

    // Транш 1 (поэтапность): 2 из 5.
    await d.connect(executor).release(1, ethers.parseEther("2"));
    expect(await d.remainingOf(1)).to.equal(ethers.parseEther("3"));
    // Транш 2: добиваем до полной суммы → статус RELEASED + событие FullyReleased.
    await expect(d.connect(executor).release(1, ethers.parseEther("3")))
      .to.emit(d, "FullyReleased")
      .withArgs(1, provider.address, FIVE);
    expect(await d.remainingOf(1)).to.equal(0);
    const c = await d.cases(1);
    expect(c.status).to.equal(2); // Status.RELEASED
    // Больше слать нельзя — кейс закрыт.
    await expect(d.connect(executor).release(1, 1n)).to.be.revertedWith(
      "Disb: not open"
    );
  });

  it("соблюдает потолок транша и остаток кейса (анти-злоупотребление)", async () => {
    const { d, executor, provider } = await deploy();
    await fund(d, executor, TEN);
    await d.connect(executor).open(CASE, PRIORITY, provider.address, TEN, REF);
    // Больше потолка транша — нельзя.
    await expect(
      d.connect(executor).release(1, MAX + 1n)
    ).to.be.revertedWith("Disb: over limit");
    // Ровно потолок — можно.
    await expect(d.connect(executor).release(1, MAX)).to.not.be.reverted;
    // Больше остатка — нельзя (остаток 7, лимит 3 → ловит лимит; проверим остаток
    // на кейсе в пределах лимита).
    await expect(
      d.connect(executor).release(1, 0)
    ).to.be.revertedWith("Disb: amount=0");
  });

  it("нельзя превысить остаток кейса даже в пределах лимита (поднимаем лимит)", async () => {
    const { d, executor, provider } = await deploy();
    await fund(d, executor, TEN);
    await d.connect(executor).open(CASE, PRIORITY, provider.address, ONE, REF);
    // Поднимем лимит транша выше суммы кейса, чтобы сработала проверка остатка.
    await d.connect(executor).setMaxRelease(TEN);
    await expect(
      d.connect(executor).release(1, ONE + 1n)
    ).to.be.revertedWith("Disb: over remaining");
  });

  it("refund возвращает остаток В КАЗНУ (не получателю) и закрывает кейс", async () => {
    const { d, executor, treasury, provider } = await deploy();
    await fund(d, executor, FIVE);
    await d.connect(executor).open(CASE, PRIORITY, provider.address, FIVE, REF);
    await d.connect(executor).release(1, ethers.parseEther("2")); // ушло 2 поставщику

    const before = await ethers.provider.getBalance(treasury.address);
    await expect(d.connect(executor).refund(1))
      .to.emit(d, "Refunded")
      .withArgs(1, treasury.address, ethers.parseEther("3"), executor.address);
    const after = await ethers.provider.getBalance(treasury.address);
    // Остаток (3) вернулся именно в казну, а не получателю помощи.
    expect(after - before).to.equal(ethers.parseEther("3"));

    const c = await d.cases(1);
    expect(c.status).to.equal(3); // Status.REFUNDED
    expect(await d.escrowedTotal()).to.equal(0);
    // Повторный refund/release невозможен.
    await expect(d.connect(executor).refund(1)).to.be.revertedWith("Disb: not open");
    await expect(d.connect(executor).release(1, 1n)).to.be.revertedWith("Disb: not open");
  });

  it("guardian ставит паузу: open/release запрещены, refund в казну разрешён", async () => {
    const { d, executor, guardian, treasury, provider, outsider } = await deploy();
    await fund(d, executor, TEN);
    await d.connect(executor).open(CASE, PRIORITY, provider.address, FIVE, REF);

    await expect(d.connect(guardian).pause()).to.emit(d, "Paused").withArgs(
      guardian.address
    );
    // На паузе нельзя открывать и слать транши...
    await expect(
      d.connect(executor).open(CASE, PRIORITY, provider.address, ONE, REF)
    ).to.be.revertedWith("Disb: paused");
    await expect(d.connect(executor).release(1, ONE)).to.be.revertedWith("Disb: paused");
    // ...но refund в казну работает (средства не зависают при инциденте).
    const before = await ethers.provider.getBalance(treasury.address);
    await d.connect(executor).refund(1);
    const after = await ethers.provider.getBalance(treasury.address);
    expect(after - before).to.equal(FIVE);

    await expect(d.connect(guardian).unpause()).to.emit(d, "Unpaused");
  });

  it("роли разделены: guardian НЕ двигает средства, executor НЕ ставит паузу", async () => {
    const { d, executor, guardian, provider } = await deploy();
    await fund(d, executor, FIVE);
    await d.connect(executor).open(CASE, PRIORITY, provider.address, ONE, REF);
    await expect(d.connect(guardian).release(1, ONE)).to.be.revertedWith(
      "Disb: not executor"
    );
    await expect(d.connect(guardian).refund(1)).to.be.revertedWith(
      "Disb: not executor"
    );
    await expect(d.connect(executor).pause()).to.be.revertedWith(
      "Disb: not guardian"
    );
  });

  it("передача ролей/казны/лимита — только executor (путь децентрализации)", async () => {
    const { d, executor, guardian, treasury, provider, outsider } = await deploy();
    await expect(
      d.connect(outsider).setExecutor(outsider.address)
    ).to.be.revertedWith("Disb: not executor");

    await expect(d.connect(executor).setExecutor(provider.address))
      .to.emit(d, "ExecutorChanged")
      .withArgs(executor.address, provider.address);
    expect(await d.executor()).to.equal(provider.address);
    // Старый executor больше не может.
    await expect(d.connect(executor).setMaxRelease(0)).to.be.revertedWith(
      "Disb: not executor"
    );

    await expect(d.connect(provider).setGuardian(outsider.address))
      .to.emit(d, "GuardianChanged")
      .withArgs(guardian.address, outsider.address);
    await expect(d.connect(provider).setTreasury(outsider.address))
      .to.emit(d, "TreasuryChanged")
      .withArgs(treasury.address, outsider.address);
    await expect(d.connect(provider).setMaxRelease(ONE))
      .to.emit(d, "MaxReleaseChanged")
      .withArgs(MAX, ONE);
    expect(await d.maxRelease()).to.equal(ONE);
  });

  it("несколько кейсов: escrowedTotal и available учитываются раздельно", async () => {
    const { d, executor, provider, applicant } = await deploy();
    await fund(d, executor, TEN);
    await d.connect(executor).open(CASE, PRIORITY, provider.address, ethers.parseEther("4"), REF);
    const CASE2 = ethers.encodeBytes32String("case-0002");
    await d.connect(executor).open(CASE2, 3, applicant.address, ethers.parseEther("3"), REF);
    expect(await d.escrowedTotal()).to.equal(ethers.parseEther("7"));
    expect(await d.available()).to.equal(ethers.parseEther("3"));
    // Нельзя открыть третий кейс сверх свободного баланса.
    await expect(
      d.connect(executor).open(CASE, 1, provider.address, ethers.parseEther("4"), REF)
    ).to.be.revertedWith("Disb: not funded");
  });
});
