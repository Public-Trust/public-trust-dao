"use client";

import { useI18n } from "@/components/Providers";

export function SiteHeader() {
  const { t, toggleLang, toggleTheme } = useI18n();

  return (
    <header className="site-header">
      <a className="skip-link" href="#main">
        {t.skipToContent}
      </a>
      <div className="container header-inner">
        <a className="brand" href="#main">
          <span className="brand-name">{t.brand}</span>
          <span className="brand-tagline">{t.tagline}</span>
        </a>
        <div className="nav-tools">
          <button
            type="button"
            className="tool-btn"
            onClick={toggleLang}
            aria-label={t.toggleLang}
          >
            {t.toggleLangShort}
          </button>
          <button
            type="button"
            className="tool-btn"
            onClick={toggleTheme}
            aria-label={t.toggleTheme}
            title={t.toggleTheme}
          >
            <span aria-hidden="true">◐</span>
          </button>
        </div>
      </div>
    </header>
  );
}
