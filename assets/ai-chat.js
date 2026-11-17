/* 站点 AI 对话（Cloudflare AI Search 的 chat-bubble-snippet）
 *
 * 职责：
 *   1. 页面空闲时才注入官方 search-snippet.es.js（首屏不请求第三方，也不用 IntersectionObserver 之类的小把戏）；
 *   2. 注入后按站点主题（<html data-theme>）给气泡设置 theme，并跟随主题切换；
 *   3. 接管 [data-ai-chat-open] 按钮（/search/ 页顶部入口），点一下打开气泡并把状态写在 [data-ai-chat-status]。
 *
 * 气泡元素本身由 _includes/ai-chat.html 输出；_data/ai_chat.yml 的 api_url 留空时
 * 模板既不输出气泡也不输出本脚本，所以这里的空值判断只是防御。
 */
(function () {
  'use strict';

  var script = document.currentScript;
  if (!script) {
    return;
  }

  var API_URL = String(script.getAttribute('data-api-url') || '').trim();
  var SCRIPT_SRC = String(script.getAttribute('data-script-src') || '').trim();
  var LOADING_TEXT = script.getAttribute('data-loading') || '';
  var ERROR_TEXT = script.getAttribute('data-error') || '';

  var bubble = document.querySelector('chat-bubble-snippet');
  if (!bubble || !API_URL || !SCRIPT_SRC) {
    return;
  }

  var booting = null;
  var loaded = false;
  var triggeredButtons = [];

  /* 官方组件在 shadow DOM 里用 :host(:not([theme="dark"])) 定义浅色变量、
     深色变量只写在 @media (prefers-color-scheme: dark) 里；theme="dark" 因此
     无法在浅色系统上强制深色（变量会缺失）。站点是浅色就给 "light"，
     深色交给媒体查询，用 "auto"。 */
  function siteTheme() {
    return document.documentElement.getAttribute('data-theme') === 'dark' ? 'auto' : 'light';
  }

  function syncTheme() {
    bubble.setAttribute('theme', siteTheme());
  }

  function say(message) {
    var nodes = document.querySelectorAll('[data-ai-chat-status]');
    for (var i = 0; i < nodes.length; i += 1) {
      var node = nodes[i];
      node.textContent = message;
      node.hidden = !message;
    }
  }

  function markBusy(busy) {
    for (var i = 0; i < triggeredButtons.length; i += 1) {
      if (busy) {
        triggeredButtons[i].setAttribute('aria-busy', 'true');
      } else {
        triggeredButtons[i].removeAttribute('aria-busy');
      }
    }
  }

  function loadModule() {
    var scriptEl = document.createElement('script');
    scriptEl.type = 'module';
    scriptEl.src = SCRIPT_SRC;
    scriptEl.crossOrigin = 'anonymous';
    document.head.appendChild(scriptEl);

    var wait = window.customElements && typeof window.customElements.whenDefined === 'function'
      ? window.customElements.whenDefined('chat-bubble-snippet')
      : Promise.reject(new Error('customElements.whenDefined is unavailable'));

    return new Promise(function (resolve, reject) {
      var settled = false;
      var timer = window.setTimeout(function () {
        if (!settled) {
          settled = true;
          reject(new Error('timed out waiting for chat-bubble-snippet'));
        }
      }, 20000);

      wait.then(function () {
        if (settled) {
          return;
        }
        settled = true;
        window.clearTimeout(timer);
        resolve();
      }, function (err) {
        if (settled) {
          return;
        }
        settled = true;
        window.clearTimeout(timer);
        reject(err);
      });

      scriptEl.addEventListener('error', function () {
        if (!settled) {
          settled = true;
          window.clearTimeout(timer);
          reject(new Error('failed to load ' + SCRIPT_SRC));
        }
      });
    });
  }

  function boot() {
    if (booting) {
      return booting;
    }
    syncTheme();
    booting = loadModule().then(function () {
      loaded = true;
      syncTheme();
    }, function (err) {
      booting = null;
      throw err;
    });
    return booting;
  }

  function openChat(button) {
    if (button && triggeredButtons.indexOf(button) === -1) {
      triggeredButtons.push(button);
    }
    if (!loaded) {
      say(LOADING_TEXT);
      markBusy(true);
    }
    boot().then(function () {
      markBusy(false);
      if (!bubble.isExpanded) {
        bubble.toggleChat();
      }
      say('');
    }, function () {
      markBusy(false);
      say(ERROR_TEXT);
    });
  }

  document.addEventListener('click', function (ev) {
    var button = ev.target && ev.target.closest ? ev.target.closest('[data-ai-chat-open]') : null;
    if (!button) {
      return;
    }
    ev.preventDefault();
    openChat(button);
  });

  if (window.MutationObserver) {
    new MutationObserver(function () {
      if (loaded) {
        syncTheme();
      }
    }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  }

  /* 页面空闲时预热：注入官方脚本，让气泡尽快可用；失败保持安静，
     真正的错误提示留给用户点击按钮的那一刻（see openChat）。 */
  function warmUp() {
    boot().catch(function () {
      /* 预热失败不打扰用户；点击时 boot() 会重试并显示错误文案 */
    });
  }

  /* 省流量模式不预热：首屏不请求第三方，点开时再加载（点击路径同样调 boot()）。 */
  var conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  if (conn && conn.saveData) {
    return;
  }

  if ('requestIdleCallback' in window) {
    window.requestIdleCallback(warmUp, { timeout: 2500 });
  } else if (document.readyState === 'complete') {
    window.setTimeout(warmUp, 800);
  } else {
    window.addEventListener('load', function () {
      window.setTimeout(warmUp, 800);
    });
  }}());
