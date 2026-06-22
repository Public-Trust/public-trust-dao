// Слой данных для экрана «Проверка личности».
//
// Простыми словами: здесь живёт устройство проверки «за аккаунтом один реальный
// живой человек» — без слежки и без сбора лиц в базу (см.
// docs/IDENTITY-VERIFICATION.md). Главное правило: один настоящий человек — один
// аккаунт, но фонд проверяет человека, а не копит на него досье.
//
// Два разных слоя, которые здесь не смешиваются:
//   1) сколько проверки нужно — зависит от действия (читать сайт — нисколько,
//      голосовать или получать помощь — строгая проверка уникальности);
//   2) каким способом человек проверяется — он выбирает сам из нескольких
//      готовых способов, в том числе без камеры и без биометрии.
//
// Жёсткая граница (повторяется на экране): уникальность — это НЕ власть. Проверка
// подтверждает, что человек настоящий и один, но не даёт доступа к деньгам.
// Деньги двигаются только голосованием и через общий кошелёк (см. GOVERNANCE.md).
//
// Пока умные контракты и проверка не запущены в тестовой сети, экран работает как
// понятная заготовка: человек выбирает действие и способ, а его выбор остаётся
// проверяемым ЧЕРНОВИКОМ-памяткой прямо в браузере (копировать/сохранить файлом).
// Ничего не уходит наружу, никакие лица или личные данные не собираются и не
// попадают в блокчейн. Настоящая проверка появится, когда оператор развернёт её в
// тестовой сети, — тот же экран переключат на работу «вживую» без переписывания
// (слой данных намеренно отделён от экрана).

// Уровень строгости проверки. Человеческие подписи — на двух языках в lib/i18n.ts
// (правило понятного языка PTD-0040).
//   L0 — без проверки: просто смотреть сайт, журнал, состояние казны;
//   L1 — лёгкая проверка «живой человек» (без раскрытия личности): подать заявку;
//   L2 — строгая проверка уникальности «настоящий и только один»: голосовать,
//        получать помощь или выплату — здесь на кону общие деньги и доверие.
export type IdentityLevel = "L0" | "L1" | "L2";

// Действие человека на платформе. От действия зависит нужный уровень проверки.
export type IdentityAction = "read" | "apply" | "vote" | "receive";

// Какой уровень нужен для какого действия (см. таблицу уровней в
// docs/IDENTITY-VERIFICATION.md). Пороги уровней — настройка под голосованием.
export const ACTION_LEVEL: Record<IdentityAction, IdentityLevel> = {
  read: "L0",
  apply: "L1",
  vote: "L2",
  receive: "L2",
};

// Готовые способы проверки. Человек выбирает любой удобный — это и про удобство,
// и про то, чтобы не зависеть от одного поставщика. Список способов — настройка,
// которую сообщество меняет голосованием.
//   social   — через социальные связи, без биометрии (пример: BrightID);
//   passport — «паспорт из множества признаков», биометрия не обязательна
//              (пример: Gitcoin Passport);
//   liveness — проверка «живости» по лицу у ВНЕШНЕГО сервиса: фонду возвращается
//              только ответ да/нет, фото у фонда не оседает (пример: World ID);
//   vouch    — запасной путь без камеры и смартфона: поручительство живых людей.
export type IdentityMethod = "social" | "passport" | "liveness" | "vouch";

export const METHODS: IdentityMethod[] = [
  "social",
  "passport",
  "liveness",
  "vouch",
];

// Нужна ли способу биометрия (для честной пометки на экране). У всех способов,
// кроме «живости по лицу», ответ — нет; и даже там фото остаётся у внешнего
// сервиса, фонду приходит только да/нет.
export function usesBiometry(method: IdentityMethod): boolean {
  return method === "liveness";
}

// ——— Выбор человека хранится только в его браузере (localStorage), нигде ещё ———

const ACTION_KEY = "ptd:identity:action";
const METHOD_KEY = "ptd:identity:method";

function isAction(v: string | null): v is IdentityAction {
  return v === "read" || v === "apply" || v === "vote" || v === "receive";
}

function isMethod(v: string | null): v is IdentityMethod {
  return v === "social" || v === "passport" || v === "liveness" || v === "vouch";
}

export function getMyAction(): IdentityAction | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(ACTION_KEY);
  return isAction(raw) ? raw : null;
}

export function setMyAction(action: IdentityAction): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(ACTION_KEY, action);
}

export function getMyMethod(): IdentityMethod | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(METHOD_KEY);
  return isMethod(raw) ? raw : null;
}

export function setMyMethod(method: IdentityMethod): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(METHOD_KEY, method);
}

export function clearMyChoice(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(ACTION_KEY);
  window.localStorage.removeItem(METHOD_KEY);
}

// ——— Черновик-памятка проверки — проверяемая запись БЕЗ личных данных ———

// В памятке нет ни имени, ни лица, ни адреса — только факт «какое действие,
// какой уровень, какой способ выбран». Это намеренно: фонд проверяет человека,
// но не собирает на него досье.
export type CheckNote = {
  kind: "demonstration-identity-note";
  version: 1;
  action: IdentityAction;
  requiredLevel: IdentityLevel;
  method: IdentityMethod;
  usesBiometry: boolean;
  carriesPersonalData: false;
  network: "testnet";
  note: string;
};

const CHECK_NOTE =
  "Показательная памятка проверки личности. В ней нет ни имени, ни лица, ни " +
  "адреса — только факт «какое действие, какой уровень, какой способ». Фонд " +
  "проверяет, что человек настоящий и один, но не собирает базу лиц. " +
  "Уникальность — это не власть над деньгами. Настоящая проверка появится после " +
  "запуска в тестовой сети; сейчас ничего не уходит наружу и не попадает в " +
  "блокчейн. / Demonstration identity note. It carries no name, face, or " +
  "address — only the fact of which action, which level, which method. The fund " +
  "verifies that a person is real and unique, but keeps no database of faces. " +
  "Uniqueness is not power over money. Real verification becomes available after " +
  "it runs on a test network; for now nothing leaves your browser and nothing " +
  "goes on-chain.";

export function buildCheckNote(
  action: IdentityAction,
  method: IdentityMethod,
): CheckNote {
  return {
    kind: "demonstration-identity-note",
    version: 1,
    action,
    requiredLevel: ACTION_LEVEL[action],
    method,
    usesBiometry: usesBiometry(method),
    carriesPersonalData: false,
    network: "testnet",
    note: CHECK_NOTE,
  };
}

export function checkNoteToJson(note: CheckNote): string {
  return JSON.stringify(note, null, 2);
}
