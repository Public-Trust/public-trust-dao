"use client";

import Link from "next/link";
import { useI18n } from "@/components/Providers";
import SeeAlso from "@/components/SeeAlso";

// Зеркало нормативного документа docs/MANIFESTO.md внутри приложения (тот же
// приём «экран-зеркало», что «Конституция» ↔ CONSTITUTION.md, «Как фонд
// принимает решения» ↔ GOVERNANCE.md, «Порядок помощи» ↔ PRIORITIES.md и др.):
// зачем существует фонд, кому помогает, чего не делает никогда и кому
// принадлежит — простым человеческим языком. Это экран-ОБЪЯСНЕНИЕ; полный
// нормативный текст — в самом документе по ссылке внизу. Тексты живут в
// lib/i18n.ts (ManifestoDict), ничего не подгружается со стороны (рельса
// прозрачности). Правило понятного языка — PTD-0040.
const MANIFESTO_DOC_URL =
  "https://github.com/Public-Trust/public-trust-dao/blob/main/docs/MANIFESTO.md";

export default function ManifestoPage() {
  const { t } = useI18n();
  const s = t.manifesto;

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{s.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="manifesto-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="manifesto-title">{s.title}</h1>
        <p className="lead">{s.lead}</p>
      </section>

      <section className="panel" aria-labelledby="manifesto-top-title">
        <h2 id="manifesto-top-title">{s.topTitle}</h2>
        <p className="wallet-note wallet-note--ok" role="note">
          {s.topNote}
        </p>
      </section>

      <section className="explain" aria-labelledby="manifesto-mission-title">
        <h2 id="manifesto-mission-title">{s.missionTitle}</h2>
        <p>{s.missionNote}</p>
      </section>

      <section className="panel" aria-labelledby="manifesto-directions-title">
        <h2 id="manifesto-directions-title">{s.directionsTitle}</h2>
        <p className="field-hint">{s.directionsHint}</p>
        <ul className="priority-list">
          {s.directions.map((dir) => (
            <li className="priority-item" key={dir.name}>
              <span className="priority-label">{dir.name}</span>
              <span className="priority-meaning">{dir.text}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="explain" aria-labelledby="manifesto-reward-title">
        <h2 id="manifesto-reward-title">{s.rewardTitle}</h2>
        <p>{s.rewardNote}</p>
      </section>

      <section className="panel" aria-labelledby="manifesto-prohibitions-title">
        <h2 id="manifesto-prohibitions-title">{s.prohibitionsTitle}</h2>
        <p className="field-hint">{s.prohibitionsHint}</p>
        <ul className="plain-list plain-list--check">
          {s.prohibitions.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="explain" aria-labelledby="manifesto-owner-title">
        <h2 id="manifesto-owner-title">{s.ownerTitle}</h2>
        <p>{s.ownerNote}</p>
      </section>

      <section className="explain" aria-labelledby="manifesto-ai-title">
        <h2 id="manifesto-ai-title">{s.aiTitle}</h2>
        <p>{s.aiNote}</p>
      </section>

      <section className="panel" aria-labelledby="manifesto-goal-title">
        <h2 id="manifesto-goal-title">{s.goalTitle}</h2>
        <p className="wallet-note wallet-note--ok" role="note">
          {s.goalNote}
        </p>
      </section>

      <section className="explain" aria-labelledby="manifesto-source-title">
        <h2 id="manifesto-source-title">{s.sourceTitle}</h2>
        <p>{s.sourceNote}</p>
        <p>
          <a className="screen-card-link" href={MANIFESTO_DOC_URL}>
            {s.sourceLink}
          </a>
        </p>
      </section>
      <SeeAlso slug="/manifesto/" />
    </main>
  );
}
