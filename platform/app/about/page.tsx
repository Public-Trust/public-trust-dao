"use client";

import Link from "next/link";
import { useI18n } from "@/components/Providers";

// Внешние адреса (тот же открытый репозиторий / главный сайт-витрина).
const CONSTITUTION_URL =
  "https://github.com/Public-Trust/public-trust-dao/blob/main/docs/CONSTITUTION.md";
const REGISTRY_URL =
  "https://github.com/Public-Trust/public-trust-dao/tree/main/governance/registry";
const SITE_URL = "https://public-trust.github.io/public-trust-dao/";

export default function AboutPage() {
  const { t } = useI18n();
  const a = t.about;

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{a.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="about-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="about-title">{a.title}</h1>
        <p className="lead">{a.lead}</p>
      </section>

      <section className="explain" aria-labelledby="about-what-title">
        <h2 id="about-what-title">{a.whatTitle}</h2>
        <ul className="plain-list">
          {a.what.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="about-now-title">
        <h2 id="about-now-title">{a.nowTitle}</h2>
        <p className="wallet-note wallet-note--warn" role="note">
          {a.nowNote}
        </p>
      </section>

      <section className="explain" aria-labelledby="about-start-title">
        <h2 id="about-start-title">{a.startTitle}</h2>
        <ul className="plain-list">
          {a.start.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="explain" aria-labelledby="about-honest-title">
        <h2 id="about-honest-title">{a.honestTitle}</h2>
        <ul className="plain-list">
          {a.honest.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="about-faq-title">
        <h2 id="about-faq-title">{a.faqTitle}</h2>
        <dl className="faq-list">
          {a.faq.map((item) => (
            <div className="faq-item" key={item.q}>
              <dt>{item.q}</dt>
              <dd>{item.a}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="explain" aria-labelledby="about-links-title">
        <h2 id="about-links-title">{a.linksTitle}</h2>
        <ul className="plain-list">
          <li>
            <a className="screen-card-link" href={CONSTITUTION_URL}>
              {a.constitutionLink} →
            </a>
          </li>
          <li>
            <a className="screen-card-link" href={REGISTRY_URL}>
              {a.registryLink} →
            </a>
          </li>
          <li>
            <a className="screen-card-link" href={SITE_URL}>
              {a.siteLink} →
            </a>
          </li>
        </ul>
      </section>
    </main>
  );
}
