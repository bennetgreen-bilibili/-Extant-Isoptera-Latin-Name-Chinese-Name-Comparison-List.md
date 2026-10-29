/* 命名差异看板 /list/name-issues/：筛选 + 分页（无依赖，渐进增强）。
   页面已在服务端渲染全部行（无 JS 也能看到全部条目）；这里只做：
     - 按 group（冲突/存疑/缺口）、source（GBIF/CoL/BSF）、关键词过滤
     - 每页 50 条分页
     - 把筛选状态写进 URL（?group=&source=&q=&page=，可分享/可刷新）
   行内 data-q 已由 Liquid 预拼好（小写拉丁名 + 中文名 + 外部名 + 接受名 + 科名）。 */
(function () {
  var root = document.getElementById('ni-root');
  if (!root) return;
  var body = document.getElementById('ni-body');
  if (!body) return;

  var rows = Array.prototype.slice.call(body.querySelectorAll('tr.ni-row'));
  var chipBox = root.querySelector('.ni-filters');
  var chips = chipBox ? Array.prototype.slice.call(chipBox.querySelectorAll('[data-group]')) : [];
  var sourceSel = document.getElementById('ni-source');
  var qInput = document.getElementById('ni-q');
  var resetBtn = document.getElementById('ni-reset');
  var statusEl = document.getElementById('ni-status');
  var emptyEl = document.getElementById('ni-empty');
  var prevBtn = document.getElementById('ni-prev');
  var nextBtn = document.getElementById('ni-next');
  var pageInfo = document.getElementById('ni-pageinfo');
  var pager = document.getElementById('ni-pager');

  var size = parseInt(root.getAttribute('data-page-size') || '50', 10);
  if (!size || size < 1) size = 50;

  var T = {
    range: root.getAttribute('data-text-range') || '{a}-{b} / {t}',
    page: root.getAttribute('data-text-page') || '{p} / {pages}',
    empty: root.getAttribute('data-text-empty') || 'No matches'
  };

  var state = { group: 'all', source: 'all', q: '', page: 1 };
  var shown = rows;

  function fill(tpl, map) {
    return String(tpl).replace(/\{(\w+)\}/g, function (m, k) {
      return map[k] == null ? '' : map[k];
    });
  }

  function readUrl() {
    try {
      var p = new URLSearchParams(window.location.search);
      var g = p.get('group');
      if (g) state.group = g;
      var s = p.get('source');
      if (s) state.source = s;
      state.q = p.get('q') || '';
      var pg = parseInt(p.get('page') || '1', 10);
      if (pg > 0) state.page = pg;
    } catch (e) { /* 老浏览器：忽略 URL 状态，用默认值 */ }
  }

  function writeUrl() {
    try {
      var p = new URLSearchParams();
      if (state.group !== 'all') p.set('group', state.group);
      if (state.source !== 'all') p.set('source', state.source);
      if (state.q) p.set('q', state.q);
      if (state.page > 1) p.set('page', String(state.page));
      var qs = p.toString();
      history.replaceState(null, '', window.location.pathname + (qs ? '?' + qs : '') + window.location.hash);
    } catch (e) { /* 忽略：不影响页面功能 */ }
  }

  function apply() {
    var q = state.q.trim().toLowerCase();
    shown = [];
    var i;
    for (i = 0; i < rows.length; i++) {
      var r = rows[i];
      var okGroup = state.group === 'all' || r.getAttribute('data-group') === state.group;
      var okSource = state.source === 'all' || r.getAttribute('data-source') === state.source;
      var okQ = !q || (r.getAttribute('data-q') || '').indexOf(q) >= 0;
      if (okGroup && okSource && okQ) shown.push(r);
      else r.hidden = true;
    }

    var pages = Math.max(1, Math.ceil(shown.length / size));
    if (state.page > pages) state.page = pages;
    if (state.page < 1) state.page = 1;
    var start = (state.page - 1) * size;
    var end = Math.min(start + size, shown.length);
    for (i = 0; i < shown.length; i++) shown[i].hidden = (i < start || i >= end);

    if (statusEl) {
      statusEl.textContent = shown.length
        ? fill(T.range, { a: start + 1, b: end, t: shown.length })
        : T.empty;
    }
    if (emptyEl) emptyEl.hidden = shown.length > 0;
    if (pageInfo) pageInfo.textContent = fill(T.page, { p: state.page, pages: pages });
    if (prevBtn) prevBtn.disabled = state.page <= 1;
    if (nextBtn) nextBtn.disabled = state.page >= pages;
    if (pager) pager.hidden = pages <= 1;
    for (i = 0; i < chips.length; i++) {
      var on = chips[i].getAttribute('data-group') === state.group;
      if (on) chips[i].classList.add('is-active');
      else chips[i].classList.remove('is-active');
      chips[i].setAttribute('aria-pressed', on ? 'true' : 'false');
    }
    if (sourceSel) sourceSel.value = state.source;
    if (qInput && qInput.value !== state.q) qInput.value = state.q;
    writeUrl();
  }

  function bind() {
    var i;
    for (i = 0; i < chips.length; i++) {
      chips[i].addEventListener('click', function (ev) {
        state.group = ev.currentTarget.getAttribute('data-group') || 'all';
        state.page = 1;
        apply();
      });
    }
    if (sourceSel) {
      sourceSel.addEventListener('change', function () {
        state.source = sourceSel.value || 'all';
        state.page = 1;
        apply();
      });
    }
    if (qInput) {
      var timer;
      qInput.addEventListener('input', function () {
        clearTimeout(timer);
        var v = qInput.value;
        timer = setTimeout(function () { state.q = v; state.page = 1; apply(); }, 140);
      });
    }
    if (prevBtn) prevBtn.addEventListener('click', function () { state.page -= 1; apply(); });
    if (nextBtn) nextBtn.addEventListener('click', function () { state.page += 1; apply(); });
    if (resetBtn) {
      resetBtn.addEventListener('click', function () {
        state = { group: 'all', source: 'all', q: '', page: 1 };
        apply();
      });
    }
  }


  readUrl();
  bind();
  apply();
})();
