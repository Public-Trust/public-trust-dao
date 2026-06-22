"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useI18n } from "@/components/Providers";
import {
  clearAll,
  clearOne,
  exportAll,
  listStored,
  type StoredEntry,
} from "@/lib/storage";

// Превратить запись из браузера в понятную человеку пару «подпись · значение».
// Тексты берём из словаря текущего языка; неизвестные значения показываем как
// есть (честно), но без личных данных там и так ничего нет.
function describe(
  entry: StoredEntry,
  d: ReturnType<typeof useI18n>["t"]["myData"],
): { label: string; value: string } {
  const m = d;
  switch (entry.kind) {
    case "identity-action": {
      const v = m.identityActionValue;
      const known =
        entry.value === "read" ||
        entry.value === "apply" ||
        entry.value === "vote" ||
        entry.value === "receive";
      return {
        label: m.kindLabels.identityAction,
        value: known ? v[entry.value as keyof typeof v] : entry.value,
      };
    }
    case "identity-method": {
      const v = m.identityMethodValue;
      const known =
        entry.value === "social" ||
        entry.value === "passport" ||
        entry.value === "liveness" ||
        entry.value === "vouch";
      return {
        label: m.kindLabels.identityMethod,
        value: known ? v[entry.value as keyof typeof v] : entry.value,
      };
    }
    case "vote": {
      const v = m.voteChoice;
      const known =
        entry.value === "for" ||
        entry.value === "against" ||
        entry.value === "abstain";
      const ref = entry.ref ? ` ${m.voteRefLabel} ${entry.ref}` : "";
      return {
        label: `${m.kindLabels.vote}${ref}`,
        value: known ? v[entry.value as keyof typeof v] : entry.value,
      };
    }
    default:
      return {
        label: m.kindLabels.other,
        value: `${m.rawLabel}: ${entry.value}`,
      };
  }
}

export default function MyDataPage() {
  const { t } = useI18n();
  const m = t.myData;

  // Записи читаем только в браузере после монтирования: на сервере их нет, и
  // статическая сборка должна совпасть с первым показом (без рассинхрона).
  const [entries, setEntries] = useState<StoredEntry[]>([]);
  const [mounted, setMounted] = useState(false);

  const refresh = useCallback(() => {
    setEntries(listStored());
  }, []);

  useEffect(() => {
    setMounted(true);
    refresh();
  }, [refresh]);

  const removeOne = useCallback(
    (key: string) => {
      clearOne(key);
      refresh();
    },
    [refresh],
  );

  const removeAll = useCallback(() => {
    clearAll();
    refresh();
  }, [refresh]);

  // Скачать копию данных одним файлом. Всё происходит в браузере: собираем
  // снимок, делаем из него файл и отдаём через временную ссылку — наружу ничего
  // не уходит. Объект-URL сразу освобождаем, чтобы не копить в памяти.
  const downloadAll = useCallback(() => {
    const blob = new Blob([JSON.stringify(exportAll(), null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "public-trust-dao-my-data.json";
    link.click();
    URL.revokeObjectURL(url);
  }, []);

  const hasEntries = mounted && entries.length > 0;

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{m.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="mydata-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="mydata-title">{m.title}</h1>
        <p className="lead">{m.lead}</p>
      </section>

      <section className="explain" aria-labelledby="mydata-why-title">
        <h2 id="mydata-why-title">{m.whyTitle}</h2>
        <ul className="plain-list">
          {m.why.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="mydata-stored-title">
        <h2 id="mydata-stored-title">{m.storedTitle}</h2>
        <p className="field-hint">{m.storedHint}</p>

        {hasEntries ? (
          <>
            <ul className="split-list">
              {entries.map((entry) => {
                const { label, value } = describe(entry, m);
                return (
                  <li key={entry.key} className="split-row">
                    <div className="split-row-main">
                      <span className="badge badge--ready">{label}</span>
                      <button
                        type="button"
                        className="btn btn-ghost"
                        onClick={() => removeOne(entry.key)}
                      >
                        {m.remove}
                      </button>
                    </div>
                    <p className="split-hint">{value}</p>
                  </li>
                );
              })}
            </ul>
            <div className="cta-row">
              <button
                type="button"
                className="btn btn-primary"
                onClick={removeAll}
              >
                {m.removeAll}
              </button>
            </div>
          </>
        ) : (
          <p className="field-hint" role="status" aria-live="polite">
            {m.empty}
          </p>
        )}
      </section>

      {hasEntries && (
        <section className="panel" aria-labelledby="mydata-export-title">
          <h2 id="mydata-export-title">{m.exportTitle}</h2>
          <p className="field-hint">{m.exportHint}</p>
          <div className="cta-row">
            <button
              type="button"
              className="btn btn-ghost"
              onClick={downloadAll}
            >
              {m.exportButton}
            </button>
          </div>
        </section>
      )}

      <section className="explain" aria-labelledby="mydata-wallet-title">
        <h2 id="mydata-wallet-title">{t.wallet.title}</h2>
        <p className="wallet-note" role="note">
          {m.walletNote}
        </p>
      </section>
    </main>
  );
}
