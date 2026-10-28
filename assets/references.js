/*
  参考文献页交互（名录页 /list/、/en/list/、/es/list/ 底部）。
  纯原生 JS，无框架、无依赖：
    1. [data-refs-copy] 按钮 → 复制目标元素（CSS 选择器）的纯文本；
       navigator.clipboard 优先，非安全上下文/老浏览器退回 textarea + execCommand。
    2. #refs-export-csl → 拉取 /data/references.json，把每条已生成的 CSL-JSON 汇成数组下载。
       该按钮在 HTML 里是 hidden，只有本脚本成功绑定后才显示：禁用 JS 时页面不会有死按钮。
  没有 JS 时：引用文本、DOI / Crossref 链接、APA / Vancouver / BibTeX / RIS（<details> 内）全部可读可选中。
*/
(function () {
  'use strict';

  // 防重复执行：若模板与布局同时引入了本文件，只初始化一次
  // （否则复制会触发两次、导出会下载两份）
  if (window.__refsPageInit) return;
  window.__refsPageInit = true;

  var COPIED_MS = 1800;

  function currentText(el) {
    if (!el) return '';
    // 只去掉结尾换行，保留 RIS 的 "ER  - " 这类尾随空格
    return el.textContent.replace(/[\r\n]+$/, '');
  }

  function legacyCopy(text) {
    return new Promise(function (resolve, reject) {
      var area = document.createElement('textarea');
      area.value = text;
      area.setAttribute('readonly', 'readonly');
      area.style.position = 'fixed';
      area.style.top = '-1000px';
      area.style.left = '-1000px';
      area.style.opacity = '0';
      document.body.appendChild(area);
      area.select();
      area.setSelectionRange(0, area.value.length);
      var ok = false;
      try {
        ok = document.execCommand('copy');
      } catch (err) {
        ok = false;
      }
      document.body.removeChild(area);
      if (ok) resolve();
      else reject(new Error('copy-failed'));
    });
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).catch(function () {
        return legacyCopy(text);
      });
    }
    return legacyCopy(text);
  }

  function flash(button) {
    var copied = button.getAttribute('data-refs-copied') || 'Copied';
    if (!button.getAttribute('data-refs-label')) {
      button.setAttribute('data-refs-label', button.textContent);
    }
    button.textContent = copied;
    button.classList.add('is-copied');
    window.clearTimeout(button._refsTimer);
    button._refsTimer = window.setTimeout(function () {
      button.textContent = button.getAttribute('data-refs-label');
      button.classList.remove('is-copied');
    }, COPIED_MS);
  }

  function onClick(event) {
    var button = event.target.closest ? event.target.closest('[data-refs-copy]') : null;
    if (!button) return;
    var selector = button.getAttribute('data-refs-copy');
    var source = selector ? document.querySelector(selector) : null;
    if (!source) return;
    event.preventDefault();
    copyText(currentText(source)).then(function () {
      flash(button);
    }).catch(function () {
      /* 复制失败时保持原状，文本仍可手动选中 */
    });
  }

  function setupExport() {
    var button = document.getElementById('refs-export-csl');
    if (!button || typeof window.fetch !== 'function' || typeof window.Blob !== 'function') return;
    button.hidden = false;
    button.addEventListener('click', function () {
      var url = button.getAttribute('data-refs-export');
      var filename = button.getAttribute('data-refs-filename') || 'references.csl.json';
      if (!url) return;
      button.disabled = true;
      window.fetch(url, { credentials: 'same-origin' }).then(function (response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return response.json();
      }).then(function (payload) {
        var items = ((payload && payload.references) || []).map(function (item) {
          return item.csl;
        }).filter(Boolean);
        var blob = new Blob([JSON.stringify(items, null, 2)], { type: 'application/json;charset=utf-8' });
        var href = URL.createObjectURL(blob);
        var link = document.createElement('a');
        link.href = href;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.setTimeout(function () { URL.revokeObjectURL(href); }, 4000);
        flash(button);
      }).catch(function () {
        /* 失败时静默：静态链接 data/references.json 仍可下载 */
      }).then(function () {
        button.disabled = false;
      });
    });
  }

  function ready(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  ready(function () {
    document.addEventListener('click', onClick);
    setupExport();
  });
})();
