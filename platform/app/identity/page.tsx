"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useI18n } from "@/components/Providers";
import {
  ACTION_LEVEL,
  METHODS,
  buildCheckNote,
  checkNoteToJson,
  clearMyChoice,
  getMyAction,
  getMyMethod,
  setMyAction,
  setMyMethod,
  usesBiometry,
  type IdentityAction,
  type IdentityMethod,
} from "@/lib/identity";

const IDENTITY_URL =
  "https://github.com/Public-Trust/public-trust-dao/blob/main/docs/IDENTITY-VERIFICATION.md";

const ACTIONS: IdentityAction[] = ["read", "apply", "vote", "receive"];

export default function IdentityPage() {
  const { t } = useI18n();
  const id = t.identity;

  // Выбор человека хранится только в его браузере. Читаем после монтирования,
  // чтобы статическая сборка и первый показ совпадали (без рассинхрона).
  const [action, setAction] = useState<IdentityAction | null>(null);
  const [method, setMethod] = useState<IdentityMethod | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setAction(getMyAction());
    setMethod(getMyMethod());
  }, []);

  const chooseAction = useCallback((a: IdentityAction) => {
    setMyAction(a);
    setAction(a);
    setCopied(false);
  }, []);

  const chooseMethod = useCallback((m: IdentityMethod) => {
    setMyMethod(m);
    setMethod(m);
    setCopied(false);
  }, []);

  const reset = useCallback(() => {
    clearMyChoice();
    setAction(null);
    setMethod(null);
    setCopied(false);
  }, []);

  const copy = useCallback(async () => {
    if (!action || !method) return;
    try {
      await navigator.clipboard.writeText(
        checkNoteToJson(buildCheckNote(action, method)),
      );
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }, [action, method]);

  const download = useCallback(() => {
    if (!action || !method) return;
    const blob = new Blob([checkNoteToJson(buildCheckNote(action, method))], {
      type: "application/json;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "identity-note-draft.json";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }, [action, method]);

  const level = action ? ACTION_LEVEL[action] : null;
  const ready = Boolean(action && method);

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{id.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="identity-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="identity-title">{id.title}</h1>
        <p className="lead">{id.lead}</p>
      </section>

      <section className="explain" aria-labelledby="identity-how-title">
        <h2 id="identity-how-title">{id.howTitle}</h2>
        <ul className="plain-list">
          {id.how.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      {/* Сколько проверки нужно — зависит от действия */}
      <section className="panel" aria-labelledby="identity-level-title">
        <h2 id="identity-level-title">{id.levelTitle}</h2>
        <p className="field-hint">{id.levelHint}</p>
        <div className="vote-buttons">
          {ACTIONS.map((a) => (
            <button
              key={a}
              type="button"
              className={action === a ? "btn btn-primary" : "btn btn-ghost"}
              aria-pressed={action === a}
              onClick={() => chooseAction(a)}
            >
              {id.actionLabels[a]}
            </button>
          ))}
        </div>
        {level ? (
          <div className="your-vote" role="status" aria-live="polite">
            <p className="wallet-state">
              <span className="badge badge--ready">{id.levelLabels[level]}</span>
            </p>
            <p className="field-hint">{id.levelMeaning[level]}</p>
          </div>
        ) : (
          <p className="field-hint">{id.levelPrompt}</p>
        )}
      </section>

      {/* Каким способом проверяться — выбирает сам человек */}
      <section className="panel" aria-labelledby="identity-method-title">
        <h2 id="identity-method-title">{id.methodTitle}</h2>
        <p className="field-hint">{id.methodHint}</p>
        <ul className="split-list">
          {METHODS.map((m) => (
            <li key={m} className="split-row">
              <div className="split-row-main">
                <button
                  type="button"
                  className={method === m ? "btn btn-primary" : "btn btn-ghost"}
                  aria-pressed={method === m}
                  onClick={() => chooseMethod(m)}
                >
                  {id.methodLabels[m]}
                </button>
                <span className={usesBiometry(m) ? "badge badge--warn" : "badge badge--ready"}>
                  {usesBiometry(m) ? id.biometryYes : id.biometryNo}
                </span>
              </div>
              <p className="split-hint">{id.methodText[m]}</p>
            </li>
          ))}
        </ul>
      </section>

      {/* Жёсткая граница: уникальность — не власть */}
      <section className="explain" aria-labelledby="identity-boundary-title">
        <h2 id="identity-boundary-title">{id.boundaryTitle}</h2>
        <p className="wallet-note wallet-note--warn" role="note">
          {id.boundaryText}
        </p>
      </section>

      {/* Запасной путь без камеры */}
      <section className="explain" aria-labelledby="identity-backup-title">
        <h2 id="identity-backup-title">{id.backupTitle}</h2>
        <p>{id.backupText}</p>
      </section>

      {/* Проверяемая памятка-черновик (ничего не уходит наружу) */}
      <section className="panel" aria-labelledby="identity-note-title">
        <h2 id="identity-note-title">{id.noteTitle}</h2>
        <p className="wallet-note wallet-note--warn" role="note">
          {id.demoNote}
        </p>
        {ready && action && method ? (
          <div className="your-vote" role="status" aria-live="polite">
            <p className="wallet-note">{id.noteLead}</p>
            <pre className="draft-json" tabIndex={0}>
              {checkNoteToJson(buildCheckNote(action, method))}
            </pre>
            <div className="cta-row">
              <button type="button" className="btn btn-primary" onClick={copy}>
                {copied ? id.copied : id.copy}
              </button>
              <button type="button" className="btn btn-ghost" onClick={download}>
                {id.download}
              </button>
              <button type="button" className="btn btn-ghost" onClick={reset}>
                {id.startOver}
              </button>
            </div>
          </div>
        ) : (
          <p className="field-hint">{id.notePrompt}</p>
        )}
      </section>

      <section className="explain" aria-labelledby="identity-verify-title">
        <h2 id="identity-verify-title">{id.privacyTitle}</h2>
        <ul className="plain-list">
          {id.privacy.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
        <p>
          <a className="screen-card-link" href={IDENTITY_URL}>
            {id.verifyLink} →
          </a>
        </p>
      </section>
    </main>
  );
}
