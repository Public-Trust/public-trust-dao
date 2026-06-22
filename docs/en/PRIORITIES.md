[Русский](../PRIORITIES.md) · [English]

# CONSTITUTION OF FAIR DISTRIBUTION — PRIORITY

> Normative document. Defines the order of priority when distributing aid.
> Derived from [`CONSTITUTION.md`](CONSTITUTION.md) (Article 5) and
> [`MANIFESTO.md`](MANIFESTO.md). This order is the specification for the
> distribution smart contracts and for the Fairness AI.

## Order of priority (from highest to lowest)

| № | Priority | Brief description |
|---|-----------|------------------|
| 1 | Threat to life | immediate danger to a person's life |
| 2 | Threat of losing housing | preventing homelessness, emergency housing |
| 3 | Medical care | treatment, medicines, emergency medical care |
| 4 | Food | groceries, hot meals |
| 5 | Children | aid for children and families with children |
| 6 | Elderly people | care, support, basic needs |
| 7 | Disability | support for people with disabilities |
| 8 | Restoring self-reliance | employment, tools, exit from crisis |
| 9 | Education | retraining, learning, digital literacy |
| 10 | Long-term public good | open source, science, ecology, infrastructure |

## Machine-readable representation

For use in code (smart contracts, Fairness AI), priorities are encoded as an
integer `1..10`, where **a smaller number = higher priority**.

```json
{
  "priorities": [
    { "level": 1,  "key": "life_threat",        "label": "Threat to life" },
    { "level": 2,  "key": "housing_loss",        "label": "Threat of losing housing" },
    { "level": 3,  "key": "medical",             "label": "Medical care" },
    { "level": 4,  "key": "food",                "label": "Food" },
    { "level": 5,  "key": "children",            "label": "Children" },
    { "level": 6,  "key": "elderly",             "label": "Elderly people" },
    { "level": 7,  "key": "disability",          "label": "Disability" },
    { "level": 8,  "key": "self_reliance",       "label": "Restoring self-reliance" },
    { "level": 9,  "key": "education",           "label": "Education" },
    { "level": 10, "key": "public_good",         "label": "Long-term public good" }
  ]
}
```

## Rules of application

1. When funds are limited, requests with a smaller `level` are served first.
2. Priority **does not override** the checks from [`ANTI-ABUSE.md`](ANTI-ABUSE.md):
   high priority speeds up review, but does not disable staged payouts,
   limits, and collective verification.
3. Priority **does not depend** on a participant's reputation, origin, or status —
   only on the nature of the need (Article 5.3 of the constitution, prohibition of discrimination).
4. Within a single priority level, distribution is fair and transparent;
   the tie-break rules are published and the same for everyone.
