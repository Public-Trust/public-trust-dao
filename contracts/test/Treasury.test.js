const { expect } = require("chai");
const { ethers } = require("hardhat");

// Тесты проверяют не «фичи ради фич», а конституционные свойства казны:
//  — никто не владеет единолично (двигать средства может только executor);
//  — guardian только останавливает, не направляет;
//  — лимит одной выплаты (поэтапность/анти-злоупотребление);
//  — каждое движение публично (события);
//  — нельзя вывести больше баланса / на нулевой адрес / на паузе.
describe("Treasury (skeleton, testnet-only)", function () {
  const ONE = ethers.parseEther("1");
  const MAX = ethers.parseEther("5"); // потолок одной выплаты
  const REF = ethers.encodeBytes32String("PTD-0000");

  async function deploy() {
    const [deployer, executor, guardian, recipient, outsider] =
      await ethers.getSigners();
    const Treasury = await ethers.getContractFactory("Treasury");
    const t = await Treasury.deploy(executor.address, guardian.address, MAX);
    await t.waitForDeployment();
    return { t, deployer, executor, guardian, recipient, outsider };
  }

  it("конструктор задаёт роли и лимит, деплойер без привилегий", async () => {
    const { t, deployer, executor, guardian } = await deploy();
    expect(await t.executor()).to.equal(executor.address);
    expect(await t.guardian()).to.equal(guardian.address);
    expect(await t.maxRelease()).to.equal(MAX);
    expect(await t.paused()).to.equal(false);
    // Деплойер — обычный адрес, не executor и не guardian.
    expect(deployer.address).to.not.equal(executor.address);
    await expect(
      t.connect(deployer).release(deployer.address, ONE, REF)
    ).to.be.revertedWith("Treasury: not executor");
  });

  it("отвергает нулевые роли в конструкторе", async () => {
    const [, , guardian] = await ethers.getSigners();
    const Treasury = await ethers.getContractFactory("Treasury");
    await expect(
      Treasury.deploy(ethers.ZeroAddress, guardian.address, MAX)
    ).to.be.revertedWith("Treasury: executor=0");
  });

  it("принимает депозиты от любого (поддержка через систему) и эмитит событие", async () => {
    const { t, outsider } = await deploy();
    await expect(
      outsider.sendTransaction({ to: await t.getAddress(), value: ONE })
    )
      .to.emit(t, "Deposited")
      .withArgs(outsider.address, ONE, ONE);
    expect(await t.balance()).to.equal(ONE);
  });

  it("ТОЛЬКО executor может двигать средства (никто не владеет единолично)", async () => {
    const { t, executor, guardian, recipient, outsider } = await deploy();
    await outsider.sendTransaction({ to: await t.getAddress(), value: MAX });

    for (const who of [outsider, guardian, recipient]) {
      await expect(
        t.connect(who).release(recipient.address, ONE, REF)
      ).to.be.revertedWith("Treasury: not executor");
    }

    await expect(t.connect(executor).release(recipient.address, ONE, REF))
      .to.emit(t, "Released")
      .withArgs(recipient.address, ONE, REF, executor.address);
  });

  it("выплата уходит получателю и уменьшает баланс казны", async () => {
    const { t, executor, recipient } = await deploy();
    await executor.sendTransaction({ to: await t.getAddress(), value: MAX });
    const before = await ethers.provider.getBalance(recipient.address);

    await t.connect(executor).release(recipient.address, ONE, REF);

    expect(await t.balance()).to.equal(MAX - ONE);
    const after = await ethers.provider.getBalance(recipient.address);
    expect(after - before).to.equal(ONE);
  });

  it("соблюдает лимит одной выплаты (поэтапность / анти-злоупотребление)", async () => {
    const { t, executor, recipient, outsider } = await deploy();
    await outsider.sendTransaction({
      to: await t.getAddress(),
      value: ethers.parseEther("10"),
    });
    await expect(
      t.connect(executor).release(recipient.address, MAX + 1n, REF)
    ).to.be.revertedWith("Treasury: over limit");
    // Ровно на лимит — проходит.
    await expect(t.connect(executor).release(recipient.address, MAX, REF)).to
      .not.be.reverted;
  });

  it("нельзя вывести больше баланса, ноль, или на нулевой адрес", async () => {
    const { t, executor, recipient } = await deploy();
    await executor.sendTransaction({ to: await t.getAddress(), value: ONE });
    await expect(
      t.connect(executor).release(recipient.address, ONE + 1n, REF)
    ).to.be.revertedWith("Treasury: insufficient");
    await expect(
      t.connect(executor).release(recipient.address, 0, REF)
    ).to.be.revertedWith("Treasury: amount=0");
    await expect(
      t.connect(executor).release(ethers.ZeroAddress, ONE, REF)
    ).to.be.revertedWith("Treasury: recipient=0");
  });

  it("guardian ставит на паузу и снимает; на паузе выплаты запрещены, депозиты идут", async () => {
    const { t, executor, guardian, recipient, outsider } = await deploy();
    await outsider.sendTransaction({ to: await t.getAddress(), value: MAX });

    await expect(t.connect(guardian).pause()).to.emit(t, "Paused").withArgs(
      guardian.address
    );
    // Выплата запрещена...
    await expect(
      t.connect(executor).release(recipient.address, ONE, REF)
    ).to.be.revertedWith("Treasury: paused");
    // ...а депозиты по-прежнему принимаются.
    await expect(
      outsider.sendTransaction({ to: await t.getAddress(), value: ONE })
    ).to.emit(t, "Deposited");

    await expect(t.connect(guardian).unpause()).to.emit(t, "Unpaused");
    await expect(t.connect(executor).release(recipient.address, ONE, REF)).to
      .not.be.reverted;
  });

  it("guardian НЕ может двигать средства, executor НЕ может ставить паузу (роли разделены)", async () => {
    const { t, executor, guardian, recipient, outsider } = await deploy();
    await outsider.sendTransaction({ to: await t.getAddress(), value: MAX });
    await expect(
      t.connect(guardian).release(recipient.address, ONE, REF)
    ).to.be.revertedWith("Treasury: not executor");
    await expect(t.connect(executor).pause()).to.be.revertedWith(
      "Treasury: not guardian"
    );
  });

  it("передача ролей и лимита — только executor (путь децентрализации)", async () => {
    const { t, executor, guardian, recipient, outsider } = await deploy();
    // Посторонний не может.
    await expect(
      t.connect(outsider).setExecutor(outsider.address)
    ).to.be.revertedWith("Treasury: not executor");

    await expect(t.connect(executor).setExecutor(recipient.address))
      .to.emit(t, "ExecutorChanged")
      .withArgs(executor.address, recipient.address);
    expect(await t.executor()).to.equal(recipient.address);
    // Старый executor больше не может.
    await expect(
      t.connect(executor).setMaxRelease(0)
    ).to.be.revertedWith("Treasury: not executor");

    await expect(t.connect(recipient).setGuardian(outsider.address))
      .to.emit(t, "GuardianChanged")
      .withArgs(guardian.address, outsider.address);
    await expect(t.connect(recipient).setMaxRelease(ONE))
      .to.emit(t, "MaxReleaseChanged")
      .withArgs(MAX, ONE);
    expect(await t.maxRelease()).to.equal(ONE);
  });
});
