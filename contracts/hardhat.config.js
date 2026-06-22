// Public Trust DAO — Hardhat config.
// РЕЛЬС: TESTNET-ONLY. Здесь НЕТ приватных ключей и mainnet-сетей.
// Реальные сети/ключи никогда не коммитятся: их подставит оператор через .env
// (см. закомментированный пример внизу), .env — в .gitignore.
require("@nomicfoundation/hardhat-ethers");
require("@nomicfoundation/hardhat-chai-matchers");

/** @type {import('hardhat/config').HardhatUserConfig} */
module.exports = {
  solidity: {
    version: "0.8.24",
    settings: {
      optimizer: { enabled: true, runs: 200 },
    },
  },
  // По умолчанию тесты гоняются на встроенной in-process сети Hardhat (локально,
  // без денег и без сети). Никаких внешних RPC/ключей в репозитории.
  networks: {
    hardhat: {},
  },

  // --- ШАБЛОН ДЛЯ ОПЕРАТОРА (НЕ включать ключи в репозиторий) -----------------
  // Когда понадобится деплой на TESTNET (напр. Polygon Amoy, chainId 80002),
  // оператор создаёт contracts/.env (он в .gitignore) и раскомментирует блок:
  //
  //   require("dotenv").config();
  //   networks: {
  //     amoy: {
  //       url: process.env.AMOY_RPC_URL,        // публичный testnet RPC
  //       accounts: [process.env.TESTNET_KEY],  // ТОЛЬКО тестовый ключ без реальных денег
  //       chainId: 80002,
  //     },
  //   }
  // ---------------------------------------------------------------------------
};
