"use client";

// Понятная страница «страница не найдена» (404) на обоих языках.
// Для статической сборки Next отдаёт её как 404.html — человек, попавший
// по устаревшей ссылке, видит дружелюбное объяснение и путь назад, а не
// пустой технический тупик. Тексты — из общего словаря (RU↔EN).

import Link from "next/link";
import { useI18n } from "@/components/Providers";

export default function NotFound() {
  const { t } = useI18n();
  const n = t.notFound;

  return (
    <main id="main" className="container">
      <section className="hero hero--screen" aria-labelledby="notfound-title">
        <p className="disclaimer" role="note">
          {n.code}
        </p>
        <h1 id="notfound-title">{n.title}</h1>
        <p className="lead">{n.lead}</p>
        <div className="cta-row">
          <Link className="btn btn-primary" href="/">
            {n.home}
          </Link>
          <Link className="btn btn-ghost" href="/about/">
            {n.about}
          </Link>
        </div>
      </section>
    </main>
  );
}
