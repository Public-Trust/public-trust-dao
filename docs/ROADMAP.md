[Русский] · [English](en/ROADMAP.md)

# ДОРОЖНАЯ КАРТА И САМОРАЗВИТИЕ — PUBLIC TRUST DAO

> Живой документ. Это «топливо» автономной стройки: когда очередь указаний
> оператора (`comms/INBOX.md`) пуста, агент-строитель берёт **следующий
> незакрытый пункт отсюда**, реализует его и предлагает новые идеи.
> Производный от [`MANIFESTO.md`](MANIFESTO.md), [`CONSTITUTION.md`](CONSTITUTION.md),
> [`PRINCIPLES.md`](PRINCIPLES.md) и плана этапов в `LAUNCH.md`.
>
> Зарегистрирован как решение в публичном реестре:
> [`governance/registry/`](../governance/registry/) (запись `PTD-0005`).
>
> **Всё — TESTNET-first.** Любая работа с деньгами — только после независимого
> аудита, явного одобрения оператора и Safe multisig 3-из-5 живых людей.

---

## Зачем этот документ

Проект должен двигаться, даже когда оператор молчит. Чтобы стройка не
останавливалась и не превращалась в хаотичный набор разрозненных правок, нужен
**единый приоритизированный список идей и задач**, который ведёт сам AI и из
которого сам же берёт работу. Это и есть механизм саморазвития:

```
INBOX пуст?  →  взять верхний открытый пункт ROADMAP  →  реализовать до зелёного
            →  отметить [x]  →  предложить 1–3 новые идеи в «Банк идей»
            →  зарегистрировать значимое решение в реестре
```

Правило закреплено в [`BUILDER.md`](../BUILDER.md) (раздел «Саморазвитие»), чтобы
оно соблюдалось каждую сессию, а не только пока про него помнят.

## Как это работает (процесс)

1. **Источник работы — по приоритету:**
   `INBOX` (указания оператора) → `ROADMAP` (этот файл) → план этапов `LAUNCH.md`.
2. **Один связный пункт за сессию.** Крупный пункт дроби: сделай первую часть,
   остальное оставь открытым с пометкой «следующий шаг».
3. **До рабочего результата.** Реальные файлы/код/тесты «до зелёного», без заглушек.
4. **Отметь сделанное** здесь (`- [x]`), перенеси в «Сделано» с номером сессии.
5. **Пополни банк идей.** Каждую сессию предлагай 1–3 новые идеи (даже сырые) —
   так список не иссякает. Идеи может добавлять и оператор.
6. **Логируй значимые решения** в [реестр](../governance/registry/) (тип `decision`).

## Рельсы саморазвития (границы автономии)

Саморазвитие НЕ снимает рельсы безопасности — оно работает строго внутри них:

- **Деньги/ключи/mainnet** — никогда сам. Только подготовка + явное «го» оператора.
- **Внешние действия от лица проекта** (публикации, рассылки, регистрация
  аккаунтов с капчей/телефоном/KYC) — агент готовит «до кнопки», нажимает оператор.
- **Конституционные запреты буквально** — ни одна идея из роадмапа не может их
  нарушать (нет доходности, нет пирамиды, нет рефералов, нет концентрации власти,
  нет скрытых операций). Идея, противоречащая конституции, не берётся в работу.
- **Двуязычность RU↔EN** в одном коммите для любого нового/изменённого дока.
- **Пульс неприкосновенен** (`loop.sh`/`report.sh`/сервис/`.env`/`logs/` не трогать).

---

## Приоритеты (P0 — выше)

`P0` блокирует/несёт наибольшую ценность · `P1` важно · `P2` желательно · `P3` идея на потом.

### P0 — основной план (этапы LAUNCH.md)

- [x] **Этап 4 — Governance, концепция (КУРС УПРАВЛЕНИЯ):** целевая модель
  «1 человек = 1 голос» (Governor → Timelock → Treasury), мультисиг как исполнитель/
  аварийка, путь децентрализации, анти-Сивилла без концентрации власти, поправки к
  конституции как предложение. → Сделано (сессия 10),
  [`GOVERNANCE.md`](GOVERNANCE.md), `PTD-0007`. Это спецификация-основа для частей 1–2.
- [x] **Этап 4 — Governance, часть 1:** макет Snapshot space (off-chain) в
  `governance/snapshot/` — `space.json`/README по [`GOVERNANCE.md`](GOVERNANCE.md):
  стратегия «1 человек = 1 голос» (не плутократия), кворум, типы предложений,
  привязка к конституции (приоритет распределения, апелляции).
  → Сделано (сессия 18), [`governance/snapshot/`](../governance/snapshot/),
  `PTD-0015` (конфиг + JSON-схема + README RU/EN + валидатор рельс
  `scripts/snapshot_config.py` + CI). Создание space (ENS/контроллер) — запрос оператору.
- [x] **Этап 4 — Governance, часть 2:** макет Safe multisig 5 хранителей (3-из-5)
  в `governance/safe/` — схема, роли (исполнитель/аварийная пауза по
  [`GOVERNANCE.md`](GOVERNANCE.md)), политика подписей, без реальных адресов.
  → Сделано (сессия 16), [`governance/safe/`](../governance/safe/), `PTD-0013`
  (вместе с INBOX #10: конфиг + валидатор рельс + CI).
- [ ] **Этап 5 — Смарт-контракты (каркас):** завести `contracts/` как проект
  (Foundry/Hardhat-конфиг), скелеты Treasury / Disbursement (по
  [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md)) /
  Governance / Reputation + первые тесты «до зелёного». Только testnet/локально.
  - [x] Часть 1 (сессия 19): проект `contracts/` (Hardhat + ethers v6 + chai,
    Solidity 0.8.24) + контракт-скелет [`Treasury.sol`](../contracts/contracts/Treasury.sol)
    (release только через executor=мультисиг/Timelock, лимит, аварийная пауза,
    события + registryRef) + 10 тестов «до зелёного» + CI. `PTD-0016`. TESTNET-ONLY.
  - [x] Часть 2 (сессия 20): [`Disbursement.sol`](../contracts/contracts/Disbursement.sol)
    — целевой escrow `open/release/refund/pause`; транш уходит строго поставщику
    из кейса («не даём деньги — оплачиваем нужду»), `refund` в казну, лимит транша,
    только executor двигает, guardian только пауза; 14 тестов «до зелёного» (24/24
    с Treasury); реестровая схема расширена `provider/category/escrow_id`. `PTD-0017`.
  - [ ] Часть 3: `Governance` (Governor → Timelock) + `Reputation` (soulbound-бейдж).
    - [x] Часть 3a (сессия 21): [`Reputation.sol`](../contracts/contracts/Reputation.sol)
      — непередаваемый (soulbound) бейдж участника по [`GOVERNANCE.md`](GOVERNANCE.md)
      §2–§3: «1 человек = 1 голос» (`votingUnits` = 1 + min(points, cap), вес в
      коридоре [1..1+cap]), нет функций перевода (непередаваем by design), `verifier`
      выдаёт/отзывает бейдж, `governor` правит параметры, ни одна роль не двигает
      средства; 11 тестов «до зелёного» (35/35 с Treasury+Disbursement). `PTD-0018`.
    - [x] Часть 3b (сессия 22): [`Governor.sol`](../contracts/contracts/Governor.sol)
      + [`Timelock.sol`](../contracts/contracts/Timelock.sol) по [`GOVERNANCE.md`](GOVERNANCE.md)
      §4–§7: прямое голосование (вес из `Reputation.votingUnits`, кворум/срок/публичный
      подсчёт), исполнение ТОЛЬКО через `Timelock` (Governor средства не двигает),
      `guardian` = аварийное вето (`cancel`), `admin` = разовый bootstrap (`renounceAdmin`),
      параметры только голосованием; 15 тестов «до зелёного» (50/50 со всеми
      контрактами). `PTD-0019`.
    - [x] Часть 3c (сессия 23): [`scripts/deploy.js`](../contracts/scripts/deploy.js)
      разворачивает и связывает контур целиком (Reputation→Timelock→Treasury/Disbursement→Governor;
      executor=Timelock, governor=Governor, `renounceAdmin`, Reputation.governor=Timelock)
      + интеграционный тест [`Integration.test.js`](../contracts/test/Integration.test.js)
      «заявка → голос → Timelock → целевая выплата поставщику через `Disbursement`»;
      +4 теста «до зелёного» (54/54 со всеми контрактами). `PTD-0020`.
  - [ ] Часть 4: прогон на публичном testnet (напр. Polygon Amoy) — сеть/RPC/тестовые
    адреса хранителей согласовать с оператором (ключи через `contracts/.env`).
- [x] **Этап 6 — AI-агенты (каркас): ЗАВЕРШЁН (8/8, сессия 31).** В `ai-agents/`
  заведены все восемь модулей-помощников соблюдения конституции (служебные модули,
  не органы власти — ст. 9; read-only к средствам, находка = сигнал, не действие),
  каждый «до зелёного» и с тест-инвариантом, все в CI `ai-agents.yml`:
  Audit, Guardian, Fairness, Reputation, Housing, Documentation, Governance, Mediator.
  - [x] Модуль 1/8 (сессия 24): каркас [`ai-agents/`](../ai-agents/) (README RU/EN
    с принципом «ИИ служит, не правит» и таблицей 8 агентов) + первый рабочий агент
    **Audit** [`audit_agent.py`](../ai-agents/audit_agent.py) — объединяет 4 рельс-
    валидатора (registry/ipfs/safe/snapshot) в один аудит-прогон с привязкой каждой
    проверки к статье конституции, опция `--with-contracts`, вывод человекочитаемый
    и `--json`; CI [`ai-agents.yml`](../.github/workflows/ai-agents.yml). «До зелёного»:
    4/4 базовый, 5/5 с контрактами (54 теста). `PTD-0021`. Реализует и идею «единый
    governance-валидатор в CI». TESTNET-ONLY.
  - [x] Модуль 2/8 (сессия 25): **Guardian** [`guardian_agent.py`](../ai-agents/guardian_agent.py)
    — отдельный явный сканер рельс безопасности по ВСЕМУ дереву репо (git-отслеживаемые
    файлы): нет закоммиченных секретов/ключей (`secrets-tracked`), `.gitignore` прикрывает
    `.env`/`logs/` (`gitignore-guards`), нет mainnet `chain_id` (`no-mainnet`), нет
    приватных ключей в тексте (`no-key-material`, 64-hex вне хэш-полей + присваивание
    секрета). Тест-инвариант [`test_guardian.py`](../ai-agents/test_guardian.py) (14/14)
    доказывает «красное ловится, зелёное не ложно-падает». CI расширен. `PTD-0022`.
  - [x] Модуль 3/8 (сессия 26): **Fairness** [`fairness_agent.py`](../ai-agents/fairness_agent.py)
    — read-only проверка справедливости распределения над записями реестра типа
    `disbursement` по [`PRIORITIES.md`](PRIORITIES.md)/[`ANTI-ABUSE.md`](ANTI-ABUSE.md):
    `priority-valid` (уровень в шкале 1..10, читается прямо из PRIORITIES.md),
    `safeguards` (приоритет не отключает лимит/проверку/окно апелляции), `collective-review`
    (≥2 независимых подтверждения), `staged-payments` (поэтапность), `applicant-privacy`
    (нет персональных данных). Тест-инвариант [`test_fairness.py`](../ai-agents/test_fairness.py)
    (17/17). Побочно исправлен латентный баг Guardian (ложно краснел на собственном
    `test_guardian.py`) — CI `ai-agents` снова зелёный. `PTD-0023`.
  - [x] Модуль 4/8 (сессия 27): **Reputation** [`reputation_agent.py`](../ai-agents/reputation_agent.py)
    — read-only статический разбор `contracts/contracts/Reputation.sol` и
    `governance/snapshot/space.json`: доказывает «1 человек = 1 голос» по
    [`GOVERNANCE.md`](GOVERNANCE.md) §2–§3 В КОДЕ — `soulbound` (нет функций
    перевода), `bounded-weight` (вес 0 / `1 + min(points, cap)`, коридор [1..1+cap]),
    `no-funds` (слой репутации не двигает средства), `roles-separated` (verifier
    выдаёт/отзывает бейдж, governor правит параметры), `off-chain-equal` (Snapshot =
    равный `ticket` value=1, не плутократия). Тест-инвариант
    [`test_reputation.py`](../ai-agents/test_reputation.py) (17/17). `PTD-0024`.
  - [x] Модуль 5/8 (сессия 28): **Housing** [`housing_agent.py`](../ai-agents/housing_agent.py)
    — профильный помощник по жилищным кейсам. Read-only доказывает модель целевого
    расхода (docs/ESCROW-TARGETED-DISBURSEMENT.md) «помощь оплачивается напрямую
    поставщику, не на руки» В КОДЕ `contracts/contracts/Disbursement.sol`:
    `release-to-provider-only` (release без адреса-параметра → транш строго на
    c.provider), `provider-fixed` (нет setProvider/.provider=), `refund-to-treasury`
    (возврат в казну, не получателю), `tranche-limit` (потолок maxRelease),
    `guardian-cannot-move` (средства двигает только executor) + проверки жилищных
    записей реестра (`targeted-escrow`/`provider-onchain`/`category-priority`,
    уровень читается из PRIORITIES.md). Тест-инвариант
    [`test_housing.py`](../ai-agents/test_housing.py) (23/23). CI расширен (+ триггеры
    на contracts/contracts и docs/PRIORITIES.md). `PTD-0025`.
  - [x] Модуль 6/8 (сессия 29): **Documentation** [`documentation_agent.py`](../ai-agents/documentation_agent.py)
    — read-only проверка двуязычности RU↔EN и целостности ссылок по git-отслеживаемым
    `.md`: `bilingual-pairs` (у каждого публичного дока есть пара по правилу пар из
    пути), `language-switcher` (вверху корректный переключатель `[Русский]·[English]`
    к парному файлу), `link-integrity` (все относительные ссылки резолвятся; внешние
    ссылки и блоки кода исключены). Тест-инвариант
    [`test_documentation.py`](../ai-agents/test_documentation.py) (17/17). При первом
    прогоне вскрыл и закрыл реальный пробел — добавлены EN-зеркала
    `governance/ipfs/README.md` и `governance/registry/README.md`. Закрывает и P2
    «авто-проверка двуязычности в CI». `PTD-0026`.
  - [x] Модуль 7/8 (сессия 30): **Governance** [`governance_agent.py`](../ai-agents/governance_agent.py)
    — read-only проверка ЖИЗНЕННОГО ЦИКЛА ПРЕДЛОЖЕНИЯ из `GOVERNANCE.md` над конфигами
    управления `governance/snapshot/space.json` и `governance/safe/safe.config.json`
    (сам НЕ голосует): `one-person-one-vote` (стратегия `ticket` value=1, не плутократия),
    `timed-vote` (`delay`/`period` > 0), `off-chain-signal` (`off_chain_signaling=true` и
    типы `binding=false`), `proposal-binding` (`disbursement-direction`→PRIORITIES+ANTI-ABUSE;
    `constitution-amendment`→CONSTITUTION+`requires_supermajority`), `multisig-not-sole`
    (порог ≥2 и < числа владельцев, 3-из-5), `lifecycle-links` (ссылки конфигов резолвятся).
    Тест-инвариант [`test_governance.py`](../ai-agents/test_governance.py) (26/26). CI
    расширен. На реальных конфигах: 6/6. `PTD-0027`.
  - [x] Модуль 8/8 — последний (сессия 31): **Mediator** [`mediator_agent.py`](../ai-agents/mediator_agent.py)
    — read-only проверка процесса споров/апелляций (артефакт
    [`governance/mediation/dispute-process.json`](../governance/mediation/dispute-process.json))
    по `ANTI-ABUSE.md` §6: `appeal-for-every-sanction` (у каждой санкции — отказ/
    репутация/заморозка/исключение — есть обжалование), `mediator-not-decider`
    (решают люди ≥2, не ИИ/один), `independent-review` (апелляцию решает не автор
    санкции), `valid-lifecycle` (один старт/терминал/без тупиков/всё достижимо),
    `bounded-timelines` (сроки > 0), `process-links` (ссылки резолвятся);
    **СТРУКТУРИРУЕТ, НЕ решает** (ст. 9.2). Тест-инвариант
    [`test_mediator.py`](../ai-agents/test_mediator.py) (26/26). CI расширен.
    На реальном артефакте: 6/6. **Закрыл каркас всех восьми агентов (8/8).** `PTD-0028`.

### P1 — материалы и инфраструктура (часть — из INBOX)

- [x] **Продвижение (INBOX #6):** лендинг для людей, короткий питч RU/EN,
  пост-анонс, FAQ «это общественное благо, НЕ инвестиция». Готовит агент;
  публикацию делает оператор. → Сделано (сессия 9), [`PROMOTION.md`](PROMOTION.md), `PTD-0006`.
- [x] **Почта проекта (INBOX #7):** инструкция оператору — варианты домена+почты
  (ProtonMail/собственный домен), тексты. Регистрацию делает оператор.
  → Сделано (сессия 14), [`EMAIL-SETUP.md`](EMAIL-SETUP.md), `PTD-0011`.
- [x] **Testnet-кошелёк + Safe (INBOX #10):** описать/создать тестовый кошелёк и
  Safe для тестовой казны (без реальных денег и приватных ключей в репо), адреса
  задокументировать открыто. → Сделано (сессия 16), [`governance/safe/`](../governance/safe/),
  `safe.config.json` + `scripts/safe_config.py` (валидатор рельс) + CI, `PTD-0013`.
- [x] **Аутрич-шаблоны (INBOX #8):** список контактов + шаблоны писем RU/EN под
  миссию «общественное благо». Отправляет оператор лично.
  → Сделано (сессия 15), [`OUTREACH.md`](OUTREACH.md), `PTD-0012`.
- [x] **Модель поддержки/донатов (INBOX):** поддержка через саму работающую
  систему (прозрачная казна-мультисиг + контракты, видна в реестре), без
  отдельной кнопки «Поддержать»; адрес для реальных денег — только после запуска
  и аудита. → Сделано (сессия 17), [`SUPPORT-MODEL.md`](SUPPORT-MODEL.md), `PTD-0014`.

### P2 — качество и прозрачность

- [ ] **CONTRIBUTING.md (+EN)** — как стороннему человеку участвовать (issues, PR,
  предложения в governance), кодекс поведения, ссылки на конституцию.
- [ ] **Глоссарий** ключевых терминов (DAO, escrow, multisig, реестр, приоритет
  распределения) простым языком, RU/EN — чтобы документы были понятны не-техническим.
- [ ] **Страница «Прозрачность» на сайте** — собрать ссылки: реестр, IPFS-манифест,
  CI-статусы, как самому проверить целостность (`registry.py verify`).
- [x] **Авто-проверка двуязычности в CI** — линтер, который валит сборку, если
  RU-док без парного EN (или наоборот), нет переключателя языка или битая ссылка.
  → Реализовано Documentation-агентом (сессия 29):
  [`ai-agents/documentation_agent.py`](../ai-agents/documentation_agent.py), `PTD-0026`.

### P3 — банк идей (сырые, обсуждаемые)

- [x] **Мета-агент «прогнать всех»** `ai-agents/run_all.py` — единая точка входа,
  которая запускает все восемь агентов и сводит их `--json`-отчёты в один
  «зелёный/красный» с разбивкой по агентам/проверкам. Упростит CI (один шаг вместо
  16) и self-check контура (предложено сессией 31, после закрытия каркаса 8/8).
  → Сделано (сессия 32), [`ai-agents/run_all.py`](../ai-agents/run_all.py) +
  тест-инвариант [`test_run_all.py`](../ai-agents/test_run_all.py) (13/13), CI сжат
  с ~15 шагов до 2, `PTD-0029`.
- [ ] **Рефакторинг общих solidity-помощников** в `ai-agents/` — статический разбор
  `.sol` дублируется (Reputation/Housing); вынести в общий модуль `solidity_scan.py`
  с тестами, чтобы агенты не расходились в логике парсинга (предложено сессией 31).
- [ ] **Шаблон/схема записи реестра типа `appeal`** + привязка к Mediator: когда спор
  доходит до `resolved`, итог фиксируется записью `appeal` в `governance/registry/`;
  агент проверяет, что у завершённого спора есть такая запись (замкнуть процесс
  обжалования на публичный реестр, как `disbursement` ↔ escrow; предложено сессией 31).
- [ ] Дашборд казны (read-only) — публичное состояние тестовой казны из реестра.
- [ ] Шаблоны заявок на помощь (анонимные, без перс. данных) — форма + схема.
- [ ] «Объясни как ребёнку» — короткие пояснялки к каждому нормативному доку.
- [ ] Автоматический changelog из реестра решений (генерировать `CHANGELOG.md`).
- [ ] Модель репутации хранителей/проверяющих (анти-сговор) — черновик спецификации.
- [ ] Превратить лендинг-копию из [`PROMOTION.md`](PROMOTION.md) в реальную
  человеко-ориентированную страницу в `web/` (проще нормативного сайта; та же
  политика «без внешних запросов/трекеров»).
- [ ] Медиа-кит проекта: единый логотип/палитра/иконка (SVG, без внешних шрифтов)
  + краткие правила использования — чтобы материалы выглядели согласованно.
- [ ] Пресс-страница/одностраничник «о проекте для прессы и партнёров» (RU/EN) на
  базе boilerplate из `PROMOTION.md` — факты, ссылки, контакты, что можно цитировать.
- [ ] Шаблоны предложений Snapshot (RU/EN) под каждый `proposal_type` из
  `governance/snapshot/space.json` — единый формат (контекст/что предлагается/
  привязка к конституции/варианты голоса), чтобы предложения были сравнимы и проверяемы.
- [x] Единый governance-валидатор в CI: один скрипт прогоняет `registry.py verify`
  + `ipfs_manifest.py verify` + `safe_config.py verify` + `snapshot_config.py verify`
  одной командой (удобный «зелёный/красный» для всего governance-слоя).
  → Реализовано Audit-агентом (сессия 24): [`ai-agents/audit_agent.py`](../ai-agents/audit_agent.py), `PTD-0021`.
- [ ] Тест-инвариант «казна не уходит мимо реестра»: проверять, что у каждого
  on-chain события `Released(registryRef)` есть запись в `governance/registry/`
  (и наоборот) — связать контракт и реестр решений в единую проверку (предложено сессией 19).
- [ ] Скрипт деплоя `contracts/scripts/deploy.js` (Hardhat) с подстановкой адресов
  Safe-мультисига как `executor` — заготовка «до кнопки» для testnet (предложено сессией 19).
- [ ] Тест-инвариант для Audit-агента: подсунуть «сломанный» governance-артефакт
  (битая цепочка/рассинхрон манифеста) и проверить, что агент возвращает «красный» —
  чтобы сам аудит был доказанно рабочим, а не «зелёным по умолчанию» (сессия 24).
- [x] Guardian-агент: явный сканер рельс безопасности по всему репо (нет 64-hex
  ключей/`mnemonic`/`seed`, нет mainnet chain_id, `.env` не в индексе) — переиспользовать
  и обобщить проверки из `safe_config.py`/`snapshot_config.py` (сессия 24).
  → Реализовано (сессия 25): [`guardian_agent.py`](../ai-agents/guardian_agent.py) +
  тест-инвариант [`test_guardian.py`](../ai-agents/test_guardian.py), `PTD-0022`.
- [x] Documentation-агент: линтер двуязычности RU↔EN (пара RU-док ↔ EN-зеркало) +
  проверка целостности относительных ссылок — закрывает и пункт P2 «авто-проверка
  двуязычности в CI» (сессия 24). → Реализовано (сессия 29):
  [`documentation_agent.py`](../ai-agents/documentation_agent.py) +
  [`test_documentation.py`](../ai-agents/test_documentation.py), `PTD-0026`.
- [x] Мета-агент «прогнать всех»: единая точка `ai-agents/run_all.py`, которая
  последовательно вызывает все готовые агенты (Audit + Guardian + …) и сводит их
  отчёты в один «зелёный/красный» для всего проекта (упростит CI и локальный self-check) (сессия 25).
  → Реализовано (сессия 32): [`run_all.py`](../ai-agents/run_all.py) +
  [`test_run_all.py`](../ai-agents/test_run_all.py), `PTD-0029`.
- [ ] Guardian: проверка `pre-commit`-хука/инструкции — заготовка локального хука,
  который гоняет Guardian перед коммитом, чтобы секрет не попал в индекс в принципе (сессия 25).
- [ ] Расширить Guardian на проверку URL-рельс: нет ли в публичных текстах
  «обещаний доходности»/«инвестиция»/«гарантия» (буквальные конституционные запреты
  PRINCIPLES.md) — лёгкий лексический линтер для лендинга/README (сессия 25).
- [ ] Тест-инвариант «выплата ↔ запись реестра» для Fairness/Audit: проверять, что
  у каждой on-chain выплаты есть запись `disbursement` в реестре (и наоборот) —
  связать контракт `Disbursement` и реестр в единую сквозную проверку (сессия 26).
- [ ] Самопроверка агентов в CI как правило: каждый новый агент обязан иметь
  `test_<agent>.py`-инвариант, а CI прогоняет их все — чтобы ни один агент не был
  «зелёным по умолчанию» (стандарт качества Этапа 6, предложено сессией 26).
- [ ] Fairness: проверка согласованности `category` ↔ `priority_level` (например,
  `housing` обычно не ниже уровня «угроза потери жилья») — мягкое предупреждение,
  не блокирующее, чтобы ловить очевидные перекосы категоризации (сессия 26).
- [ ] Reputation-агент: распространить статический разбор «1 человек = 1 голос» на
  `Governor.sol` (вес голоса берётся из `Reputation.votingUnits`, а не из баланса;
  порог внесения предложения равный, не денежный) — замкнуть проверку всей цепочки
  голоса, а не только бейджа (сессия 27).
- [ ] Reputation-агент: сверять `reputationCap` в `scripts/deploy.js`/конфиге деплоя
  с разумным потолком (например, ≤ небольшого N), чтобы множитель за вклад не мог
  тихо превратиться в новую элиту через слишком высокий cap (сессия 27).
- [ ] Лёгкий Solidity-инвариант-сканер как переиспользуемый модуль: вынести из
  Reputation-агента вырезание комментариев + извлечение тела функции по балансу
  скобок в общий `ai-agents/solidity_scan.py` — пригодится будущим агентам по
  контрактам (Governance/Audit) (сессия 27). Housing-агент (сессия 28) продублировал
  те же помощники (`strip_solidity_comments`/`_function_body`/`_function_sig`) — уже
  ТРИ копии, рефакторинг назрел.
- [ ] Housing-агент: когда появится вайтлист поставщиков (открытый вопрос
  [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md) §8 — кто ведёт
  и как верифицирует арендодателей/аптеки), добавить проверку `provider-whitelisted`:
  `provider` жилищной записи входит в публичный реестр проверенных поставщиков
  (категории `housing`) — закрыть критическую точку доверия модели B (сессия 28).
- [ ] Сквозной тест-инвариант Housing «запись ↔ on-chain escrow»: сверять, что у
  жилищной записи реестра `escrow_id` соответствует реально открытому кейсу в
  `Disbursement` (через события `Opened(id, …, provider, …)`), а `provider` записи =
  `provider` кейса — связать реестр и контракт в одну проверку целевого расхода
  (развитие идеи «выплата ↔ запись реестра», сессия 28).
- [ ] Documentation-агент: проверка «свежести перевода» — RU-док и его EN-зеркало
  должны меняться В ОДНОМ коммите (git-diff: если в коммите/диффе тронут только один
  из пары — мягкое предупреждение). Закроет «двуязычность синхронна», а не только
  «оба файла существуют» (сессия 29).
- [ ] Documentation-агент: проверка якорей ссылок (`FILE.md#section`) — что `#section`
  соответствует реальному заголовку в целевом файле, чтобы внутренние ссылки не
  гнили при переименовании разделов (сессия 29).
- [ ] Лексический линтер конституционных запретов для публичных текстов
  (README/web/PROMOTION): нет «гарантированной доходности»/«инвестиция»/«пирамида»/
  «рефералы» (буквальные запреты `PRINCIPLES.md`) — может стать частью Documentation
  или отдельным мини-агентом (сессия 29; ранее предлагалось как расширение Guardian).
- [ ] Run-All: машиночитаемая сводка-бейдж в `governance/` (последний вердикт
  `run_all --json` сохраняется в файл-артефакт) — основа для будущего публичного
  «статус-светофора» проекта без внешних сервисов (сессия 32).
- [ ] Тест-инвариант для Audit (`test_audit.py`) — единственный из агентов без
  собственного инварианта; подсунуть «сломанный» governance-артефакт и проверить,
  что Audit краснеет (закрыть пробел стандарта качества Этапа 6; сессия 32).
- [ ] Общий модуль `ai-agents/agent_report.py` — единый помощник вывода отчёта
  (`{agent, verdict, passed, total, checks}` + человекочитаемый рендер), чтобы
  восемь агентов не дублировали один и тот же код печати и не расходились в формате,
  на который опирается `run_all` (сессия 32; родственно идее `solidity_scan.py`).

---

## Сделано

- **PTD-0029 (сессия 32):** Этап 6 (AI-агенты), консолидация каркаса 8/8 —
  **мета-агент Run-All**. [`run_all.py`](../ai-agents/run_all.py) — служебный
  read-only мета-модуль (ст. 9): запускает всех восьмерых агентов с `--json` и
  сводит их отчёты в один вердикт «зелёно/красно». Единая точка входа: локальный
  self-check одной командой вместо восьми; CI сжат с ~15 шагов до двух
  (`--with-tests` гоняет и агентов, и их семь тест-инвариантов); `--with-contracts`
  пробрасывается в Audit; `--json` — машиночитаемая сводка. Считает агента
  «красным» не только по его вердикту, но и при аномалии (невалидный JSON = агент
  упал; `verdict=green` при коде ≠ 0). **Тест-инвариант**
  [`test_run_all.py`](../ai-agents/test_run_all.py) (13/13) на фейковых агентах/
  тестах доказывает «красное сводится в красное, зелёное не ложно-падает». На
  реальном репо: агенты 8/8, тесты 7/7. `PTD-0029`. TESTNET-ONLY.
- **PTD-0027 (сессия 30):** Этап 6 (AI-агенты), модуль 7/8 — **Governance-агент**.
  [`governance_agent.py`](../ai-agents/governance_agent.py) — служебный read-only агент
  (ст. 9; **сам НЕ голосует**, ничего не вносит и ничем не распоряжается): превращает в
  машинную проверку жизненный цикл предложения из `GOVERNANCE.md` над конфигами управления
  `governance/snapshot/space.json` и `governance/safe/safe.config.json`. Шесть проверок:
  `one-person-one-vote` (стратегия голоса = `ticket` value=1, любая плутократия по балансу
  краснит — ст. 2/запрет №5), `timed-vote` (срок голосования `delay`/`period` > 0 — §7),
  `off-chain-signal` (`off_chain_signaling=true` и все типы `binding=false` — Snapshot
  обсуждает, исполняет Safe/Timelock — ст. 4/§5), `proposal-binding` (типы про деньги/
  конституцию привязаны к PRIORITIES/ANTI-ABUSE/CONSTITUTION + супербольшинство для поправок
  — ст. 5/§7–§8/ст. 10), `multisig-not-sole` (порог Safe ≥2 и < числа владельцев, 3-из-5,
  никто единолично — ст. 5/§5), `lifecycle-links` (все ссылки конфигов резолвятся — ст. 3).
  Тест-инвариант [`test_governance.py`](../ai-agents/test_governance.py) (26/26). CI
  `ai-agents.yml` расширен (+ тест Governance + Governance). На реальных конфигах: 6/6.
  `PTD-0027`. TESTNET-ONLY. Дальше — последний модуль 8/8 (Mediator).
- **PTD-0026 (сессия 29):** Этап 6 (AI-агенты), модуль 6/8 — **Documentation-агент**.
  [`documentation_agent.py`](../ai-agents/documentation_agent.py) — служебный
  read-only агент: превращает в машинную проверку правило проекта «вся документация
  двуязычна (RU↔EN)» и конституционную проверяемость (ст. 3) / открытость (ст. 6).
  Три проверки по git-отслеживаемым `.md`: `bilingual-pairs` (у каждого публичного
  дока есть пара RU↔EN — правило пар выводится из пути: `docs/NAME.md`↔`docs/en/NAME.md`;
  `<dir>/README.md`↔`<dir>/README.en.md`; корневой `NAME.md`↔`NAME.en.md`),
  `language-switcher` (вверху корректный переключатель `[Русский]·[English]` к
  парному файлу), `link-integrity` (все относительные ссылки резолвятся; внешние
  ссылки и блоки кода исключены — без ложных срабатываний). Служебные одноязычные
  файлы (`BUILDER`/`LAUNCH`/`PROGRESS`/`DECISIONS`/`comms`) исключены by design.
  Вывод человекочитаемый и `--json`; код 0/1; «красный» = сигнал. **Тест-инвариант**
  [`test_documentation.py`](../ai-agents/test_documentation.py) (17/17) доказывает
  «красное ловится, зелёное не ложно-падает». **Польза сразу:** при первом прогоне
  агент вскрыл реальный пробел двуязычности — у `governance/ipfs/README.md` и
  `governance/registry/README.md` не было EN-зеркал; добавлены EN-зеркала +
  переключатели (теперь 8/8 проверок зелёные). Закрывает и P2 «авто-проверка
  двуязычности в CI». CI [`ai-agents.yml`](../.github/workflows/ai-agents.yml)
  расширен (+ тест Documentation + Documentation; триггеры на `**/*.md`, `*.md`).
  `PTD-0026`. TESTNET-ONLY. Дальше — модули 7–8 (Governance / Mediator).
- **PTD-0025 (сессия 28):** Этап 6 (AI-агенты), модуль 5/8 — **Housing-агент**.
  [`housing_agent.py`](../ai-agents/housing_agent.py) — служебный read-only агент,
  профильный помощник по жилищным кейсам: доказывает, что модель целевого расхода
  ([`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md)) — «помощь
  оплачивается напрямую поставщику, не на руки» — заложена В КОД контракта
  [`Disbursement.sol`](../contracts/contracts/Disbursement.sol): `release-to-provider-only`
  (release без адреса-параметра → транш строго на c.provider), `provider-fixed`
  (нет setProvider/.provider=), `refund-to-treasury` (возврат в казну, не получателю),
  `tranche-limit` (потолок maxRelease), `guardian-cannot-move` (средства двигает
  только executor; guardian лишь ставит паузу) + проверки жилищных записей реестра
  (`targeted-escrow`/`provider-onchain`/`category-priority`, уровень читается из
  [`PRIORITIES.md`](PRIORITIES.md)). Вывод человекочитаемый и `--json`; код 0/1;
  «красный» = сигнал. **Тест-инвариант** [`test_housing.py`](../ai-agents/test_housing.py)
  (23/23) доказывает «красное ловится, зелёное не ложно-падает» (отравленные версии
  контракта/записей; не-жилищные записи игнорируются; отсев комментариев). CI
  [`ai-agents.yml`](../.github/workflows/ai-agents.yml) расширен (+ триггеры на
  contracts/contracts и docs/PRIORITIES.md). На реальном `Disbursement.sol`: 8/8.
  `PTD-0025`. TESTNET-ONLY. Дальше — модули 6–8 (Governance / Mediator / Documentation).
- **PTD-0024 (сессия 27):** Этап 6 (AI-агенты), модуль 4/8 — **Reputation-агент**.
  [`reputation_agent.py`](../ai-agents/reputation_agent.py) — служебный read-only
  агент: статически разбирает ончейн-контракт репутации
  [`Reputation.sol`](../contracts/contracts/Reputation.sol) и офчейн-настройки
  [`space.json`](../governance/snapshot/space.json) и доказывает, что модель
  «1 человек = 1 голос» ([`GOVERNANCE.md`](GOVERNANCE.md) §2–§3) сохранена В КОДЕ:
  `soulbound` (у бейджа нет функций перевода — голос не продать), `bounded-weight`
  (`votingUnits`: не участник → 0, участник → `1 + min(points, cap)`, коридор
  [1..1+cap] — власть денег невозможна), `no-funds` (слой репутации не двигает
  средства — «уникальность ≠ власть»), `roles-separated` (verifier подтверждает
  уникальность, governor правит параметры; роли не смешаны), `off-chain-equal`
  (стратегия Snapshot = равный `ticket` value=1, не плутократия по балансу; допуск
  только участникам). Вывод человекочитаемый и `--json`; код 0/1; «красный» =
  сигнал. **Тест-инвариант** [`test_reputation.py`](../ai-agents/test_reputation.py)
  (17/17) доказывает «красное ловится, зелёное не ложно-падает» (включая отсев
  упоминаний в комментариях Solidity). CI
  [`ai-agents.yml`](../.github/workflows/ai-agents.yml) расширен. `PTD-0024`.
  TESTNET-ONLY. Дальше — модули 5–8 (Housing / Governance / Mediator / Documentation).
- **PTD-0023 (сессия 26):** Этап 6 (AI-агенты), модуль 3/8 — **Fairness-агент**.
  [`fairness_agent.py`](../ai-agents/fairness_agent.py) — служебный read-only агент:
  проходит по записям публичного реестра типа `disbursement` и проверяет КАЖДУЮ
  выплату на справедливость распределения и антизлоупотребление — `priority-valid`
  (уровень приоритета в шкале 1..10, читается ПРЯМО из [`PRIORITIES.md`](PRIORITIES.md)),
  `safeguards` (приоритет не отключает `limit_ok`/`collective_review`/окно апелляции),
  `collective-review` (≥2 независимых подтверждения — не единолично), `staged-payments`
  (поэтапность `1<=index<=of`), `applicant-privacy` (нет персональных данных — только
  псевдонимный `case_id`). Вывод человекочитаемый и `--json`; код 0/1; «красный» =
  сигнал. **Тест-инвариант** [`test_fairness.py`](../ai-agents/test_fairness.py) (17/17)
  доказывает «красное ловится, зелёное не ложно-падает» (включая пустой реестр).
  **Побочно:** найден и исправлен латентный баг с сессии 25 — Guardian ложно краснел
  на собственном тест-инварианте (строка-фикстура `private_key: 0x...`), из-за чего
  CI `ai-agents` на `main` был фактически красным; Guardian научен пропускать
  текстовый скан тест-инвариантов агентов (`ai-agents/test_*.py`), +регрессионный
  сценарий. CI [`ai-agents.yml`](../.github/workflows/ai-agents.yml) расширен. `PTD-0023`.
  TESTNET-ONLY. Дальше — модули 4–8 (Reputation / Housing / …).
- **PTD-0022 (сессия 25):** Этап 6 (AI-агенты), модуль 2/8 — **Guardian-агент**.
  [`guardian_agent.py`](../ai-agents/guardian_agent.py) — отдельный явный сканер рельс
  безопасности по ВСЕМУ дереву репо (по git-отслеживаемым файлам): `secrets-tracked`
  (нет закоммиченных секретов/ключей/состояния пульса), `gitignore-guards`
  (`.gitignore` прикрывает `.env`/`logs/`), `no-mainnet` (нет mainnet `chain_id` в JSON),
  `no-key-material` (нет приватных ключей в тексте: 64-hex вне хэш-полей + присваивание
  `private key`/`mnemonic`/`seed`). Без ложных срабатываний на легитимных sha256/CID
  реестра и манифеста (64-hex считается ключом только вне хэш-полей). **Тест-инвариант**
  [`test_guardian.py`](../ai-agents/test_guardian.py) (14/14) на временном git-репо
  доказывает «красное реально ловится, зелёное не ложно-падает». CI
  [`ai-agents.yml`](../.github/workflows/ai-agents.yml) расширен (Audit + тест Guardian +
  Guardian). `PTD-0022`. TESTNET-ONLY. Дальше — модули 3–8 (Fairness / Reputation / …).
- **PTD-0021 (сессия 24):** Этап 6 (AI-агенты), модуль 1/8 — **каркас
  [`ai-agents/`](../ai-agents/) + первый рабочий агент Audit**. README (RU/EN)
  фиксирует принцип ст. 9 «ИИ служит, не правит» и границы для всех агентов
  (read-only к средствам, находка = сигнал, не действие), таблицу восьми агентов.
  [`audit_agent.py`](../ai-agents/audit_agent.py) объединяет четыре рельс-валидатора
  (`registry`/`ipfs`/`safe`/`snapshot`) в один аудит-прогон и связывает каждую
  проверку со статьёй конституции (ст. 3/2/4); опция `--with-contracts` добавляет
  тесты контрактов (ст. 4/7); вывод человекочитаемый и `--json`; код возврата 0/1.
  CI [`ai-agents.yml`](../.github/workflows/ai-agents.yml) на push/PR. «До зелёного»:
  4/4 базовый, 5/5 с контрактами (54 теста). Реализует и идею «единый governance-
  валидатор в CI». При первом прогоне агент поймал реальный рассинхрон IPFS-манифеста
  (исправлен). TESTNET-ONLY. Дальше — модуль 2/8 (Guardian) и остальные.
- **PTD-0020 (сессия 23):** Этап 5 (Смарт-контракты), часть 3c — **сборка всего
  он-чейн контура**. [`contracts/scripts/deploy.js`](../contracts/scripts/deploy.js)
  разворачивает пять контрактов и связывает их в единый механизм
  (Reputation→Timelock→Treasury/Disbursement→Governor): `executor` казны/escrow =
  `Timelock`, `governor` Timelock = `Governor`, bootstrap-admin снят (`renounceAdmin`),
  `Reputation.governor` = `Timelock`. После проводки никто не двигает средства
  единолично (деплойер без привилегий, исполняет только прошедшее+отложенное
  голосование). Интеграционный тест [`Integration.test.js`](../contracts/test/Integration.test.js)
  прогоняет главный сценарий фонда «заявка-кейс → прямое голосование → задержка
  `Timelock` → **целевая выплата напрямую поставщику** через `Disbursement`», а также
  guardian-вето и проверку проводки; +4 теста «до зелёного» (54/54 со всеми
  контрактами). `npm run deploy:local` для демо. TESTNET-ONLY. Этап 5 (каркас)
  собран целиком; дальше — часть 4 (публичный testnet, сеть с оператором) либо Этап 6.
- **PTD-0019 (сессия 22):** Этап 5 (Смарт-контракты), часть 3b — контракты
  [`Governor.sol`](../contracts/contracts/Governor.sol) + [`Timelock.sol`](../contracts/contracts/Timelock.sol)
  по [`GOVERNANCE.md`](GOVERNANCE.md) §4–§7. Прямое голосование верифицированных
  участников: `propose`/`castVote`/`queue`/`execute`, вес голоса из
  `Reputation.votingUnits` («1 человек = 1 голос», не плутократия), кворум/срок,
  публичный детерминированный подсчёт. Принятое решение исполняется **только через
  `Timelock`** (обязательная задержка = окно на аудит/апелляцию; Governor сам
  средства не двигает — двигает казна по приказу Timelock). `guardian` = аварийное
  вето (`cancel`), `admin` = разовый bootstrap (`renounceAdmin`); параметры и роли
  меняются только голосованием (`onlyTimelock`/`onlySelf`). 15 тестов «до зелёного»,
  включая полный цикл «предложение → голос → Timelock → выплата поставщику» (50/50
  со всеми контрактами). TESTNET-ONLY. Дальше — часть 3c (сборка контура) и часть 4
  (testnet-деплой).
- **PTD-0018 (сессия 21):** Этап 5 (Смарт-контракты), часть 3a — контракт
  [`Reputation.sol`](../contracts/contracts/Reputation.sol): непередаваемый
  (soulbound) бейдж верифицированного участника по [`GOVERNANCE.md`](GOVERNANCE.md)
  §2–§3. «1 человек = 1 голос» в коде: `votingUnits(addr)` = 0 для не-участника и
  1 + min(`reputationPoints`, `reputationCap`) для участника — вес всегда в коридоре
  [1..1+cap], власть денег невозможна. Soulbound: у контракта **нет функций перевода**
  (transfer/approve/transferFrom) by design. «Уникальность ≠ власть»: `verifier`
  выдаёт/отзывает бейдж, `governor` правит параметры, ни одна роль не двигает
  средства. Отзыв сбрасывает вес в 0 и репутацию. 11 тестов «до зелёного» (35/35 с
  Treasury+Disbursement). TESTNET-ONLY. Дальше — часть 3b (`Governor`+`Timelock`).
- **PTD-0017 (сессия 20):** Этап 5 (Смарт-контракты), часть 2 — контракт целевого
  escrow [`Disbursement.sol`](../contracts/contracts/Disbursement.sol) по
  [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md): `open` фиксирует
  поставщика в кейсе, `release(id, amount)` **не принимает адрес получателя** — транш
  уходит строго поставщику («не даём деньги — оплачиваем нужду»); `refund` возвращает
  остаток в казну (не получателю); поэтапность (накопление `released` + лимит транша
  `maxRelease`); обеспеченность escrow (`available()`); только `executor` двигает,
  `guardian` только пауза; события + `registryRef`. 14 тестов «до зелёного» (24/24 с
  Treasury). Реестровая схема `disbursement` расширена `provider/category/escrow_id`.
  TESTNET-ONLY. Дальше — часть 3 (`Governance` + `Reputation`).
- **PTD-0016 (сессия 19):** Этап 5 (Смарт-контракты), часть 1 — проект
  [`contracts/`](../contracts/) (Hardhat + ethers v6 + chai, Solidity 0.8.24) +
  базовый контракт-скелет [`Treasury.sol`](../contracts/contracts/Treasury.sol):
  казна отдаёт средства только через `executor` (мультисиг/Timelock), лимит одной
  выплаты, аварийная пауза `guardian`, события на каждое движение + `registryRef`
  (связь с реестром). 10 тестов конституционных свойств «до зелёного» + CI
  [`contracts.yml`](../.github/workflows/contracts.yml). TESTNET-ONLY, без реальных
  средств/ключей. Открывает Этап 5 (части 2–4 — Disbursement/Governance/Reputation/деплой).
- **PTD-0015 (сессия 18):** макет off-chain голосования
  [`governance/snapshot/`](../governance/snapshot/) — `space.json` (настройки
  Snapshot: стратегия `ticket` value=1 = «1 человек = 1 голос», допуск только
  верифицированных, типы предложений, привязка к GOVERNANCE/PRIORITIES/CONSTITUTION)
  + JSON-схема + README (RU/EN) + валидатор рельс `scripts/snapshot_config.py` (только
  testnet, без плутократии по балансу токена, анти-Сивилла, без приватных ключей) + CI.
  Snapshot = палата обсуждения/сигнала, средства не двигает. Закрывает Этап 4 часть 1.
- **PTD-0014 (сессия 17):** модель поддержки [`SUPPORT-MODEL.md`](SUPPORT-MODEL.md)
  (+EN) — поддержка приходит из самой работающей системы (прозрачная казна-мультисиг
  3-из-5 + контракты, каждый поток в реестре и on-chain, расход по голосованию), а НЕ
  отдельной кнопкой/адресом сбоку. До запуска и аудита адрес для реальных денег не
  публикуется. На сайте — честное объяснение без кнопки-доната. Закрывает INBOX-пункт о донатах.
- **PTD-0012 (сессия 15):** аутрич [`OUTREACH.md`](OUTREACH.md) (+EN) —
  категории адресатов (с приоритетами P0–P3) + где искать официальный публичный
  контакт, правила персонализации и «лестница просьб», 5 шаблонов писем RU + 5 EN,
  регламент после ответа, таблица «агент vs оператор». Заготовка «до кнопки»:
  отправляет оператор лично, агент не рассылает. Закрывает INBOX #8.
- **PTD-0011 (сессия 14):** почта проекта [`EMAIL-SETUP.md`](EMAIL-SETUP.md)
  (+EN) — сравнение вариантов (свой домен / ProtonMail / Gmail) с рекомендацией,
  адреса/алиасы, пошаговая инструкция оператору (Proton-старт + свой домен с
  MX/SPF/DKIM/DMARC), подпись-boilerplate, шаблоны ответов RU/EN. Заготовка «до
  кнопки»: регистрацию ящика и хранение пароля делает оператор. Закрывает INBOX #7.
- **PTD-0006 (сессия 9):** материалы продвижения [`PROMOTION.md`](PROMOTION.md)
  (+EN) — рельсы сообщения, boilerplate+дисклеймер, лендинг-копия, питч RU/EN
  (3 формата), пост-анонс (Telegram + Twitter/X), FAQ «общественное благо, НЕ
  инвестиция», чек-лист публикации. Все тексты сверены с конституционными
  запретами. Заготовки «до кнопки» — публикует оператор. Закрывает INBOX #6.
- **PTD-0005 (сессия 8):** заведён сам механизм саморазвития — этот `ROADMAP.md`
  (+EN), правило в `BUILDER.md` («INBOX пуст → следующий пункт ROADMAP») и режим
  автономии по умолчанию (INBOX #9). Закрывает INBOX #5 и #9.

---

## Лог идей (кто/когда предложил)

Чтобы саморазвитие было прозрачным, фиксируем происхождение идей.

| Идея | Источник | Сессия |
|------|----------|--------|
| Механизм саморазвития (ROADMAP + правило) | оператор (INBOX #5) | 8 |
| Режим автономии по умолчанию | оператор (INBOX #9) | 8 |
| CONTRIBUTING / глоссарий / страница прозрачности / CI-двуязычность | агент | 8 |
| Дашборд казны / шаблоны заявок / changelog / репутация | агент | 8 |
| Лендинг-страница в web / медиа-кит / пресс-страница | агент | 9 |
| Шаблоны предложений Snapshot / единый governance-валидатор в CI | агент | 18 |
| Тест-инвариант Audit / Guardian-агент / Documentation-агент (двуязычность) | агент | 24 |
| Мета-агент «прогнать всех» / pre-commit-хук / лексический линтер запретов | агент | 25 |
| Тест-инвариант «выплата ↔ запись реестра» / самопроверка агентов в CI / Reputation-агент | агент | 26 |
| Reputation на Governor.sol / проверка cap деплоя / общий solidity_scan.py | агент | 27 |
| Рефакторинг общих solidity-помощников (3 копии) / Housing provider-whitelist / сквозной тест «запись ↔ on-chain escrow» | агент | 28 |
| Мета-агент run_all / линтер запретов в публичных текстах / changelog из реестра | агент | 29 |
| Статус-бейдж run_all / тест-инвариант Audit / общий agent_report.py | агент | 32 |
