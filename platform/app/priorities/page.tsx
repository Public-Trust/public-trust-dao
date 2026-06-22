"use client";

import Link from "next/link";
import { useI18n } from "@/components/Providers";
import SeeAlso from "@/components/SeeAlso";
import { PRIORITIES } from "@/lib/application";

// Зеркало нормативного документа docs/PRIORITIES.md внутри приложения.
// Короткие подписи уровней живут в apply.priorityLabels (переиспользуем),
// человеческие пояснения — в priorities.meanings (правило понятного языка
// PTD-0040). Данные приходят из слоя lib/application.ts, ничего не подгружается
// со стороны (рельса прозрачности).
const PRIORITIES_DOC_URL =
  "https://github.com/Public-Trust/public-trust-dao/blob/main/docs/PRIORITIES.md";

export default function PrioritiesPage() {
  const { t } = useI18n();
  const p = t.priorities;
  const labels = t.apply.priorityLabels;

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{p.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="priorities-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="priorities-title">{p.title}</h1>
        <p className="lead">{p.lead}</p>
      </section>

      <section className="explain" aria-labelledby="priorities-key-title">
        <h2 id="priorities-key-title">{p.keyTitle}</h2>
        <ul className="plain-list">
          {p.key.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="priorities-order-title">
        <h2 id="priorities-order-title">{p.orderTitle}</h2>
        <p className="field-hint">{p.orderHint}</p>
        <ol className="priority-list">
          {PRIORITIES.map((item) => (
            <li className="priority-item" key={item.key}>
              <span className="priority-label">{labels[item.key]}</span>
              <span className="priority-meaning">{p.meanings[item.key]}</span>
            </li>
          ))}
        </ol>
      </section>

      <section className="explain" aria-labelledby="priorities-how-title">
        <h2 id="priorities-how-title">{p.howTitle}</h2>
        <ul className="plain-list">
          {p.how.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="priorities-fair-title">
        <h2 id="priorities-fair-title">{p.fairTitle}</h2>
        <p className="wallet-note wallet-note--warn" role="note">
          {p.fairNote}
        </p>
        <p className="backlink">
          <Link className="screen-card-link" href="/apply/">
            {p.applyLink}
          </Link>
        </p>
      </section>

      <section className="explain" aria-labelledby="priorities-source-title">
        <h2 id="priorities-source-title">{p.sourceTitle}</h2>
        <p>{p.sourceNote}</p>
        <p>
          <a className="screen-card-link" href={PRIORITIES_DOC_URL}>
            {p.sourceLink}
          </a>
        </p>
      </section>
      <SeeAlso slug="/priorities/" />
    </main>
  );
}
