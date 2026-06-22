// Слой данных для экрана «Подать заявку на помощь».
//
// Простыми словами: здесь живёт устройство заявки — какие у неё поля и в каком
// порядке фонд помогает (порядок важности нужд из docs/PRIORITIES.md). Ничего
// личного здесь не хранится и никуда не отправляется. Пока умные контракты не
// запущены в тестовой сети, экран собирает ЧЕРНОВИК заявки прямо в браузере
// человека — его можно скопировать или сохранить файлом. Настоящая подача
// появится, когда оператор развернёт контракты в тестовой сети.
//
// Слой намеренно отделён от экрана (UI): позже его можно подключить к реестру
// или контрактам «переключением тумблера», не переписывая интерфейс.

// Порядок важности нужд — ровно как в docs/PRIORITIES.md (статья 5
// конституции «справедливое распределение»). Уровень 1 — самая срочная беда.
// Человеческие подписи к ключам живут в двух языках в lib/i18n.ts (правило
// понятного языка PTD-0040), здесь — только нейтральные ключ и уровень.
export type PriorityKey =
  | "life_threat"
  | "housing_loss"
  | "medical"
  | "food"
  | "children"
  | "elderly"
  | "disability"
  | "self_reliance"
  | "education"
  | "public_good";

export type Priority = { level: number; key: PriorityKey };

export const PRIORITIES: Priority[] = [
  { level: 1, key: "life_threat" },
  { level: 2, key: "housing_loss" },
  { level: 3, key: "medical" },
  { level: 4, key: "food" },
  { level: 5, key: "children" },
  { level: 6, key: "elderly" },
  { level: 7, key: "disability" },
  { level: 8, key: "self_reliance" },
  { level: 9, key: "education" },
  { level: 10, key: "public_good" },
];

export function priorityByKey(key: string): Priority | null {
  return PRIORITIES.find((p) => p.key === key) ?? null;
}

// Что вводит человек на экране.
export type DraftInput = {
  priorityKey: string;
  need: string;
  directSpend: string;
  amount: string;
};

// Черновик заявки — простая, проверяемая структура без личных данных.
// Поле directSpend отражает модель целевого расхода из
// docs/ESCROW-TARGETED-DISBURSEMENT.md: фонд оплачивает нужду напрямую, а не
// выдаёт деньги на руки. amount необязателен (свободный текст: «≈ X на лечение»).
export type ApplicationDraft = {
  kind: "aid-application-draft";
  version: 1;
  priorityLevel: number;
  priorityKey: PriorityKey;
  need: string;
  directSpend: string;
  amount: string | null;
  status: "draft";
  network: "testnet";
  note: string;
};

const DRAFT_NOTE =
  "Черновик заявки. Реальная подача появится после запуска контрактов в " +
  "тестовой сети. Личные данные сюда вносить не нужно. / Application draft. " +
  "Real submission becomes available after the contracts run on a test " +
  "network. No personal data is needed here.";

export type Validation = {
  ok: boolean;
  fields: { priority: boolean; need: boolean; directSpend: boolean };
};

// Заявку нельзя подать без выбора важности нужды, описания беды и того, на что
// именно пойдут средства (целевой расход). Сумма необязательна.
export function validate(input: DraftInput): Validation {
  const priority = priorityByKey(input.priorityKey) !== null;
  const need = input.need.trim().length > 0;
  const directSpend = input.directSpend.trim().length > 0;
  return { ok: priority && need && directSpend, fields: { priority, need, directSpend } };
}

export function buildDraft(input: DraftInput): ApplicationDraft | null {
  const priority = priorityByKey(input.priorityKey);
  if (!priority || !validate(input).ok) return null;
  const amount = input.amount.trim();
  return {
    kind: "aid-application-draft",
    version: 1,
    priorityLevel: priority.level,
    priorityKey: priority.key,
    need: input.need.trim(),
    directSpend: input.directSpend.trim(),
    amount: amount.length > 0 ? amount : null,
    status: "draft",
    network: "testnet",
    note: DRAFT_NOTE,
  };
}

export function draftToJson(draft: ApplicationDraft): string {
  return JSON.stringify(draft, null, 2);
}

// Мягкая (необязывающая) проверка приватности: похоже ли, что в тексте остались
// личные данные — длинная цепочка цифр (телефон/паспорт/карта) или адрес
// электронной почты. Это не блокирует подачу, а вежливо напоминает убрать
// лишнее, ведь заявка анонимна (конституция: понятность и защита человека).
export function looksLikePersonalData(...texts: string[]): boolean {
  const joined = texts.join(" ");
  const longDigitRun = /\d[\d\s().-]{6,}\d/.test(joined); // 8+ цифр подряд (с разделителями)
  const email = /[^\s@]+@[^\s@]+\.[^\s@]+/.test(joined);
  return longDigitRun || email;
}
