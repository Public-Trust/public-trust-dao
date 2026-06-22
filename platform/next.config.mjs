// Конфигурация Next.js для Public Trust DAO.
//
// Простыми словами: мы собираем платформу как НАБОР ОБЫЧНЫХ ФАЙЛОВ (HTML/CSS/JS),
// которые можно выложить на бесплатный хостинг (GitHub Pages) без платного сервера.
// При этом архитектура полноценная — позже тот же код можно запустить как сервер,
// просто убрав режим статической сборки.
//
// Technical note (for developers): `output: 'export'` produces a fully static site
// in `out/`. `basePath` is read from the environment so the same build works both at
// the domain root (future custom domain / server) and under a GitHub Pages subpath.
// No remote image optimization, no telemetry — transparency rail (no third parties).

/** @type {import('next').NextConfig} */
const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? '';

const nextConfig = {
  output: 'export',
  basePath,
  // Префикс ассетов = basePath, чтобы статика грузилась тем же origin (без CDN).
  assetPrefix: basePath || undefined,
  // На статическом хостинге нет сервера для оптимизации картинок — отключаем.
  images: { unoptimized: true },
  // Завершающий слэш делает пути предсказуемыми на GitHub Pages.
  trailingSlash: true,
  reactStrictMode: true,
  // Не отправлять анонимную телеметрию Next наружу (рельса прозрачности).
  // (Дублируется переменной NEXT_TELEMETRY_DISABLED=1 в CI.)
};

export default nextConfig;
