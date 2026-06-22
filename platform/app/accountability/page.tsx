"use client";

import Link from "next/link";
import { useI18n } from "@/components/Providers";
import SeeAlso from "@/components/SeeAlso";

// Зеркало нормативного документа docs/ACCOUNTABILITY.md внутри приложения
// (тот же приём, что «Порядок помощи» ↔ PRIORITIES.md, «Помощь и награда» ↔
// REWARDS-MODEL.md, «Защита от обмана» ↔ ANTI-ABUSE.md и «Оплачиваемая работа» ↔
// PROOF-OF-CONTRIBUTION.md): простым языком, как фонд держит всё под подписью и
// прослеживаемо — у каждого значимого действия есть автор, оно подписано и
// записано так, что переписать прошлое незаметно нельзя.
// Тексты живут в lib/i18n.ts (AccountabilityDict), ничего не подгружается со
// стороны (рельса прозрачности). Правило понятного языка — PTD-0040.
const ACCOUNTABILITY_DOC_URL =
  "https://github.com/Public-Trust/public-trust-dao/blob/main/docs/ACCOUNTABILITY.md";

export default function AccountabilityPage() {
  const { t } = useI18n();
  const s = t.accountability;

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{s.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="acc-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="acc-title">{s.title}</h1>
        <p className="lead">{s.lead}</p>
      </section>

      <section className="panel" aria-labelledby="acc-idea-title">
        <h2 id="acc-idea-title">{s.mainIdeaTitle}</h2>
        <p className="wallet-note wallet-note--ok" role="note">
          {s.mainIdea}
        </p>
      </section>

      <section className="explain" aria-labelledby="acc-key-title">
        <h2 id="acc-key-title">{s.keyTitle}</h2>
        <ul className="plain-list plain-list--check">
          {s.key.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="acc-levels-title">
        <h2 id="acc-levels-title">{s.levelsTitle}</h2>
        <p className="field-hint">{s.levelsHint}</p>
        <ul className="priority-list">
          {s.levels.map((level) => (
            <li className="priority-item" key={level.name}>
              <span className="priority-label">{level.name}</span>
              <span className="priority-meaning">{level.text}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="acc-roles-title">
        <h2 id="acc-roles-title">{s.rolesTitle}</h2>
        <p className="field-hint">{s.rolesHint}</p>
        <ul className="priority-list">
          {s.roles.map((role) => (
            <li className="priority-item" key={role.name}>
              <span className="priority-label">{role.name}</span>
              <span className="priority-meaning">{role.text}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="acc-ai-title">
        <h2 id="acc-ai-title">{s.aiTitle}</h2>
        <p className="wallet-note wallet-note--warn" role="note">
          {s.aiNote}
        </p>
      </section>

      <section className="panel" aria-labelledby="acc-limit-title">
        <h2 id="acc-limit-title">{s.limitTitle}</h2>
        <p className="wallet-note wallet-note--warn" role="note">
          {s.limitNote}
        </p>
      </section>

      <section className="explain" aria-labelledby="acc-source-title">
        <h2 id="acc-source-title">{s.sourceTitle}</h2>
        <p>{s.sourceNote}</p>
        <p>
          <a className="screen-card-link" href={ACCOUNTABILITY_DOC_URL}>
            {s.sourceLink}
          </a>
        </p>
      </section>
      <SeeAlso slug="/accountability/" />
    </main>
  );
}
