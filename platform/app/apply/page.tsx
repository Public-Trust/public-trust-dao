"use client";

import { useCallback, useMemo, useState, type FormEvent } from "react";
import Link from "next/link";
import { useI18n } from "@/components/Providers";
import {
  PRIORITIES,
  buildDraft,
  draftToJson,
  looksLikePersonalData,
  validate,
  type ApplicationDraft,
  type DraftInput,
} from "@/lib/application";

const EMPTY: DraftInput = {
  priorityKey: "",
  need: "",
  directSpend: "",
  amount: "",
};

export default function ApplyPage() {
  const { t } = useI18n();
  const a = t.apply;

  const [input, setInput] = useState<DraftInput>(EMPTY);
  const [submitted, setSubmitted] = useState(false);
  const [draft, setDraft] = useState<ApplicationDraft | null>(null);
  const [copied, setCopied] = useState(false);

  const v = useMemo(() => validate(input), [input]);
  const personalData = useMemo(
    () => looksLikePersonalData(input.need, input.directSpend),
    [input.need, input.directSpend],
  );

  const set = useCallback(
    (key: keyof DraftInput, value: string) => {
      setInput((prev) => ({ ...prev, [key]: value }));
    },
    [],
  );

  const onSubmit = useCallback(
    (event: FormEvent) => {
      event.preventDefault();
      const built = buildDraft(input);
      if (!built) return; // браузерная и наша проверки не пройдены
      setDraft(built);
      setSubmitted(true);
      setCopied(false);
    },
    [input],
  );

  const startOver = useCallback(() => {
    setInput(EMPTY);
    setDraft(null);
    setSubmitted(false);
    setCopied(false);
  }, []);

  const copy = useCallback(async () => {
    if (!draft) return;
    try {
      await navigator.clipboard.writeText(draftToJson(draft));
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }, [draft]);

  const download = useCallback(() => {
    if (!draft) return;
    const blob = new Blob([draftToJson(draft)], {
      type: "application/json;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "aid-application-draft.json";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }, [draft]);

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{a.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="apply-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="apply-title">{a.title}</h1>
        <p className="lead">{a.lead}</p>
      </section>

      <section className="explain" aria-labelledby="privacy-title">
        <h2 id="privacy-title">{a.privacyTitle}</h2>
        <ul className="plain-list plain-list--check">
          {a.privacy.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      {submitted && draft ? (
        <section className="panel" aria-labelledby="draft-title">
          <div className="wallet-card draft-card" role="status" aria-live="polite">
            <p className="wallet-state">
              <span className="dot dot--ok" aria-hidden="true" />
              {a.draftTitle}
            </p>
            <p className="wallet-note">{a.draftLead}</p>
            <pre className="draft-json" tabIndex={0}>
              {draftToJson(draft)}
            </pre>
            <div className="cta-row">
              <button type="button" className="btn btn-primary" onClick={copy}>
                {copied ? a.copied : a.copy}
              </button>
              <button type="button" className="btn btn-ghost" onClick={download}>
                {a.download}
              </button>
              <button type="button" className="btn btn-ghost" onClick={startOver}>
                {a.startOver}
              </button>
            </div>
          </div>
        </section>
      ) : (
        <section className="panel" aria-labelledby="form-title">
          <h2 id="form-title">{a.formTitle}</h2>
          <form className="apply-form" onSubmit={onSubmit} noValidate>
            <div className="field">
              <label htmlFor="priority">{a.priorityLabel}</label>
              <p className="field-hint">{a.priorityHint}</p>
              <select
                id="priority"
                value={input.priorityKey}
                onChange={(e) => set("priorityKey", e.target.value)}
                required
              >
                <option value="">{a.priorityChoose}</option>
                {PRIORITIES.map((p) => (
                  <option key={p.key} value={p.key}>
                    {a.priorityLabels[p.key]}
                  </option>
                ))}
              </select>
            </div>

            <div className="field">
              <label htmlFor="need">{a.needLabel}</label>
              <p className="field-hint">{a.needHint}</p>
              <textarea
                id="need"
                rows={4}
                value={input.need}
                onChange={(e) => set("need", e.target.value)}
                placeholder={a.needPlaceholder}
                required
              />
            </div>

            <div className="field">
              <label htmlFor="spend">{a.spendLabel}</label>
              <p className="field-hint">{a.spendHint}</p>
              <textarea
                id="spend"
                rows={3}
                value={input.directSpend}
                onChange={(e) => set("directSpend", e.target.value)}
                placeholder={a.spendPlaceholder}
                required
              />
            </div>

            <div className="field">
              <label htmlFor="amount">{a.amountLabel}</label>
              <p className="field-hint">{a.amountHint}</p>
              <input
                id="amount"
                type="text"
                inputMode="text"
                value={input.amount}
                onChange={(e) => set("amount", e.target.value)}
                placeholder={a.amountPlaceholder}
              />
            </div>

            {personalData ? (
              <p className="wallet-note wallet-note--warn" role="alert">
                {a.personalDataWarn}
              </p>
            ) : null}

            <button type="submit" className="btn btn-primary" disabled={!v.ok}>
              {a.submit}
            </button>
          </form>
        </section>
      )}

      <section className="explain" aria-labelledby="how-title">
        <h2 id="how-title">{a.howTitle}</h2>
        <ul className="plain-list">
          {a.how.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
    </main>
  );
}
