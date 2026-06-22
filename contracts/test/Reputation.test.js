const { expect } = require("chai");
const { ethers } = require("hardhat");

// Тесты проверяют конституционные свойства бейджа участника (docs/GOVERNANCE.md §2–§3),
// а не «фичи ради фич»:
//  — «1 человек = 1 голос»: вес участника = 1 (+ ограниченный множитель), не-участник = 0;
//  — soulbound: бейдж непередаваем (нет ни одной функции перевода — проверяем отсутствие ABI);
//  — «уникальность ≠ власть»: verifier выдаёт/отзывает бейдж, governor правит параметры,
//    ни одна роль не пересекается и ни одна не двигает средства (в этом контракте их нет);
//  — жёсткий потолок множителя: вес всегда в коридоре [1 .. 1+cap] (нет «власти денег»);
//  — отзыв сбрасывает вес в 0 и репутацию;
//  — каждое изменение публично (события); передача ролей — путь децентрализации.
describe("Reputation (soulbound membership badge, testnet-only)", function () {
  const REF = ethers.encodeBytes32String("PTD-0000");
  const CAP = 3n; // жёсткий потолок бонусного веса

  async function deploy() {
    const [deployer, verifier, governor, alice, bob, outsider] = await ethers.getSigners();
    const Reputation = await ethers.getContractFactory("Reputation");
    const r = await Reputation.deploy(verifier.address, governor.address, CAP);
    await r.waitForDeployment();
    return { r, deployer, verifier, governor, alice, bob, outsider };
  }

  it("конструктор задаёт роли/потолок, деплойер без привилегий", async () => {
    const { r, deployer, verifier, governor, alice } = await deploy();
    expect(await r.verifier()).to.equal(verifier.address);
    expect(await r.governor()).to.equal(governor.address);
    expect(await r.reputationCap()).to.equal(CAP);
    expect(await r.memberCount()).to.equal(0);
    // Деплойер — обычный адрес, не verifier и не governor.
    await expect(r.connect(deployer).mint(alice.address, REF)).to.be.revertedWith("Rep: not verifier");
    await expect(r.connect(deployer).setReputationCap(1)).to.be.revertedWith("Rep: not governor");
  });

  it("отвергает нулевые роли в конструкторе", async () => {
    const [, verifier, governor] = await ethers.getSigners();
    const Reputation = await ethers.getContractFactory("Reputation");
    await expect(
      Reputation.deploy(ethers.ZeroAddress, governor.address, CAP)
    ).to.be.revertedWith("Rep: verifier=0");
    await expect(
      Reputation.deploy(verifier.address, ethers.ZeroAddress, CAP)
    ).to.be.revertedWith("Rep: governor=0");
  });

  it("soulbound: у контракта НЕТ функций перевода (transfer/approve/transferFrom)", async () => {
    const { r } = await deploy();
    // Бейдж непередаваем by design — таких методов не существует в интерфейсе.
    expect(r.interface.fragments.some((f) => f.type === "function" && /transfer|approve/i.test(f.name)))
      .to.equal(false);
    expect(r.transfer).to.equal(undefined);
    expect(r.transferFrom).to.equal(undefined);
    expect(r.approve).to.equal(undefined);
  });

  it("«1 человек = 1 голос»: не-участник=0, участник=1; mint только verifier", async () => {
    const { r, verifier, outsider, alice } = await deploy();
    expect(await r.votingUnits(alice.address)).to.equal(0);
    expect(await r.isVerified(alice.address)).to.equal(false);

    await expect(r.connect(outsider).mint(alice.address, REF)).to.be.revertedWith("Rep: not verifier");

    await expect(r.connect(verifier).mint(alice.address, REF))
      .to.emit(r, "BadgeMinted")
      .withArgs(alice.address, REF, verifier.address);

    expect(await r.isMember(alice.address)).to.equal(true);
    expect(await r.isVerified(alice.address)).to.equal(true);
    expect(await r.votingUnits(alice.address)).to.equal(1);
    expect(await r.memberCount()).to.equal(1);
  });

  it("нельзя выдать бейдж дважды и на нулевой адрес", async () => {
    const { r, verifier, alice } = await deploy();
    await r.connect(verifier).mint(alice.address, REF);
    await expect(r.connect(verifier).mint(alice.address, REF)).to.be.revertedWith("Rep: already member");
    await expect(r.connect(verifier).mint(ethers.ZeroAddress, REF)).to.be.revertedWith("Rep: account=0");
  });

  it("множитель за вклад ограничен жёстким потолком: вес ∈ [1 .. 1+cap]", async () => {
    const { r, verifier, governor, alice } = await deploy();
    await r.connect(verifier).mint(alice.address, REF);

    // В пределах потолка — учитывается полностью.
    await expect(r.connect(governor).setReputation(alice.address, 2, REF))
      .to.emit(r, "ReputationSet")
      .withArgs(alice.address, 0, 2, REF);
    expect(await r.votingUnits(alice.address)).to.equal(3); // 1 + 2

    // Выше потолка — обрезается до cap, «власть денег» невозможна.
    await r.connect(governor).setReputation(alice.address, 100, REF);
    expect(await r.reputationPoints(alice.address)).to.equal(100);
    expect(await r.votingUnits(alice.address)).to.equal(1n + CAP); // 1 + 3
  });

  it("репутацию назначает только governor и только участнику", async () => {
    const { r, verifier, governor, alice, bob } = await deploy();
    await r.connect(verifier).mint(alice.address, REF);
    // Не governor (даже verifier) — нельзя.
    await expect(r.connect(verifier).setReputation(alice.address, 1, REF)).to.be.revertedWith("Rep: not governor");
    // Не участнику — нельзя.
    await expect(r.connect(governor).setReputation(bob.address, 1, REF)).to.be.revertedWith("Rep: not member");
  });

  it("потолок меняет только governor", async () => {
    const { r, verifier, governor } = await deploy();
    await expect(r.connect(verifier).setReputationCap(10)).to.be.revertedWith("Rep: not governor");
    await expect(r.connect(governor).setReputationCap(10))
      .to.emit(r, "ReputationCapChanged")
      .withArgs(CAP, 10);
    expect(await r.reputationCap()).to.equal(10);
  });

  it("отзыв бейджа: вес→0, репутация сброшена, memberCount уменьшен; только verifier", async () => {
    const { r, verifier, governor, outsider, alice } = await deploy();
    await r.connect(verifier).mint(alice.address, REF);
    await r.connect(governor).setReputation(alice.address, 2, REF);
    expect(await r.votingUnits(alice.address)).to.equal(3);

    await expect(r.connect(outsider).revoke(alice.address, REF)).to.be.revertedWith("Rep: not verifier");

    await expect(r.connect(verifier).revoke(alice.address, REF))
      .to.emit(r, "BadgeRevoked")
      .withArgs(alice.address, REF, verifier.address);

    expect(await r.isMember(alice.address)).to.equal(false);
    expect(await r.votingUnits(alice.address)).to.equal(0);
    expect(await r.reputationPoints(alice.address)).to.equal(0);
    expect(await r.memberCount()).to.equal(0);

    await expect(r.connect(verifier).revoke(alice.address, REF)).to.be.revertedWith("Rep: not member");
  });

  it("memberCount корректно считает несколько участников", async () => {
    const { r, verifier, alice, bob } = await deploy();
    await r.connect(verifier).mint(alice.address, REF);
    await r.connect(verifier).mint(bob.address, REF);
    expect(await r.memberCount()).to.equal(2);
    await r.connect(verifier).revoke(alice.address, REF);
    expect(await r.memberCount()).to.equal(1);
    expect(await r.votingUnits(bob.address)).to.equal(1);
  });

  it("передача ролей: setVerifier/setGovernor только governor, путь децентрализации", async () => {
    const { r, verifier, governor, alice, bob } = await deploy();
    // verifier не может менять роли.
    await expect(r.connect(verifier).setVerifier(alice.address)).to.be.revertedWith("Rep: not governor");

    await expect(r.connect(governor).setVerifier(alice.address))
      .to.emit(r, "VerifierChanged")
      .withArgs(verifier.address, alice.address);
    expect(await r.verifier()).to.equal(alice.address);
    // Новый verifier работает, старый — нет.
    await expect(r.connect(verifier).mint(bob.address, REF)).to.be.revertedWith("Rep: not verifier");
    await r.connect(alice).mint(bob.address, REF);
    expect(await r.isMember(bob.address)).to.equal(true);

    await expect(r.connect(governor).setGovernor(alice.address))
      .to.emit(r, "GovernorChanged")
      .withArgs(governor.address, alice.address);
    expect(await r.governor()).to.equal(alice.address);
    // Старый governor больше не правит параметры.
    await expect(r.connect(governor).setReputationCap(1)).to.be.revertedWith("Rep: not governor");

    await expect(r.connect(alice).setVerifier(ethers.ZeroAddress)).to.be.revertedWith("Rep: verifier=0");
    await expect(r.connect(alice).setGovernor(ethers.ZeroAddress)).to.be.revertedWith("Rep: governor=0");
  });
});
