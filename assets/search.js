/* 名录检索：中文名 / 拉丁学名 / 次异名 / 拼音（py、pi）/ 繁体（zt）
   索引由 .github/workflows/build_search_index.py 生成；
   未命中时给出跳转「全站全文搜索」（Pagefind，/search/ 等页面）的入口。 */
(function(){
  var BASE = "https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md";
  var input = document.getElementById('search-input');
  var results = document.getElementById('search-results');
  if (!input || !results) return;
  var data = null;
  var LIST = input.getAttribute('data-list-url') || (BASE + '/list/');
  var LANG = input.getAttribute('data-lang') || 'zh';
  var RANK = { '支系':'Clade','科':'Family','亚科':'Subfamily','属':'Genus','种':'Species','亚种':'Subspecies' };
  var RANK_ES = { '支系':'Clado','科':'Familia','亚科':'Subfamilia','属':'Género','种':'Especie','亚种':'Subespecie' };
  var TEXT = {
    zh: { syn:'次异名', pinyin:'拼音', trad:'繁体', empty:'无匹配结果', hint:'在全文搜索中查找' },
    en: { syn:'junior synonym', pinyin:'pinyin', trad:'traditional', empty:'No matches', hint:'Search the whole site' },
    es: { syn:'sinónimo junior', pinyin:'pinyin', trad:'tradicional', empty:'Sin resultados', hint:'Buscar en todo el sitio' }
  };
  var T = TEXT[LANG] || TEXT.zh;
  var SEARCH_PAGE = BASE + (LANG === 'en' ? '/en' : LANG === 'es' ? '/es' : '') + '/search/';

  function rank(r){ return (LANG==='en') ? (RANK[r]||r) : (LANG==='es' ? (RANK_ES[r]||r) : r); }
  function esc(s){ return String(s==null?'':s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function norm(s){ return String(s==null?'':s).toLowerCase(); }
  function compact(s){ return String(s||'').replace(/[^a-z0-9]/g, ''); }

  fetch(BASE + '/search-index.json').then(function(r){ return r.json(); }).then(function(arr){ data = arr; }).catch(function(){});

  function hint(via){
    if (!via) return '';
    var label = via === 'syn' ? T.syn : via === 'pinyin' ? T.pinyin : via === 'trad' ? T.trad : '';
    return label ? ' <span class="syn-hint">· ' + esc(label) + '</span>' : '';
  }

  function render(list, query){
    if (!list.length){
      results.innerHTML = '<li class="search-empty">' + esc(T.empty) +
        ' · <a href="' + esc(SEARCH_PAGE + (query ? '?q=' + encodeURIComponent(query) : '')) + '">' +
        esc(T.hint) + '</a></li>';
      results.style.display = 'block';
      return;
    }
    var html = '';
    for (var i=0;i<list.length;i++){
      var r = list[i], e = r.e;
      var href = (e.p && (e.r === '种' || e.r === '亚种')) ? (BASE + '/species/' + encodeURIComponent(e.p) + '/') : (LIST + '#' + e.h);
      html += '<li><a href="'+href+'"><span class="rank">'+esc(rank(e.r))+'</span>'+esc(e.z)+' <span class="latin">'+esc(e.l)+'</span>'+hint(r.via)+'</a></li>';
    }
    results.innerHTML = html;
    results.style.display = 'block';
  }

  function search(q){
    var raw = String(q == null ? '' : q).trim();
    if (!raw){ results.style.display='none'; results.innerHTML=''; return; }
    if (!data){ return; }
    var qn = norm(raw);
    var qc = compact(qn);
    var asciiQuery = /^[a-z0-9][a-z0-9\s.\-'’]*$/.test(qn);
    var scored = [];
    for (var i=0;i<data.length;i++){
      var e = data[i];
      var l = norm(e.l), z = norm(e.z), s = norm(e.s || ''), zt = norm(e.zt || '');
      var li = l.indexOf(qn), zi = z.indexOf(qn), si = s.indexOf(qn), ti = zt.indexOf(qn);
      var score = -1, via = null;
      if (li >= 0 || zi >= 0 || si >= 0 || ti >= 0){
        if (l === qn || z === qn || zt === qn || s === qn) score = 0;
        else if (li === 0 || zi === 0 || ti === 0) score = 1;
        else score = 2;
        if (li < 0 && zi < 0 && ti < 0) via = 'syn';
        else if (ti >= 0 && li < 0 && zi < 0) via = 'trad';
      } else if (asciiQuery && qc.length >= 2){
        var py = e.py || '', pi = e.pi || '';
        if (py && (py === qc || pi === qc)) { score = 3; via = 'pinyin'; }
        else if (py && py.indexOf(qc) >= 0) { score = 4; via = 'pinyin'; }
        else if (pi && qc.length >= 3 && pi.indexOf(qc) === 0) { score = 5; via = 'pinyin'; }
      }
      if (score < 0) continue;
      scored.push({ score: score, len: (l.length + z.length), e: e, via: via });
    }
    scored.sort(function(a,b){ return a.score-b.score || a.len-b.len; });
    render(scored.slice(0, 60), raw);
  }

  var timer;
  input.addEventListener('input', function(){ clearTimeout(timer); var v = input.value; timer = setTimeout(function(){ search(v); }, 140); });
  input.addEventListener('focus', function(){ if (input.value) search(input.value); });
  document.addEventListener('click', function(ev){ if (results.style.display !== 'none' && !ev.target.closest('.search-wrap')) results.style.display = 'none'; });
  input.addEventListener('keydown', function(ev){ if (ev.key === 'Escape'){ results.style.display='none'; } });
})();
