"use client";

import Link from "next/link";
import { useI18n } from "@/components/Providers";
import SeeAlso from "@/components/SeeAlso";

// Зеркало нормативного документа docs/ANTI-ABUSE.md внутри приложения
// (тот же приём, что «Порядок помощи» ↔ PRIORITIES.md и «Помощь и награда»
// ↔ REWARDS-MODEL.md): простым языком, как устроена защита общего кошелька —
// что мешает украсть, выманить обманом или потратить не на того, кому нужнее.
// Тексты живут в lib/i18n.ts (SafeguardsDict), ничего не подгружается со
// стороны (рельса прозрачности). Правило понятного языка — PTD-0040.
const SAFEGUARDS_DOC_URL =
  "https://github.com/Public-Trust/public-trust-dao/blob/main/docs/ANTI-ABUSE.md";

export default function SafeguardsPage() {
  const { t } = useI18n();
  const s = t.safeguards;

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{s.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="safeguards-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="safeguards-title">{s.title}</h1>
        <p className="lead">{s.lead}</p>
      </section>

      <section className="panel" aria-labelledby="safeguards-idea-title">
        <h2 id="safeguards-idea-title">{s.mainIdeaTitle}</h2>
        <p className="wallet-note wallet-note--ok" role="note">
          {s.mainIdea}
        </p>
      </section>

      <section className="explain" aria-labelledby="safeguards-key-title">
        <h2 id="safeguards-key-title">{s.keyTitle}</h2>
        <ul className="plain-list">
          {s.key.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="safeguards-pillars-title">
        <h2 id="safeguards-pillars-title">{s.pillarsTitle}</h2>
        <p className="field-hint">{s.pillarsHint}</p>
        <ul className="priority-list">
          {s.pillars.map((pillar) => (
            <li className="priority-item" key={pillar.name}>
              <span className="priority-label">{pillar.name}</span>
              <span className="priority-meaning">{pillar.text}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="explain" aria-labelledby="safeguards-rep-title">
        <h2 id="safeguards-rep-title">{s.repTitle}</h2>
        <p>{s.repNote}</p>
        <ul className="plain-list plain-list--check">
          {s.repBounds.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="safeguards-limit-title">
        <h2 id="safeguards-limit-title">{s.limitTitle}</h2>
        <p className="wallet-note wallet-note--warn" role="note">
          {s.limitNote}
        </p>
      </section>

      <section className="explain" aria-labelledby="safeguards-source-title">
        <h2 id="safeguards-source-title">{s.sourceTitle}</h2>
        <p>{s.sourceNote}</p>
        <p>
          <a className="screen-card-link" href={SAFEGUARDS_DOC_URL}>
            {s.sourceLink}
          </a>
        </p>
      </section>
      <SeeAlso slug="/safeguards/" />
    </main>
  );
}
