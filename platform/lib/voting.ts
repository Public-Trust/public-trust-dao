// Слой данных для экрана «Голосование».
//
// Простыми словами: здесь живёт устройство голосования — что такое предложение,
// какие у него состояния и как считаются голоса. Главное правило фонда: один
// человек — один голос (см. docs/GOVERNANCE.md). Поэтому вес любого голоса здесь
// всегда равен единице — его нельзя купить или усилить деньгами.
//
// Пока умные контракты не запущены в тестовой сети, экран показывает несколько
// ПОКАЗАТЕЛЬНЫХ предложений (примеры) и собирает голос как проверяемый ЧЕРНОВИК
// прямо в браузере человека — его можно скопировать или сохранить файлом.
// Ничего не уходит на сторонние серверы и ничего не попадает в блокчейн.
// Настоящее голосование появится, когда оператор развернёт контракты в тестовой
// сети, — тогда этот же экран переключат на чтение «вживую» без переписывания
// (слой данных намеренно отделён от экрана).

// Что можно выбрать в голосовании.
export type VoteChoice = "for" | "against" | "abstain";

// Состояние предложения. Человеческие подписи к ним живут на двух языках в
// lib/i18n.ts (правило понятного языка PTD-0040).
//   open      — идёт голосование, можно голосовать;
//   timelock  — прошло, ждёт в окне на проверку (задержка перед исполнением);
//   passed    — принято и исполнено;
//   rejected  — не набрало большинства.
export type ProposalStatus = "open" | "timelock" | "passed" | "rejected";

// Голоса считаются в ЛЮДЯХ (один человек — один голос), а не в деньгах/токенах.
export type Proposal = {
  id: string;
  status: ProposalStatus;
  for: number;
  against: number;
  abstain: number;
};

// Показательные предложения (примеры) — чтобы экран работал уже сейчас, до
// запуска контрактов. Тексты к ним (заголовок/суть) — в lib/i18n.ts по этим id.
export const PROPOSALS: Proposal[] = [
  { id: "demo-1", status: "open", for: 142, against: 17, abstain: 9 },
  { id: "demo-2", status: "timelock", for: 318, against: 64, abstain: 22 },
  { id: "demo-3", status: "rejected", for: 88, against: 211, abstain: 14 },
];

// Сумма поданных голосов по предложению (всего людей высказалось).
export function totalVotes(p: Proposal): number {
  return p.for + p.against + p.abstain;
}

// Доля выбора в процентах (для понятной полоски-итога). Без дробей — людям проще.
export function sharePercent(count: number, total: number): number {
  if (total <= 0) return 0;
  return Math.round((count / total) * 100);
}

// Прибавить голос самого человека к показательным итогам — чтобы он сразу видел,
// что его голос засчитан и весит ровно один.
export function withMyVote(p: Proposal, choice: VoteChoice | null): Proposal {
  return {
    ...p,
    for: p.for + (choice === "for" ? 1 : 0),
    against: p.against + (choice === "against" ? 1 : 0),
    abstain: p.abstain + (choice === "abstain" ? 1 : 0),
  };
}

// ——— Голос человека хранится только в его браузере (localStorage), нигде ещё ———

const VOTE_KEY_PREFIX = "ptd:vote:";

export function getMyVote(proposalId: string): VoteChoice | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(VOTE_KEY_PREFIX + proposalId);
  if (raw === "for" || raw === "against" || raw === "abstain") return raw;
  return null;
}

export function setMyVote(proposalId: string, choice: VoteChoice): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(VOTE_KEY_PREFIX + proposalId, choice);
}

export function clearMyVote(proposalId: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(VOTE_KEY_PREFIX + proposalId);
}

// ——— Черновик бюллетеня — простая проверяемая запись без личных данных ———

// Вес всегда 1: один человек — один голос (это не настройка, а правило фонда).
export type Ballot = {
  kind: "demonstration-ballot";
  version: 1;
  proposalId: string;
  choice: VoteChoice;
  weight: 1;
  network: "testnet";
  note: string;
};

const BALLOT_NOTE =
  "Показательный бюллетень. Вес голоса всегда один — один человек, один голос. " +
  "Настоящее голосование появится после запуска контрактов в тестовой сети; " +
  "сейчас ничего не уходит наружу и не попадает в блокчейн. / Demonstration " +
  "ballot. A vote always weighs one — one person, one vote. Real voting becomes " +
  "available after the contracts run on a test network; for now nothing leaves " +
  "your browser and nothing goes on-chain.";

export function buildBallot(proposalId: string, choice: VoteChoice): Ballot {
  return {
    kind: "demonstration-ballot",
    version: 1,
    proposalId,
    choice,
    weight: 1,
    network: "testnet",
    note: BALLOT_NOTE,
  };
}

export function ballotToJson(ballot: Ballot): string {
  return JSON.stringify(ballot, null, 2);
}
