// Двуязычные тексты платформы (русский ↔ английский).
//
// Простыми словами: всё, что видит человек, хранится здесь сразу на двух языках.
// Переключатель языка в шапке выбирает нужный набор. Технических терминов в
// основном тексте нет — это требование понятного языка (решение PTD-0040).

import type { ProposalStatus, VoteChoice } from "@/lib/voting";

export type Lang = "ru" | "en";

export const LANGS: Lang[] = ["ru", "en"];
export const DEFAULT_LANG: Lang = "ru";

export type WalletDict = {
  back: string;
  title: string;
  lead: string;
  whatTitle: string;
  whatText: string;
  whyTitle: string;
  why: string[];
  safeTitle: string;
  safe: string[];
  connect: string;
  connecting: string;
  connected: string;
  yourAddress: string;
  network: string;
  forget: string;
  noWalletTitle: string;
  noWalletText: string;
  noWalletLink: string;
  errRejected: string;
  errNoWallet: string;
  testnetOk: string;
  testnetWarn: string;
  testnetUnknown: string;
};

export type ApplyDict = {
  back: string;
  title: string;
  lead: string;
  privacyTitle: string;
  privacy: string[];
  formTitle: string;
  priorityLabel: string;
  priorityHint: string;
  priorityChoose: string;
  priorityLabels: Record<string, string>;
  needLabel: string;
  needHint: string;
  needPlaceholder: string;
  spendLabel: string;
  spendHint: string;
  spendPlaceholder: string;
  amountLabel: string;
  amountHint: string;
  amountPlaceholder: string;
  personalDataWarn: string;
  priorityRequired: string;
  needRequired: string;
  spendRequired: string;
  submit: string;
  draftTitle: string;
  draftLead: string;
  copy: string;
  copied: string;
  download: string;
  startOver: string;
  howTitle: string;
  how: string[];
};

export type JournalDict = {
  back: string;
  title: string;
  lead: string;
  whatTitle: string;
  whatText: string;
  countLabel: string;
  headHashLabel: string;
  headHashHint: string;
  filterLabel: string;
  filterAll: string;
  typeLabels: Record<string, string>;
  searchLabel: string;
  searchPlaceholder: string;
  showing: string;
  nothingFound: string;
  hashLabel: string;
  viewRecord: string;
  howTitle: string;
  how: string[];
  verifyLink: string;
};

export type VotingDict = {
  back: string;
  title: string;
  lead: string;
  demoNote: string;
  howTitle: string;
  how: string[];
  proposalsTitle: string;
  statusLabels: Record<ProposalStatus, string>;
  choiceLabels: Record<VoteChoice, string>;
  proposals: Record<string, { title: string; summary: string }>;
  peopleLabel: string;
  closedNote: string;
  yourVoteTitle: string;
  votePrompt: string;
  voted: string;
  weightNote: string;
  ballotLead: string;
  copy: string;
  copied: string;
  download: string;
  changeVote: string;
  finalTitle: string;
  final: string[];
  verifyLink: string;
};

export type Dict = {
  htmlLang: string;
  brand: string;
  tagline: string;
  skipToContent: string;
  toggleLang: string;
  toggleLangShort: string;
  toggleTheme: string;
  disclaimer: string;
  heroTitle: string;
  heroLead: string;
  ctaRegistry: string;
  ctaSite: string;
  screensTitle: string;
  screensLead: string;
  soon: string;
  ready: string;
  open: string;
  screens: { title: string; text: string; href?: string }[];
  transparencyTitle: string;
  transparencyText: string;
  footerNote: string;
  contact: string;
  builtNote: string;
  wallet: WalletDict;
  apply: ApplyDict;
  journal: JournalDict;
  voting: VotingDict;
};

export const DICT: Record<Lang, Dict> = {
  ru: {
    htmlLang: "ru",
    brand: "Public Trust DAO",
    tagline: "Общественный фонд доверия",
    skipToContent: "Перейти к содержимому",
    toggleLang: "English",
    toggleLangShort: "EN",
    toggleTheme: "Сменить тему",
    disclaimer:
      "Это общественное благо, а не вложение денег. Здесь не обещают доход, нет пирамиды и нет платы за привлечение людей.",
    heroTitle: "Платформа фонда — место, где помощь видна каждому",
    heroLead:
      "Это рабочее приложение фонда. Через него люди смогут попросить помощь, видеть открытый журнал решений, голосовать наравне со всеми и проверять состояние общей казны. Мы собираем платформу шаг за шагом и показываем каждый готовый экран здесь.",
    ctaRegistry: "Открытый журнал решений",
    ctaSite: "О фонде (главный сайт)",
    screensTitle: "Что появится в платформе",
    screensLead:
      "Каждый экран делаем сразу рабочим. Пока умные контракты не запущены в тестовой сети, экраны показывают данные из открытого журнала и понятные заготовки — приложение «оживает» уже сейчас.",
    soon: "скоро",
    ready: "готово",
    open: "Открыть",
    screens: [
      {
        title: "Подключить кошелёк",
        text: "Простое подключение кошелька с понятным объяснением, что это и зачем — без скрытых действий.",
        href: "/wallet/",
      },
      {
        title: "Подать заявку на помощь",
        text: "Спокойная форма без лишних личных данных. Помощь идёт по честному порядку: сначала самые срочные нужды.",
        href: "/apply/",
      },
      {
        title: "Открытый журнал",
        text: "Любое решение фонда можно посмотреть и проверить — ничего не спрятано.",
        href: "/journal/",
      },
      {
        title: "Голосование",
        text: "Один человек — один голос. Голос не покупается и не продаётся.",
        href: "/voting/",
      },
      {
        title: "Окно казны",
        text: "Видно состояние общей казны и куда уходят средства — только для просмотра.",
      },
      {
        title: "Проверка личности",
        text: "Подтверждение «живой и один человек» без слежки и без сбора лиц в базу.",
      },
    ],
    transparencyTitle: "Честно и без слежки",
    transparencyText:
      "В платформе нет сторонних счётчиков, рекламы и слежки. Шрифты системные, ничего не подгружается с чужих серверов. Весь код открыт, каждое решение записано в открытый журнал.",
    footerNote:
      "Public Trust DAO — общественное благо, не инвестиция. Всё на тестовой сети, без реальных денег.",
    contact: "Контакт",
    builtNote: "Платформа на Next.js · статическая сборка · открытый код",
    wallet: {
      back: "← На главную",
      title: "Подключить кошелёк",
      lead: "Кошелёк — это ваш способ войти в платформу и в будущем голосовать и получать помощь как один человек. Подключение ничего не списывает и не даёт фонду доступ к вашим деньгам.",
      whatTitle: "Что такое кошелёк простыми словами",
      whatText:
        "Кошелёк — небольшое приложение (например, MetaMask), которое хранит ваш личный ключ и ваш публичный адрес. Публичный адрес похож на номер почтового ящика: его видно всем, и это нормально. Личный ключ остаётся только у вас — фонд его никогда не видит и не запрашивает.",
      whyTitle: "Зачем подключать",
      why: [
        "Войти в платформу без логина и пароля.",
        "В будущем — голосовать наравне со всеми: один человек, один голос.",
        "Видеть свои заявки и решения, которые вас касаются.",
      ],
      safeTitle: "Что НЕ происходит при подключении",
      safe: [
        "Деньги не списываются и никуда не переводятся — подключение лишь показывает ваш публичный адрес.",
        "Фонд не получает доступ к вашим средствам и не видит ваш личный ключ.",
        "Отключиться можно в любой момент — кнопкой ниже и в самом кошельке.",
      ],
      connect: "Подключить кошелёк",
      connecting: "Подключаем…",
      connected: "Кошелёк подключён",
      yourAddress: "Ваш публичный адрес",
      network: "Сеть",
      forget: "Отключить",
      noWalletTitle: "Кошелёк не найден",
      noWalletText:
        "В этом браузере не найден кошелёк (например, MetaMask). Это нормально — устанавливать кошелёк дело добровольное. Платформу можно смотреть и без него; кошелёк нужен только для входа, голосования и заявок.",
      noWalletLink: "Как завести кошелёк (официальный сайт MetaMask)",
      errRejected:
        "Подключение отменено. Это нормально — можно попробовать снова в любой момент.",
      errNoWallet: "Кошелёк не найден в этом браузере.",
      testnetOk:
        "Это тестовая сеть — реальных денег здесь нет, всё для проверки.",
      testnetWarn:
        "Сейчас выбрана основная сеть с реальными деньгами. Фонд работает только в тестовой сети — реальные средства не используются. Пожалуйста, переключите кошелёк на тестовую сеть.",
      testnetUnknown:
        "Сеть не распознана. Фонд работает в тестовой сети — при необходимости переключите кошелёк.",
    },
    apply: {
      back: "← На главную",
      title: "Подать заявку на помощь",
      lead: "Это спокойная форма для просьбы о помощи. Заявка анонимна — личные данные вносить не нужно. Помощь идёт по честному порядку: сначала самые срочные беды. Пока приложение работает в тестовом режиме: форма собирает черновик заявки в вашем браузере, ничего не уходит на сторонние серверы.",
      privacyTitle: "Что НЕ нужно писать в заявке",
      privacy: [
        "Не нужно настоящее имя, адрес, телефон, почту или номера документов.",
        "Не нужны фотографии и сканы — фонд не собирает лица и документы в базу.",
        "Опишите беду своими словами: что случилось и какая помощь нужна. Этого достаточно, чтобы решение приняли честно.",
      ],
      formTitle: "Заявка",
      priorityLabel: "Какая это беда",
      priorityHint: "Выберите, к чему ближе всего ваша ситуация. От этого зависит, насколько срочно её рассмотрят.",
      priorityChoose: "— выберите —",
      priorityLabels: {
        life_threat: "1 · Угроза жизни",
        housing_loss: "2 · Угроза остаться без жилья",
        medical: "3 · Здоровье и лечение",
        food: "4 · Еда",
        children: "5 · Дети",
        elderly: "6 · Пожилые люди",
        disability: "7 · Люди с инвалидностью",
        self_reliance: "8 · Встать на ноги",
        education: "9 · Учёба",
        public_good: "10 · Долгая польза для всех",
      },
      needLabel: "Что случилось и какая помощь нужна",
      needHint: "Своими словами, без личных данных. Коротко и по делу.",
      needPlaceholder: "Например: после пожара нет где жить, нужно временное жильё на месяц.",
      spendLabel: "На что именно пойдут средства",
      spendHint: "Фонд не выдаёт деньги на руки, а оплачивает нужду напрямую (например, аренду — арендодателю, лекарство — аптеке). Напишите, что нужно оплатить.",
      spendPlaceholder: "Например: оплата аренды комнаты за один месяц напрямую арендодателю.",
      amountLabel: "Примерная сумма (необязательно)",
      amountHint: "Если знаете — укажите приблизительно. Все суммы пока в тестовой сети, без реальных денег.",
      amountPlaceholder: "Например: около 300 (тестовые единицы)",
      personalDataWarn: "Похоже, в тексте остались личные данные (телефон, почта или номер документа). Заявка анонимна — пожалуйста, уберите их. Подать всё равно можно.",
      priorityRequired: "Пожалуйста, выберите, какая это беда.",
      needRequired: "Пожалуйста, опишите, что случилось и какая помощь нужна.",
      spendRequired: "Пожалуйста, напишите, на что именно пойдут средства.",
      submit: "Собрать черновик заявки",
      draftTitle: "Черновик заявки готов",
      draftLead: "Вот ваша анонимная заявка простой проверяемой записью. Реальная подача появится, когда контракты запустят в тестовой сети. Пока вы можете скопировать или сохранить черновик.",
      copy: "Скопировать",
      copied: "Скопировано",
      download: "Сохранить файлом",
      startOver: "Заполнить заново",
      howTitle: "Что будет дальше",
      how: [
        "Срочную беду рассматривают первой, но проверку это не отменяет.",
        "Деньги идут по частям, с лимитами, а каждую выплату проверяют несколько независимых людей.",
        "Очередь зависит только от тяжести беды, а не от того, кто человек: происхождение, статус и репутация на очередь не влияют.",
        "Любое решение по заявке попадёт в открытый журнал — его можно будет посмотреть и проверить.",
      ],
    },
    journal: {
      back: "← На главную",
      title: "Открытый журнал решений",
      lead: "Это список всех решений фонда по порядку, новые сверху. Здесь ничего не спрятано: каждое решение видно и его можно проверить. Записи нельзя задним числом изменить или удалить — журнал устроен так, что любая подмена сразу заметна.",
      whatTitle: "Как устроена защита от подмены простыми словами",
      whatText:
        "Каждая запись несёт короткий контрольный отпечаток и помнит отпечаток предыдущей — записи сцеплены в цепочку. Если кто-то изменит хотя бы одну старую запись, её отпечаток перестанет совпадать, и это сразу увидят все. Поэтому общий «отпечаток журнала» внизу — это контрольный код всего списка целиком.",
      countLabel: "Записей в журнале",
      headHashLabel: "Отпечаток журнала",
      headHashHint:
        "Контрольный код всей цепочки записей. Меняется, если подменить хоть одну запись.",
      filterLabel: "Показать вид записей",
      filterAll: "Все виды",
      typeLabels: {
        genesis: "Открытие журнала",
        decision: "Решение",
        disbursement: "Выплата",
        governance: "Управление",
        audit: "Проверка",
        appeal: "Апелляция",
        reputation: "Репутация",
        note: "Заметка",
      },
      searchLabel: "Поиск по записям",
      searchPlaceholder: "Например: кошелёк, выплата или PTD-0075",
      showing: "Показано записей:",
      nothingFound: "По запросу ничего не найдено. Попробуйте другие слова.",
      hashLabel: "отпечаток",
      viewRecord: "Посмотреть полную запись →",
      howTitle: "Как это проверить самому",
      how: [
        "Весь журнал открыт: каждая запись — отдельный файл в общем репозитории, ссылка ведёт прямо на него.",
        "Любой может пересчитать отпечатки и убедиться, что цепочка цела — для этого есть открытый инструмент проверки в репозитории.",
        "Пока контракты не запущены в тестовой сети, важные отпечатки будут дополнительно закрепляться в блокчейне — тогда подмену станет невозможно скрыть совсем.",
      ],
      verifyLink: "Открытый журнал и инструмент проверки (репозиторий)",
    },
    voting: {
      back: "← На главную",
      title: "Голосование",
      lead: "Здесь решают сами люди. Главное правило: один человек — один голос. Голос нельзя купить за деньги и нельзя продать — голос каждого весит одинаково. Любой участник может предложить решение, а сообщество голосует «за» или «против».",
      demoNote:
        "Пока умные контракты не запущены в тестовой сети, ниже — показательные предложения (примеры). Ваш голос собирается как проверяемый черновик прямо в браузере: ничего не уходит на сторонние серверы и пока не попадает в блокчейн.",
      howTitle: "Как устроено голосование простыми словами",
      how: [
        "Один человек — один голос. Право голоса даёт подтверждённая уникальность живого человека, а не количество денег на счету.",
        "Любой участник может предложить решение. Чтобы оно прошло, нужно, чтобы проголосовало достаточно людей и большинство было «за».",
        "Прошедшее решение казна исполняет сама — но с задержкой на проверку. В это окно можно заметить и остановить явно вредное или «угнанное» решение, пока деньги ещё не ушли.",
        "Деньгами не распоряжается ни один человек: хранители лишь технически проводят уже принятое решение и могут нажать «паузу» при явной поломке — направить деньги по своему желанию они не могут.",
      ],
      proposalsTitle: "Предложения",
      statusLabels: {
        open: "Идёт голосование",
        timelock: "Принято — идёт проверка",
        passed: "Принято и исполнено",
        rejected: "Отклонено",
      },
      choiceLabels: {
        for: "За",
        against: "Против",
        abstain: "Воздержаться",
      },
      proposals: {
        "demo-1": {
          title: "Пример: помощь семье после пожара",
          summary:
            "Оплатить напрямую арендодателю временное жильё на один месяц для семьи, потерявшей дом при пожаре. Деньги не выдаются на руки — оплачивается нужда напрямую (целевой расход).",
        },
        "demo-2": {
          title: "Пример: настройка доли на помощь при малой казне",
          summary:
            "Когда в казне мало средств, направлять на прямую помощь людям не меньше 70%, а награды за работу держать минимальными. Изменение настройки — голосованием, с задержкой на проверку.",
        },
        "demo-3": {
          title: "Пример: единоразовая крупная выплата без проверки",
          summary:
            "Предложение выдать крупную сумму одному получателю сразу и без независимой проверки. Отклонено: противоречит правилам — выплаты идут по частям, с лимитами и независимой проверкой.",
        },
      },
      peopleLabel: "чел.",
      closedNote: "Голосование по этому предложению уже завершено — показан итог.",
      yourVoteTitle: "Ваш голос",
      votePrompt: "Как вы голосуете по этому предложению?",
      voted: "Ваш голос учтён — он весит ровно один, как у каждого.",
      weightNote: "Вес вашего голоса: 1 (один человек — один голос).",
      ballotLead:
        "Вот ваш голос простой проверяемой записью. Настоящая подача появится, когда контракты запустят в тестовой сети. Пока вы можете скопировать или сохранить черновик.",
      copy: "Скопировать",
      copied: "Скопировано",
      download: "Сохранить файлом",
      changeVote: "Изменить голос",
      finalTitle: "Что будет, когда заработает по-настоящему",
      final: [
        "Голосовать сможет каждый, чья реальность и уникальность подтверждена, — без сбора лиц в базу и без слежки.",
        "Каждый голос и каждый итог попадут в открытый журнал и будут закреплены отпечатком — подменить нельзя.",
        "Принятое решение исполнит сама казна по правилам, с задержкой на проверку; ни один человек не сможет направить деньги в обход голосования.",
      ],
      verifyLink: "Как устроено управление (документ GOVERNANCE)",
    },
  },
  en: {
    htmlLang: "en",
    brand: "Public Trust DAO",
    tagline: "A public trust fund",
    skipToContent: "Skip to content",
    toggleLang: "Русский",
    toggleLangShort: "RU",
    toggleTheme: "Switch theme",
    disclaimer:
      "This is a public good, not an investment. No promised returns, no pyramid, and no payment for bringing in people.",
    heroTitle: "The fund's platform — where help is visible to everyone",
    heroLead:
      "This is the fund's working application. Through it people will be able to ask for help, see the open record of decisions, vote as equals, and check the state of the shared treasury. We are building the platform step by step and show each finished screen here.",
    ctaRegistry: "Open record of decisions",
    ctaSite: "About the fund (main site)",
    screensTitle: "What the platform will include",
    screensLead:
      "Each screen is built to actually work. Until the smart contracts run on a test network, screens show data from the open record and clear placeholders — the app already comes to life now.",
    soon: "soon",
    ready: "ready",
    open: "Open",
    screens: [
      {
        title: "Connect a wallet",
        text: "A simple wallet connection with a clear explanation of what it is and why — no hidden actions.",
        href: "/wallet/",
      },
      {
        title: "Apply for help",
        text: "A calm form with no unnecessary personal data. Help follows a fair order: the most urgent needs first.",
        href: "/apply/",
      },
      {
        title: "Open record",
        text: "Every decision of the fund can be viewed and checked — nothing is hidden.",
        href: "/journal/",
      },
      {
        title: "Voting",
        text: "One person, one vote. A vote cannot be bought or sold.",
        href: "/voting/",
      },
      {
        title: "Treasury window",
        text: "See the state of the shared treasury and where funds go — view only.",
      },
      {
        title: "Identity check",
        text: "Confirming 'a real, single person' without surveillance and without collecting faces into a database.",
      },
    ],
    transparencyTitle: "Honest and without surveillance",
    transparencyText:
      "The platform has no third-party counters, ads, or tracking. Fonts are system fonts, nothing loads from other people's servers. All code is open and every decision is written to the open record.",
    footerNote:
      "Public Trust DAO — a public good, not an investment. Everything is on a test network, with no real money.",
    contact: "Contact",
    builtNote: "Platform on Next.js · static export · open source",
    wallet: {
      back: "← Back to home",
      title: "Connect a wallet",
      lead: "A wallet is how you sign in to the platform and, in the future, vote and receive help as a single person. Connecting takes nothing from you and gives the fund no access to your money.",
      whatTitle: "What a wallet is, in plain words",
      whatText:
        "A wallet is a small app (such as MetaMask) that holds your private key and your public address. The public address is like a mailbox number: everyone can see it, and that is fine. The private key stays only with you — the fund never sees it and never asks for it.",
      whyTitle: "Why connect",
      why: [
        "Sign in to the platform without a login or password.",
        "In the future — vote as equals: one person, one vote.",
        "See your own applications and the decisions that concern you.",
      ],
      safeTitle: "What does NOT happen when you connect",
      safe: [
        "No money is taken or moved anywhere — connecting only shows your public address.",
        "The fund gets no access to your funds and never sees your private key.",
        "You can disconnect at any time — with the button below and in the wallet itself.",
      ],
      connect: "Connect a wallet",
      connecting: "Connecting…",
      connected: "Wallet connected",
      yourAddress: "Your public address",
      network: "Network",
      forget: "Disconnect",
      noWalletTitle: "No wallet found",
      noWalletText:
        "No wallet (such as MetaMask) was found in this browser. That is fine — installing a wallet is entirely optional. You can browse the platform without one; a wallet is only needed to sign in, vote, and apply.",
      noWalletLink: "How to get a wallet (official MetaMask site)",
      errRejected:
        "Connection cancelled. That is fine — you can try again at any time.",
      errNoWallet: "No wallet was found in this browser.",
      testnetOk:
        "This is a test network — there is no real money here, everything is for testing.",
      testnetWarn:
        "A main network with real money is currently selected. The fund works only on a test network — no real funds are used. Please switch your wallet to a test network.",
      testnetUnknown:
        "The network is not recognised. The fund works on a test network — switch your wallet if needed.",
    },
    apply: {
      back: "← Back to home",
      title: "Apply for help",
      lead: "This is a calm form to ask for help. The application is anonymous — no personal data is needed. Help follows a fair order: the most urgent needs first. For now the app runs in test mode: the form builds a draft application in your browser, and nothing is sent to outside servers.",
      privacyTitle: "What you should NOT write in the application",
      privacy: [
        "No real name, address, phone, email, or document numbers.",
        "No photos or scans — the fund does not collect faces or documents into a database.",
        "Describe the situation in your own words: what happened and what help you need. That is enough for a fair decision.",
      ],
      formTitle: "Application",
      priorityLabel: "What kind of need is this",
      priorityHint: "Choose what your situation is closest to. This sets how urgently it is reviewed.",
      priorityChoose: "— choose —",
      priorityLabels: {
        life_threat: "1 · Threat to life",
        housing_loss: "2 · Threat of losing housing",
        medical: "3 · Health and treatment",
        food: "4 · Food",
        children: "5 · Children",
        elderly: "6 · Elderly people",
        disability: "7 · People with disabilities",
        self_reliance: "8 · Getting back on one's feet",
        education: "9 · Learning",
        public_good: "10 · Long-term benefit for everyone",
      },
      needLabel: "What happened and what help is needed",
      needHint: "In your own words, without personal data. Short and to the point.",
      needPlaceholder: "For example: after a fire there is nowhere to live, temporary housing is needed for a month.",
      spendLabel: "What exactly the funds will pay for",
      spendHint: "The fund does not hand out cash — it pays the need directly (for example, rent to the landlord, medicine to the pharmacy). Write what needs to be paid.",
      spendPlaceholder: "For example: one month of room rent paid directly to the landlord.",
      amountLabel: "Approximate amount (optional)",
      amountHint: "If you know it — give a rough figure. All amounts are on a test network for now, with no real money.",
      amountPlaceholder: "For example: about 300 (test units)",
      personalDataWarn: "It looks like the text still contains personal data (a phone, email, or document number). The application is anonymous — please remove it. You can still submit.",
      priorityRequired: "Please choose what kind of need this is.",
      needRequired: "Please describe what happened and what help is needed.",
      spendRequired: "Please write what exactly the funds will pay for.",
      submit: "Build application draft",
      draftTitle: "Application draft is ready",
      draftLead: "Here is your anonymous application as a simple, verifiable record. Real submission becomes available once the contracts run on a test network. For now you can copy or save the draft.",
      copy: "Copy",
      copied: "Copied",
      download: "Save as file",
      startOver: "Fill in again",
      howTitle: "What happens next",
      how: [
        "An urgent need is reviewed first, but that does not skip the checks.",
        "Money is released in parts, with limits, and every payment is reviewed by several independent people.",
        "The queue depends only on the severity of the need, not on who the person is: origin, status, and reputation do not move the queue.",
        "Any decision on the application goes into the open record — it can be viewed and checked.",
      ],
    },
    journal: {
      back: "← Back to home",
      title: "Open record of decisions",
      lead: "This is the list of all of the fund's decisions in order, newest first. Nothing is hidden here: every decision is visible and can be checked. Records cannot be changed or deleted after the fact — the journal is built so that any tampering shows up immediately.",
      whatTitle: "How tamper protection works, in plain words",
      whatText:
        "Each record carries a short check fingerprint and remembers the fingerprint of the one before it — the records are linked into a chain. If anyone changes even a single old record, its fingerprint will no longer match, and everyone sees it at once. So the overall 'journal fingerprint' below is a check code for the whole list together.",
      countLabel: "Records in the journal",
      headHashLabel: "Journal fingerprint",
      headHashHint:
        "A check code for the entire chain of records. It changes if even one record is tampered with.",
      filterLabel: "Show record type",
      filterAll: "All types",
      typeLabels: {
        genesis: "Journal opening",
        decision: "Decision",
        disbursement: "Disbursement",
        governance: "Governance",
        audit: "Audit",
        appeal: "Appeal",
        reputation: "Reputation",
        note: "Note",
      },
      searchLabel: "Search the records",
      searchPlaceholder: "For example: wallet, payment, or PTD-0075",
      showing: "Records shown:",
      nothingFound: "Nothing matched your search. Try different words.",
      hashLabel: "fingerprint",
      viewRecord: "View the full record →",
      howTitle: "How to check it yourself",
      how: [
        "The whole journal is open: each record is a separate file in the shared repository, and the link goes straight to it.",
        "Anyone can recompute the fingerprints and confirm the chain is intact — there is an open verification tool in the repository for this.",
        "Until the contracts run on a test network, important fingerprints will also be anchored on the blockchain — then tampering becomes impossible to hide at all.",
      ],
      verifyLink: "Open journal and verification tool (repository)",
    },
    voting: {
      back: "← Back to home",
      title: "Voting",
      lead: "Here the people decide for themselves. The core rule: one person, one vote. A vote cannot be bought with money and cannot be sold — everyone's vote weighs the same. Any member can propose a decision, and the community votes 'for' or 'against'.",
      demoNote:
        "Until the smart contracts run on a test network, the items below are demonstration proposals (examples). Your vote is built as a verifiable draft right in your browser: nothing is sent to outside servers and nothing goes on-chain yet.",
      howTitle: "How voting works, in plain words",
      how: [
        "One person, one vote. The right to vote comes from a confirmed, unique living person — not from how much money is in an account.",
        "Any member can propose a decision. For it to pass, enough people must vote and the majority must be 'for'.",
        "A passed decision is executed by the treasury itself — but with a delay for review. In that window a clearly harmful or 'hijacked' decision can be spotted and stopped before money moves.",
        "No single person controls the money: keepers only technically carry out an already-passed decision and can hit 'pause' on a clear malfunction — they cannot direct funds wherever they wish.",
      ],
      proposalsTitle: "Proposals",
      statusLabels: {
        open: "Voting open",
        timelock: "Passed — under review",
        passed: "Passed and executed",
        rejected: "Rejected",
      },
      choiceLabels: {
        for: "For",
        against: "Against",
        abstain: "Abstain",
      },
      proposals: {
        "demo-1": {
          title: "Example: help for a family after a fire",
          summary:
            "Pay one month of temporary housing directly to the landlord for a family that lost their home in a fire. No cash is handed out — the need is paid directly (targeted spend).",
        },
        "demo-2": {
          title: "Example: setting the help share when the treasury is low",
          summary:
            "When the treasury is low, direct at least 70% to helping people directly and keep work rewards minimal. Changing the setting is done by vote, with a delay for review.",
        },
        "demo-3": {
          title: "Example: a one-off large payment with no review",
          summary:
            "A proposal to pay a large sum to a single recipient at once and without independent review. Rejected: it breaks the rules — payments go out in parts, with limits and independent review.",
        },
      },
      peopleLabel: "ppl",
      closedNote: "Voting on this proposal has already ended — the result is shown.",
      yourVoteTitle: "Your vote",
      votePrompt: "How do you vote on this proposal?",
      voted: "Your vote is counted — it weighs exactly one, like everyone's.",
      weightNote: "Your vote weight: 1 (one person, one vote).",
      ballotLead:
        "Here is your vote as a simple, verifiable record. Real submission becomes available once the contracts run on a test network. For now you can copy or save the draft.",
      copy: "Copy",
      copied: "Copied",
      download: "Save as file",
      changeVote: "Change vote",
      finalTitle: "What happens when it works for real",
      final: [
        "Everyone whose reality and uniqueness is confirmed will be able to vote — without collecting faces into a database and without surveillance.",
        "Every vote and every result will go into the open record and be anchored by a fingerprint — no tampering possible.",
        "A passed decision is executed by the treasury itself by the rules, with a delay for review; no single person can route money around the vote.",
      ],
      verifyLink: "How governance works (GOVERNANCE document)",
    },
  },
};

export function getDict(lang: Lang): Dict {
  return DICT[lang] ?? DICT[DEFAULT_LANG];
}
