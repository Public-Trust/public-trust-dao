// Двуязычные тексты платформы (русский ↔ английский).
//
// Простыми словами: всё, что видит человек, хранится здесь сразу на двух языках.
// Переключатель языка в шапке выбирает нужный набор. Технических терминов в
// основном тексте нет — это требование понятного языка (решение PTD-0040).

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
      },
      {
        title: "Открытый журнал",
        text: "Любое решение фонда можно посмотреть и проверить — ничего не спрятано.",
      },
      {
        title: "Голосование",
        text: "Один человек — один голос. Голос не покупается и не продаётся.",
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
      },
      {
        title: "Open record",
        text: "Every decision of the fund can be viewed and checked — nothing is hidden.",
      },
      {
        title: "Voting",
        text: "One person, one vote. A vote cannot be bought or sold.",
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
  },
};

export function getDict(lang: Lang): Dict {
  return DICT[lang] ?? DICT[DEFAULT_LANG];
}
