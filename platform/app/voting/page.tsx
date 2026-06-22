"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useI18n } from "@/components/Providers";
import {
  PROPOSALS,
  ballotToJson,
  buildBallot,
  clearMyVote,
  getMyVote,
  setMyVote,
  sharePercent,
  totalVotes,
  withMyVote,
  type Proposal,
  type VoteChoice,
} from "@/lib/voting";

const GOVERNANCE_URL =
  "https://github.com/Public-Trust/public-trust-dao/blob/main/docs/GOVERNANCE.md";

const CHOICES: VoteChoice[] = ["for", "against", "abstain"];

function ProposalCard({ proposal }: { proposal: Proposal }) {
  const { t } = useI18n();
  const v = t.voting;
  const text = v.proposals[proposal.id] ?? { title: proposal.id, summary: "" };

  // Голос человека хранится только в его браузере. Читаем после монтирования,
  // чтобы статическая сборка и первый показ совпадали (без рассинхрона).
  const [myVote, setMyVoteState] = useState<VoteChoice | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setMyVoteState(getMyVote(proposal.id));
  }, [proposal.id]);

  const open = proposal.status === "open";
  const shown = withMyVote(proposal, open ? myVote : null);
  const total = totalVotes(shown);

  const cast = useCallback(
    (choice: VoteChoice) => {
      setMyVote(proposal.id, choice);
      setMyVoteState(choice);
      setCopied(false);
    },
    [proposal.id],
  );

  const change = useCallback(() => {
    clearMyVote(proposal.id);
    setMyVoteState(null);
    setCopied(false);
  }, [proposal.id]);

  const copy = useCallback(async () => {
    if (!myVote) return;
    try {
      await navigator.clipboard.writeText(
        ballotToJson(buildBallot(proposal.id, myVote)),
      );
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }, [myVote, proposal.id]);

  const download = useCallback(() => {
    if (!myVote) return;
    const blob = new Blob([ballotToJson(buildBallot(proposal.id, myVote))], {
      type: "application/json;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `ballot-${proposal.id}-draft.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }, [myVote, proposal.id]);

  const statusClass =
    proposal.status === "passed"
      ? "badge badge--ready"
      : proposal.status === "rejected"
        ? "badge badge--warn"
        : "badge";

  return (
    <li className="proposal">
      <div className="proposal-head">
        <span className={statusClass}>{v.statusLabels[proposal.status]}</span>
        <span className="proposal-total">
          {total} {v.peopleLabel}
        </span>
      </div>
      <h3 className="proposal-title">{text.title}</h3>
      <p className="proposal-summary">{text.summary}</p>

      <dl className="tally">
        {CHOICES.map((choice) => {
          const count = shown[choice];
          const pct = sharePercent(count, total);
          return (
            <div key={choice} className={`tally-row tally-row--${choice}`}>
              <dt>{v.choiceLabels[choice]}</dt>
              <dd>
                <span className="tally-bar" aria-hidden="true">
                  <span
                    className="tally-fill"
                    style={{ width: `${pct}%` }}
                  />
                </span>
                <span className="tally-num">
                  {count} {v.peopleLabel} · {pct}%
                </span>
              </dd>
            </div>
          );
        })}
      </dl>

      {open ? (
        myVote ? (
          <div className="your-vote" role="status" aria-live="polite">
            <p className="wallet-state">
              <span className="dot dot--ok" aria-hidden="true" />
              {v.voted}
            </p>
            <p className="field-hint">{v.weightNote}</p>
            <p className="wallet-note">{v.ballotLead}</p>
            <pre className="draft-json" tabIndex={0}>
              {ballotToJson(buildBallot(proposal.id, myVote))}
            </pre>
            <div className="cta-row">
              <button type="button" className="btn btn-primary" onClick={copy}>
                {copied ? v.copied : v.copy}
              </button>
              <button type="button" className="btn btn-ghost" onClick={download}>
                {v.download}
              </button>
              <button type="button" className="btn btn-ghost" onClick={change}>
                {v.changeVote}
              </button>
            </div>
          </div>
        ) : (
          <div className="your-vote">
            <p className="field-hint">{v.votePrompt}</p>
            <div className="vote-buttons">
              {CHOICES.map((choice) => (
                <button
                  key={choice}
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => cast(choice)}
                >
                  {v.choiceLabels[choice]}
                </button>
              ))}
            </div>
          </div>
        )
      ) : (
        <p className="wallet-note">{v.closedNote}</p>
      )}
    </li>
  );
}

export default function VotingPage() {
  const { t } = useI18n();
  const v = t.voting;

  return (
    <main id="main" className="container">
      <p className="backlink">
        <Link href="/">{v.back}</Link>
      </p>

      <section className="hero hero--screen" aria-labelledby="voting-title">
        <p className="disclaimer" role="note">
          {t.disclaimer}
        </p>
        <h1 id="voting-title">{v.title}</h1>
        <p className="lead">{v.lead}</p>
      </section>

      <section className="explain" aria-labelledby="how-title">
        <h2 id="how-title">{v.howTitle}</h2>
        <ul className="plain-list">
          {v.how.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="panel" aria-labelledby="proposals-title">
        <h2 id="proposals-title">{v.proposalsTitle}</h2>
        <p className="wallet-note wallet-note--warn" role="note">
          {v.demoNote}
        </p>
        <ul className="proposal-list">
          {PROPOSALS.map((p) => (
            <ProposalCard key={p.id} proposal={p} />
          ))}
        </ul>
      </section>

      <section className="explain" aria-labelledby="final-title">
        <h2 id="final-title">{v.finalTitle}</h2>
        <ul className="plain-list">
          {v.final.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
        <p>
          <a className="screen-card-link" href={GOVERNANCE_URL}>
            {v.verifyLink} →
          </a>
        </p>
      </section>
    </main>
  );
}
