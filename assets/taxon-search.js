/* 中转页局部检索（科 / 亚科 / 属页）
   与 /search/ 的全文搜索共用同一份 Pagefind 索引（含研究记述），
   再用 scope 过滤器把范围限制在本页登记的分类单元：
     科页 → 整个科；亚科页 → 整个亚科；属页 → 该属。
   scope / lang 过滤器由 _layouts/default.html 按 front matter 写成隐藏 span
   （每一页都带本页及所有上级 id），所以这里只需过滤 `data-anchors` 的首项，
   即本页自身 id。研究记述已从 data-pagefind-ignore 中移出，会被一起检索到。

   Pagefind 不可用（本地 jekyll serve、或 CI 里 Pagefind 构建失败）时，
   回退到 /search-index.json 的结构化字段检索（名字 / 分布 / 模式产地），
   不改动名录页的 assets/search.js。 */
(function(){
  var box = document.querySelector('.taxon-search');
  if (!box) return;
  var input = box.querySelector('.taxon-search-input');
  var results = box.querySelector('.taxon-search-results');
  var status = box.querySelector('.taxon-search-status');
  if (!input || !results) return;

  var anchors = (box.getAttribute('data-anchors') || '').split(',');
  var scope = Object.create(null);
  var selfId = '';
  for (var i = 0; i < anchors.length; i++){
    var a = anchors[i].trim();
    if (!a) continue;
    scope[a] = 1;
    if (!selfId) selfId = a;   /* 生成器把本页自身 id 放在首位 */
  }
  var INDEX = box.getAttribute('data-index') || '/search-index.json';
  /* 三语分页：页面语言与本语言的站内前缀。搜索结果要跳到**同语言**的中转页/物种页，
     否则英文页上点一条结果会掉回中文页（LP = '' / '/en' / '/es'）。 */
  var LANG = box.getAttribute('data-lang') || document.documentElement.lang || 'zh-CN';
  var LP = box.getAttribute('data-lang-prefix') || '';
  var SEARCH_PAGE = box.getAttribute('data-search-page') || (LP + '/search/');
  var BASE = INDEX.replace(/\/search-index\.json$/, '');
  var BUNDLE = BASE + '/pagefind/';
  var LIMIT = 40;

  /* 界面文案：只在本页语言那一份里取，缺配置时回落中文（生成器应总是写好 data-lang）。 */
  var STR = {
    'zh-CN': {
      loading: '检索中…',
      empty: '本范围内没有匹配的内容（名字、分布、模式产地、研究记述都会检索） · ',
      allSearch: '在全站全文搜索中查找', zero: '0 个结果',
      full: '显示前 %n 个结果（本范围内全文，含研究记述），输入更精确的词可缩小范围',
      count: '%n 个结果（本范围内全文，含研究记述）',
      jEmpty: '本范围内没有匹配的分类单元 · 可试试中文名、拉丁学名，或分布国 / 地区（如 澳大利亚、云南、Brazil） · ',
      jZero: '0 个匹配',
      jFull: '显示前 %n 个匹配（名字 / 分布 / 模式产地），输入更精确的词可缩小范围',
      jCount: '%n 个匹配（名字 / 分布 / 模式产地）',
      dz: '分布', t: '模式产地', sl: '异名产地', de: '分布（英）',
      ranks: { '种': '种', '亚种': '亚种', '属': '属', '科': '科', '亚科': '亚科' }
    },
    en: {
      loading: 'Searching…',
      empty: 'Nothing in this scope matches (names, distribution, type localities and literature notes are all searched) · ',
      allSearch: 'Search the whole site', zero: '0 results',
      full: 'Showing the first %n results (full text in this scope, literature notes included); use a more specific term to narrow down',
      count: '%n results (full text in this scope, literature notes included)',
      jEmpty: 'No taxon on this page matches · try a Latin name, a Chinese name, or a country / region (e.g. Australia, Yunnan, Brazil) · ',
      jZero: '0 matches',
      jFull: 'Showing the first %n matches (name / distribution / type locality); use a more specific term to narrow down',
      jCount: '%n matches (name / distribution / type locality)',
      dz: 'Distribution', t: 'Type locality', sl: 'Synonym localities', de: 'Distribution (EN)',
      ranks: { '种': 'species', '亚种': 'subspecies', '属': 'genus', '科': 'family', '亚科': 'subfamily' }
    },
    es: {
      loading: 'Buscando…',
      empty: 'Nada coincide en este ámbito (se buscan nombres, distribución, localidad tipo y notas bibliográficas) · ',
      allSearch: 'Buscar en todo el sitio', zero: '0 resultados',
      full: 'Se muestran los primeros %n resultados (texto completo de este ámbito, incluidas las notas bibliográficas); use un término más preciso para acotar',
      count: '%n resultados (texto completo de este ámbito, incluidas las notas bibliográficas)',
      jEmpty: 'Ningún taxón de esta página coincide · pruebe un nombre latino, un nombre chino o un país / región (p. ej. Australia, Yunnan, Brasil) · ',
      jZero: '0 coincidencias',
      jFull: 'Se muestran las primeras %n coincidencias (nombre / distribución / localidad tipo); use un término más preciso para acotar',
      jCount: '%n coincidencias (nombre / distribución / localidad tipo)',
      dz: 'Distribución', t: 'Localidad tipo', sl: 'Localidades de sinónimos', de: 'Distribución (EN)',
      ranks: { '种': 'especie', '亚种': 'subespecie', '属': 'género', '科': 'familia', '亚科': 'subfamilia' }
    }
  };
  var S = STR[LANG] || STR['zh-CN'];
  function fmt(s, n){ return s.replace(/%n/g, String(n)); }
  function rankLabel(r){ return S.ranks[r] || r; }

  function esc(s){
    return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];
    });
  }
  function show(open){
    results.hidden = !open;
    if (status) status.hidden = !open;
    input.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  function showEmpty(raw){
    results.innerHTML = '<li class="taxon-search-empty">' + esc(S.empty)
      + '<a href="' + esc(SEARCH_PAGE + '?q=' + encodeURIComponent(raw)) + '">' + esc(S.allSearch) + '</a></li>';
    if (status) status.textContent = S.zero;
    show(true);
  }

  /* ---------- Pagefind：与 /search/ 相同的全文索引 ---------- */

  var dynamicImport = null;
  try { dynamicImport = new Function('p', 'return import(p);'); } catch (e) { dynamicImport = null; }

  var pagefindPromise = null;
  var pagefindUnavailable = false;
  var seq = 0;

  // Pagefind 结果 URL 可能是绝对地址（已带 baseUrl）或站内相对路径；只有两者都不是时才补前缀，
  // 避免把 /base/base/… 拼成死链（逻辑与 assets/search-widget.js 的 fixUrl 一致）。
  var REL_BASE = BASE ? BASE.replace(/^https?:\/\/[^/]+/, '') : '';
  function fixUrl(url){
    if (!url) return SEARCH_PAGE;
    if (!BASE) return url;
    if (REL_BASE && (url === REL_BASE || url.indexOf(REL_BASE + '/') === 0)) return url;
    if (url.indexOf(BASE + '/') === 0) return url;
    return url.charAt(0) === '/' ? BASE + url : BASE + '/' + url;
  }

  function loadPagefind(){
    if (!dynamicImport || pagefindUnavailable) return Promise.resolve(null);
    if (!pagefindPromise){
      pagefindPromise = dynamicImport(BUNDLE + 'pagefind.js').then(function(pf){
        if (!pf) return null;
        var setup;
        try {
          setup = (typeof pf.options === 'function' && BASE)
            ? Promise.resolve(pf.options({ basePath: BUNDLE, baseUrl: BASE + '/' }))
            : Promise.resolve();
        } catch (e) {
          setup = Promise.resolve();
        }
        return setup.then(function(){
          return pf.init ? pf.init() : null;
        }).then(function(){ return pf; });
      }).catch(function(err){
        console.warn('[taxon-search] Pagefind 加载失败，回退到结构化索引：', err);
        pagefindUnavailable = true;
        return null;
      });
    }
    return pagefindPromise;
  }

  function titleOf(it){
    var m = it.meta || {};
    if (m.zh && m.latin) return m.zh + ' · ' + m.latin;
    return m.zh || m.latin || m.title || it.url || '';
  }

  function renderPagefind(items, total, raw){
    if (!items.length){ showEmpty(raw); return; }
    var html = '';
    for (var i = 0; i < items.length; i++){
      var it = items[i];
      html += '<li><a href="' + esc(fixUrl(it.url)) + '">' + esc(titleOf(it)) + '</a>';
      var excerpt = it.excerpt || '';
      if (excerpt) html += '<div class="taxon-search-snippet">' + excerpt + '</div>';
      html += '</li>';
    }
    results.innerHTML = html;
    if (status) status.textContent = total > LIMIT ? fmt(S.full, LIMIT) : fmt(S.count, total);
    show(true);
  }

  function searchPagefind(raw, mySeq){
    return loadPagefind().then(function(pf){
      if (mySeq !== seq) return;
      if (!pf){ pagefindUnavailable = true; return jsonSearch(raw); }
      var filters = {};
      if (selfId) filters.scope = selfId;
      if (LANG) filters.lang = LANG.toLowerCase();
      return pf.search(raw, { filters: filters }).then(function(res){
        if (mySeq !== seq) return;
        var all = (res && res.results) || [];
        var slice = all.slice(0, LIMIT);
        return Promise.all(slice.map(function(r){ return r.data(); })).then(function(items){
          if (mySeq !== seq) return;
          renderPagefind(items, all.length, raw);
        });
      });
    }).catch(function(err){
      console.warn('[taxon-search] Pagefind 检索失败，回退到结构化索引：', err);
      pagefindUnavailable = true;
      if (mySeq === seq) jsonSearch(raw);
    });
  }

  /* ---------- 回退：/search-index.json 的结构化字段检索 ---------- */

  var CONTEXT_FIELDS = [
    { key: 'dz', label: S.dz },
    { key: 't',  label: S.t },
    { key: 'sl', label: S.sl },
    { key: 'de', label: S.de }
  ];

  var data = null, loading = false, pending = null;

  function norm(s){ return String(s == null ? '' : s).toLowerCase(); }
  function compact(s){ return String(s || '').replace(/[^a-z0-9]/g, ''); }

  function loadJson(){
    if (data || loading) return;
    loading = true;
    fetch(INDEX).then(function(r){ return r.json(); }).then(function(arr){
      data = arr; loading = false;
      if (pending != null){ var v = pending; pending = null; run(v); }
    }).catch(function(err){
      loading = false;
      console.warn('[taxon-search] search-index.json 加载失败：', err);
    });
  }

  function jsonHref(e){
    if ((e.r === '种' || e.r === '亚种') && e.p) return BASE + LP + '/species/' + encodeURIComponent(e.p) + '/';
    if (e.r === '属') return BASE + LP + '/genus/' + encodeURIComponent(e.h) + '/';
    if (e.r === '亚科') return BASE + LP + '/subfamily/' + encodeURIComponent(e.h) + '/';
    if (e.r === '科') return BASE + LP + '/family/' + encodeURIComponent(e.h) + '/';
    return BASE + LP + '/list/#' + encodeURIComponent(e.h);
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

  function renderJson(list, raw, tokens){
    if (!list.length){
      results.innerHTML = '<li class="taxon-search-empty">' + esc(S.jEmpty)
        + '<a href="' + esc(SEARCH_PAGE + '?q=' + encodeURIComponent(raw)) + '">' + esc(S.allSearch) + '</a></li>';
      if (status) status.textContent = S.jZero;
      show(true);
      return;
    }
    var html = '';
    for (var i = 0; i < list.length; i++){
      var item = list[i], e = item.e;
      html += '<li><a href="' + esc(jsonHref(e)) + '"><span class="rank">' + esc(rankLabel(e.r)) + '</span>'
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
      ? fmt(S.jFull, LIMIT)
      : fmt(S.jCount, list.length);
    show(true);
  }

  function jsonSearch(raw){
    if (!data){ pending = raw; loadJson(); return; }
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
    renderJson(scored.slice(0, LIMIT), raw, tokens);
  }

  /* ---------- 入口 ---------- */

  function run(q){
    var raw = String(q == null ? '' : q).trim();
    if (!raw){
      results.innerHTML = '';
      if (status){ status.textContent = ''; status.hidden = true; }
      show(false);
      return;
    }
    var mySeq = ++seq;
    if (status){ status.hidden = false; status.textContent = S.loading; }
    show(true);
    if (pagefindUnavailable){ jsonSearch(raw); return; }
    searchPagefind(raw, mySeq);
  }

  var timer;
  input.addEventListener('input', function(){
    clearTimeout(timer);
    var v = input.value;
    timer = setTimeout(function(){ run(v); }, 150);
  });
  input.addEventListener('focus', function(){
    loadPagefind();
    if (input.value) run(input.value);
  });
  input.addEventListener('keydown', function(ev){
    if (ev.key === 'Escape'){ show(false); input.blur(); return; }
    if (ev.key === 'Enter'){
      var first = results.querySelector('a');
      if (first){
        ev.preventDefault();
        window.location.href = first.getAttribute('href');
      } else if (input.value.trim()){
        ev.preventDefault();
        window.location.href = SEARCH_PAGE + '?q=' + encodeURIComponent(input.value.trim());
      }
    }
  });
  document.addEventListener('click', function(ev){
    if (results.hidden) return;
    if (ev.target.closest && ev.target.closest('.taxon-search')) return;
    show(false);
  });
})();
