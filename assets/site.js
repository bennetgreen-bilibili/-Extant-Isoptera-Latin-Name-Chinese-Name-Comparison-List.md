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
    var wrap = content.parentNode;
    wrap.classList.add('has-toc');
    wrap.insertBefore(aside, content);
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
      if (!childA) continue;
      var row = document.createElement('div');
      row.className = 'toc-row';
      if (childUl) {
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
        btn.addEventListener('click', (function (li, btn) {
          return function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var isCollapsed = li.classList.toggle('collapsed');
            btn.setAttribute('aria-expanded', isCollapsed ? 'false' : 'true');
            btn.textContent = isCollapsed ? '▸' : '▾';
          };
        })(li, btn));
        row.appendChild(btn);
      } else {
        var sp = document.createElement('span');
        sp.className = 'toc-spacer';
        sp.setAttribute('aria-hidden', 'true');
        row.appendChild(sp);
      }
      li.insertBefore(row, childA);
      row.appendChild(childA);
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

  function copyText(text, done) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { legacyCopy(text, done); });
      return;
    }
    legacyCopy(text, done);
  }

  function legacyCopy(text, done) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.top = '-1000px';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); done(); } catch (e) { /* 剪贴板不可用：保持原样 */ }
    document.body.removeChild(ta);
  }

  function setupCitations() {
    var blocks = document.querySelectorAll('.cite-block');
    for (var i = 0; i < blocks.length; i++) {
      (function (block) {
        var pre = block.querySelector('.cite-text');
        var btn = block.querySelector('.cite-copy');
        if (!pre || !btn) return;
        var label = btn.getAttribute('data-label') || btn.textContent;
        var copied = btn.getAttribute('data-copied-label') || label;
        btn.addEventListener('click', function () {
          copyText(pre.textContent, function () {
            btn.textContent = copied;
            btn.classList.add('is-copied');
            setTimeout(function () { btn.textContent = label; btn.classList.remove('is-copied'); }, 1600);
          });
        });
      })(blocks[i]);
    }
  }

  /* 打印时自动展开「引用本种」区块，避免 <details> 折叠内容打印不出来 */
  function openCiteDetailsForPrint() {
    var details = document.querySelectorAll('details.species-cite');
    for (var i = 0; i < details.length; i++) details[i].open = true;
  }

  function ready(fn) { if (document.readyState !== 'loading') fn(); else document.addEventListener('DOMContentLoaded', fn); }
  ready(function () {
    setupToc(); italicizeTaxa(); setupBackTop(); setupCitations();
    window.addEventListener('beforeprint', openCiteDetailsForPrint);
  });
})();
