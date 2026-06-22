"use client";

import Link from "next/link";
import { useI18n } from "@/components/Providers";
import SeeAlso from "@/components/SeeAlso";

// Зеркало нормативного документа docs/REWARDS-MODEL.md внутри приложения
// (тот же приём, что «Порядок помощи» ↔ PRIORITIES.md): простым языком,
// сколько денег идёт на помощь нуждающимся, а сколько — в благодарность за труд.
// Тексты живут в lib/i18n.ts (RewardsDict), ничего не подгружается со стороны
// (рельса прозрачности). Правило понятного языка — PTD-0040.
const REWARDS_DOC_URL =
  "https://github.com/Public-Trust/public-trust-dao/blob/main/docs/REWARDS-MODEL.md";

export default function RewardsPage() {
  const { t } = useI18n();
  const r = t.rewards;

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{r.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="rewards-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="rewards-title">{r.title}</h1>
        <p className="lead">{r.lead}</p>
      </section>

      <section className="explain" aria-labelledby="rewards-key-title">
        <h2 id="rewards-key-title">{r.keyTitle}</h2>
        <ul className="plain-list">
          {r.key.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="rewards-rule-title">
        <h2 id="rewards-rule-title">{r.ruleTitle}</h2>
        <p className="wallet-note wallet-note--ok" role="note">
          {r.rule}
        </p>
      </section>

      <section className="panel" aria-labelledby="rewards-streams-title">
        <h2 id="rewards-streams-title">{r.streamsTitle}</h2>
        <p className="field-hint">{r.streamsHint}</p>
        <ul className="priority-list">
          {r.streams.map((stream) => (
            <li className="priority-item" key={stream.name}>
              <span className="priority-label">{stream.name}</span>
              <span className="priority-meaning">{stream.text}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="explain" aria-labelledby="rewards-adaptive-title">
        <h2 id="rewards-adaptive-title">{r.adaptiveTitle}</h2>
        <ul className="plain-list">
          {r.adaptive.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="explain" aria-labelledby="rewards-check-title">
        <h2 id="rewards-check-title">{r.checkTitle}</h2>
        <ul className="plain-list plain-list--check">
          {r.check.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="rewards-limit-title">
        <h2 id="rewards-limit-title">{r.limitTitle}</h2>
        <p className="wallet-note wallet-note--warn" role="note">
          {r.limitNote}
        </p>
      </section>

      <section className="explain" aria-labelledby="rewards-source-title">
        <h2 id="rewards-source-title">{r.sourceTitle}</h2>
        <p>{r.sourceNote}</p>
        <p>
          <a className="screen-card-link" href={REWARDS_DOC_URL}>
            {r.sourceLink}
          </a>
        </p>
      </section>
      <SeeAlso slug="/rewards/" />
    </main>
  );
}
