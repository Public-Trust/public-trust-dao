/*
 * Живой «светофор» состояния проекта / Live project status light.
 *
 * Читает служебный артефакт ./status.json (копию governance/status/run_all_status.json,
 * которую кладёт сюда деплой-воркфлоу) и рисует человеку зелёно/красно + счёт
 * агентов/тестов/стража и мягкие предупреждения. Запрос — тем же origin, что и сайт:
 * ни одного стороннего сервиса, бейджа или трекера (политика прозрачности).
 *
 * Один и тот же скрипт обслуживает два вида:
 *   - полный виджет #statuslight (страница «Прозрачность») — лампа, метрики, подсказки;
 *   - компактный значок .statusbadge (шапка и/или футер остальных страниц) — точка +
 *     слово, ведёт на секцию «Прозрачность» с подробностями. Значков на странице может
 *     быть несколько (напр. один в шапке, один в футере) — рисуются все.
 * Делается один запрос; рисуется тот вид, который есть на странице (или оба).
 *
 * Язык берётся из <html lang>. DOM строится через textContent — никаких innerHTML
 * с данными, даже из своего же артефакта.
 */
(function () {
  var full = document.getElementById('statuslight');
  var badges = document.querySelectorAll('.statusbadge');
  if (!full && !badges.length) return;

  var en = document.documentElement.lang === 'en';
  var T = en ? {
    green: 'All checks are green',
    red: 'Something is out of sync — see details below',
    err: 'Could not load the status artifact. Open it directly or check CI.',
    agents: 'Agents', tests: 'Tests', guard: 'Structure guard', warns: 'Soft warnings',
    warnsHead: 'Guard hints (do not fail the build):',
    schema: 'Artifact schema v', source: 'source', open: 'open JSON',
    bGreen: 'checks are green', bRed: 'out of sync', bErr: 'status unavailable',
    bTitleGreen: 'All checks are green — open the Transparency page for details',
    bTitleRed: 'Something is out of sync — open the Transparency page for details',
    bTitleErr: 'Status artifact is unavailable — open the Transparency page'
  } : {
    green: 'Все проверки зелёные',
    red: 'Есть расхождение — смотрите детали ниже',
    err: 'Не удалось загрузить артефакт состояния. Откройте его напрямую или сверьтесь с CI.',
    agents: 'Агенты', tests: 'Тесты', guard: 'Страж структуры', warns: 'Мягкие предупреждения',
    warnsHead: 'Подсказки стража (не валят проверку):',
    schema: 'Артефакт, схема v', source: 'источник', open: 'открыть JSON',
    bGreen: 'проверки в порядке', bRed: 'есть расхождение', bErr: 'состояние недоступно',
    bTitleGreen: 'Все проверки зелёные — откройте страницу «Прозрачность» за подробностями',
    bTitleRed: 'Есть расхождение — откройте страницу «Прозрачность» за подробностями',
    bTitleErr: 'Артефакт состояния недоступен — откройте страницу «Прозрачность»'
  };
  var ARTIFACT = 'https://github.com/Public-Trust/public-trust-dao/blob/main/governance/status/run_all_status.json';

  function role(box, name) { return box.querySelector('[data-role="' + name + '"]'); }

  function chip(label, value) {
    var f = document.createElement('span');
    f.className = 'fact';
    var b = document.createElement('b');
    b.textContent = label + ': ';
    f.appendChild(b);
    f.appendChild(document.createTextNode(value));
    return f;
  }

  function renderFull(s) {
    var green = s && s.verdict === 'green';
    full.setAttribute('data-state', green ? 'green' : 'red');
    full.classList.remove('is-green', 'is-red');
    full.classList.add(green ? 'is-green' : 'is-red');

    var label = role(full, 'label');
    if (label) label.textContent = green ? T.green : T.red;

    var metrics = role(full, 'metrics');
    if (metrics) {
      metrics.textContent = '';
      if (s.agents) metrics.appendChild(chip(T.agents, s.agents.green + '/' + s.agents.total));
      if (s.tests) metrics.appendChild(chip(T.tests, s.tests.green + '/' + s.tests.total));
      if (s.guard) {
        metrics.appendChild(chip(T.guard, s.guard.passed + '/' + s.guard.total));
        metrics.appendChild(chip(T.warns, String(s.guard.warnings || 0)));
      }
    }

    var lines = (s.guard && s.guard.warning_lines) || [];
    var warns = role(full, 'warns');
    if (warns) {
      warns.textContent = '';
      if (lines.length) {
        warns.hidden = false;
        var head = document.createElement('li');
        head.className = 'warns-head';
        head.textContent = T.warnsHead;
        warns.appendChild(head);
        lines.forEach(function (ln) {
          var li = document.createElement('li');
          li.textContent = '⚠ ' + ln;
          warns.appendChild(li);
        });
      } else {
        warns.hidden = true;
      }
    }

    var src = role(full, 'src');
    if (src) {
      src.textContent = '';
      src.appendChild(document.createTextNode(
        T.schema + (s.schema_version || '?') + ' · ' + T.source + ': ' + (s.source || '') + ' · '));
      var a = document.createElement('a');
      a.href = ARTIFACT;
      a.textContent = T.open;
      src.appendChild(a);
    }
  }

  function renderBadge(badge, s) {
    var green = s && s.verdict === 'green';
    badge.setAttribute('data-state', green ? 'green' : 'red');
    badge.classList.remove('is-green', 'is-red', 'is-error');
    badge.classList.add(green ? 'is-green' : 'is-red');
    badge.setAttribute('title', green ? T.bTitleGreen : T.bTitleRed);
    var text = role(badge, 'badgetext');
    if (text) text.textContent = green ? T.bGreen : T.bRed;
  }

  function failFull() {
    full.setAttribute('data-state', 'error');
    var label = role(full, 'label');
    if (label) label.textContent = T.err;
  }

  function failBadge(badge) {
    badge.setAttribute('data-state', 'error');
    badge.classList.remove('is-green', 'is-red');
    badge.classList.add('is-error');
    badge.setAttribute('title', T.bTitleErr);
    var text = role(badge, 'badgetext');
    if (text) text.textContent = T.bErr;
  }

  function eachBadge(fn) { Array.prototype.forEach.call(badges, fn); }
  function render(s) { if (full) renderFull(s); eachBadge(function (b) { renderBadge(b, s); }); }
  function fail() { if (full) failFull(); eachBadge(failBadge); }

  if (!('fetch' in window)) { fail(); return; }
  fetch('status.json', { cache: 'no-store' })
    .then(function (r) { if (!r.ok) throw new Error('http ' + r.status); return r.json(); })
    .then(render)
    .catch(fail);
})();
