"use client";

import Link from "next/link";
import { useI18n } from "@/components/Providers";

// Адреса наружу (тот же открытый репозиторий / главный сайт-витрина).
const REGISTRY_URL =
  "https://github.com/Public-Trust/public-trust-dao/tree/main/governance/registry";
const SITE_URL = "https://public-trust.github.io/public-trust-dao/";

export default function Home() {
  const { t } = useI18n();

  return (
    <main id="main" className="container">
      <section className="hero" aria-labelledby="hero-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="hero-title">{t.heroTitle}</h1>
        <p className="lead">{t.heroLead}</p>
        <div className="cta-row">
          <a className="btn btn-primary" href={REGISTRY_URL}>
            {t.ctaRegistry}
          </a>
          <a className="btn btn-ghost" href={SITE_URL}>
            {t.ctaSite}
          </a>
        </div>
      </section>

      <section className="screens" aria-labelledby="screens-title">
        <h2 id="screens-title">{t.screensTitle}</h2>
        <p className="lead">{t.screensLead}</p>
        <ul className="screen-grid">
          {t.screens.map((screen) => (
            <li
              key={screen.title}
              className={
                screen.href ? "screen-card screen-card--ready" : "screen-card"
              }
            >
              <div className="screen-card-head">
                <h3>{screen.title}</h3>
                <span className={screen.href ? "badge badge--ready" : "badge"}>
                  {screen.href ? t.ready : t.soon}
                </span>
              </div>
              <p>{screen.text}</p>
              {screen.href ? (
                <Link className="screen-card-link" href={screen.href}>
                  {t.open} →
                </Link>
              ) : null}
            </li>
          ))}
        </ul>
      </section>

      <section className="transparency" aria-labelledby="transparency-title">
        <h2 id="transparency-title">{t.transparencyTitle}</h2>
        <p>{t.transparencyText}</p>
      </section>
    </main>
  );
}
