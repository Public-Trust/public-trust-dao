// Слой данных для экрана «Открытый журнал».
//
// Простыми словами: здесь живёт устройство открытого журнала решений — что в
// каждой записи и как их показать человеку. Сами записи берутся из снимка
// journal-data.json, который кладёт рядом скрипт scripts/sync_journal.py из
// открытого реестра governance/registry/. Платформа ничего не подгружает с
// чужих серверов — снимок едет вместе с приложением (требование прозрачности).
//
// Слой намеренно отделён от экрана (UI): позже, когда контракты запустят в
// тестовой сети, тот же экран можно переключить на чтение «вживую» из реестра
// или из блокчейна — «переключением тумблера», не переписывая интерфейс.

import snapshot from "@/lib/journal-data.json";

// Виды записей в журнале (как в схеме реестра). Человеческие подписи к ним
// живут на двух языках в lib/i18n.ts (правило понятного языка PTD-0040).
export type RecordType =
  | "genesis"
  | "decision"
  | "disbursement"
  | "governance"
  | "audit"
  | "appeal"
  | "reputation"
  | "note";

export type JournalEntry = {
  seq: number;
  id: string;
  type: RecordType;
  timestamp: string;
  summary: string;
  hash: string;
  file: string;
};

export type Journal = {
  count: number;
  headHash: string;
  entries: JournalEntry[];
};

const RAW = snapshot as unknown as {
  count: number;
  headHash: string;
  entries: JournalEntry[];
};

// Записи журнала, новые сверху (по порядковому номеру seq, убыванием).
export const ENTRIES: JournalEntry[] = [...RAW.entries].sort(
  (a, b) => b.seq - a.seq,
);

export const COUNT: number = RAW.count;

// «Отпечаток» вершины цепочки — короткий контрольный код всего журнала.
// Если хоть одну запись подменят, этот отпечаток изменится (защита от подмены).
export const HEAD_HASH: string = RAW.headHash;

// Все виды записей, которые реально встречаются в журнале — для фильтра.
export const PRESENT_TYPES: RecordType[] = Array.from(
  new Set(ENTRIES.map((e) => e.type)),
);

// Короткий вид отпечатка для показа (полный — в подсказке и в записи реестра).
export function shortHash(hash: string): string {
  if (hash.length <= 14) return hash;
  return `${hash.slice(0, 8)}…${hash.slice(-6)}`;
}

// Дата записи человеку: YYYY-MM-DD (без времени — короче и понятнее в списке).
export function shortDate(timestamp: string): string {
  return timestamp.slice(0, 10);
}

// Ссылка на полную запись в открытом репозитории (одна запись — один файл).
// Это обычная ссылка по клику, а не фоновая подгрузка: платформа сама на
// сторонние серверы не ходит (прозрачность).
const REPO_BLOB =
  "https://github.com/Public-Trust/public-trust-dao/blob/main/governance/registry/";

export function recordUrl(file: string): string {
  return REPO_BLOB + file;
}

// Простой текстовый поиск по записям (номер, код PTD, суть). Регистр не важен.
export function search(entries: JournalEntry[], query: string): JournalEntry[] {
  const q = query.trim().toLowerCase();
  if (!q) return entries;
  return entries.filter(
    (e) =>
      e.id.toLowerCase().includes(q) ||
      e.summary.toLowerCase().includes(q) ||
      String(e.seq) === q,
  );
}
