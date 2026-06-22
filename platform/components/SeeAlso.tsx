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

// Карта связей между экранами-объяснениями по адресу (язык-независимая
// структура).
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

// Мягкие переходы «объяснение → действие»: с экрана-объяснения ведём на тот
// рабочий экран, где прочитанное можно применить. Источник заголовков — тот же
// t.screens, что и витрина шести рабочих экранов на главной (без задвоения).
// Включаем только там, где переход естественен для человека.
const RELATED_ACTIONS: Record<string, string[]> = {
  "/governance/": ["/voting/"],
  "/priorities/": ["/apply/"],
  "/rewards/": ["/treasury/"],
  "/direct-help/": ["/apply/", "/treasury/"],
  "/safeguards/": ["/identity/"],
  "/work/": ["/treasury/"],
  "/accountability/": ["/journal/", "/treasury/"],
};

type LearnItem = { title: string; text: string; href: string };
type ScreenItem = { title: string; text: string; href?: string; short?: string };

export default function SeeAlso({ slug }: { slug: string }) {
  const { t } = useI18n();
  const related = RELATED[slug] ?? [];
  const items = related
    .map((href) => t.learn.find((l) => l.href === href))
    .filter((l): l is LearnItem => l !== undefined);

  const actions = (RELATED_ACTIONS[slug] ?? [])
    .map((href) => t.screens.find((s) => s.href === href))
    .filter((s): s is ScreenItem & { href: string } => s?.href !== undefined);

  if (items.length === 0 && actions.length === 0) return null;

  return (
    <section className="see-also" aria-labelledby="see-also-title">
      <h2 id="see-also-title">{t.seeAlso}</h2>
      {items.length > 0 && (
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
      )}
      {actions.length > 0 && (
        <>
          <p className="see-also-do-label">{t.seeAlsoDo}</p>
          <ul className="see-also-list see-also-do">
            {actions.map((item) => (
              <li key={item.href} className="see-also-item">
                <Link className="see-also-link" href={item.href}>
                  {item.title} →
                </Link>
                <span className="see-also-text">{item.text}</span>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
