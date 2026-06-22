"use client";

import Link from "next/link";
import { useI18n } from "@/components/Providers";

// Зеркало нормативного документа docs/CONSTITUTION.md внутри приложения (тот же
// приём «экран-зеркало», что «Порядок помощи» ↔ PRIORITIES.md, «Помощь и
// награда» ↔ REWARDS-MODEL.md, «Защита от обмана» ↔ ANTI-ABUSE.md, «Оплачиваемая
// работа» ↔ PROOF-OF-CONTRIBUTION.md, «Всё под подписью» ↔ ACCOUNTABILITY.md,
// «Оплата напрямую» ↔ ESCROW-TARGETED-DISBURSEMENT.md): высший закон фонда,
// 10 статей пересказаны простым человеческим языком, плюс неизменяемое ядро.
// Тексты живут в lib/i18n.ts (ConstitutionDict), ничего не подгружается со
// стороны (рельса прозрачности). Правило понятного языка — PTD-0040.
const CONSTITUTION_DOC_URL =
  "https://github.com/Public-Trust/public-trust-dao/blob/main/docs/CONSTITUTION.md";

export default function ConstitutionPage() {
  const { t } = useI18n();
  const s = t.constitution;

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{s.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="constitution-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="constitution-title">{s.title}</h1>
        <p className="lead">{s.lead}</p>
      </section>

      <section className="panel" aria-labelledby="constitution-top-title">
        <h2 id="constitution-top-title">{s.topTitle}</h2>
        <p className="wallet-note wallet-note--ok" role="note">
          {s.topNote}
        </p>
      </section>

      <section className="panel" aria-labelledby="constitution-articles-title">
        <h2 id="constitution-articles-title">{s.articlesTitle}</h2>
        <p className="field-hint">{s.articlesHint}</p>
        <ul className="priority-list">
          {s.articles.map((article) => (
            <li className="priority-item" key={article.name}>
              <span className="priority-label">{article.name}</span>
              <span className="priority-meaning">{article.text}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="explain" aria-labelledby="constitution-core-title">
        <h2 id="constitution-core-title">{s.coreTitle}</h2>
        <p className="field-hint">{s.coreHint}</p>
        <ul className="plain-list plain-list--check">
          {s.core.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="constitution-limit-title">
        <h2 id="constitution-limit-title">{s.limitTitle}</h2>
        <p className="wallet-note wallet-note--warn" role="note">
          {s.limitNote}
        </p>
      </section>

      <section className="explain" aria-labelledby="constitution-source-title">
        <h2 id="constitution-source-title">{s.sourceTitle}</h2>
        <p>{s.sourceNote}</p>
        <p>
          <a className="screen-card-link" href={CONSTITUTION_DOC_URL}>
            {s.sourceLink}
          </a>
        </p>
      </section>
    </main>
  );
}
