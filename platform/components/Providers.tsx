"use client";

// Хранилище выбора языка и темы. Выбор живёт только в браузере человека
// (localStorage) — никаких серверов и слежки (рельса прозрачности).

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { DEFAULT_LANG, DICT, getDict, type Dict, type Lang } from "@/lib/i18n";

type Theme = "light" | "dark";

type I18nValue = {
  lang: Lang;
  setLang: (lang: Lang) => void;
  toggleLang: () => void;
  t: Dict;
  theme: Theme;
  toggleTheme: () => void;
};

const I18nContext = createContext<I18nValue | null>(null);

const LANG_KEY = "ptd.lang";
const THEME_KEY = "ptd.theme";

function isLang(value: string | null): value is Lang {
  return value === "ru" || value === "en";
}

export function Providers({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(DEFAULT_LANG);
  const [theme, setTheme] = useState<Theme>("light");

  // При первой загрузке восстанавливаем выбор человека из браузера.
  useEffect(() => {
    const savedLang = window.localStorage.getItem(LANG_KEY);
    if (isLang(savedLang)) {
      setLangState(savedLang);
    }
    const savedTheme = window.localStorage.getItem(THEME_KEY);
    if (savedTheme === "dark" || savedTheme === "light") {
      setTheme(savedTheme);
    } else if (window.matchMedia?.("(prefers-color-scheme: dark)").matches) {
      setTheme("dark");
    }
  }, []);

  // Отражаем язык и тему в самом документе (для доступности и стилей).
  useEffect(() => {
    document.documentElement.lang = DICT[lang].htmlLang;
  }, [lang]);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  const setLang = useCallback((next: Lang) => {
    setLangState(next);
    window.localStorage.setItem(LANG_KEY, next);
  }, []);

  const toggleLang = useCallback(() => {
    setLangState((prev) => {
      const next: Lang = prev === "ru" ? "en" : "ru";
      window.localStorage.setItem(LANG_KEY, next);
      return next;
    });
  }, []);

  const toggleTheme = useCallback(() => {
    setTheme((prev) => {
      const next: Theme = prev === "light" ? "dark" : "light";
      window.localStorage.setItem(THEME_KEY, next);
      return next;
    });
  }, []);

  const value = useMemo<I18nValue>(
    () => ({ lang, setLang, toggleLang, t: getDict(lang), theme, toggleTheme }),
    [lang, setLang, toggleLang, theme, toggleTheme],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nValue {
  const ctx = useContext(I18nContext);
  if (!ctx) {
    throw new Error("useI18n must be used inside <Providers>");
  }
  return ctx;
}
