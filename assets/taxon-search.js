/* 中转页局部检索（科 / 亚科 / 属页）
   只在本页登记的分类单元里过滤 /search-index.json：
   每个条目带 h 字段（种/亚种的 h 是所属属的锚点 id），与 .taxon-search 的
   data-anchors 求交即为「本页范围」。索引仍由 .github/workflows/build_search_index.py 生成，
   本脚本只在首次输入时按需加载一次，不改动名录页的 assets/search.js。 */
(function(){
  var box = document.querySelector('.taxon-search');
  if (!box) return;
  var input = box.querySelector('.taxon-search-input');
  var results = box.querySelector('.taxon-search-results');
  var status = box.querySelector('.taxon-search-status');
  if (!input || !results) return;

  var anchors = (box.getAttribute('data-anchors') || '').split(',');
  var scope = Object.create(null);
  for (var i = 0; i < anchors.length; i++){
    var a = anchors[i].trim();
    if (a) scope[a] = 1;
  }
  var INDEX = box.getAttribute('data-index') || '/search-index.json';
  var SEARCH_PAGE = box.getAttribute('data-search-page') || '/search/';
  var BASE = INDEX.replace(/\/search-index\.json$/, '');
  var LIMIT = 40;

  var data = null, loading = false, pending = null;

  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function norm(s){ return String(s == null ? '' : s).toLowerCase(); }
  function compact(s){ return String(s || '').replace(/[^a-z0-9]/g, ''); }

  function load(){
    if (data || loading) return;
    loading = true;
    fetch(INDEX).then(function(r){ return r.json(); }).then(function(arr){
      data = arr; loading = false;
      if (pending != null){ var v = pending; pending = null; search(v); }
    }).catch(function(){ loading = false; });
  }

  function href(e){
    if ((e.r === '种' || e.r === '亚种') && e.p) return BASE + '/species/' + encodeURIComponent(e.p) + '/';
    if (e.r === '属') return BASE + '/genus/' + encodeURIComponent(e.h) + '/';
    if (e.r === '亚科') return BASE + '/subfamily/' + encodeURIComponent(e.h) + '/';
    if (e.r === '科') return BASE + '/family/' + encodeURIComponent(e.h) + '/';
    return BASE + '/list/#' + encodeURIComponent(e.h);
  }

  function show(open){
    results.hidden = !open;
    if (status) status.hidden = !open;
    input.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  function render(list, raw){
    if (!list.length){
      results.innerHTML = '<li class="taxon-search-empty">本范围内没有匹配的分类单元 · '
        + '<a href="' + esc(SEARCH_PAGE + '?q=' + encodeURIComponent(raw)) + '">在全站全文搜索中查找</a></li>';
      if (status) status.textContent = '0 个匹配';
      show(true);
      return;
    }
    var html = '';
    for (var i = 0; i < list.length; i++){
      var e = list[i];
      html += '<li><a href="' + esc(href(e)) + '"><span class="rank">' + esc(e.r) + '</span>'
        + esc(e.z) + ' <span class="latin">' + esc(e.l) + '</span>'
        + (e.f ? ' <span class="fam">· ' + esc(e.f) + '</span>' : '') + '</a></li>';
    }
    results.innerHTML = html;
    if (status) status.textContent = list.length >= LIMIT
      ? '显示前 ' + LIMIT + ' 个匹配，输入更精确的词可缩小范围'
      : list.length + ' 个匹配';
    show(true);
  }

  function search(q){
    var raw = String(q == null ? '' : q).trim();
    if (!raw){ results.innerHTML = ''; show(false); return; }
    if (!data){ pending = raw; load(); return; }
    var qn = norm(raw), qc = compact(qn);
    var asciiQuery = /^[a-z][a-z0-9\s.\-'’]*$/.test(qn);
    var scored = [];
    for (var i = 0; i < data.length; i++){
      var e = data[i];
      if (!scope[e.h]) continue;
      var l = norm(e.l), z = norm(e.z), s = norm(e.s || '');
      var li = l.indexOf(qn), zi = z.indexOf(qn), si = s.indexOf(qn);
      var score = -1;
      if (li >= 0 || zi >= 0 || si >= 0){
        if (l === qn || z === qn || s === qn) score = 0;
        else if (li === 0 || zi === 0) score = 1;
        else score = 2;
      } else if (asciiQuery && qc.length >= 3){
        // 拉丁学名整个属名的紧凑匹配（例如 amitermesabruptus）
        var lc = compact(l);
        if (lc === qc) score = 3;
        else if (lc.indexOf(qc) === 0) score = 4;
        else if (lc.indexOf(qc) > 0) score = 5;
      }
      if (score < 0) continue;
      scored.push({ score: score, len: l.length + z.length, e: e });
    }
    scored.sort(function(a, b){ return a.score - b.score || a.len - b.len || (a.e.l < b.e.l ? -1 : 1); });
    render(scored.slice(0, LIMIT), raw);
  }

  var timer;
  input.addEventListener('input', function(){
    clearTimeout(timer);
    var v = input.value;
    timer = setTimeout(function(){ search(v); }, 140);
  });
  input.addEventListener('focus', function(){ load(); if (input.value) search(input.value); });
  input.addEventListener('keydown', function(ev){
    if (ev.key === 'Escape'){ show(false); input.blur(); return; }
    if (ev.key === 'Enter'){
      var first = results.querySelector('a');
      if (first){ ev.preventDefault(); window.location.href = first.getAttribute('href'); }
    }
  });
  document.addEventListener('click', function(ev){
    if (!results.hidden && !ev.target.closest('.taxon-search')) show(false);
  });
})();
