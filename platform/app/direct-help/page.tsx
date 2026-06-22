"use client";

import Link from "next/link";
import { useI18n } from "@/components/Providers";

// Зеркало нормативного документа docs/ESCROW-TARGETED-DISBURSEMENT.md внутри
// приложения (тот же приём «экран-зеркало», что «Порядок помощи» ↔ PRIORITIES.md,
// «Помощь и награда» ↔ REWARDS-MODEL.md, «Защита от обмана» ↔ ANTI-ABUSE.md,
// «Оплачиваемая работа» ↔ PROOF-OF-CONTRIBUTION.md, «Всё под подписью» ↔
// ACCOUNTABILITY.md): простым языком, как фонд оплачивает нужду напрямую
// поставщику — не выдаёт деньги на руки, а сам платит за жильё, лекарство, еду.
// Тексты живут в lib/i18n.ts (EscrowDict), ничего не подгружается со стороны
// (рельса прозрачности). Правило понятного языка — PTD-0040.
const ESCROW_DOC_URL =
  "https://github.com/Public-Trust/public-trust-dao/blob/main/docs/ESCROW-TARGETED-DISBURSEMENT.md";

export default function DirectHelpPage() {
  const { t } = useI18n();
  const s = t.escrow;

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{s.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="escrow-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="escrow-title">{s.title}</h1>
        <p className="lead">{s.lead}</p>
      </section>

      <section className="panel" aria-labelledby="escrow-idea-title">
        <h2 id="escrow-idea-title">{s.mainIdeaTitle}</h2>
        <p className="wallet-note wallet-note--ok" role="note">
          {s.mainIdea}
        </p>
      </section>

      <section className="explain" aria-labelledby="escrow-key-title">
        <h2 id="escrow-key-title">{s.keyTitle}</h2>
        <ul className="plain-list plain-list--check">
          {s.key.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="escrow-ways-title">
        <h2 id="escrow-ways-title">{s.waysTitle}</h2>
        <p className="field-hint">{s.waysHint}</p>
        <ul className="priority-list">
          {s.ways.map((way) => (
            <li className="priority-item" key={way.name}>
              <span className="priority-label">{way.name}</span>
              <span className="priority-meaning">{way.text}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="escrow-disclosure-title">
        <h2 id="escrow-disclosure-title">{s.disclosureTitle}</h2>
        <p className="field-hint">{s.disclosureHint}</p>
        <ul className="priority-list">
          {s.disclosure.map((row) => (
            <li className="priority-item" key={row.open}>
              <span className="priority-label">{row.open}</span>
              <span className="priority-meaning">{row.closed}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="escrow-limit-title">
        <h2 id="escrow-limit-title">{s.limitTitle}</h2>
        <p className="wallet-note wallet-note--warn" role="note">
          {s.limitNote}
        </p>
      </section>

      <section className="explain" aria-labelledby="escrow-source-title">
        <h2 id="escrow-source-title">{s.sourceTitle}</h2>
        <p>{s.sourceNote}</p>
        <p>
          <a className="screen-card-link" href={ESCROW_DOC_URL}>
            {s.sourceLink}
          </a>
        </p>
      </section>
    </main>
  );
}
