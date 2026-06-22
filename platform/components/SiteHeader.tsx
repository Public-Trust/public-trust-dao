"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useI18n } from "@/components/Providers";

// Убираем хвостовой слэш, чтобы «/wallet/» и «/wallet» считались одним адресом.
function normalizePath(path: string): string {
  if (path.length > 1 && path.endsWith("/")) {
    return path.slice(0, -1);
  }
  return path;
}

export function SiteHeader() {
  const { t, toggleLang, toggleTheme } = useI18n();
  const pathname = normalizePath(usePathname());

  // Постоянное меню платформы: главная + готовые экраны (у которых есть адрес).
  const navItems = [
    { label: t.navHome, href: "/" },
    { label: t.navAbout, href: "/about/" },
    { label: t.navPriorities, href: "/priorities/" },
    { label: t.navRewards, href: "/rewards/" },
    { label: t.navSafeguards, href: "/safeguards/" },
    { label: t.navWork, href: "/work/" },
    { label: t.navAccountability, href: "/accountability/" },
    ...t.screens
      .filter((s) => s.href)
      .map((s) => ({ label: s.short ?? s.title, href: s.href as string })),
    { label: t.navGlossary, href: "/glossary/" },
    { label: t.navMyData, href: "/privacy/" },
  ];

  return (
    <header className="site-header">
      <a className="skip-link" href="#main">
        {t.skipToContent}
      </a>
      <div className="container header-inner">
        <Link className="brand" href="/">
          <span className="brand-name">{t.brand}</span>
          <span className="brand-tagline">{t.tagline}</span>
        </Link>
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
      <nav className="primary-nav" aria-label={t.navLabel}>
        <ul className="container primary-nav-list">
          {navItems.map((item) => {
            const active = normalizePath(item.href) === pathname;
            return (
              <li key={item.href}>
                <Link
                  className={active ? "nav-link nav-link--active" : "nav-link"}
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                >
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </header>
  );
}
