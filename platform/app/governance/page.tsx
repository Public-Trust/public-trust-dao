"use client";

import Link from "next/link";
import { useI18n } from "@/components/Providers";
import SeeAlso from "@/components/SeeAlso";

// Зеркало нормативного документа docs/GOVERNANCE.md внутри приложения (тот же
// приём «экран-зеркало», что «Конституция» ↔ CONSTITUTION.md, «Порядок помощи» ↔
// PRIORITIES.md, «Помощь и награда» ↔ REWARDS-MODEL.md, «Защита от обмана» ↔
// ANTI-ABUSE.md, «Оплачиваемая работа» ↔ PROOF-OF-CONTRIBUTION.md, «Всё под
// подписью» ↔ ACCOUNTABILITY.md, «Оплата напрямую» ↔ ESCROW-TARGETED-DISBURSEMENT.md):
// как фонд принимает решения — один человек один голос, казна исполняет с
// задержкой на проверку, хранители = исполнитель и аварийный тормоз (не власть),
// уникальность ≠ власть, путь к самостоятельности. Это экран-ОБЪЯСНЕНИЕ; сам
// бюллетень — на экране «Голосование» (/voting/). Тексты живут в lib/i18n.ts
// (GovernanceDict), ничего не подгружается со стороны (рельса прозрачности).
// Правило понятного языка — PTD-0040.
const GOVERNANCE_DOC_URL =
  "https://github.com/Public-Trust/public-trust-dao/blob/main/docs/GOVERNANCE.md";

export default function GovernancePage() {
  const { t } = useI18n();
  const s = t.governance;

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{s.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="governance-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="governance-title">{s.title}</h1>
        <p className="lead">{s.lead}</p>
      </section>

      <section className="panel" aria-labelledby="governance-top-title">
        <h2 id="governance-top-title">{s.topTitle}</h2>
        <p className="wallet-note wallet-note--ok" role="note">
          {s.topNote}
        </p>
      </section>

      <section className="panel" aria-labelledby="governance-rules-title">
        <h2 id="governance-rules-title">{s.rulesTitle}</h2>
        <p className="field-hint">{s.rulesHint}</p>
        <ul className="priority-list">
          {s.rules.map((rule) => (
            <li className="priority-item" key={rule.name}>
              <span className="priority-label">{rule.name}</span>
              <span className="priority-meaning">{rule.text}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="explain" aria-labelledby="governance-keepers-title">
        <h2 id="governance-keepers-title">{s.keepersTitle}</h2>
        <p>{s.keepersNote}</p>
      </section>

      <section className="explain" aria-labelledby="governance-sybil-title">
        <h2 id="governance-sybil-title">{s.sybilTitle}</h2>
        <p className="field-hint">{s.sybilHint}</p>
        <ul className="plain-list plain-list--check">
          {s.sybil.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="explain" aria-labelledby="governance-path-title">
        <h2 id="governance-path-title">{s.pathTitle}</h2>
        <p>{s.pathNote}</p>
      </section>

      <section className="panel" aria-labelledby="governance-limit-title">
        <h2 id="governance-limit-title">{s.limitTitle}</h2>
        <p className="wallet-note wallet-note--warn" role="note">
          {s.limitNote}
        </p>
      </section>

      <section className="explain" aria-labelledby="governance-vote-title">
        <h2 id="governance-vote-title">{s.voteTitle}</h2>
        <p>{s.voteNote}</p>
        <p>
          <Link className="screen-card-link" href="/voting/">
            {s.voteLink}
          </Link>
        </p>
      </section>

      <section className="explain" aria-labelledby="governance-source-title">
        <h2 id="governance-source-title">{s.sourceTitle}</h2>
        <p>{s.sourceNote}</p>
        <p>
          <a className="screen-card-link" href={GOVERNANCE_DOC_URL}>
            {s.sourceLink}
          </a>
        </p>
      </section>
      <SeeAlso slug="/governance/" />
    </main>
  );
}
