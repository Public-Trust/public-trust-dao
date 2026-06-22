"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useI18n } from "@/components/Providers";
import SeeAlso from "@/components/SeeAlso";
import { countTerms, searchGlossary } from "@/lib/glossary";

// Полный нормативный глоссарий в открытом репозитории — словарь на экране
// является его зеркалом простым языком.
const GLOSSARY_URL =
  "https://github.com/Public-Trust/public-trust-dao/blob/main/docs/GLOSSARY.md";

export default function GlossaryPage() {
  const { t } = useI18n();
  const g = t.glossary;

  const [query, setQuery] = useState<string>("");

  const visible = useMemo(() => searchGlossary(g.groups, query), [g.groups, query]);
  const total = useMemo(() => countTerms(g.groups), [g.groups]);
  const shown = useMemo(() => countTerms(visible), [visible]);

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{g.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="glossary-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="glossary-title">{g.title}</h1>
        <p className="lead">{g.lead}</p>
      </section>

      <section className="panel" aria-labelledby="glossary-key-title">
        <h2 id="glossary-key-title">{g.keyTitle}</h2>
        <ul className="plain-list">
          {g.key.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="glossary-search-title">
        <h2 id="glossary-search-title" className="visually-hidden">
          {g.searchLabel}
        </h2>
        <div className="field">
          <label htmlFor="glossary-search">{g.searchLabel}</label>
          <input
            id="glossary-search"
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={g.searchPlaceholder}
          />
        </div>
        <p className="field-hint" role="status" aria-live="polite">
          {query.trim() ? `${shown} / ${total}` : `${total} ${g.countLabel}`}
        </p>
      </section>

      {visible.length === 0 ? (
        <p className="wallet-note">{g.nothingFound}</p>
      ) : (
        visible.map((group) => (
          <section
            key={group.id}
            className="explain"
            aria-labelledby={`group-${group.id}`}
          >
            <h2 id={`group-${group.id}`}>{group.title}</h2>
            <dl className="faq-list glossary-list">
              {group.entries.map((entry) => (
                <div className="faq-item" key={entry.term}>
                  <dt>{entry.term}</dt>
                  <dd>{entry.def}</dd>
                </div>
              ))}
            </dl>
          </section>
        ))
      )}

      <section className="explain" aria-labelledby="glossary-source-title">
        <h2 id="glossary-source-title">{g.sourceTitle}</h2>
        <p>{g.sourceNote}</p>
        <p>
          <a className="screen-card-link" href={GLOSSARY_URL}>
            {g.sourceLink} →
          </a>
        </p>
      </section>
      <SeeAlso slug="/glossary/" />
    </main>
  );
}
