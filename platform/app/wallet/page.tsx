"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useI18n } from "@/components/Providers";
import {
  getAccounts,
  getChainId,
  getProvider,
  hasWallet,
  isTestnet,
  networkName,
  requestAccounts,
  shortAddress,
} from "@/lib/wallet";

type Status = "idle" | "connecting" | "connected" | "no-wallet" | "error";

const METAMASK_URL = "https://metamask.io/download/";

export default function WalletPage() {
  const { t, lang } = useI18n();
  const w = t.wallet;

  const [status, setStatus] = useState<Status>("idle");
  const [account, setAccount] = useState<string | null>(null);
  const [chainId, setChainId] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // При загрузке: есть ли кошелёк и не подключён ли он уже (без запроса доступа).
  useEffect(() => {
    if (!hasWallet()) {
      setStatus("no-wallet");
      return;
    }
    let active = true;
    void (async () => {
      const accounts = await getAccounts();
      const id = await getChainId();
      if (!active) return;
      setChainId(id);
      if (accounts.length > 0) {
        setAccount(accounts[0]);
        setStatus("connected");
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  // Реакция на смену счёта/сети прямо в кошельке.
  useEffect(() => {
    const provider = getProvider();
    if (!provider?.on || !provider.removeListener) return;
    const onAccounts = (...args: unknown[]) => {
      const accounts = Array.isArray(args[0]) ? (args[0] as string[]) : [];
      if (accounts.length > 0) {
        setAccount(accounts[0]);
        setStatus("connected");
      } else {
        setAccount(null);
        setStatus("idle");
      }
    };
    const onChain = (...args: unknown[]) => {
      setChainId(typeof args[0] === "string" ? args[0] : null);
    };
    provider.on("accountsChanged", onAccounts);
    provider.on("chainChanged", onChain);
    return () => {
      provider.removeListener?.("accountsChanged", onAccounts);
      provider.removeListener?.("chainChanged", onChain);
    };
  }, []);

  const connect = useCallback(async () => {
    setErrorMsg(null);
    if (!hasWallet()) {
      setStatus("no-wallet");
      return;
    }
    setStatus("connecting");
    try {
      const accounts = await requestAccounts();
      const id = await getChainId();
      setChainId(id);
      if (accounts.length > 0) {
        setAccount(accounts[0]);
        setStatus("connected");
      } else {
        setStatus("idle");
      }
    } catch (err) {
      const noWallet = err instanceof Error && err.message === "no-wallet";
      setErrorMsg(noWallet ? w.errNoWallet : w.errRejected);
      setStatus(noWallet ? "no-wallet" : "error");
    }
  }, [w]);

  // «Отключить» = забыть выбор на стороне приложения. У кошелька нет
  // программного «выхода»: полный отзыв доступа делается в самом кошельке.
  const forget = useCallback(() => {
    setAccount(null);
    setStatus("idle");
    setErrorMsg(null);
  }, []);

  const testnet = isTestnet(chainId);

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{w.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="wallet-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="wallet-title">{w.title}</h1>
        <p className="lead">{w.lead}</p>
      </section>

      <section className="panel" aria-labelledby="connect-title">
        <h2 id="connect-title" className="visually-hidden">
          {w.connect}
        </h2>

        {status === "connected" && account ? (
          <div className="wallet-card" role="status" aria-live="polite">
            <p className="wallet-state">
              <span className="dot dot--ok" aria-hidden="true" />
              {w.connected}
            </p>
            <dl className="wallet-facts">
              <div>
                <dt>{w.yourAddress}</dt>
                <dd>
                  <code title={account}>{shortAddress(account)}</code>
                </dd>
              </div>
              <div>
                <dt>{w.network}</dt>
                <dd>{networkName(chainId, lang)}</dd>
              </div>
            </dl>
            {testnet === false ? (
              <p className="wallet-note wallet-note--warn">{w.testnetWarn}</p>
            ) : testnet === true ? (
              <p className="wallet-note wallet-note--ok">{w.testnetOk}</p>
            ) : (
              <p className="wallet-note">{w.testnetUnknown}</p>
            )}
            <button type="button" className="btn btn-ghost" onClick={forget}>
              {w.forget}
            </button>
          </div>
        ) : status === "no-wallet" ? (
          <div className="wallet-card" role="status">
            <h3>{w.noWalletTitle}</h3>
            <p>{w.noWalletText}</p>
            <a
              className="btn btn-ghost"
              href={METAMASK_URL}
              target="_blank"
              rel="noreferrer noopener"
            >
              {w.noWalletLink}
            </a>
          </div>
        ) : (
          <div className="wallet-card">
            <button
              type="button"
              className="btn btn-primary"
              onClick={connect}
              disabled={status === "connecting"}
            >
              {status === "connecting" ? w.connecting : w.connect}
            </button>
            {errorMsg ? (
              <p className="wallet-note wallet-note--warn" role="alert">
                {errorMsg}
              </p>
            ) : null}
          </div>
        )}
      </section>

      <section className="explain" aria-labelledby="what-title">
        <h2 id="what-title">{w.whatTitle}</h2>
        <p className="lead">{w.whatText}</p>
      </section>

      <section className="explain" aria-labelledby="why-title">
        <h2 id="why-title">{w.whyTitle}</h2>
        <ul className="plain-list">
          {w.why.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="explain" aria-labelledby="safe-title">
        <h2 id="safe-title">{w.safeTitle}</h2>
        <ul className="plain-list plain-list--check">
          {w.safe.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
    </main>
  );
}
