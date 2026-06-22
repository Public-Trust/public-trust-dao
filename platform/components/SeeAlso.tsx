"use client";

import Link from "next/link";
import { useI18n } from "@/components/Providers";

// Перекрёстные ссылки «См. также» между экранами-объяснениями (зеркалами
// нормативных доков: «Манифест», «Конституция», «Как решаем», «Порядок помощи»,
// «Помощь и награда», «Оплата напрямую», «Защита от обмана», «Оплачиваемая
// работа», «Всё под подписью», «Поддержать проект», «Словарь»). Чтобы человек
// ходил между объяснениями, не возвращаясь каждый раз на главную.
//
// Заголовки и короткие описания НЕ задвоены: берутся из того же списка
// lib/i18n.ts (t.learn), что и витрина «Разобраться, как устроен фонд» на
// главной — зеркало остаётся одним источником текста (RU↔EN). Чисто-фронтенд,
// без новых зависимостей. Развитие приёма «экран-зеркало» (PTD-0102/0103).

// Карта связей между экранами по адресу (язык-независимая структура).
const RELATED: Record<string, string[]> = {
  "/manifesto/": ["/constitution/", "/governance/", "/support/"],
  "/constitution/": ["/manifesto/", "/governance/", "/accountability/"],
  "/governance/": ["/constitution/", "/priorities/", "/safeguards/"],
  "/priorities/": ["/rewards/", "/direct-help/", "/governance/"],
  "/rewards/": ["/priorities/", "/work/", "/direct-help/"],
  "/direct-help/": ["/priorities/", "/accountability/", "/support/"],
  "/safeguards/": ["/accountability/", "/work/", "/governance/"],
  "/work/": ["/rewards/", "/safeguards/", "/accountability/"],
  "/accountability/": ["/safeguards/", "/governance/", "/direct-help/"],
  "/support/": ["/direct-help/", "/governance/", "/manifesto/"],
  "/glossary/": ["/constitution/", "/manifesto/", "/priorities/"],
};

type LearnItem = { title: string; text: string; href: string };

export default function SeeAlso({ slug }: { slug: string }) {
  const { t } = useI18n();
  const related = RELATED[slug] ?? [];
  const items = related
    .map((href) => t.learn.find((l) => l.href === href))
    .filter((l): l is LearnItem => l !== undefined);

  if (items.length === 0) return null;

  return (
    <section className="see-also" aria-labelledby="see-also-title">
      <h2 id="see-also-title">{t.seeAlso}</h2>
      <ul className="see-also-list">
        {items.map((item) => (
          <li key={item.href} className="see-also-item">
            <Link className="see-also-link" href={item.href}>
              {item.title}
            </Link>
            <span className="see-also-text">{item.text}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
