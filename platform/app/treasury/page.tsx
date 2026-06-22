"use client";

import Link from "next/link";
import { useI18n } from "@/components/Providers";
import {
  MOVEMENTS,
  SNAPSHOT,
  distributable,
  formatAmount,
  movementSign,
  sharePercent,
  type Movement,
} from "@/lib/treasury";

const REWARDS_URL =
  "https://github.com/Public-Trust/public-trust-dao/blob/main/docs/REWARDS-MODEL.md";

function MovementRow({ movement }: { movement: Movement }) {
  const { t } = useI18n();
  const tr = t.treasury;
  const text = tr.movements[movement.id] ?? movement.id;
  const sign = movementSign(movement.kind);

  return (
    <li className={`movement movement--${movement.kind}`}>
      <div className="movement-main">
        <span className="badge">{tr.movementLabels[movement.kind]}</span>
        <span className="movement-desc">{text}</span>
      </div>
      <div className="movement-meta">
        <span className={`movement-amount movement-amount--${sign === "+" ? "in" : "out"}`}>
          {sign} {formatAmount(movement.amount)} {tr.unit}
        </span>
        <span className="movement-date">{movement.date}</span>
      </div>
    </li>
  );
}

export default function TreasuryPage() {
  const { t } = useI18n();
  const tr = t.treasury;
  const s = SNAPSHOT;

  const dist = distributable(s);
  const helpPct = sharePercent(s.helpPool, dist);
  const rewardPct = sharePercent(s.rewardPool, dist);

  // Полоски состава всей казны (запас / помощь / благодарность) — в долях от всего.
  const reservePctOfAll = sharePercent(s.reserve, s.balance);
  const helpPctOfAll = sharePercent(s.helpPool, s.balance);
  const rewardPctOfAll = sharePercent(s.rewardPool, s.balance);

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{tr.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="treasury-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="treasury-title">{tr.title}</h1>
        <p className="lead">{tr.lead}</p>
      </section>

      <section className="panel" aria-labelledby="balance-title">
        <p className="wallet-note wallet-note--warn" role="note">
          {tr.demoNote}
        </p>

        <h2 id="balance-title" className="balance-label">
          {tr.balanceLabel}
        </h2>
        <p className="balance-amount">
          {formatAmount(s.balance)} <span className="balance-unit">{tr.unit}</span>
        </p>
        <p className="field-hint">{tr.balanceHint}</p>
        <p className="field-hint">
          {tr.asOfLabel}: {s.asOf} · {t.wallet.network}: testnet · {tr.unit}
        </p>

        {/* Состав всей казны одной понятной полоской */}
        <div className="compose-bar" aria-hidden="true">
          <span className="compose-seg compose-seg--reserve" style={{ width: `${reservePctOfAll}%` }} />
          <span className="compose-seg compose-seg--help" style={{ width: `${helpPctOfAll}%` }} />
          <span className="compose-seg compose-seg--reward" style={{ width: `${rewardPctOfAll}%` }} />
        </div>
      </section>

      <section className="panel" aria-labelledby="split-title">
        <h2 id="split-title">{tr.splitTitle}</h2>
        <dl className="split-list">
          <div className="split-row split-row--reserve">
            <dt>{tr.reserveLabel}</dt>
            <dd>
              <span className="split-amount">
                {formatAmount(s.reserve)} {tr.unit}
              </span>
              <span className="split-hint">{tr.reserveHint}</span>
            </dd>
          </div>
          <div className="split-row split-row--help">
            <dt>{tr.helpLabel}</dt>
            <dd>
              <span className="split-amount">
                {formatAmount(s.helpPool)} {tr.unit} · {helpPct}% {tr.ofDistributable}
              </span>
              <span className="split-hint">{tr.helpHint}</span>
            </dd>
          </div>
          <div className="split-row split-row--reward">
            <dt>{tr.rewardLabel}</dt>
            <dd>
              <span className="split-amount">
                {formatAmount(s.rewardPool)} {tr.unit} · {rewardPct}% {tr.ofDistributable}
              </span>
              <span className="split-hint">{tr.rewardHint}</span>
            </dd>
          </div>
        </dl>
      </section>

      <section className="explain" aria-labelledby="coverage-title">
        <h2 id="coverage-title">{tr.coverageTitle}</h2>
        <p className="coverage-state">
          <span className={`badge badge--ready coverage-badge coverage-badge--${s.coverage}`}>
            {tr.coverageLabels[s.coverage]}
          </span>
        </p>
        <p className="field-hint">{tr.coverageHint}</p>
      </section>

      <section className="panel" aria-labelledby="movements-title">
        <h2 id="movements-title">{tr.movementsTitle}</h2>
        <p className="field-hint">{tr.movementsHint}</p>
        <ul className="movement-list">
          {MOVEMENTS.map((m) => (
            <MovementRow key={m.id} movement={m} />
          ))}
        </ul>
        <p className="wallet-note" role="note">
          {tr.readonlyNote}
        </p>
      </section>

      <section className="explain" aria-labelledby="treasury-how-title">
        <h2 id="treasury-how-title">{tr.howTitle}</h2>
        <ul className="plain-list">
          {tr.how.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
        <p>
          <a className="screen-card-link" href={REWARDS_URL}>
            {tr.verifyLink} →
          </a>
        </p>
      </section>
    </main>
  );
}
