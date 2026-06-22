[Русский](../PRIORITIES.md) · [English]

# In what order the fund helps: who comes first when there isn't enough for everyone

> This is one of the fund's core documents. It answers a simple, honest question:
> if there is less money in the shared treasury than there are requests for help,
> **whose hardship do we cover first**. The document follows from the
> [constitution](CONSTITUTION.md) (Article 5, "fair distribution") and the
> [manifesto](MANIFESTO.md).

## The main idea — in plain words

- **Saving a life and keeping a roof overhead come first.** If a person is in
  immediate danger of death, or is about to end up on the street, that comes
  ahead of everything else. Then come medical care and food. These are the basics
  a person cannot survive without.
- **Help follows the severity of the hardship, not who the person is.** Help goes
  first not to whoever is "one of us", better known, more active, or longer in
  the project, but to whoever's need is most acute. Origin, reputation, and
  participant status **do not affect** the queue — only the hardship itself (this
  is a direct prohibition of discrimination, Article 5.3 of the constitution).
- **The queue is about how fast a request is reviewed, not about easing the
  checks.** An urgent hardship is reviewed first, but that **does not switch off**
  the usual safeguards: money still goes out in parts, there are limits, and every
  payout is verified by several independent people. High priority speeds things
  up, but does not open a "green corridor" that skips verification.
- **When hardships are equally severe, we split fairly and openly.** If two
  requests are at the same level of importance, the rule for who is served first
  is published in advance and is the same for everyone — no closed "who-you-know"
  decisions.
- **Long-term benefit for everyone is at the bottom of the list, but not thrown
  out.** Supporting open source, science, ecology, and shared infrastructure
  matters, but it waits until people's living hardships are covered. First we save
  people, then we invest in the common future.

## Order of help — from the most urgent to the less urgent

| № | Who we help first | What it means in plain words |
|---|-------------------|-------------------------------|
| 1 | Threat to life | a person is in immediate danger of death |
| 2 | Threat of losing housing | keeping a person off the street, emergency housing |
| 3 | Health | treatment, medicines, emergency medical care |
| 4 | Food | groceries, hot meals |
| 5 | Children | aid for children and families with children |
| 6 | Elderly people | care, support, basic needs |
| 7 | People with disabilities | support for people with disabilities |
| 8 | Getting back on one's feet | work, tools, exiting a crisis on one's own |
| 9 | Learning | retraining, a new profession, digital literacy |
| 10 | Long-term benefit for everyone | open source, science, ecology, shared infrastructure |

## How it works in practice

1. **When money is scarce, those with the more severe hardship come first.** The
   higher a person is on the list (closer to "threat to life"), the sooner their
   request is taken up.
2. **The queue does not switch off fraud protection.** All the rules from
   ["How the fund is protected from deception and theft"](ANTI-ABUSE.md) always
   apply: money in parts, limits on large sums, collective verification. Urgency
   speeds up review but never removes the checks.
3. **The queue depends only on the hardship, not on the person.** Reputation,
   origin, and participant status do not move a person up or down — only the
   nature of the need does (Article 5.3 of the constitution, prohibition of
   discrimination).
4. **Those equally severe are served by a fair, open rule.** Within a single
   level, distribution is transparent; the rule for who is taken first (for
   example, who applied earlier) is published and the same for everyone.

---

## Technical section — for developers

This order is the specification for the distribution smart contracts and for the
Fairness AI. Below is the machine-readable representation; everything above is
stated in plain words.

Priorities are encoded as an integer `level` from `1` to `10`, where **a smaller
number = higher priority** (`level: 1` is served before `level: 10`). The keys
(`key`) are stable and meant for use in code; the labels (`label`) are
human-readable and may be translated.

```json
{
  "priorities": [
    { "level": 1,  "key": "life_threat",         "label": "Threat to life" },
    { "level": 2,  "key": "housing_loss",        "label": "Threat of losing housing" },
    { "level": 3,  "key": "medical",             "label": "Health" },
    { "level": 4,  "key": "food",                "label": "Food" },
    { "level": 5,  "key": "children",            "label": "Children" },
    { "level": 6,  "key": "elderly",             "label": "Elderly people" },
    { "level": 7,  "key": "disability",          "label": "People with disabilities" },
    { "level": 8,  "key": "self_reliance",       "label": "Getting back on one's feet" },
    { "level": 9,  "key": "education",           "label": "Learning" },
    { "level": 10, "key": "public_good",         "label": "Long-term benefit for everyone" }
  ]
}
```

When funds are limited, requests with a smaller `level` are served first.
Priority does not override the safeguards from [`ANTI-ABUSE.md`](ANTI-ABUSE.md)
(staged payouts, limits, collective verification) and does not depend on a
participant's reputation, origin, or status — only on the nature of the need
(Article 5.3 of the constitution). Within a single level, the tie-break rules are
published and the same for everyone.
