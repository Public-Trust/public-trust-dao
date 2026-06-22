#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Documentation AI-агент — Public Trust DAO (Этап 6, модуль 6/8).

СЛУЖЕБНЫЙ МОДУЛЬ, НЕ ОРГАН ВЛАСТИ (Конституция, ст. 9).
Агент НИЧЕГО не двигает и ничем не владеет: он только ПРОВЕРЯЕТ целостность
документации и докладывает «зелёно/красно». Вся власть — у голосования сообщества
и Safe-мультисига; ИИ лишь помогает соблюдать конституцию (ст. 9).

Зачем: указание оператора — вся документация ведётся ПАРАЛЛЕЛЬНО на русском И
английском (RU↔EN), а проект обязан быть ПРОВЕРЯЕМ (ст. 3) и ОТКРЫТ/ПОНЯТЕН
(ст. 6). Этот агент превращает оба правила в машинную проверку, чтобы документы
не разъезжались молча: чтобы у каждого публичного RU-дока было EN-зеркало (и
наоборот), чтобы переключатель языка был на месте, и чтобы ни одна относительная
ссылка не вела «в никуда».

Что делает (read-only, по git-отслеживаемым .md — по тому, что реально
опубликовано):

  • bilingual-pairs   → у каждого публичного дока есть пара RU↔EN ........... ст. 6
  • language-switcher → вверху дока корректный переключатель [RU]·[EN] ...... ст. 6
  • link-integrity    → все относительные ссылки в .md ведут к чему-то ...... ст. 3
  • anchor-integrity  → якорь ссылки FILE.md#section ведёт к реальному ....... ст. 3
    заголовку (МЯГКАЯ: предупреждает, не роняет вердикт — расчёт слага имеет
    краевые случаи; ловит «гниль» якорей при переименовании разделов)
  • glossary-coverage → ключевые термины проекта описаны в глоссарии ........ ст. 3/6
    (МЯГКАЯ проверка: только предупреждает, не роняет вердикт — чтобы глоссарий
     не отставал от документов; PTD-0040)
  • glossary-no-dead  → у каждой статьи глоссария термин реально используется . ст. 3/6
    (МЯГКАЯ, обратная к coverage: предупреждает, если статья есть, а сам термин
     нигде в документах не встречается — глоссарий «оброс» лишним; PTD-0040)
  • glossary-symmetry → число статей в RU-глоссарии и EN-зеркале совпадает ..... ст. 3/6
    (МЯГКАЯ: предупреждает, если глоссарии разъехались по объёму — статью добавили
     в один язык, а в зеркало перенести забыли; PTD-0040)
  • see-also-targets  → адреса карт «См. также» платформы есть в текстах i18n ... ст. 3/6
    (МЯГКАЯ: предупреждает, если адрес из RELATED/RELATED_ACTIONS в SeeAlso.tsx не
     найден в t.learn/t.screens — перекрёстная ссылка тихо исчезнет; PTD-0105)
  • see-also-present  → экран-источник карты реально рисует <SeeAlso/> .......... ст. 3/6
    (МЯГКАЯ: предупреждает, если экран есть в карте «См. также», но его page.tsx
     не отрисовывает компонент — блок ссылок молча не появится; PTD-0104)
  • mirror-doc-link   → экран-зеркало платформы ссылается на свой док в docs/ .... ст. 3/6
    (МЯГКАЯ: предупреждает, если экран-пересказ нормативного документа не ставит
     ссылку на первоисточник — зеркало нельзя сверить с нормой; PTD-0040)
  • mirror-doc-coverage → каждый экран из витрины t.learn есть в карте MIRROR_DOCS . ст. 3/6
    (МЯГКАЯ, обратная к mirror-doc-link: предупреждает, если завели новый экран-
     зеркало, но в MIRROR_DOCS внести забыли — его пересказ не сверяется; PTD-0109)
  • mirror-doc-exists  → путь дока из карты MIRROR_DOCS реально есть в репо ....... ст. 3/6
    (МЯГКАЯ: предупреждает, если нормативный документ переименовали/перенесли, а
     путь-значение в карте поправить забыли — ссылка экрана-зеркала молча ведёт в
     никуда, а mirror-doc-link этого не видит; PTD-0110)
  • mirror-doc-showcase → заведённый экран-зеркало показан в витрине t.learn ...... ст. 3/6
    (МЯГКАЯ, парная к mirror-doc-coverage: предупреждает, если экран есть в карте и
     его страница заведена, но в витрину t.learn он не попал — человек не дойдёт до
     него с главной; PTD-0110)
  • see-also-symmetric → связь «См. также» между объяснениями взаимна .......... ст. 3/6
    (МЯГКАЯ: предупреждает, если экран A ведёт на B, а B не ведёт обратно на A —
     односторонняя связь оставляет человека без обратного пути; PTD-0106)

Правило пар (выводится из пути, а не зашито пофайлово):
  docs/NAME.md            ↔ docs/en/NAME.md
  <dir>/README.md         ↔ <dir>/README.en.md  (и корневой README.md ↔ README.en.md)
  NAME.md (в корне)       ↔ NAME.en.md           (напр. REPO-STRUCTURE, AUTHORS)
Внутренние/служебные файлы (мандат строителя, переписка с оператором, журналы
прогресса) одноязычны by design и в правило двуязычности НЕ входят — их список
явный (SINGLE_LANG ниже), чтобы агент не падал ложно.

Вывод:
  • человекочитаемый отчёт в stdout (✓/✗ по каждой проверке + привязка к статье);
  • при --json — машиночитаемый отчёт (для CI и других агентов);
  • код возврата 0, если все проверки прошли, иначе 1.

«Красный» — это СИГНАЛ сообществу (повод для решения людей), а не действие: агент
сам ничего не исправляет (не дописывает переводы и не правит ссылки).

Зависимостей нет — только стандартная библиотека (детерминированно в любом CI).
TESTNET-ONLY: агент не трогает реальные средства/ключи и не выходит в сеть.
"""

import argparse
import json
import os
import re
import subprocess
import sys

# Корень репозитория = на уровень выше каталога ai-agents/.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Одноязычные by design (НЕ требуют EN-зеркала и переключателя): внутренний
# мандат строителя, план, журналы памяти, переписка с оператором. Это рабочая
# кухня контура, а не публичная документация фонда. Сюда же — GitHub-формы
# (шаблон PR): это служебный конфиг платформы с единым файлом, двуязычный ВНУТРИ
# себя (RU+EN в одном теле), а не пара RU↔EN-документов. (Шаблоны issue — .yml,
# в скан .md не попадают вовсе.)
SINGLE_LANG = {
    "BUILDER.md",
    "LAUNCH.md",
    "PROGRESS.md",
    "DECISIONS.md",
    "comms/INBOX.md",
    "comms/operator-thread.md",
    ".github/pull_request_template.md",
}

# Переключатель языка вверху публичного дока. Текущий язык — простой текст в
# скобках, другой — ссылка на парный файл.
SWITCHER_RU_RE = re.compile(r"^\[Русский\]\s*·\s*\[English\]\(([^)]+)\)\s*$")
SWITCHER_EN_RE = re.compile(r"^\[Русский\]\(([^)]+)\)\s*·\s*\[English\]\s*$")

# Ссылки вида [текст](цель). Цель берём «как есть» — потом отфильтруем внешние.
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
# Внешние/неотносительные цели (их целостность не наша забота).
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "//", "#")
# Огороженные блоки кода ```...``` вырезаем перед извлечением ссылок — там
# может быть `](` внутри примеров, не являющийся ссылкой.
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)

# Глоссарий проекта (RU-оригинал и EN-зеркало). На нём держится мягкая проверка
# «термин определён»: правило понятного языка (PTD-0040, ст. 3/6) требует, чтобы
# непонятные технические слова были объяснены простыми словами именно здесь.
GLOSSARY_RU = "docs/GLOSSARY.md"
GLOSSARY_EN = "docs/en/GLOSSARY.md"

# Перекрёстная навигация «См. также» в платформе. Компонент SeeAlso.tsx держит
# две карты адресов: RELATED (объяснение → близкое объяснение) и RELATED_ACTIONS
# (объяснение → рабочий экран, где это применить). Заголовки берутся не из карт, а
# из списков t.learn / t.screens в lib/i18n.ts (один источник текста RU↔EN). Эти
# мягкие проверки следят, чтобы карты и тексты не разъехались молча: чтобы каждый
# адрес карты существовал в i18n, а каждый экран-источник реально отрисовывал блок
# «См. также» (ст. 3 — проверяемость; ст. 6 — понятность; PTD-0104/0105).
SEEALSO_TSX = "platform/components/SeeAlso.tsx"
I18N_TS = "platform/lib/i18n.ts"
PLATFORM_APP = "platform/app"

# Экраны-зеркала платформы: каждый пересказывает простыми словами свой нормативный
# документ из docs/ (приём «экран-зеркало», PTD-0040 и далее). Мягкая проверка
# mirror-doc-link следит, чтобы экран ссылался на ПЕРВОИСТОЧНИК — чтобы человек мог
# сверить пересказ с нормой, а зеркало не «уехало» от документа молча при правках
# (ст. 3 — проверяемость; ст. 6 — понятность). Слаг экрана → нормативный док в docs/.
# Адрес дока ищем как подстроку (покрывает и относительную ссылку `docs/X.md`, и
# абсолютную `…/blob/main/docs/X.md` на репозиторий).
MIRROR_DOCS = {
    "manifesto": "docs/MANIFESTO.md",
    "constitution": "docs/CONSTITUTION.md",
    "governance": "docs/GOVERNANCE.md",
    "priorities": "docs/PRIORITIES.md",
    "rewards": "docs/REWARDS-MODEL.md",
    "safeguards": "docs/ANTI-ABUSE.md",
    "work": "docs/PROOF-OF-CONTRIBUTION.md",
    "accountability": "docs/ACCOUNTABILITY.md",
    "direct-help": "docs/ESCROW-TARGETED-DISBURSEMENT.md",
    "support": "docs/SUPPORT-MODEL.md",
    "glossary": "docs/GLOSSARY.md",
}

# Адрес-слаг экрана платформы в кавычках: "/manifesto/", "/voting/" и т.п.
TS_HREF_RE = re.compile(r'"(/[^"]*/)"')
# Запись карты SeeAlso: "ключ-адрес": [ "адрес", ... ] — ключ и тело списка.
TS_MAP_ENTRY_RE = re.compile(r'"(/[^"]*/)"\s*:\s*\[([^\]]*)\]')
# href в элементе массива i18n: href: "/apply/".
TS_ARRAY_HREF_RE = re.compile(r'href:\s*"([^"]+)"')

# Жирный заголовок статьи глоссария: строка, начинающаяся с **...** (термин).
BOLD_HEAD_RE = re.compile(r"^\*\*.+?\*\*", re.MULTILINE)

# Ключевые технические термины, которые проект ОБЯЗУЕТСЯ объяснять простым языком
# в глоссарии (ст. 3 «понятность», ст. 6 «объяснимость», правило PTD-0040). Для
# каждого — как он выглядит в статье глоссария на RU и на EN (подстрока в жирном
# заголовке, регистр игнорируется). Если статьи нет — мягкое предупреждение, чтобы
# глоссарий не отставал от документов. Список заведомо консервативный (только то,
# что реально встречается в нормативных документах) — расширяется по мере роста
# корпуса, отдельным решением.
KEY_TERMS = [
    {"id": "DAO", "ru": "dao", "en": "dao"},
    {"id": "escrow / целевой расход", "ru": "escrow", "en": "escrow"},
    {"id": "мультисиг (multisig)", "ru": "мультисиг", "en": "multisig"},
    {"id": "казна (treasury)", "ru": "казна", "en": "treasury"},
    {"id": "хранитель (guardian)", "ru": "хранитель", "en": "guardian"},
    {"id": "кворум (quorum)", "ru": "кворум", "en": "quorum"},
    {"id": "предложение (proposal)", "ru": "предложение", "en": "proposal"},
    {"id": "Snapshot", "ru": "snapshot", "en": "snapshot"},
    {"id": "Timelock", "ru": "timelock", "en": "timelock"},
    {"id": "Governor", "ru": "governor", "en": "governor"},
    {"id": "governance", "ru": "governance", "en": "governance"},
    {"id": "репутация (reputation)", "ru": "репутация", "en": "reputation"},
    {"id": "soulbound-бейдж", "ru": "soulbound", "en": "soulbound"},
    {"id": "защита от Сивиллы (Sybil)", "ru": "сивилл", "en": "sybil"},
    {"id": "IPFS", "ru": "ipfs", "en": "ipfs"},
    {"id": "CID", "ru": "cid", "en": "cid"},
    {"id": "hash-chain", "ru": "hash-chain", "en": "hash-chain"},
    {"id": "смарт-контракт (smart contract)", "ru": "смарт-контракт", "en": "smart contract"},
    {"id": "testnet / mainnet", "ru": "testnet", "en": "testnet"},
    {"id": "приватный ключ (private key)", "ru": "приватный ключ", "en": "private key"},
    {"id": "аудит (audit)", "ru": "аудит", "en": "audit"},
    {"id": "реестр решений (registry)", "ru": "реестр", "en": "registry"},
    {"id": "рельсы (guardrails)", "ru": "рельсы", "en": "guardrails"},
    {"id": "апелляция (appeal)", "ru": "апелляция", "en": "appeal"},
    {"id": "поэтапные выплаты (staged payments)", "ru": "поэтапные выплаты", "en": "staged payments"},
    {"id": "поставщик (provider)", "ru": "поставщик", "en": "provider"},
]

# --- Лексический линтер конституционных запретов в публичных текстах ----------
# Конституция (ст. 3/6, PRINCIPLES.md «Конституционные запреты») требует: никакой
# публичный текст не обещает доходность/прибыль, не зовёт в инвестицию/пирамиду и
# не платит за привлечение людей. Этот мягкий линтер ищет такие ОБЕЩАНИЯ в
# человеко-видимых текстах (публичные .md + витрина web/*.html) и предупреждает,
# если нашёл их БЕЗ отрицания рядом (наши же дисклеймеры «это НЕ инвестиция»,
# списки запретов и т.п. — законны и не должны давать ложную тревогу).
#
# Каждый «концепт» — это запрещённое ПОЗИТИВНОЕ обещание. Триггер ищет фразу,
# затем проверяется окно вокруг неё: если рядом стоит маркер отрицания/запрета
# (NEG_RE) — это дисклеймер/перечисление запретов, пропускаем. Иначе — мягкое
# предупреждение (расчёт «обещание это или отрицание» имеет краевые случаи,
# поэтому проверка не роняет вердикт и пульс).
PROHIBITION_CONCEPTS = [
    {
        "id": "обещание доходности/прибыли (запрет №1/№2)",
        "re": re.compile(
            r"(гарант\w+|обеща\w+)[\s,–—/-]+(доход\w*|прибыл\w*|выгод\w*)"
            r"|(доход\w*|прибыл\w*)[\s,–—/-]+гарант\w+"
            r"|(guarantee\w*|promis\w*)[\s,–—/-]+(return\w*|profit\w*|income|gain\w*|yield\w*)",
            re.IGNORECASE,
        ),
    },
    {
        "id": "пассивный доход (запрет №1)",
        "re": re.compile(r"пассивн\w+\s+доход\w*|passive\s+income", re.IGNORECASE),
    },
    {
        "id": "финансовая пирамида (запрет №3)",
        "re": re.compile(r"пирамид\w*|\bpyramid\b", re.IGNORECASE),
    },
    {
        "id": "инвестиционное предложение (НЕ инвестиция — рельс)",
        "re": re.compile(r"\bинвести\w+|\binvestment\b|\binvest\b", re.IGNORECASE),
    },
    {
        "id": "плата за привлечение людей / рефералы (запрет №4)",
        "re": re.compile(
            r"реферальн\w+|referral\b|refer\s+a\s+friend"
            r"|(приведи|пригласи)\w*\s+друг"
            r"|(бонус|выплат\w*|плат\w*|вознагражд\w*|заработ\w*)[\s\wа-я]{0,20}"
            r"за\s+(приглаш\w+|привлеч\w+|реферал\w*)",
            re.IGNORECASE,
        ),
    },
]

# Маркеры отрицания/запрета. Если такой стоит в окне вокруг найденной фразы —
# это дисклеймер («НЕ инвестиция»), перечень запретов («запрещается …», «❌ …»)
# или контраст («в отличие от …»), а не обещание. Тогда фразу пропускаем.
PROHIBITION_NEG_RE = re.compile(
    r"(❌|\b(не|нет|ни|без|никогда|нельзя|запрещ\w*|запрет\w*|отказ\w*|вместо|"
    r"no|not|never|without|don't|doesn't|won't|cannot|can't|prohibit\w*|"
    r"forbidden|ban\w*|unlike|reject\w*)\b|в\s+отлич|не\s+являет|"
    r"is\s+not|isn't|are\s+not|aren't|instead\s+of|rather\s+than)",
    re.IGNORECASE,
)

# Окно вокруг найденной фразы, в котором ищем маркер отрицания: до 240 символов
# слева (накрывает заголовок «Запрещается:» над списком) и до 180 справа (маркер
# нередко стоит после: «… пирамида — буквальные запреты», «referral ban»).
PROHIBITION_NEG_BACK = 240
PROHIBITION_NEG_FWD = 180


def git_tracked_web_html(root):
    """Git-отслеживаемые HTML витрины web/ (публичный человеко-видимый текст)."""
    try:
        out = subprocess.run(
            ["git", "-C", root, "ls-files", "web/*.html", "web/**/*.html"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True,
        ).stdout
        files = sorted({line.strip() for line in out.splitlines() if line.strip()})
        if files:
            return files
    except (OSError, subprocess.CalledProcessError):
        pass
    files = []
    web_dir = os.path.join(root, "web")
    for dirpath, dirnames, filenames in os.walk(web_dir):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
        for name in filenames:
            if name.endswith(".html"):
                rel = os.path.relpath(os.path.join(dirpath, name), root)
                files.append(rel.replace(os.sep, "/"))
    return sorted(files)


def git_tracked_md(root):
    """Возвращает отсортированный список git-отслеживаемых .md (относительные пути)."""
    try:
        out = subprocess.run(
            ["git", "-C", root, "ls-files", "*.md"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True,
        ).stdout
        files = [line.strip() for line in out.splitlines() if line.strip()]
        if files:
            return sorted(files)
    except (OSError, subprocess.CalledProcessError):
        pass
    # Фолбэк (например, тест без git): обход дерева.
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
        for name in filenames:
            if name.endswith(".md"):
                rel = os.path.relpath(os.path.join(dirpath, name), root)
                files.append(rel.replace(os.sep, "/"))
    return sorted(files)


def is_en_mirror(path):
    """EN-зеркало — это docs/en/** или файл, оканчивающийся на .en.md."""
    return path.startswith("docs/en/") or path.endswith(".en.md")


def expected_en_for_ru(path):
    """По RU-оригиналу вычисляет ожидаемый путь EN-зеркала (правило пар)."""
    if path.startswith("docs/") and not path.startswith("docs/en/"):
        return "docs/en/" + path[len("docs/"):]
    # Везде ещё: NAME.md → NAME.en.md (README.md→README.en.md и т.п.).
    return path[:-len(".md")] + ".en.md"


def expected_ru_for_en(path):
    """По EN-зеркалу вычисляет ожидаемый путь RU-оригинала (обратное правило)."""
    if path.startswith("docs/en/"):
        return "docs/" + path[len("docs/en/"):]
    return path[:-len(".en.md")] + ".md"


def partner_of(path):
    """Возвращает ожидаемый путь парного файла (RU↔EN) для публичного дока."""
    if is_en_mirror(path):
        return expected_ru_for_en(path)
    return expected_en_for_ru(path)


def read_text(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as fh:
        return fh.read()


def first_nonempty_line(text):
    for line in text.splitlines():
        if line.strip():
            return line.rstrip()
    return ""


def extract_links(text):
    """Все цели относительных ссылок из markdown (вне блоков кода)."""
    cleaned = FENCE_RE.sub("", text)
    out = []
    for target in LINK_RE.findall(cleaned):
        target = target.strip()
        # Markdown допускает заголовок ссылки: [t](url "title") — отрезаем.
        if " " in target:
            target = target.split(" ", 1)[0]
        out.append(target)
    return out


def is_external(target):
    return target.startswith(EXTERNAL_PREFIXES) or target.startswith("<")


def resolve_link(root, src_rel, target):
    """Резолвит относительную ссылку src→target. Возвращает (ok, resolved_rel)."""
    # Якорь и query отрезаем — проверяем существование самого файла/каталога.
    path = target.split("#", 1)[0].split("?", 1)[0]
    if not path:
        return True, None  # чистый якорь внутри того же файла
    base = os.path.dirname(src_rel)
    joined = os.path.normpath(os.path.join(base, path))
    if joined.startswith(".."):
        return False, joined  # ведёт за пределы репозитория
    full = os.path.join(root, joined)
    return os.path.exists(full), joined


# --- Якоря заголовков (для проверки ссылок вида FILE.md#section) ---
# Заголовок markdown: 1..6 решёток, текст, опц. закрывающие решётки (ATX-closed).
HEADING_RE = re.compile(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$", re.MULTILINE)
# HTML-якоря в теле дока: <a name="..."> / <a id="..."> — тоже валидные цели.
HTML_ANCHOR_RE = re.compile(r'<a\b[^>]*?\b(?:name|id)\s*=\s*"([^"]+)"', re.IGNORECASE)
# Пунктуация, которую GitHub-slugger ВЫРЕЗАЕТ из заголовка при построении якоря.
# Дефис и подчёркивание он СОХРАНЯЕТ; буквы (в т.ч. кириллица) и цифры остаются.
SLUG_DROP = set("'\"!#$%&()*+,./:;<=>?@[\\]^`{|}~")


def clean_heading_md(text):
    """Снимает markdown-разметку с текста заголовка перед построением якоря."""
    text = re.sub(r"`([^`]*)`", r"\1", text)             # инлайн-код
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # ссылка [t](u) → t
    text = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", text)  # ссылка-ссылка [t][r] → t
    text = text.replace("**", "").replace("__", "")        # жирный
    return text


def slugify_heading(text):
    """Якорь заголовка по правилу GitHub: нижний регистр, без пунктуации,
    пробелы → дефисы. Кириллица сохраняется (как и на github.com)."""
    s = clean_heading_md(text)
    s = re.sub(r"<[^>]+>", "", s)            # снять остаточные html-теги
    s = s.strip().lower()
    s = "".join(ch for ch in s if ch not in SLUG_DROP)
    s = re.sub(r"\s+", "-", s)
    return s


def extract_anchors(text):
    """Множество якорей, доступных в доке: слаги заголовков (с учётом повторов,
    как у GitHub: второй одинаковый → `-1`, третий → `-2`) + явные HTML-якоря."""
    cleaned = FENCE_RE.sub("", text)
    anchors = set()
    seen = {}
    for m in HEADING_RE.finditer(cleaned):
        base = slugify_heading(m.group(2))
        if not base:
            continue
        n = seen.get(base, 0)
        anchors.add(base if n == 0 else f"{base}-{n}")
        seen[base] = n + 1
    for name in HTML_ANCHOR_RE.findall(cleaned):
        anchors.add(name.strip().lower())
    return anchors


def split_anchor(target):
    """Делит цель ссылки на (путь, якорь|None). Query (?...) отбрасываем."""
    no_q = target.split("?", 1)[0]
    if "#" in no_q:
        path, anchor = no_q.split("#", 1)
        return path, anchor
    return no_q, None


# ---- Проверки. Каждая возвращает (status, violations[list]). ----

def check_bilingual_pairs(root, public_docs, existing):
    """У каждого публичного дока есть существующая пара RU↔EN."""
    violations = []
    for doc in public_docs:
        partner = partner_of(doc)
        if partner not in existing:
            side = "EN-зеркало" if not is_en_mirror(doc) else "RU-оригинал"
            violations.append({
                "record": doc,
                "problem": f"нет парного файла ({side}): ожидался '{partner}'",
            })
    return ("pass" if not violations else "fail"), violations


def check_language_switcher(root, public_docs, existing):
    """Вверху публичного дока — корректный переключатель, ведущий к парному файлу."""
    violations = []
    for doc in public_docs:
        partner = partner_of(doc)
        head = first_nonempty_line(read_text(root, doc))
        rx = SWITCHER_EN_RE if is_en_mirror(doc) else SWITCHER_RU_RE
        m = rx.match(head)
        if not m:
            violations.append({
                "record": doc,
                "problem": f"первая строка не переключатель языка: {head!r}",
            })
            continue
        # Ссылка в переключателе должна резолвиться в парный файл.
        link = m.group(1).strip()
        ok, resolved = resolve_link(root, doc, link)
        if not ok:
            violations.append({"record": doc,
                               "problem": f"ссылка переключателя ведёт в никуда: {link!r}"})
        elif resolved != partner:
            violations.append({
                "record": doc,
                "problem": f"переключатель ведёт на '{resolved}', а пара — '{partner}'",
            })
    return ("pass" if not violations else "fail"), violations


def check_link_integrity(root, all_docs):
    """Каждая относительная ссылка в каждом .md ведёт к существующему файлу/каталогу."""
    violations = []
    for doc in all_docs:
        text = read_text(root, doc)
        for target in extract_links(text):
            if is_external(target):
                continue
            ok, resolved = resolve_link(root, doc, target)
            if not ok:
                violations.append({
                    "record": doc,
                    "problem": f"битая относительная ссылка → {target!r} (→ {resolved})",
                })
    return ("pass" if not violations else "fail"), violations


def check_anchor_integrity(root, all_docs, existing):
    """МЯГКАЯ проверка: ссылка вида FILE.md#section (или #section внутри того же
    файла) указывает на реально существующий заголовок целевого .md.

    Зачем: при переименовании раздела внутренние ссылки молча «гниют» — файл на
    месте (link-integrity зелёный), а якорь уже не ведёт никуда. Проверяем только
    .md-цели, существующие и git-отслеживаемые; если файла нет — это уже ловит
    блокирующая link-integrity, здесь молчим. Якорь строим по правилу GitHub.
    Проверка МЯГКАЯ (warn): расчёт слага имеет краевые случаи, поэтому она лишь
    предупреждает, а не роняет вердикт и пульс (ст. 3 — проверяемость).
    """
    anchors_cache = {}

    def anchors_for(rel):
        if rel not in anchors_cache:
            anchors_cache[rel] = extract_anchors(read_text(root, rel))
        return anchors_cache[rel]

    violations = []
    for doc in all_docs:
        text = read_text(root, doc)
        for target in extract_links(text):
            # Внешние цели пропускаем; но чистый «#anchor» (своя страница) НЕ внешний.
            if target.startswith(("http://", "https://", "mailto:", "//", "<")):
                continue
            path, anchor = split_anchor(target)
            if not anchor:
                continue
            if not path:
                tgt_rel = doc  # якорь внутри того же файла
            else:
                ok, resolved = resolve_link(root, doc, path)
                if not ok or resolved is None:
                    continue  # битый файл — забота блокирующей link-integrity
                tgt_rel = resolved
            # Проверяем якоря только в существующих git-отслеживаемых .md.
            if not tgt_rel.endswith(".md") or tgt_rel not in existing:
                continue
            if anchor.strip().lower() not in anchors_for(tgt_rel):
                where = "в этом же файле" if tgt_rel == doc else f"в {tgt_rel}"
                violations.append({
                    "record": doc,
                    "problem": (f"якорь ссылки не найден как заголовок: → {target!r} "
                                f"(нет раздела «#{anchor}» {where})"),
                })
    return ("pass" if not violations else "warn"), violations


def glossary_headings_blob(text):
    """Склеивает жирные заголовки статей глоссария в один blob (нижний регистр)."""
    return "\n".join(BOLD_HEAD_RE.findall(text)).lower()


def check_glossary_coverage(root, existing):
    """МЯГКАЯ проверка: ключевой технический термин имеет статью в глоссарии (RU+EN).

    Не блокирует (статус pass/warn, в вердикт не входит) — только предупреждает,
    чтобы глоссарий не отставал от документов (ст. 3/6, правило PTD-0040). Если
    глоссария нет (например, мини-репозиторий в тесте) — проверять нечего → pass.
    """
    if GLOSSARY_RU not in existing or GLOSSARY_EN not in existing:
        return "pass", []
    ru_blob = glossary_headings_blob(read_text(root, GLOSSARY_RU))
    en_blob = glossary_headings_blob(read_text(root, GLOSSARY_EN))
    violations = []
    for term in KEY_TERMS:
        missing = []
        if term["ru"] not in ru_blob:
            missing.append("RU")
        if term["en"] not in en_blob:
            missing.append("EN")
        if missing:
            violations.append({
                "record": GLOSSARY_RU if "RU" in missing else GLOSSARY_EN,
                "problem": (f"ключевой термин «{term['id']}» не описан в глоссарии "
                            f"({', '.join(missing)}) — глоссарий отстаёт от документов"),
            })
    return ("pass" if not violations else "warn"), violations


# Разделители альтернативных написаний внутри заголовка статьи: запятая, слэш,
# точка с запятой, тире-разделитель, союзы «and»/«и»/«&». По ним заголовок дробится
# на ключи поиска (например «Testnet and Mainnet» → «testnet» + «mainnet»).
SPLIT_KEYS_RE = re.compile(r"[,/;]|\s—\s|\s-\s|\s(?:and|и|&)\s")
# Скобочная часть заголовка: «(multisig)», «(proof-of-personhood)» и т.п.
PAREN_RE = re.compile(r"\(([^)]*)\)")
# Кавычки-ёлочки и обычные — внутри заголовка считаем разделителями (а не частью
# термина): `"NOT an investment"` → ключ «not an investment».
QUOTES_RE = re.compile(r"[\"«»“”]")
# Короткие служебные слова — НЕ ключи (иначе ловили бы совпадения на «and»/«для»).
WORD_STOP = {
    "this", "that", "from", "with", "есть", "быть", "либо", "также", "когда",
    "чтобы", "своей", "этот", "или", "для", "без", "как", "что", "при", "над",
    "под", "and", "the", "not", "for",
}
# Заголовок статьи глоссария = строка ЦЕЛИКОМ из жирного термина (а не выделение
# **жирным** внутри абзаца). Берём только полностью-жирные строки, дальше ещё
# отфильтруем по завершающей точке (см. glossary_article_headings).
ARTICLE_HEAD_LINE_RE = re.compile(r"^\*\*(.+)\*\*\s*$", re.MULTILINE)


def glossary_article_headings(text):
    """Внутренности заголовков статей глоссария (без обрамляющих **).

    Статья — это строка, состоящая ЦЕЛИКОМ из жирного термина и заканчивающаяся
    точкой (точка может стоять под закрывающей кавычкой: `vote."`). Обычное
    выделение **жирным** в теле абзаца сюда НЕ попадает: после него либо идёт текст
    (строка не заканчивается на **), либо нет завершающей точки.
    """
    heads = []
    for inner in ARTICLE_HEAD_LINE_RE.findall(text):
        tail = inner.rstrip().rstrip("\"»'").rstrip()
        if tail.endswith("."):
            heads.append(inner)
    return heads


def article_title(inner):
    """Человекочитаемый заголовок статьи: содержимое заголовка без завершающей точки."""
    return inner.strip().rstrip(".").strip()


def article_search_keys(inner):
    """Ключи для поиска термина статьи в корпусе документов.

    Намеренно ГЕНЕРОЗНО: основной термин (до первой скобки) + все альтернативы из
    скобок (по разделителям) + отдельные значимые слова основного термина (пословный
    фолбэк для многословных заголовков вроде «Liveness check»). Чем больше ключей,
    тем КОНСЕРВАТИВНЕЕ проверка: статья объявляется «мёртвой», только если НИ ОДИН
    ключ не встречается в корпусе. Это мягкая проверка — лучше промолчать, чем дать
    ложную тревогу.
    """
    norm = QUOTES_RE.sub(" ", article_title(inner))
    raw = set()
    # альтернативные написания из скобок
    for paren in PAREN_RE.findall(norm):
        raw.update(SPLIT_KEYS_RE.split(paren))
    # основной термин — всё до скобок (как фраза целиком и по разделителям)
    primary = re.sub(r"\(.*", "", norm)
    raw.add(primary)
    raw.update(SPLIT_KEYS_RE.split(primary))
    keys = set()
    for k in raw:
        k = re.sub(r"\s+", " ", k.strip().strip("«».,—-").strip()).lower()
        if len(k) >= 3:  # отбрасываем мусорные обрезки
            keys.add(k)
    # пословный фолбэк: длинное значимое слово основного термина — тоже ключ.
    for w in re.split(r"[\s.,/;]+", primary.lower()):
        w = w.strip("«».,—-()")
        if len(w) >= 4 and w not in WORD_STOP:
            keys.add(w)
    return keys


def check_glossary_no_dead(root, existing, corpus_docs):
    """МЯГКАЯ проверка (обратная к coverage): у каждой статьи глоссария термин
    реально встречается хотя бы в одном нормативном документе.

    Если термин статьи не найден НИГДЕ в корпусе — глоссарий «оброс» лишней статьёй
    (предупреждение, не блокирует). Корпус — все публичные доки, кроме самих
    глоссариев. Если глоссария нет (мини-репозиторий в тесте) — проверять нечего → pass.
    """
    glossaries = [g for g in (GLOSSARY_RU, GLOSSARY_EN) if g in existing]
    if not glossaries:
        return "pass", []
    corpus = "\n".join(read_text(root, d) for d in corpus_docs).lower()
    violations = []
    for gloss in glossaries:
        for inner in glossary_article_headings(read_text(root, gloss)):
            keys = article_search_keys(inner)
            if keys and not any(k in corpus for k in keys):
                violations.append({
                    "record": gloss,
                    "problem": (f"статья «{article_title(inner)}»: термин не встречается "
                                "ни в одном нормативном документе — глоссарий мог обрасти лишним"),
                })
    return ("pass" if not violations else "warn"), violations


def check_glossary_symmetry(root, existing):
    """МЯГКАЯ проверка: число статей в RU-глоссарии и EN-зеркале совпадает.

    Глоссарий ведётся параллельно на двух языках (RU↔EN). Если в одном языке статью
    добавили, а в зеркало перенести забыли — глоссарии «разъезжаются» по объёму, и
    одна из аудиторий молча теряет термин. Эта проверка сравнивает КОЛИЧЕСТВО статей
    (полностью-жирные строки-заголовки, как их видит `glossary_article_headings`) в
    `docs/GLOSSARY.md` и `docs/en/GLOSSARY.md`. Расхождение — мягкое предупреждение,
    не блок: счёт статей — грубый индикатор (термин может законно объединять два
    написания в один заголовок), поэтому проверка лишь сигналит «глоссарии разошлись
    по объёму», а вердикт и пульс не роняет (ст. 3/6 — понятность/проверяемость,
    PTD-0040). Если хотя бы одного из двух глоссариев нет (мини-репозиторий в
    тесте) — сравнивать нечего → pass.
    """
    if GLOSSARY_RU not in existing or GLOSSARY_EN not in existing:
        return "pass", []
    ru_n = len(glossary_article_headings(read_text(root, GLOSSARY_RU)))
    en_n = len(glossary_article_headings(read_text(root, GLOSSARY_EN)))
    if ru_n == en_n:
        return "pass", []
    more, less = (GLOSSARY_RU, GLOSSARY_EN) if ru_n > en_n else (GLOSSARY_EN, GLOSSARY_RU)
    return "warn", [{
        "record": less,
        "problem": (f"глоссарии разошлись по объёму: статей RU={ru_n}, EN={en_n} "
                    f"(в «{more}» больше на {abs(ru_n - en_n)}) — перенос термина в "
                    "зеркало мог потеряться, одна из аудиторий не видит статью"),
    }]


def check_constitutional_prohibitions(root, public_texts):
    """МЯГКАЯ проверка: публичные тексты не дают запрещённых обещаний.

    Сканирует человеко-видимые тексты (публичные .md + витрина web/*.html) на
    буквальные конституционные запреты PRINCIPLES.md для публичных текстов:
    обещание доходности/прибыли, пассивный доход, зов в инвестицию/пирамиду,
    плата за привлечение людей (рефералы). Найденную фразу пропускаем, если
    рядом стоит маркер отрицания/запрета (наши дисклеймеры «это НЕ инвестиция»,
    перечни запретов «Запрещается: …», «❌ …» — законны). Проверка МЯГКАЯ (warn):
    различение «обещание/отрицание» имеет краевые случаи, поэтому она лишь
    предупреждает, а не роняет вердикт и пульс (ст. 3/6 — понятность/рельсы).
    """
    violations = []
    for rel in public_texts:
        text = read_text(root, rel)
        if rel.endswith(".md"):
            text = FENCE_RE.sub("", text)  # примеры в ```...``` — не публичная копия
        for concept in PROHIBITION_CONCEPTS:
            for m in concept["re"].finditer(text):
                window = text[max(0, m.start() - PROHIBITION_NEG_BACK):
                              m.end() + PROHIBITION_NEG_FWD]
                if PROHIBITION_NEG_RE.search(window):
                    continue  # рядом отрицание/запрет — это дисклеймер, не обещание
                line = text[:m.start()].count("\n") + 1
                phrase = " ".join(m.group(0).split())
                violations.append({
                    "record": f"{rel}:{line}",
                    "problem": (f"возможное запрещённое обещание «{phrase}» "
                                f"({concept['id']}) без отрицания рядом — публичный "
                                "текст не должен этого обещать (PRINCIPLES.md)"),
                })
    return ("pass" if not violations else "warn"), violations


def _ts_object_block(text, name):
    """Тело объектного литерала `const <name>: ... = { ... }` из .tsx/.ts.

    Возвращает строку между внешними фигурными скобками (с учётом вложенности)
    или None, если объявление не найдено. Списки внутри используют [ ], а не { },
    поэтому первая закрывающая `}` на нулевой глубине — это конец карты.
    """
    m = re.search(r"const\s+" + re.escape(name) + r"\s*:[^=]*=\s*\{", text)
    if not m:
        return None
    start = m.end() - 1  # позиция открывающей «{»
    depth = 0
    for j in range(start, len(text)):
        ch = text[j]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:j]
    return None


def parse_seealso_map(text, name):
    """Карта SeeAlso (`RELATED`/`RELATED_ACTIONS`) → {ключ-адрес: [адрес, ...]}."""
    block = _ts_object_block(text, name)
    if block is None:
        return {}
    out = {}
    for key, body in TS_MAP_ENTRY_RE.findall(block):
        out[key] = TS_HREF_RE.findall(body)
    return out


def parse_i18n_hrefs(text, key):
    """Множество адресов href из массива `<key>: [ ... ]` в lib/i18n.ts.

    Массив встречается дважды (блоки RU и EN) — адреса в них одинаковы, объединяем.
    Объявление типа `<key>: {...}[]` сюда не попадает (требуется именно `[`).
    """
    hrefs = set()
    for m in re.finditer(r"\b" + re.escape(key) + r"\s*:\s*\[", text):
        start = m.end() - 1  # позиция открывающей «[»
        depth = 0
        for j in range(start, len(text)):
            ch = text[j]
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    hrefs.update(TS_ARRAY_HREF_RE.findall(text[start + 1:j]))
                    break
    return hrefs


def check_see_also_targets(root):
    """МЯГКАЯ: каждый адрес карт «См. также» существует в текстах i18n.

    Компонент `SeeAlso.tsx` разрешает адреса так: ключи и значения `RELATED` ищет
    в `t.learn` (экраны-объяснения), значения `RELATED_ACTIONS` — в `t.screens`
    (рабочие экраны). Если экран переименуют в `lib/i18n.ts`, а карту поправить
    забудут, `find(...)` молча вернёт `undefined` и ссылка тихо исчезнет с экрана.
    Эта проверка сверяет каждый адрес обеих карт с адресами из i18n и предупреждает
    о «висячих» (warn, не блок — ст. 3/6, PTD-0105). Если файлов платформы нет
    (мини-репозиторий в тесте) или их не удалось распарсить — проверять нечего → pass.
    """
    if not (os.path.exists(os.path.join(root, SEEALSO_TSX)) and
            os.path.exists(os.path.join(root, I18N_TS))):
        return "pass", []
    related = parse_seealso_map(read_text(root, SEEALSO_TSX), "RELATED")
    actions = parse_seealso_map(read_text(root, SEEALSO_TSX), "RELATED_ACTIONS")
    i18n = read_text(root, I18N_TS)
    learn = parse_i18n_hrefs(i18n, "learn")
    screens = parse_i18n_hrefs(i18n, "screens")
    # Ничего не распарсили (дрейф формата) — молчим, чтобы не кричать ложно.
    if (not related and not actions) or not learn or not screens:
        return "pass", []
    violations = []
    # Ключи обеих карт — это экраны-объяснения → должны быть в t.learn.
    for src, mapping in (("RELATED", related), ("RELATED_ACTIONS", actions)):
        for key in mapping:
            if key not in learn:
                violations.append({
                    "record": f"{SEEALSO_TSX} → {src}",
                    "problem": (f"экран-ключ «{key}» карты не найден в t.learn "
                                "(lib/i18n.ts) — экран переименовали, а карту нет"),
                })
    # Значения RELATED ведут на объяснения (t.learn); RELATED_ACTIONS — на рабочие
    # экраны (t.screens). Каждый адрес должен существовать в своём списке.
    for key, vals in related.items():
        for href in vals:
            if href not in learn:
                violations.append({
                    "record": f"{SEEALSO_TSX} → RELATED[{key}]",
                    "problem": (f"адрес «{href}» не найден в t.learn — ссылка «См. "
                                "также» тихо исчезнет с экрана"),
                })
    for key, vals in actions.items():
        for href in vals:
            if href not in screens:
                violations.append({
                    "record": f"{SEEALSO_TSX} → RELATED_ACTIONS[{key}]",
                    "problem": (f"адрес «{href}» не найден в t.screens — ссылка-"
                                "действие тихо исчезнет с экрана"),
                })
    return ("pass" if not violations else "warn"), violations


def check_see_also_present(root):
    """МЯГКАЯ: каждый экран-источник карт «См. также» отрисовывает <SeeAlso/>.

    Адрес-ключ в `RELATED`/`RELATED_ACTIONS` означает «на этом экране снизу должен
    стоять блок перекрёстных ссылок». Если экран добавили в карту, но забыли
    вставить сам компонент `<SeeAlso slug=…/>` в его `page.tsx`, навигация молча не
    появится. Проверка сверяет: у каждого экрана-ключа есть файл страницы и в нём
    встречается `<SeeAlso` (warn, не блок — ст. 3/6, PTD-0104). Если компонента нет
    (мини-репозиторий в тесте) или карты пусты — проверять нечего → pass.
    """
    if not os.path.exists(os.path.join(root, SEEALSO_TSX)):
        return "pass", []
    tsx = read_text(root, SEEALSO_TSX)
    keys = set(parse_seealso_map(tsx, "RELATED")) | set(parse_seealso_map(tsx, "RELATED_ACTIONS"))
    if not keys:
        return "pass", []
    violations = []
    for slug in sorted(keys):
        page = f"{PLATFORM_APP}/{slug.strip('/')}/page.tsx"
        full = os.path.join(root, page)
        if not os.path.exists(full):
            violations.append({
                "record": page,
                "problem": (f"экран «{slug}» есть в карте «См. также», но файла "
                            "страницы нет — перекрёстная навигация молча отвалится"),
            })
        elif "<SeeAlso" not in read_text(root, page):
            violations.append({
                "record": page,
                "problem": (f"экран «{slug}» есть в карте «См. также», но страница не "
                            "отрисовывает <SeeAlso/> — человек не увидит блок ссылок"),
            })
    return ("pass" if not violations else "warn"), violations


def check_mirror_doc_link(root):
    """МЯГКАЯ: каждый экран-зеркало платформы ссылается на свой нормативный док.

    Часть экранов платформы — это «зеркала»: они пересказывают простыми словами
    нормативный документ из `docs/` (Манифест, Конституция, Как решаем, …). Чтобы
    пересказ можно было сверить с первоисточником и он не «уехал» от нормы при
    правках, на экране должна стоять ссылка на свой документ. Проверка сверяет: у
    каждого экрана-зеркала из карты `MIRROR_DOCS`, если его страница заведена, в
    `page.tsx` встречается путь к нормативному документу (warn, не блок — ст. 3/6,
    PTD-0040). Если каталог платформы отсутствует (мини-репозиторий в тесте) —
    проверять нечего → pass. Экран, которого ещё нет, молча пропускаем (его
    отсутствие — забота других сигналов), чтобы не кричать ложно.
    """
    if not os.path.isdir(os.path.join(root, PLATFORM_APP)):
        return "pass", []
    violations = []
    for slug, doc in sorted(MIRROR_DOCS.items()):
        page = f"{PLATFORM_APP}/{slug}/page.tsx"
        if not os.path.exists(os.path.join(root, page)):
            continue
        if doc not in read_text(root, page):
            violations.append({
                "record": page,
                "problem": (f"экран-зеркало «{slug}» не ссылается на свой нормативный "
                            f"документ {doc} — пересказ нельзя сверить с первоисточником"),
            })
    return ("pass" if not violations else "warn"), violations


def check_mirror_doc_complete(root):
    """МЯГКАЯ: каждый экран-объяснение из витрины t.learn зарегистрирован в MIRROR_DOCS.

    Обратная к `mirror-doc-link`. Набор экранов-зеркал задаётся витриной
    «Разобраться, как устроен фонд» (`t.learn` в `lib/i18n.ts`) — это и есть
    пересказы нормативных документов простыми словами. `mirror-doc-link` сверяет
    КАЖДЫЙ экран из карты `MIRROR_DOCS` со своим первоисточником. Но если заведут
    новый экран-зеркало (добавят его в `t.learn`), а в `MIRROR_DOCS` внести забудут —
    `mirror-doc-link` молча его пропустит, и пересказ останется без проверки на
    сверку с нормой. Эта проверка ловит такой пропуск: каждый адрес из `t.learn`
    должен быть ключом `MIRROR_DOCS` (warn, не блок — ст. 3/6, PTD-0109). Если файла
    `lib/i18n.ts` нет (мини-репозиторий в тесте) или список не распарсился — проверять
    нечего → pass.
    """
    if not os.path.exists(os.path.join(root, I18N_TS)):
        return "pass", []
    learn = parse_i18n_hrefs(read_text(root, I18N_TS), "learn")
    if not learn:
        return "pass", []
    violations = []
    for href in sorted(learn):
        slug = href.strip("/")
        if slug not in MIRROR_DOCS:
            violations.append({
                "record": f"{I18N_TS} → t.learn",
                "problem": (f"экран-объяснение «{href}» есть в витрине «Разобраться, "
                            "как устроен фонд», но не зарегистрирован в карте "
                            "MIRROR_DOCS (documentation_agent.py) — его пересказ не "
                            "сверяется с первоисточником (mirror-doc-link его пропустит)"),
            })
    return ("pass" if not violations else "warn"), violations


def check_mirror_doc_exists(root):
    """МЯГКАЯ: путь нормативного документа из карты MIRROR_DOCS реально есть в репо.

    `mirror-doc-link` проверяет, что экран-зеркало СОДЕРЖИТ ссылку на путь своего
    документа (как строку в `page.tsx`). Но если сам нормативный документ
    переименуют/перенесут, а путь-значение в карте `MIRROR_DOCS` поправить забудут,
    `mirror-doc-link` останется зелёным (строка-то на экране есть), а ссылка молча
    поведёт в никуда. Эта проверка ловит разрыв: для каждого экрана-зеркала, чья
    страница заведена, путь-значение из `MIRROR_DOCS` (`docs/X.md`) должен
    существовать в репозитории (warn, не блок — ст. 3/6, PTD-0110). Если каталога
    платформы нет (мини-репозиторий в тесте) — проверять нечего → pass. Экран,
    которого ещё нет, молча пропускаем (как и mirror-doc-link), чтобы не кричать ложно.
    """
    if not os.path.isdir(os.path.join(root, PLATFORM_APP)):
        return "pass", []
    violations = []
    for slug, doc in sorted(MIRROR_DOCS.items()):
        page = f"{PLATFORM_APP}/{slug}/page.tsx"
        if not os.path.exists(os.path.join(root, page)):
            continue
        if not os.path.exists(os.path.join(root, doc)):
            violations.append({
                "record": f"MIRROR_DOCS[{slug}]",
                "problem": (f"нормативный документ {doc} не найден в репозитории — "
                            "путь-значение в карте устарел (документ переименовали/"
                            "перенесли), ссылка экрана-зеркала ведёт в никуда "
                            "(mirror-doc-link этого не замечает)"),
            })
    return ("pass" if not violations else "warn"), violations


def check_mirror_doc_showcase(root):
    """МЯГКАЯ: заведённый экран-зеркало из MIRROR_DOCS показан в витрине t.learn.

    Парная к `mirror-doc-coverage`, в обратную сторону. Набор экранов-объяснений на
    главной задаёт витрина «Разобраться, как устроен фонд» (`t.learn` в
    `lib/i18n.ts`). `mirror-doc-coverage` следит, чтобы каждый экран витрины был в
    карте `MIRROR_DOCS`. Эта проверка следит за обратным: если экран есть в карте и
    его страница заведена, но адреса нет в `t.learn`, человек не дойдёт до него с
    главной — построенный экран «спрятан». Сверяет: для каждого экрана-зеркала, чья
    страница заведена, адрес `/slug/` есть в `t.learn` (warn, не блок — ст. 3/6,
    PTD-0110). Если каталога платформы нет, файла `lib/i18n.ts` нет или список не
    распарсился — проверять нечего → pass.
    """
    if not os.path.isdir(os.path.join(root, PLATFORM_APP)):
        return "pass", []
    if not os.path.exists(os.path.join(root, I18N_TS)):
        return "pass", []
    learn = parse_i18n_hrefs(read_text(root, I18N_TS), "learn")
    if not learn:
        return "pass", []
    violations = []
    for slug in sorted(MIRROR_DOCS):
        page = f"{PLATFORM_APP}/{slug}/page.tsx"
        if not os.path.exists(os.path.join(root, page)):
            continue
        href = f"/{slug}/"
        if href not in learn:
            violations.append({
                "record": f"MIRROR_DOCS[{slug}]",
                "problem": (f"экран-зеркало «{href}» заведён и в карте MIRROR_DOCS, но "
                            "его нет в витрине «Разобраться, как устроен фонд» (t.learn, "
                            "lib/i18n.ts) — человек не дойдёт до него с главной"),
            })
    return ("pass" if not violations else "warn"), violations


def check_see_also_symmetric(root):
    """МЯГКАЯ: связь «См. также» между экранами-объяснениями взаимна.

    Карта `RELATED` в `SeeAlso.tsx` связывает экраны-объяснения друг с другом. Если
    экран A ведёт «См. также» на экран B, человек ждёт, что и с B сможет вернуться к
    A — иначе попадает в тупик без обратного пути. Проверка ищет односторонние связи:
    A→B есть, B→A нет. Несимметрия — НЕ ошибка (иногда так и задумано: например,
    словарь ссылается на всех, но не все на словарь), поэтому только предупреждение
    (warn, не блок — ст. 3/6, PTD-0106). Касается лишь `RELATED` (объяснение↔
    объяснение); `RELATED_ACTIONS` (объяснение→рабочий экран) по смыслу односторонняя
    и сюда не входит. Если файла нет (мини-репозиторий в тесте) или карта пуста —
    проверять нечего → pass.
    """
    if not os.path.exists(os.path.join(root, SEEALSO_TSX)):
        return "pass", []
    related = parse_seealso_map(read_text(root, SEEALSO_TSX), "RELATED")
    if not related:
        return "pass", []
    violations = []
    for src in sorted(related):
        for dst in related[src]:
            # B упоминает A обратно? Если у B вообще нет записи в карте или в его
            # списке нет A — связь односторонняя.
            if src not in related.get(dst, []):
                violations.append({
                    "record": f"{SEEALSO_TSX} → RELATED[{dst}]",
                    "problem": (f"экран «{src}» ведёт «См. также» на «{dst}», но «{dst}» "
                                f"не ведёт обратно на «{src}» — связь односторонняя, "
                                "человек попадает в тупик без обратного пути"),
                })
    return ("pass" if not violations else "warn"), violations


CHECKS = [
    {
        "key": "bilingual-pairs",
        "title": "У каждого публичного дока есть пара RU↔EN",
        "guards": "ст. 6 — открытость/понятность; указание оператора «вся документация двуязычна»",
        "fn": "pairs",
    },
    {
        "key": "language-switcher",
        "title": "Вверху дока корректный переключатель языка [Русский]·[English]",
        "guards": "ст. 6 — доступность на обоих языках; переключатель ведёт к парному файлу",
        "fn": "switcher",
    },
    {
        "key": "link-integrity",
        "title": "Все относительные ссылки в документации ведут к существующему файлу",
        "guards": "ст. 3 — проверяемость; документ без битых ссылок реально читаем и проверяем",
        "fn": "links",
    },
    {
        "key": "anchor-integrity",
        "title": "Якоря ссылок FILE.md#section ведут к реальным заголовкам",
        "guards": "ст. 3 — проверяемость; внутренние ссылки не гниют при переименовании разделов; МЯГКАЯ — предупреждает, не блокирует",
        "fn": "anchors",
        "soft": True,
    },
    {
        "key": "glossary-coverage",
        "title": "Ключевые технические термины описаны в глоссарии (RU+EN)",
        "guards": "ст. 3/6 — понятность/объяснимость (PTD-0040); МЯГКАЯ — предупреждает, не блокирует",
        "fn": "coverage",
        "soft": True,
    },
    {
        "key": "glossary-no-dead",
        "title": "У каждой статьи глоссария термин реально используется в документах",
        "guards": "ст. 3/6 — понятность/объяснимость (PTD-0040); МЯГКАЯ, обратная к coverage — предупреждает, не блокирует",
        "fn": "nodead",
        "soft": True,
    },
    {
        "key": "glossary-symmetry",
        "title": "Число статей в RU-глоссарии и EN-зеркале совпадает",
        "guards": "ст. 3/6 — понятность/объяснимость (PTD-0040); МЯГКАЯ — предупреждает, не блокирует",
        "fn": "symmetry",
        "soft": True,
    },
    {
        "key": "constitutional-prohibitions",
        "title": "Публичные тексты не дают запрещённых обещаний (доход/инвестиция/пирамида/рефералы)",
        "guards": "ст. 3/6 + PRINCIPLES.md «Конституционные запреты» для публичных текстов; МЯГКАЯ — предупреждает, не блокирует",
        "fn": "prohibitions",
        "soft": True,
    },
    {
        "key": "see-also-targets",
        "title": "Адреса карт «См. также» (SeeAlso.tsx) существуют в текстах i18n",
        "guards": "ст. 3/6 — перекрёстная навигация платформы не «отвалится» молча при переименовании экрана (PTD-0105); МЯГКАЯ — предупреждает, не блокирует",
        "fn": "seealso_targets",
        "soft": True,
    },
    {
        "key": "see-also-present",
        "title": "Каждый экран-источник карты «См. также» отрисовывает <SeeAlso/>",
        "guards": "ст. 3/6 — у экрана-объяснения не пропадёт молча блок перекрёстных ссылок (PTD-0104); МЯГКАЯ — предупреждает, не блокирует",
        "fn": "seealso_present",
        "soft": True,
    },
    {
        "key": "mirror-doc-link",
        "title": "Каждый экран-зеркало платформы ссылается на свой нормативный документ в docs/",
        "guards": "ст. 3/6 — пересказ простыми словами можно сверить с первоисточником, зеркало не «уезжает» от нормы (PTD-0040); МЯГКАЯ — предупреждает, не блокирует",
        "fn": "mirror_doc_link",
        "soft": True,
    },
    {
        "key": "mirror-doc-coverage",
        "title": "Каждый экран-объяснение из витрины t.learn зарегистрирован в карте MIRROR_DOCS",
        "guards": "ст. 3/6 — новый экран-зеркало не останется без сверки с первоисточником (обратная к mirror-doc-link, PTD-0109); МЯГКАЯ — предупреждает, не блокирует",
        "fn": "mirror_doc_complete",
        "soft": True,
    },
    {
        "key": "mirror-doc-exists",
        "title": "Путь нормативного документа из карты MIRROR_DOCS реально есть в репозитории",
        "guards": "ст. 3/6 — переименование документа не оставит ссылку экрана-зеркала висящей в никуда (PTD-0110); МЯГКАЯ — предупреждает, не блокирует",
        "fn": "mirror_doc_exists",
        "soft": True,
    },
    {
        "key": "mirror-doc-showcase",
        "title": "Заведённый экран-зеркало из MIRROR_DOCS показан в витрине t.learn",
        "guards": "ст. 3/6 — построенный экран-объяснение не «спрячется» от человека мимо витрины на главной (парная к mirror-doc-coverage, PTD-0110); МЯГКАЯ — предупреждает, не блокирует",
        "fn": "mirror_doc_showcase",
        "soft": True,
    },
    {
        "key": "see-also-symmetric",
        "title": "Связь «См. также» между экранами-объяснениями взаимна (A→B ⇒ B→A)",
        "guards": "ст. 3/6 — у человека есть обратный путь между объяснениями, нет тупиков односторонних ссылок (PTD-0106); МЯГКАЯ — предупреждает, не блокирует",
        "fn": "seealso_symmetric",
        "soft": True,
    },
]


def run(root):
    """Прогоняет все проверки. Возвращает report dict."""
    all_md = git_tracked_md(root)
    existing = set(all_md)
    # Публичные двуязычные доки = всё .md, кроме явно одноязычных служебных.
    public_docs = [p for p in all_md if p not in SINGLE_LANG]

    pairs_status, pairs_v = check_bilingual_pairs(root, public_docs, existing)
    switch_status, switch_v = check_language_switcher(root, public_docs, existing)
    links_status, links_v = check_link_integrity(root, all_md)
    anchors_status, anchors_v = check_anchor_integrity(root, all_md, existing)
    cov_status, cov_v = check_glossary_coverage(root, existing)
    # Корпус для «мёртвых статей» — публичные доки минус сами глоссарии.
    corpus_docs = [p for p in public_docs if p not in (GLOSSARY_RU, GLOSSARY_EN)]
    nodead_status, nodead_v = check_glossary_no_dead(root, existing, corpus_docs)
    sym_status, sym_v = check_glossary_symmetry(root, existing)
    # Публичные человеко-видимые тексты = двуязычные .md + витрина web/*.html.
    public_texts = public_docs + git_tracked_web_html(root)
    prohib_status, prohib_v = check_constitutional_prohibitions(root, public_texts)
    seealso_t_status, seealso_t_v = check_see_also_targets(root)
    seealso_p_status, seealso_p_v = check_see_also_present(root)
    mirror_status, mirror_v = check_mirror_doc_link(root)
    mirror_cov_status, mirror_cov_v = check_mirror_doc_complete(root)
    mirror_exist_status, mirror_exist_v = check_mirror_doc_exists(root)
    mirror_show_status, mirror_show_v = check_mirror_doc_showcase(root)
    seealso_sym_status, seealso_sym_v = check_see_also_symmetric(root)

    results = {
        "pairs": (pairs_status, pairs_v),
        "switcher": (switch_status, switch_v),
        "links": (links_status, links_v),
        "anchors": (anchors_status, anchors_v),
        "coverage": (cov_status, cov_v),
        "nodead": (nodead_status, nodead_v),
        "symmetry": (sym_status, sym_v),
        "prohibitions": (prohib_status, prohib_v),
        "seealso_targets": (seealso_t_status, seealso_t_v),
        "seealso_present": (seealso_p_status, seealso_p_v),
        "mirror_doc_link": (mirror_status, mirror_v),
        "mirror_doc_complete": (mirror_cov_status, mirror_cov_v),
        "mirror_doc_exists": (mirror_exist_status, mirror_exist_v),
        "mirror_doc_showcase": (mirror_show_status, mirror_show_v),
        "seealso_symmetric": (seealso_sym_status, seealso_sym_v),
    }

    checks = []
    for spec in CHECKS:
        status, violations = results[spec["fn"]]
        checks.append({
            "key": spec["key"],
            "title": spec["title"],
            "guards": spec["guards"],
            "status": status,
            "soft": spec.get("soft", False),
            "violations": violations,
        })

    # Вердикт — ТОЛЬКО по блокирующим проверкам. Мягкие (soft) проверки лишь
    # предупреждают: они не делают вердикт «красным» и не меняют код возврата.
    blocking = [c for c in checks if not c["soft"]]
    all_pass = all(c["status"] == "pass" for c in blocking)
    passed = sum(1 for c in blocking if c["status"] == "pass")
    warnings = sum(len(c["violations"]) for c in checks if c["soft"])
    return {
        "agent": "documentation",
        "role": "служебный модуль, не орган власти (Конституция, ст. 9)",
        "verdict": "green" if all_pass else "red",
        "passed": passed,
        "total": len(blocking),
        "warnings": warnings,
        "md_files_total": len(all_md),
        "public_docs_checked": len(public_docs),
        "single_lang_skipped": sorted(SINGLE_LANG & existing),
        "checks": checks,
    }


def main(argv):
    parser = argparse.ArgumentParser(
        description="Documentation AI-агент Public Trust DAO: двуязычность RU↔EN + целостность ссылок."
    )
    parser.add_argument(
        "--root", default=ROOT,
        help="корень репозитория (по умолчанию — на уровень выше ai-agents/).",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="вывести машиночитаемый JSON-отчёт вместо человекочитаемого.",
    )
    args = parser.parse_args(argv[1:])

    report = run(args.root)
    all_pass = report["verdict"] == "green"

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if all_pass else 1

    print("=" * 70)
    print("DOCUMENTATION AI-АГЕНТ — Public Trust DAO")
    print("Служебный модуль (ст. 9): проверяет документацию, не правит. Ничего не двигает.")
    print("=" * 70)
    print(f"Всего .md (git-отслеживаемых): {report['md_files_total']}")
    print(f"Публичных доков проверено (двуязычность): {report['public_docs_checked']}")
    print(f"Одноязычных служебных пропущено: {len(report['single_lang_skipped'])}")
    for c in report["checks"]:
        mark = {"pass": "✓", "fail": "✗", "error": "⚠", "warn": "⚠"}[c["status"]]
        soft = "  (мягкая — не влияет на вердикт)" if c.get("soft") else ""
        print(f"\n{mark} [{c['key']}] {c['title']}{soft}")
        print(f"    защищает: {c['guards']}")
        for v in c["violations"]:
            print(f"    | {v['record']}: {v['problem']}")
    print("\n" + "-" * 70)
    verdict = "ЗЕЛЁНО ✓" if all_pass else "КРАСНО ✗"
    warn_n = report.get("warnings", 0)
    warn_note = f"; предупреждений (мягких): {warn_n}" if warn_n else ""
    print(f"ИТОГ: {verdict}  ({report['passed']}/{report['total']} блокирующих проверок прошли{warn_note})")
    print("-" * 70)
    if warn_n:
        print("Есть мягкие предупреждения (глоссарий отстаёт от документов): это")
        print("повод дополнить глоссарий, но НЕ ошибка — вердикт остаётся прежним.")
    if not all_pass:
        print("Documentation нашёл расхождение в документации (нет пары / битый")
        print("переключатель / битая ссылка). Это сигнал сообществу, а не действие:")
        print("агент не дописывает переводы и не правит ссылки — это делают люди.")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
