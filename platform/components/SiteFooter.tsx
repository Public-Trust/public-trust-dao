"use client";

import { useI18n } from "@/components/Providers";

export function SiteFooter() {
  const { t } = useI18n();

  return (
    <footer className="site-footer">
      <div className="container">
        <p className="footer-note">{t.footerNote}</p>
        <p className="footer-meta">
          <span>{t.builtNote}</span>
          <span className="dot" aria-hidden="true">
            ·
          </span>
          <span>{t.contact}: </span>
          <a href="mailto:fedorgrigorev@proton.me">fedorgrigorev@proton.me</a>
        </p>
      </div>
    </footer>
  );
}
