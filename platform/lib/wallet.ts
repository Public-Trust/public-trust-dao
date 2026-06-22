// Слой работы с блокчейном — кошелёк. Без React: это чистый доступ к провайдеру
// кошелька по стандарту EIP-1193 (window.ethereum). Экран (UI) отделён от этого
// слоя намеренно — чтобы позже без переписывания добавить настоящие контракты и,
// при переходе на сервер, переиспользовать ту же логику.
//
// Простыми словами: здесь живут «кнопки связи» с кошельком — спросить адрес,
// узнать сеть, красиво сократить адрес. Деньги отсюда НЕ двигаются: мы только
// спрашиваем публичный адрес и читаем номер сети. Личный ключ остаётся у человека.
//
// Technical note (for developers): a thin EIP-1193 wrapper. No web3 library is
// bundled (supply-chain / transparency rail) — we talk to window.ethereum
// directly. Read-only here: we never send transactions, only request accounts
// and read the chain id.

export type Eip1193Provider = {
  request: (args: { method: string; params?: unknown[] }) => Promise<unknown>;
  on?: (event: string, handler: (...args: unknown[]) => void) => void;
  removeListener?: (
    event: string,
    handler: (...args: unknown[]) => void,
  ) => void;
};

declare global {
  interface Window {
    ethereum?: Eip1193Provider;
  }
}

export function getProvider(): Eip1193Provider | null {
  if (typeof window === "undefined") return null;
  return window.ethereum ?? null;
}

export function hasWallet(): boolean {
  return getProvider() !== null;
}

function toAddressList(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((a): a is string => typeof a === "string") : [];
}

// Спросить доступ к кошельку (открывает окно кошелька, если он есть).
export async function requestAccounts(): Promise<string[]> {
  const provider = getProvider();
  if (!provider) throw new Error("no-wallet");
  return toAddressList(await provider.request({ method: "eth_requestAccounts" }));
}

// Узнать уже разрешённые адреса, НЕ открывая окно кошелька.
export async function getAccounts(): Promise<string[]> {
  const provider = getProvider();
  if (!provider) return [];
  return toAddressList(await provider.request({ method: "eth_accounts" }));
}

export async function getChainId(): Promise<string | null> {
  const provider = getProvider();
  if (!provider) return null;
  const id = await provider.request({ method: "eth_chainId" });
  return typeof id === "string" ? id : null;
}

// Сократить адрес для показа: 0x1234…abcd.
export function shortAddress(addr: string): string {
  if (!addr || addr.length < 10) return addr;
  return `${addr.slice(0, 6)}…${addr.slice(-4)}`;
}

// Понятные названия известных сетей. Фонд работает в ТЕСТОВОЙ сети
// (Polygon Amoy, chain_id 80002 = 0x13882 — см. governance/safe/).
export const KNOWN_NETWORKS: Record<
  string,
  { ru: string; en: string; testnet: boolean }
> = {
  "0x1": { ru: "Ethereum (основная сеть)", en: "Ethereum (mainnet)", testnet: false },
  "0x89": { ru: "Polygon (основная сеть)", en: "Polygon (mainnet)", testnet: false },
  "0x13882": {
    ru: "Polygon Amoy (тестовая сеть)",
    en: "Polygon Amoy (testnet)",
    testnet: true,
  },
  "0xaa36a7": { ru: "Sepolia (тестовая сеть)", en: "Sepolia (testnet)", testnet: true },
};

export function networkName(chainId: string | null, lang: "ru" | "en"): string {
  if (!chainId) return lang === "ru" ? "неизвестно" : "unknown";
  const net = KNOWN_NETWORKS[chainId.toLowerCase()];
  if (!net) return lang === "ru" ? `сеть ${chainId}` : `network ${chainId}`;
  return lang === "ru" ? net.ru : net.en;
}

// true — тестовая сеть, false — основная (реальные деньги), null — не распознана.
export function isTestnet(chainId: string | null): boolean | null {
  if (!chainId) return null;
  const net = KNOWN_NETWORKS[chainId.toLowerCase()];
  return net ? net.testnet : null;
}
