/* 全站全文搜索页（Pagefind）：初始化 Pagefind UI，支持 ?q= 预填。
   索引 /pagefind/ 由 CI 在 Jekyll 构建之后用 Pagefind（extended，含中文分词）生成；
   本地未跑 Pagefind（例如 jekyll serve）时给出回退提示，不报错。 */
(function () {
  var target = document.getElementById('pagefind-search');
  if (!target) return;

  var lang = target.getAttribute('data-lang') || 'zh-CN';
  var base = (target.getAttribute('data-base') || '').replace(/\/$/, '');
  var bundle = base + '/pagefind/';

  var TEXT = {
    'zh-CN': {
      placeholder: '搜索全站：名录、物种页、统计、博客…',
      zero_results: '未找到「[SEARCH_TERM]」相关结果',
      load_more: '加载更多结果',
      clear_search: '清空',
      search_label: '搜索本站',
      fallback: '全文索引尚未生成（本地预览时属正常——GitHub Pages 构建时会自动生成）。请改用',
      fallback_link: '名录检索',
      fallback_end: '。',
      fallback_url: base + '/list/'
    },
    en: {
      placeholder: 'Search the whole site: checklist, species pages, blog…',
      zero_results: 'No results for “[SEARCH_TERM]”',
      load_more: 'Load more results',
      clear_search: 'Clear',
      search_label: 'Search this site',
      fallback: 'The full-text index has not been generated yet (expected in local preview — it is built automatically on GitHub Pages). Meanwhile use the',
      fallback_link: 'checklist search',
      fallback_end: '.',
      fallback_url: base + '/en/list/'
    },
    es: {
      placeholder: 'Buscar en todo el sitio: listado, especies, blog…',
      zero_results: 'Sin resultados para «[SEARCH_TERM]»',
      load_more: 'Cargar más resultados',
      clear_search: 'Limpiar',
      search_label: 'Buscar en este sitio',
      fallback: 'El índice de texto completo aún no se ha generado (es normal en la vista local: se genera automáticamente en GitHub Pages). Mientras tanto, use el',
      fallback_link: 'buscador del listado',
      fallback_end: '.',
      fallback_url: base + '/es/list/'
    }
  };

  var i18n = TEXT[lang] || TEXT['zh-CN'];

  function showFallback() {
    target.innerHTML = '<p class="search-fallback">' + i18n.fallback +
      ' <a href="' + i18n.fallback_url + '">' + i18n.fallback_link + '</a>' + (i18n.fallback_end || '.') + '</p>';
  }

  // 结果 URL 由 Pagefind 按站点根目录记录（如 /list/），站点若部署在 baseurl 子路径下需要补前缀；
  // 这里统一改写，避免依赖 Pagefind UI 是否支持 baseUrl 选项。
  function fixUrl(url) {
    if (!url || !base) return url;
    if (url.indexOf(base + '/') === 0) return url;
    if (url.charAt(0) === '/') return base + url;
    return base + '/' + url;
  }

  function processResult(result) {
    if (!result) return result;
    result.url = fixUrl(result.url);
    if (result.sub_results && result.sub_results.length) {
      for (var i = 0; i < result.sub_results.length; i++) {
        result.sub_results[i].url = fixUrl(result.sub_results[i].url);
      }
    }
    return result;
  }

  // 搜索词回流：Pagefind UI 的输入框停手 1.5 秒且词长 ≥ 2 时记一次 GoatCounter 事件
  var loggedTerms = {};
  function trackTerm(raw) {
    var q = String(raw || '').trim();
    if (q.length < 2 || loggedTerms[q]) return;
    loggedTerms[q] = 1;
    try {
      if (window.goatcounter && window.goatcounter.count) {
        window.goatcounter.count({ path: '/search?q=' + encodeURIComponent(q), title: 'search', event: true });
      }
    } catch (err) { /* 统计失败不影响检索 */ }
  }
  function setupTracking(initial) {
    var box = document.getElementById('pagefind-search');
    if (!box) return;
    var timer = null;
    box.addEventListener('input', function (ev) {
      var target = ev.target;
      if (!target || !target.value) return;
      var value = target.value;
      clearTimeout(timer);
      timer = setTimeout(function () { trackTerm(value); }, 1500);
    });
    if (initial) trackTerm(initial);
  }

  function init() {
    if (typeof PagefindUI === 'undefined') { showFallback(); return; }
    var ui;
    try {
      ui = new PagefindUI({
        element: '#pagefind-search',
        bundlePath: bundle,
        baseUrl: base + '/',
        showSubResults: true,
        showImages: false,
        autofocus: true,
        processResult: processResult,
        translations: {
          placeholder: i18n.placeholder,
          zero_results: i18n.zero_results,
          load_more: i18n.load_more,
          clear_search: i18n.clear_search,
          search_label: i18n.search_label
        }
      });
    } catch (err) {
      showFallback();
      return;
    }
    var q = '';
    try { q = new URLSearchParams(window.location.search).get('q') || ''; } catch (err) { q = ''; }
    if (q && typeof ui.triggerSearch === 'function') ui.triggerSearch(q);
    setupTracking(q);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
