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
    aside.appendChild(list.cloneNode(true));
    content.classList.add('layout-with-toc');
    content.insertBefore(aside, content.firstChild);
    toc.parentNode.removeChild(toc);
    list.parentNode.removeChild(list);
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
