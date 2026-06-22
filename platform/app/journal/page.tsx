"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useI18n } from "@/components/Providers";
import {
  COUNT,
  ENTRIES,
  HEAD_HASH,
  PRESENT_TYPES,
  recordUrl,
  search,
  shortDate,
  shortHash,
} from "@/lib/journal";

const REGISTRY_URL =
  "https://github.com/Public-Trust/public-trust-dao/tree/main/governance/registry";

export default function JournalPage() {
  const { t } = useI18n();
  const j = t.journal;

  const [type, setType] = useState<string>("all");
  const [query, setQuery] = useState<string>("");

  const visible = useMemo(() => {
    const byType =
      type === "all" ? ENTRIES : ENTRIES.filter((e) => e.type === type);
    return search(byType, query);
  }, [type, query]);

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{j.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="journal-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="journal-title">{j.title}</h1>
        <p className="lead">{j.lead}</p>
      </section>

      <section className="explain" aria-labelledby="what-title">
        <h2 id="what-title">{j.whatTitle}</h2>
        <p>{j.whatText}</p>
        <dl className="wallet-facts journal-facts">
          <div>
            <dt>{j.countLabel}</dt>
            <dd>{COUNT}</dd>
          </div>
          <div>
            <dt>{j.headHashLabel}</dt>
            <dd>
              <code title={HEAD_HASH}>{shortHash(HEAD_HASH)}</code>
            </dd>
          </div>
        </dl>
        <p className="field-hint">{j.headHashHint}</p>
      </section>

      <section className="panel" aria-labelledby="list-title">
        <h2 id="list-title" className="visually-hidden">
          {j.title}
        </h2>

        <div className="journal-controls">
          <div className="field">
            <label htmlFor="filter-type">{j.filterLabel}</label>
            <select
              id="filter-type"
              value={type}
              onChange={(e) => setType(e.target.value)}
            >
              <option value="all">{j.filterAll}</option>
              {PRESENT_TYPES.map((rt) => (
                <option key={rt} value={rt}>
                  {j.typeLabels[rt] ?? rt}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="search">{j.searchLabel}</label>
            <input
              id="search"
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={j.searchPlaceholder}
            />
          </div>
        </div>

        <p className="field-hint" role="status" aria-live="polite">
          {j.showing} {visible.length}
        </p>

        {visible.length === 0 ? (
          <p className="wallet-note">{j.nothingFound}</p>
        ) : (
          <ol className="journal-list">
            {visible.map((e) => (
              <li key={e.id} className="journal-item">
                <div className="journal-item-head">
                  <span className="journal-id">{e.id}</span>
                  <span className="badge">{j.typeLabels[e.type] ?? e.type}</span>
                  <span className="journal-date">{shortDate(e.timestamp)}</span>
                </div>
                <p className="journal-summary">{e.summary}</p>
                <div className="journal-item-foot">
                  <span className="journal-hash">
                    {j.hashLabel}: <code title={e.hash}>{shortHash(e.hash)}</code>
                  </span>
                  <a
                    className="screen-card-link"
                    href={recordUrl(e.file)}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {j.viewRecord}
                  </a>
                </div>
              </li>
            ))}
          </ol>
        )}
      </section>

      <section className="explain" aria-labelledby="how-title">
        <h2 id="how-title">{j.howTitle}</h2>
        <ul className="plain-list">
          {j.how.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
        <p>
          <a className="screen-card-link" href={REGISTRY_URL}>
            {j.verifyLink} →
          </a>
        </p>
      </section>
    </main>
  );
}
