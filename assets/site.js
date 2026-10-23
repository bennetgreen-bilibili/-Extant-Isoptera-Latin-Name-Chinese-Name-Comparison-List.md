/* 站点交互增强：目录侧栏 / 学名斜体 / 回到顶部 */
(function () {
  function setupToc() {
    var toc = document.getElementById('toc');
    if (!toc) return;
    var list = toc.nextElementSibling;
    while (list && list.tagName !== 'UL') list = list.nextElementSibling;
    if (!list) return;
    var content = document.querySelector('.content');
    if (!content) return;
    var aside = document.createElement('aside');
    aside.className = 'toc-side';
    var h = document.createElement('div');
    h.className = 'toc-heading';
    h.textContent = toc.textContent;
    aside.appendChild(h);
    var tree = list.cloneNode(true);
    aside.appendChild(tree);
    enhanceToc(tree);
    content.classList.add('layout-with-toc');
    content.insertBefore(aside, content.firstChild);
    toc.parentNode.removeChild(toc);
    list.parentNode.removeChild(list);
  }

  function enhanceToc(tree) {
    var items = tree.querySelectorAll('li');
    for (var i = 0; i < items.length; i++) {
      var li = items[i];
      var childUl = null, childA = null;
      for (var j = 0; j < li.children.length; j++) {
        var c = li.children[j];
        if (c.tagName === 'UL' && !childUl) childUl = c;
        else if (c.tagName === 'A' && !childA) childA = c;
      }
      if (!childUl || !childA) continue;
      var depth = 0, n = li;
      while ((n = n.parentElement)) { if (n.tagName === 'UL') depth++; }
      var collapsed = depth >= 3;
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'toc-toggle';
      btn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
      btn.setAttribute('aria-label', '展开/收起');
      btn.textContent = collapsed ? '▸' : '▾';
      if (collapsed) li.classList.add('collapsed');
      li.insertBefore(btn, childA);
      btn.addEventListener('click', (function (li, btn) {
        return function (ev) {
          ev.preventDefault();
          ev.stopPropagation();
          var isCollapsed = li.classList.toggle('collapsed');
          btn.setAttribute('aria-expanded', isCollapsed ? 'false' : 'true');
          btn.textContent = isCollapsed ? '▸' : '▾';
        };
      })(li, btn));
    }
  }

  function italicizeTaxa() {
    if (!document.body.classList.contains('is-list-page')) return;
    var content = document.querySelector('.content');
    if (!content) return;
    var ps = content.querySelectorAll('p');
    var re = /^(\*?)([A-Z][a-z]+(?:\s[a-z][a-z\-]+)?)(\s[\u4e00-\u9fff])/;
    for (var i = 0; i < ps.length; i++) {
      var p = ps[i];
      if (p.querySelector('a')) continue;
      var t = p.textContent;
      var m = t.match(re);
      if (!m) continue;
      p.classList.add('taxa-item');
      var node = p.firstChild;
      while (node && node.nodeType !== 3) node = node.nextSibling;
      if (!node) continue;
      var full = node.textContent;
      var idx = m[1].length + m[2].length;
      node.textContent = full.slice(idx);
      if (m[1] === '*') {
        var star = document.createElement('span');
        star.className = 'type-mark';
        star.textContent = '*';
        p.insertBefore(star, node);
      }
      var em = document.createElement('i');
      em.className = 'latin';
      em.textContent = m[2];
      p.insertBefore(em, node);
    }
  }

  function setupBackTop() {
    var btn = document.getElementById('back-top');
    if (!btn) return;
    btn.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
    window.addEventListener('scroll', function () {
      var on = window.scrollY > 400;
      btn.style.opacity = on ? '1' : '0';
      btn.style.pointerEvents = on ? 'auto' : 'none';
    });
  }

  function ready(fn) { if (document.readyState !== 'loading') fn(); else document.addEventListener('DOMContentLoaded', fn); }
  ready(function () { setupToc(); italicizeTaxa(); setupBackTop(); });
})();
