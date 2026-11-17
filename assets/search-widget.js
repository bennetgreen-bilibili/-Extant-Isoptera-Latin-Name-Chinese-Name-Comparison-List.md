/* 全局搜索浮层：Ctrl/⌘+K（或点击导航里的搜索按钮）在任何页面直接搜索。
   用 Pagefind 的 JS API（/pagefind/pagefind.js，由 CI 在 Jekyll 构建后生成），
   索引不存在（本地 jekyll serve）时自动回退到 /search/ 页面。
   不新增第三方依赖；样式见 assets/custom.css 的 .search-overlay。 */
(function () {
  var overlay = document.getElementById('search-overlay');
  if (!overlay) return;

  var script = document.currentScript;
  var attr = function (name, fallback) {
    var v = script && script.getAttribute(name);
    return v ? v : fallback;
  };
  var BASE = attr('data-base', '');
  var BUNDLE = attr('data-bundle', BASE + '/pagefind/');
  var SEARCH_PAGE = attr('data-search-page', BASE + '/search/');
  var T = {
    empty: attr('data-text-empty', 'No matching results'),
    loading: attr('data-text-loading', 'Searching…')
  };

  var input = document.getElementById('search-overlay-input');
  var resultsEl = document.getElementById('search-overlay-results');
  var allLink = document.getElementById('search-overlay-all');
  var closeBtn = document.getElementById('search-overlay-close');
  var backdrop = document.getElementById('search-overlay-backdrop');
  var trigger = document.getElementById('nav-search-btn');
  if (!input || !resultsEl) return;

  var dynamicImport = null;
  try {
    dynamicImport = new Function('p', 'return import(p);');
  } catch (e) {
    dynamicImport = null;
  }

  var pagefindPromise = null;
  var timer = null;
  var requestSeq = 0;
  var logged = {};

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  // 结果 URL 的两种形态都要认：Pagefind 若已按 baseUrl 前缀化，则可能是
  // 绝对地址（https://host/baseurl/stats/）或站点内相对路径（/baseurl/stats/）；
  // 只有两者都不是时才补前缀。重复补前缀会拼出 /baseurl/baseurl/… 而 404。
  var REL_BASE = BASE ? BASE.replace(/^https?:\/\/[^/]+/, '') : '';
  function fixUrl(url) {
    if (!url) return SEARCH_PAGE;
    if (!BASE) return url;
    if (REL_BASE && (url === REL_BASE || url.indexOf(REL_BASE + '/') === 0)) return url;
    if (url.indexOf(BASE + '/') === 0) return url;
    return url.charAt(0) === '/' ? BASE + url : BASE + '/' + url;
  }

  function loadPagefind() {
    if (!dynamicImport) return Promise.resolve(null);
    if (!pagefindPromise) {
      pagefindPromise = dynamicImport(BUNDLE + 'pagefind.js').then(function (pf) {
        if (!pf) return null;
        // 非 UI 入口不会自动带上 site.baseurl，这里显式设定，结果 URL 即带前缀的绝对地址
        var setup;
        try {
          setup = (typeof pf.options === 'function' && BASE)
            ? Promise.resolve(pf.options({ basePath: BUNDLE, baseUrl: BASE + '/' }))
            : Promise.resolve();
        } catch (e) {
          setup = Promise.resolve();
        }
        return setup.then(function () {
          return pf.init ? pf.init() : null;
        }).then(function () { return pf; });
      }).catch(function () { return null; });
    }
    return pagefindPromise;
  }

  function track(term) {
    if (!term || logged[term]) return;
    logged[term] = 1;
    try {
      if (window.goatcounter && window.goatcounter.count) {
        window.goatcounter.count({ path: '/search?q=' + encodeURIComponent(term), title: 'search', event: true });
      }
    } catch (e) { /* 统计失败不影响搜索 */ }
  }

  function showState(text) {
    resultsEl.innerHTML = '<li class="so-state">' + esc(text) + '</li>';
  }

  function setAllLink(term) {
    if (!allLink) return;
    allLink.href = SEARCH_PAGE + (term ? '?q=' + encodeURIComponent(term) : '');
  }

  function render(items) {
    if (!items.length) {
      showState(T.empty);
      return;
    }
    var html = '';
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      var title = (it.meta && it.meta.title) || it.url || '';
      var excerpt = it.excerpt || it.plain_excerpt || '';
      html += '<li><a href="' + esc(fixUrl(it.url)) + '">'
        + '<span class="so-title">' + esc(title) + '</span>'
        + '<span class="so-excerpt">' + excerpt + '</span></a></li>';
    }
    resultsEl.innerHTML = html;
  }

  function run(term) {
    var q = String(term || '').trim();
    if (!q) {
      resultsEl.innerHTML = '';
      setAllLink('');
      return;
    }
    var seq = ++requestSeq;
    showState(T.loading);
    loadPagefind().then(function (pf) {
      if (seq !== requestSeq) return;
      if (!pf) {
        showState(T.empty);
        return;
      }
      return pf.search(q).then(function (res) {
        if (seq !== requestSeq) return;
        var slice = (res.results || []).slice(0, 8);
        return Promise.all(slice.map(function (r) { return r.data(); })).then(function (items) {
          if (seq !== requestSeq) return;
          render(items);
          track(q);
        });
      });
    }).catch(function () {
      if (seq === requestSeq) showState(T.empty);
    });
  }

  var lastFocused = null;

  function open() {
    if (!overlay.hidden) return;
    lastFocused = document.activeElement;
    overlay.hidden = false;
    document.body.classList.add('search-overlay-open');
    setAllLink(input.value);
    input.focus();
    if (input.value) run(input.value);
  }

  function close() {
    if (overlay.hidden) return;
    overlay.hidden = true;
    document.body.classList.remove('search-overlay-open');
    if (lastFocused && lastFocused.focus) lastFocused.focus();
  }

  function toggle() {
    if (overlay.hidden) open();
    else close();
  }

  input.addEventListener('input', function () {
    clearTimeout(timer);
    var v = input.value;
    setAllLink(v.trim());
    timer = setTimeout(function () { run(v); }, 180);
  });

  input.addEventListener('keydown', function (ev) {
    if (ev.key === 'Enter') {
      var first = resultsEl.querySelector('a');
      if (first) {
        ev.preventDefault();
        window.location.href = first.getAttribute('href');
      } else if (input.value.trim()) {
        window.location.href = SEARCH_PAGE + '?q=' + encodeURIComponent(input.value.trim());
      }
    } else if (ev.key === 'ArrowDown') {
      var link = resultsEl.querySelector('a');
      if (link) {
        ev.preventDefault();
        link.focus();
      }
    }
  });

  resultsEl.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape') close();
  });

  // AI 搜索弹窗（Cloudflare search-modal-snippet，见 assets/ai-search.js）也可能
  // 已经挂到页面上；它自己会锁 body 滚动，键盘入口仍只认本站浮层。
  function aiModal() {
    var node = document.querySelector('search-modal-snippet');
    if (!node || typeof node.isModalOpen !== 'function' || !node.isModalOpen()) return null;
    return node;
  }

  // Ctrl/⌘+K 在捕获阶段处理并截断：官方 AI 弹窗也监听 document 上的同一个组合键，
  // 不截断就会同时打开两个界面（且哪一个盖在上面取决于 z-index）。截断后
  // 只有本站浮层响应；浮层里的「AI 搜索」按钮再进入官方弹窗。
  document.addEventListener('keydown', function (ev) {
    var key = ev.key || '';
    if ((ev.ctrlKey || ev.metaKey) && (key === 'k' || key === 'K')) {
      ev.preventDefault();
      ev.stopImmediatePropagation();
      var ai = aiModal();
      if (ai) { ai.close(); return; }  // AI 弹窗开着就关它，不叠开本站浮层
      toggle();
    }
  }, true);

  document.addEventListener('keydown', function (ev) {
    if (aiModal()) return;  // 焦点在 AI 弹窗里时，Esc / 「/」交还给官方组件自己处理
    var key = ev.key || '';
    if (key === 'Escape' && !overlay.hidden) {
      close();
      return;
    }
    if (key === '/' && overlay.hidden) {
      var t = ev.target;
      var tag = t && t.tagName ? t.tagName.toLowerCase() : '';
      if (tag !== 'input' && tag !== 'textarea' && tag !== 'select' && !(t && t.isContentEditable)) {
        ev.preventDefault();
        open();
      }
    }
  });

  if (trigger) trigger.addEventListener('click', toggle);
  if (closeBtn) closeBtn.addEventListener('click', close);
  if (backdrop) backdrop.addEventListener('click', close);
})();
