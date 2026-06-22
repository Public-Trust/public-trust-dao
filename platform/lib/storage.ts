// Слой данных для экрана «Что приложение помнит о вас».
//
// Простыми словами: всё, что экраны платформы сохраняют, остаётся ТОЛЬКО в вашем
// браузере и нигде больше — ни на каком сервере, ни в блокчейне. Здесь живёт
// единое место, которое знает обо всех таких записях и умеет их показать и
// стереть. Это право человека: видеть, что о нём помнят, и в любой момент всё
// удалить (достоинство и «без слежки» — см. docs/ACCOUNTABILITY.md, GOVERNANCE.md).
//
// Все записи платформы лежат под общим именем-приставкой «ptd:». Любой новый
// экран, который что-то сохранит под этой приставкой, автоматически появится
// здесь — чтобы человеку не пришлось искать свои данные по разным углам.
//
// Кошелёк здесь НЕ хранится: подключение кошелька читается «вживую» у самого
// кошелька и платформой не запоминается. Поэтому в списке его нет — и это честно
// проговаривается на экране.

// Общая приставка всех записей платформы в браузере. Единый источник правды —
// если меняется здесь, меняется везде.
export const STORAGE_PREFIX = "ptd:";

// Вид записи — чтобы показать человеку понятную подпись на его языке. Подписи
// (что это и откуда) живут на двух языках в lib/i18n.ts (правило понятного
// языка PTD-0040). Сюда кладём только стабильный «вид», без текста.
export type StoredKind =
  | "identity-action" // выбранное действие на экране «Проверка личности»
  | "identity-method" // выбранный способ проверки
  | "vote" // голос по предложению на экране «Голосование»
  | "other"; // что-то ещё под приставкой ptd: (на будущее)

// Одна запись, которую платформа помнит в этом браузере.
export type StoredEntry = {
  // Полный ключ в браузере (нужен, чтобы стереть именно его).
  key: string;
  // Вид записи — для понятной подписи на экране.
  kind: StoredKind;
  // Что сохранено (само значение, как лежит в браузере).
  value: string;
  // Для голоса — за какое предложение он подан (часть ключа после «ptd:vote:»).
  // Для остальных видов — пусто.
  ref?: string;
};

// Классифицировать ключ в понятный вид. Разбор по приставке, без связи с другими
// слоями, — так список остаётся единым местом и не ломается при изменениях экранов.
function classify(key: string): { kind: StoredKind; ref?: string } {
  if (key === "ptd:identity:action") return { kind: "identity-action" };
  if (key === "ptd:identity:method") return { kind: "identity-method" };
  if (key.startsWith("ptd:vote:")) {
    return { kind: "vote", ref: key.slice("ptd:vote:".length) };
  }
  return { kind: "other" };
}

// Все записи платформы, которые сейчас лежат в этом браузере. Пустой список —
// значит платформа о человеке ничего не помнит. Безопасно на сервере (SSR):
// без браузера вернёт пустой список.
export function listStored(): StoredEntry[] {
  if (typeof window === "undefined") return [];
  const entries: StoredEntry[] = [];
  const store = window.localStorage;
  for (let i = 0; i < store.length; i += 1) {
    const key = store.key(i);
    if (!key || !key.startsWith(STORAGE_PREFIX)) continue;
    const value = store.getItem(key);
    if (value === null) continue;
    const { kind, ref } = classify(key);
    entries.push({ key, kind, value, ref });
  }
  // Устойчивый порядок (по ключу) — чтобы список не «прыгал» между показами.
  entries.sort((a, b) => a.key.localeCompare(b.key));
  return entries;
}

// Стереть одну запись по её ключу.
export function clearOne(key: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(key);
}

// Стереть всё, что платформа помнит в этом браузере (только записи под «ptd:» —
// чужие данные других сайтов не трогаем).
export function clearAll(): void {
  if (typeof window === "undefined") return;
  const store = window.localStorage;
  const toRemove: string[] = [];
  for (let i = 0; i < store.length; i += 1) {
    const key = store.key(i);
    if (key && key.startsWith(STORAGE_PREFIX)) toRemove.push(key);
  }
  for (const key of toRemove) store.removeItem(key);
}
