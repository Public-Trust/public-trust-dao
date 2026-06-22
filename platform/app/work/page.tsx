"use client";

import Link from "next/link";
import { useI18n } from "@/components/Providers";
import SeeAlso from "@/components/SeeAlso";

// Зеркало нормативного документа docs/PROOF-OF-CONTRIBUTION.md внутри приложения
// (тот же приём, что «Порядок помощи» ↔ PRIORITIES.md, «Помощь и награда» ↔
// REWARDS-MODEL.md и «Защита от обмана» ↔ ANTI-ABUSE.md): простым языком, как
// фонд создаёт честную оплачиваемую работу вокруг помощи и как доказуемо
// убеждается, что работа сделана, прежде чем за неё заплатить.
// Тексты живут в lib/i18n.ts (WorkDict), ничего не подгружается со стороны
// (рельса прозрачности). Правило понятного языка — PTD-0040.
const WORK_DOC_URL =
  "https://github.com/Public-Trust/public-trust-dao/blob/main/docs/PROOF-OF-CONTRIBUTION.md";

export default function WorkPage() {
  const { t } = useI18n();
  const s = t.work;

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{s.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="work-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="work-title">{s.title}</h1>
        <p className="lead">{s.lead}</p>
      </section>

      <section className="panel" aria-labelledby="work-idea-title">
        <h2 id="work-idea-title">{s.mainIdeaTitle}</h2>
        <p className="wallet-note wallet-note--ok" role="note">
          {s.mainIdea}
        </p>
      </section>

      <section className="panel" aria-labelledby="work-question-title">
        <h2 id="work-question-title">{s.questionTitle}</h2>
        <p className="wallet-note wallet-note--warn" role="note">
          {s.question}
        </p>
      </section>

      <section className="explain" aria-labelledby="work-key-title">
        <h2 id="work-key-title">{s.keyTitle}</h2>
        <ul className="plain-list">
          {s.key.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="work-formats-title">
        <h2 id="work-formats-title">{s.formatsTitle}</h2>
        <p className="field-hint">{s.formatsHint}</p>
        <ul className="priority-list">
          {s.formats.map((format) => (
            <li className="priority-item" key={format.name}>
              <span className="priority-label">{format.name}</span>
              <span className="priority-meaning">{format.text}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="explain" aria-labelledby="work-proof-title">
        <h2 id="work-proof-title">{s.proofTitle}</h2>
        <p className="field-hint">{s.proofHint}</p>
        <ul className="plain-list plain-list--check">
          {s.proof.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="work-honest-title">
        <h2 id="work-honest-title">{s.honestTitle}</h2>
        <p className="wallet-note wallet-note--warn" role="note">
          {s.honestNote}
        </p>
      </section>

      <section className="panel" aria-labelledby="work-limit-title">
        <h2 id="work-limit-title">{s.limitTitle}</h2>
        <p className="wallet-note wallet-note--warn" role="note">
          {s.limitNote}
        </p>
      </section>

      <section className="explain" aria-labelledby="work-source-title">
        <h2 id="work-source-title">{s.sourceTitle}</h2>
        <p>{s.sourceNote}</p>
        <p>
          <a className="screen-card-link" href={WORK_DOC_URL}>
            {s.sourceLink}
          </a>
        </p>
      </section>
      <SeeAlso slug="/work/" />
    </main>
  );
}
