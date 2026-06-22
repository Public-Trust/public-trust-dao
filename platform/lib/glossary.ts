// Слой данных для экрана «Словарь простыми словами».
//
// Простыми словами: здесь живёт устройство словаря — как термин и его понятное
// объяснение собраны в группы и как искать по ним. Сами слова и объяснения
// хранятся сразу на двух языках в lib/i18n.ts (t.glossary.groups), потому что
// это текст для человека (правило понятного языка PTD-0040). Словарь — это
// платформенное зеркало нормативного документа docs/GLOSSARY.md: ничего не
// подгружается со стороны, текст едет вместе с приложением (прозрачность).
//
// Слой намеренно отделён от экрана (UI): если словарь позже начнут собирать
// автоматически из docs/GLOSSARY.md, поменяется только источник данных, а
// интерфейс останется прежним — «переключением тумблера».

export type GlossaryEntry = {
  // Термин человеческими словами; технический термин, если нужен, — в скобках.
  term: string;
  // Короткое объяснение «как для человека без технического бэкграунда».
  def: string;
};

export type GlossaryGroup = {
  // Устойчивый ключ группы (для адреса-якоря и ключа React) — не переводится.
  id: string;
  // Человеческий заголовок группы (на языке интерфейса).
  title: string;
  entries: GlossaryEntry[];
};

// Простой текстовый поиск по словарю: оставляем только группы, где есть
// совпадение в названии термина или в объяснении. Регистр не важен. Пустой
// запрос возвращает словарь целиком.
export function searchGlossary(
  groups: GlossaryGroup[],
  query: string,
): GlossaryGroup[] {
  const q = query.trim().toLowerCase();
  if (!q) return groups;
  return groups
    .map((group) => ({
      ...group,
      entries: group.entries.filter(
        (e) =>
          e.term.toLowerCase().includes(q) || e.def.toLowerCase().includes(q),
      ),
    }))
    .filter((group) => group.entries.length > 0);
}

// Сколько всего терминов в словаре — для честной подписи «слов в словаре: N».
export function countTerms(groups: GlossaryGroup[]): number {
  return groups.reduce((sum, group) => sum + group.entries.length, 0);
}
