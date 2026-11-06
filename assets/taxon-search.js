/* 中转页局部检索（科 / 亚科 / 属页）
   只在本页登记的分类单元里过滤 /search-index.json：
   每个条目带 h 字段（种/亚种的 h 是所属属的锚点 id），与 .taxon-search 的
   data-anchors 求交即为「本页范围」。索引仍由 .github/workflows/build_search_index.py 生成，
   本脚本只在首次输入时按需加载一次，不改动名录页的 assets/search.js。

   检索字段（索引字段名见 build_search_index.py 头部注释）：
     l 拉丁学名 / z 中文名 / s 次异名 —— 名字类，命中优先
     dz 分布（中文）/ de 分布（英文）/ t 模式产地 / sl 异名模式产地 —— 产地类
   多个词（空格分隔）按 AND 处理，每个词都要命中某一个字段；
   结果里给出命中字段的标签与带高亮的片段。 */
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

  /* 产地类字段：用于匹配与片段展示；顺序即同等命中时的展示优先级 */
  var CONTEXT_FIELDS = [
    { key: 'dz', label: '分布' },
    { key: 't',  label: '模式产地' },
    { key: 'sl', label: '异名产地' },
    { key: 'de', label: '分布（英）' }
  ];

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

  /* 在 text 里给每个 token 的出现位置加 <mark>（大小写不敏感，保留原文大小写） */
  function highlight(text, tokens){
    var src = String(text == null ? '' : text);
    var low = src.toLowerCase();
    var spans = [], k, t, idx, from;
    for (k = 0; k < tokens.length; k++){
      t = tokens[k];
      if (!t) continue;
      from = 0;
      while ((idx = low.indexOf(t, from)) >= 0){
        spans.push([idx, idx + t.length]);
        from = idx + t.length;
      }
    }
    if (!spans.length) return esc(src);
    spans.sort(function(p, q){ return p[0] - q[0] || p[1] - q[1]; });
    var merged = [spans[0]];
    for (k = 1; k < spans.length; k++){
      var last = merged[merged.length - 1];
      if (spans[k][0] <= last[1]) last[1] = Math.max(last[1], spans[k][1]);
      else merged.push(spans[k]);
    }
    var html = '', pos = 0;
    for (k = 0; k < merged.length; k++){
      html += esc(src.slice(pos, merged[k][0])) + '<mark>' + esc(src.slice(merged[k][0], merged[k][1])) + '</mark>';
      pos = merged[k][1];
    }
    return html + esc(src.slice(pos));
  }

  /* 截取命中词附近的片段，两端视情况加省略号 */
  function snippet(text, tokens){
    var src = String(text == null ? '' : text);
    var low = src.toLowerCase(), at = -1, hitLen = 0, k, idx;
    for (k = 0; k < tokens.length; k++){
      if (!tokens[k]) continue;
      idx = low.indexOf(tokens[k]);
      if (idx >= 0 && (at < 0 || idx < at)){ at = idx; hitLen = tokens[k].length; }
    }
    if (at < 0) return esc(src);
    var start = Math.max(0, at - 22);
    var end = Math.min(src.length, at + hitLen + 30);
    if (start > 0){ var sp = src.slice(start, at).search(/[、,;：:；\s]/); if (sp >= 0) start += sp + 1; }
    if (end < src.length){
      // 在窗口末尾找分隔符断开，但断点离命中词太近（< 12 字）时宁可保留整段窗口
      var ep = src.slice(at + hitLen, end).search(/[、,;：:；\s]/);
      if (ep >= 12) end = at + hitLen + ep;
    }
    return (start > 0 ? '…' : '') + highlight(src.slice(start, end), tokens) + (end < src.length ? '…' : '');
  }

  /* 单词命中：返回 {score, key}，score 越小越贴题；没命中返回 null */
  function hitOne(e, qn, qc, ascii){
    var l = norm(e.l), z = norm(e.z), s = norm(e.s || '');
    if (l === qn || z === qn || s === qn) return { score: 0, key: l === qn ? 'l' : (z === qn ? 'z' : 's') };
    var li = l.indexOf(qn), zi = z.indexOf(qn), si = s.indexOf(qn);
    if (li === 0 || zi === 0) return { score: 1, key: li === 0 ? 'l' : 'z' };
    if (li > 0 || zi > 0 || si >= 0) return { score: 2, key: li > 0 ? 'l' : (zi > 0 ? 'z' : 's') };
    if (ascii && qc.length >= 3){
      // 拉丁学名的紧凑匹配（例如 amitermesabruptus）
      var lc = compact(l);
      if (lc === qc) return { score: 3, key: 'l' };
      if (lc.indexOf(qc) === 0) return { score: 4, key: 'l' };
      if (lc.indexOf(qc) > 0) return { score: 5, key: 'l' };
    }
    var best = null;
    for (var i = 0; i < CONTEXT_FIELDS.length; i++){
      var f = CONTEXT_FIELDS[i], text = norm(e[f.key]);
      if (!text) continue;
      var at = text.indexOf(qn);
      if (at < 0) continue;
      var score = at === 0 ? 6 : 7;
      if (!best || score < best.score) best = { score: score, key: f.key };
      if (score === 6) break;
    }
    return best;
  }

  function render(list, raw, tokens){
    if (!list.length){
      results.innerHTML = '<li class="taxon-search-empty">本范围内没有匹配的分类单元 · 可试试中文名、拉丁学名，'
        + '或分布国 / 地区（如 澳大利亚、云南、Brazil） · '
        + '<a href="' + esc(SEARCH_PAGE + '?q=' + encodeURIComponent(raw)) + '">在全站全文搜索中查找</a></li>';
      if (status) status.textContent = '0 个匹配';
      show(true);
      return;
    }
    var html = '';
    for (var i = 0; i < list.length; i++){
      var item = list[i], e = item.e;
      html += '<li><a href="' + esc(href(e)) + '"><span class="rank">' + esc(e.r) + '</span>'
        + highlight(e.z, tokens) + ' <span class="latin">' + highlight(e.l, tokens) + '</span>'
        + (e.f ? ' <span class="fam">· ' + esc(e.f) + '</span>' : '') + '</a>';
      if (item.ctx){
        html += '<div class="taxon-search-snippet"><span class="taxon-search-field">'
          + esc(item.ctx.label) + '</span>' + snippet(e[item.ctx.key], tokens) + '</div>';
      }
      html += '</li>';
    }
    results.innerHTML = html;
    if (status) status.textContent = list.length >= LIMIT
      ? '显示前 ' + LIMIT + ' 个匹配（名字 / 分布 / 模式产地），输入更精确的词可缩小范围'
      : list.length + ' 个匹配（名字 / 分布 / 模式产地）';
    show(true);
  }

  function search(q){
    var raw = String(q == null ? '' : q).trim();
    if (!raw){ results.innerHTML = ''; show(false); return; }
    if (!data){ pending = raw; load(); return; }
    var tokens = raw.toLowerCase().split(/[\s\u3000]+/);
    var clean = [], k;
    for (k = 0; k < tokens.length; k++){ if (tokens[k]) clean.push(tokens[k]); }
    tokens = clean;
    if (!tokens.length){ results.innerHTML = ''; show(false); return; }

    var prepared = [], j;
    for (j = 0; j < tokens.length; j++){
      prepared.push({ qn: tokens[j], qc: compact(tokens[j]), ascii: /^[a-z][a-z0-9.\-'’]*$/.test(tokens[j]) });
    }

    var scored = [];
    for (var i = 0; i < data.length; i++){
      var e = data[i];
      if (!scope[e.h]) continue;
      var total = 0, worst = 0, ctx = null, ok = true;
      for (j = 0; j < prepared.length; j++){
        var p = prepared[j], h = hitOne(e, p.qn, p.qc, p.ascii);
        if (!h){ ok = false; break; }
        total += h.score;
        if (h.score > worst) worst = h.score;
        if (h.score >= 6 && !ctx){
          for (k = 0; k < CONTEXT_FIELDS.length; k++){
            if (CONTEXT_FIELDS[k].key === h.key){ ctx = CONTEXT_FIELDS[k]; break; }
          }
        }
      }
      if (!ok) continue;
      scored.push({ worst: worst, total: total, ctx: ctx, len: (e.l || '').length + (e.z || '').length, e: e });
    }
    scored.sort(function(a, b){
      return a.worst - b.worst || a.total - b.total || a.len - b.len || (a.e.l < b.e.l ? -1 : 1);
    });
    render(scored.slice(0, LIMIT), raw, tokens);
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
