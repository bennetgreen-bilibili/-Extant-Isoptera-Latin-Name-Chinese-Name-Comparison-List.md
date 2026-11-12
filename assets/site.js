/* 站点交互增强：目录侧栏 / 学名斜体 / 回到顶部 */
(function () {
  /* 目录侧栏的文案（按页面语言） */
  var TOC_TITLES = { zh: '目录', en: 'Contents', es: 'Índice' };
  var TOC_TOGGLE_LABELS = { zh: '展开/收起', en: 'Expand/collapse', es: 'Expandir/contraer' };

  function pageLang() {
    var lang = (document.documentElement.getAttribute('lang') || '').toLowerCase();
    if (lang.indexOf('en') === 0) return 'en';
    if (lang.indexOf('es') === 0) return 'es';
    return 'zh';
  }

  /* 标题自身没有 id 时（如 kramdown 生成的锚点不同）按文本补一个 */
  function ensureHeadingId(heading) {
    if (heading.id) return heading.id;
    var text = (heading.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase();
    var id = text.replace(/[^0-9a-z\u00c0-\uffff\-]+/g, '-').replace(/^-+|-+$/g, '');
    if (!id) id = 'section';
    var base = id, n = 2;
    while (document.getElementById(id)) { id = base + '-' + n; n++; }
    heading.id = id;
    return id;
  }

  /* 按标题层级搭出嵌套目录树：li > a + ul */
  function buildTocTree(headings) {
    var root = document.createElement('ul');
    var stack = [{ level: 1, ul: root }];
    for (var i = 0; i < headings.length; i++) {
      var heading = headings[i];
      var level = parseInt(heading.tagName.charAt(1), 10);
      while (stack.length > 1 && stack[stack.length - 1].level >= level) stack.pop();
      var top = stack[stack.length - 1];
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = '#' + ensureHeadingId(heading);
      a.textContent = (heading.textContent || '').replace(/\s+/g, ' ').trim();
      var sub = document.createElement('ul');
      li.appendChild(a);
      li.appendChild(sub);
      top.ul.appendChild(li);
      stack.push({ level: level, ul: sub });
    }
    /* 没有子项的 UL 去掉，否则会多出空白的折叠按钮 */
    var empty = root.querySelectorAll('ul');
    for (var k = empty.length - 1; k >= 0; k--) {
      if (!empty[k].children.length) empty[k].parentNode.removeChild(empty[k]);
    }
    return root;
  }

  var tocAside = null;

  /* 页面顶部有横幅时吸顶导航不在视口顶端：目录顶边跟着导航底边走，避免被导航压住 */
  function syncTocTop() {
    if (!tocAside) return;
    if (window.matchMedia && window.matchMedia('(max-width:1080px)').matches) {
      tocAside.style.top = '';
      tocAside.style.maxHeight = '';
      return;
    }
    var nav = document.querySelector('.site-nav');
    var bottom = nav ? nav.getBoundingClientRect().bottom : 0;
    var top = Math.max(0, Math.round(bottom)) + 16;
    tocAside.style.top = top + 'px';
    tocAside.style.maxHeight = 'calc(100vh - ' + (top + 16) + 'px)';
  }

  function setupToc() {
    if (!document.body.classList.contains('is-list-page')) return;
    var content = document.querySelector('.content');
    if (!content) return;
    var headings = content.querySelectorAll('h2, h3, h4, h5, h6');
    if (headings.length < 3) return;
    var lang = pageLang();
    var aside = document.createElement('aside');
    aside.className = 'toc-side';
    aside.setAttribute('aria-label', TOC_TITLES[lang]);
    aside.setAttribute('data-pagefind-ignore', '');
    var h = document.createElement('div');
    h.className = 'toc-heading';
    h.textContent = TOC_TITLES[lang];
    aside.appendChild(h);
    var tree = buildTocTree(headings);
    aside.appendChild(tree);
    enhanceToc(tree, lang);
    var wrap = content.parentNode;
    wrap.classList.add('has-toc');
    wrap.insertBefore(aside, content);
    tocAside = aside;
    syncTocTop();
    var pending = false;
    function onShift() {
      if (pending) return;
      pending = true;
      window.requestAnimationFrame(function () { pending = false; syncTocTop(); });
    }
    window.addEventListener('scroll', onShift, { passive: true });
    window.addEventListener('resize', onShift);
  }

  function enhanceToc(tree, lang) {
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
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'toc-toggle';
        btn.setAttribute('aria-expanded', 'true');
        btn.setAttribute('aria-label', TOC_TOGGLE_LABELS[lang] || TOC_TOGGLE_LABELS.zh);
        btn.textContent = '▾';
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
