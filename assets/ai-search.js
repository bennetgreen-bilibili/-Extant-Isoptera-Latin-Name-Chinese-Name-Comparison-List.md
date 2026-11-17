/* AI 搜索（Cloudflare AI Search）按需接入：全局搜索浮层与 /search/ 页面共用。
   1. 首屏不请求第三方：第一次点「AI 搜索」时才加载 search.ai.cloudflare.com 的
      search-snippet.es.js，随后创建 <search-modal-snippet> 并复用同一个实例。
   2. 键盘归本站浮层：assets/search-widget.js 在捕获阶段处理 Ctrl/⌘+K 并截断事件，
      官方弹窗虽然也监听同一个组合键，但拿不到事件，不会出现两个界面同时打开。
   3. 主题：弹窗用官方 theme 属性。本站为浅色时强制 light（系统是深色也不跟），
      本站为深色时留 auto——v0.0.25 的 dark 主题只在系统偏好为深色时生效，硬写
      theme="dark" 在浅色系统下反而没有配色。
   4. 文案（占位、加载、失败）由模板按 _data/i18n.yml 三语传入，不在 JS 里写死。
   5. 停用方式：_data/ai_search.yml 的 api_url 留空，模板就不输出这段脚本。 */
(function () {
  var script = document.currentScript;
  if (!script) return;

  var attr = function (name, fallback) {
    var v = script.getAttribute(name);
    return v == null || v === '' ? fallback : v;
  };

  var API = attr('data-api-url', '');
  var SRC = attr('data-script-src', '');
  var MAX = parseInt(attr('data-max-results', '10'), 10) || 10;
  var PLACEHOLDER = attr('data-placeholder', '');
  var T = {
    loading: attr('data-loading', 'Loading…'),
    error: attr('data-error', 'AI search failed to load.')
  };
  if (!API || !SRC) return;

  var statusNodes = document.querySelectorAll('[data-ai-search-status]');
  var triggers = document.querySelectorAll('[data-ai-search-open]');
  if (!triggers.length) return;

  var elems = null;
  var pending = null;
  var tracked = false;

  function say(msg) {
    for (var i = 0; i < statusNodes.length; i++) {
      var node = statusNodes[i];
      node.textContent = msg || '';
      node.hidden = !msg;
    }
  }

  function siteTheme() {
    return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  }

  // 见文件头第 3 点：只有浅色才需要强制，深色交给 auto。
  function snippetTheme() {
    return siteTheme() === 'light' ? 'light' : 'auto';
  }

  function track() {
    if (tracked) return;
    tracked = true;
    try {
      if (window.goatcounter && window.goatcounter.count) {
        window.goatcounter.count({ path: '/ai-search', title: 'ai-search', event: true });
      }
    } catch (e) { /* 统计失败不影响搜索 */ }
  }

  function loadModule() {
    if (typeof customElements === 'undefined' || !customElements.whenDefined) {
      return Promise.reject(new Error('custom elements unsupported'));
    }
    return new Promise(function (resolve, reject) {
      var tag = document.createElement('script');
      tag.type = 'module';
      tag.src = SRC;
      tag.crossOrigin = 'anonymous';
      tag.onload = function () { resolve(); };
      tag.onerror = function () { reject(new Error('search-snippet module failed to load')); };
      document.head.appendChild(tag);
    }).then(function () {
      return Promise.race([
        customElements.whenDefined('search-modal-snippet'),
        new Promise(function (_, reject) {
          window.setTimeout(function () { reject(new Error('search-modal-snippet not defined')); }, 20000);
        })
      ]);
    });
  }

  function ensure() {
    if (elems) return Promise.resolve(elems);
    if (pending) return pending;
    say(T.loading);
    pending = loadModule().then(function () {
      var node = document.createElement('search-modal-snippet');
      node.setAttribute('api-url', API);
      node.setAttribute('theme', snippetTheme());
      node.setAttribute('max-results', String(MAX));
      if (PLACEHOLDER) node.setAttribute('placeholder', PLACEHOLDER);
      document.body.appendChild(node);
      elems = node;
      say('');
      return node;
    }).catch(function (err) {
      pending = null;
      say(T.error);
      throw err;
    });
    return pending;
  }

  function open(query) {
    return ensure().then(function (node) {
      node.setAttribute('theme', snippetTheme());
      // 先开官方弹窗（它自己锁滚动），再关本站浮层：这样加载/失败提示留在浮层
      // 底部的状态行里，访客看得见；两套滚动锁也不会互相覆盖。
      node.open();
      closeOverlay();
      if (query) {
        try { node.search(query); } catch (e) { /* 输入框已聚焦，用户可自行输入 */ }
      }
      track();
    }).catch(function () {
      /* 失败提示已由 ensure() 写进状态行 */
    });
  }

  function queryFromOverlay() {
    var overlay = document.getElementById('search-overlay');
    var input = document.getElementById('search-overlay-input');
    if (!overlay || overlay.hidden) return '';
    return input ? String(input.value || '').trim() : '';
  }

  // 取完查询词再关浮层，把 body 的滚动锁交还给页面（官方弹窗此时已自己锁上）。
  function closeOverlay() {
    var overlay = document.getElementById('search-overlay');
    if (!overlay || overlay.hidden) return;
    var closeBtn = document.getElementById('search-overlay-close');
    if (closeBtn) closeBtn.click();
    else {
      overlay.hidden = true;
      document.body.classList.remove('search-overlay-open');
    }
  }

  function onTrigger(ev) {
    var btn = ev.currentTarget;
    var query = queryFromOverlay();
    if (btn && btn.setAttribute) btn.setAttribute('aria-busy', 'true');
    open(query).then(function () {
      if (btn && btn.removeAttribute) btn.removeAttribute('aria-busy');
    });
  }

  for (var i = 0; i < triggers.length; i++) {
    triggers[i].addEventListener('click', onTrigger);
  }
})();
