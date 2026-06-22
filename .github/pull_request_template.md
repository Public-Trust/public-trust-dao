<!--
Двуязычный шаблон pull request — Public Trust DAO.
Bilingual pull request template — Public Trust DAO.
Заполните оба языка там, где это текст для людей. Чек-лист рельс — обязателен.
Fill both languages for human-facing text. The rails checklist is required.
Подробнее — CONTRIBUTING. See CONTRIBUTING for details.
-->

## Что меняется · What changes

<!-- Кратко и по делу: что и зачем. · Briefly: what and why. -->

## Связанные issue · Related issues

<!-- Напр. Closes #123 · e.g. Closes #123 -->

## Тип · Type

- [ ] Документ · Documentation
- [ ] Код (контракт / скрипт / агент) · Code (contract / script / agent)
- [ ] Governance / реестр · Governance / registry
- [ ] Другое · Other

## Рельсы (обязательно) · Rails (required)

- [ ] **Общественное благо, НЕ инвестиция.** Никаких обещаний доходности, пирамиды, рефералов или концентрации власти ([`docs/PRINCIPLES.md`](../docs/PRINCIPLES.md)). · **Public good, NOT an investment.** No yield promises, pyramid, referrals or power concentration.
- [ ] **TESTNET-first.** Никаких mainnet-деплоев и реальных средств/приватных ключей. · No mainnet deploys and no real funds/private keys.
- [ ] **Секреты не в репозитории.** Нет `.env`, ключей, токенов, паролей (Guardian-агент это проверяет). · No `.env`, keys, tokens, passwords in the repo (the Guardian agent checks this).
- [ ] **Двуязычность RU↔EN.** Любой новый/изменённый публичный документ обновлён на обоих языках В ЭТОМ PR, с переключателем `[Русский] · [English]`. · Any new/changed public doc is updated in both languages in THIS PR, with a `[Русский] · [English]` switcher.
- [ ] **Тесты «до зелёного».** Изменения кода сопровождаются тестами; проверки ниже зелёные. · Code changes come with tests; the checks below are green.
- [ ] **Прозрачность.** Значимое решение залогировано в [реестр](../governance/registry/) (если применимо). · A significant decision is logged in the registry (if applicable).

## Самопроверка · Self-check

```sh
python3 scripts/registry.py verify        # реестр решений · decisions registry
python3 ai-agents/run_all.py --with-tests # AI-агенты соблюдения конституции · constitution-compliance agents
```

<!-- Для контрактов также: cd contracts && npm test
     For contracts also: cd contracts && npm test -->

---

Открывая PR, вы соглашаетесь с [кодексом поведения](../CODE_OF_CONDUCT.md) и
лицензиями проекта (код — AGPL-3.0, документы — CC-BY-SA-4.0).
By opening a PR you agree to the [Code of Conduct](../CODE_OF_CONDUCT.md) and the
project licenses (code — AGPL-3.0, docs — CC-BY-SA-4.0).
