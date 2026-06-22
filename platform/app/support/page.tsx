"use client";

import Link from "next/link";
import { useI18n } from "@/components/Providers";
import SeeAlso from "@/components/SeeAlso";

// Зеркало нормативного документа docs/SUPPORT-MODEL.md внутри приложения (тот же
// приём «экран-зеркало», что «Манифест» ↔ MANIFESTO.md, «Конституция» ↔
// CONSTITUTION.md, «Как фонд принимает решения» ↔ GOVERNANCE.md и др.): как фонд
// принимает поддержку — из самой работающей системы, а не отдельной кнопкой
// сбоку — простым человеческим языком. Это экран-ОБЪЯСНЕНИЕ; полный нормативный
// текст — в самом документе по ссылке внизу. Тексты живут в lib/i18n.ts
// (SupportDict), ничего не подгружается со стороны (рельса прозрачности).
// Правило понятного языка — PTD-0040.
const SUPPORT_DOC_URL =
  "https://github.com/Public-Trust/public-trust-dao/blob/main/docs/SUPPORT-MODEL.md";

export default function SupportPage() {
  const { t } = useI18n();
  const s = t.support;

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{s.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="support-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="support-title">{s.title}</h1>
        <p className="lead">{s.lead}</p>
      </section>

      <section className="panel" aria-labelledby="support-top-title">
        <h2 id="support-top-title">{s.topTitle}</h2>
        <p className="wallet-note wallet-note--ok" role="note">
          {s.topNote}
        </p>
      </section>

      <section className="explain" aria-labelledby="support-why-title">
        <h2 id="support-why-title">{s.whyTitle}</h2>
        <p>{s.whyNote}</p>
      </section>

      <section className="panel" aria-labelledby="support-how-title">
        <h2 id="support-how-title">{s.howTitle}</h2>
        <p className="field-hint">{s.howHint}</p>
        <ul className="plain-list">
          {s.how.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="support-constitution-title">
        <h2 id="support-constitution-title">{s.constitutionTitle}</h2>
        <p className="field-hint">{s.constitutionHint}</p>
        <ul className="priority-list">
          {s.constitution.map((rule) => (
            <li className="priority-item" key={rule.name}>
              <span className="priority-label">{rule.name}</span>
              <span className="priority-meaning">{rule.text}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="support-now-title">
        <h2 id="support-now-title">{s.nowTitle}</h2>
        <p className="field-hint">{s.nowHint}</p>
        <ul className="plain-list">
          {s.now.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="support-notdoing-title">
        <h2 id="support-notdoing-title">{s.notDoingTitle}</h2>
        <p className="field-hint">{s.notDoingHint}</p>
        <ul className="plain-list plain-list--check">
          {s.notDoing.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="explain" aria-labelledby="support-plain-title">
        <h2 id="support-plain-title">{s.plainTitle}</h2>
        <p>{s.plainNote}</p>
      </section>

      <section className="panel" aria-labelledby="support-safety-title">
        <h2 id="support-safety-title">{s.safetyTitle}</h2>
        <p className="wallet-note wallet-note--warn" role="note">
          {s.safetyNote}
        </p>
      </section>

      <section className="explain" aria-labelledby="support-source-title">
        <h2 id="support-source-title">{s.sourceTitle}</h2>
        <p>{s.sourceNote}</p>
        <p>
          <a className="screen-card-link" href={SUPPORT_DOC_URL}>
            {s.sourceLink}
          </a>
        </p>
      </section>
      <SeeAlso slug="/support/" />
    </main>
  );
}
