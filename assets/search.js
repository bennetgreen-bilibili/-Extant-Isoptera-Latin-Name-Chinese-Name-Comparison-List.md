(function(){
  var BASE = "https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md";
  var input = document.getElementById('search-input');
  var results = document.getElementById('search-results');
  if (!input || !results) return;
  var data = null;
  var LIST = input.getAttribute('data-list-url') || (BASE + '/list/');
  var LANG = input.getAttribute('data-lang') || 'zh';
  var EMPTY = input.getAttribute('data-empty') || '无匹配结果';
  var RANK = { '支系':'Clade','科':'Family','亚科':'Subfamily','属':'Genus','种':'Species','亚种':'Subspecies' };
  function rank(r){ return (LANG==='en') ? (RANK[r]||r) : r; }

  function esc(s){ return String(s==null?'':s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function norm(s){ return String(s==null?'':s).toLowerCase(); }

  fetch(BASE + '/search-index.json').then(function(r){ return r.json(); }).then(function(arr){ data = arr; }).catch(function(){});

  function render(list){
    if (!list.length){ results.innerHTML = '<li>'+esc(EMPTY)+'</li>'; results.style.display='block'; return; }
    var html = '';
    for (var i=0;i<list.length;i++){
      var r = list[i];
      var e = r.e;
      var synHint = r.viaSyn ? ' <span class="syn-hint">· ' + esc(LANG==='en'?'junior synonym':'次异名') + '</span>' : '';
      html += '<li><a href="'+LIST+'#'+esc(e.h)+'"><span class="rank">'+esc(rank(e.r))+'</span>'+esc(e.z)+' <span class="latin">'+esc(e.l)+'</span>'+synHint+'</a></li>';
    }
    results.innerHTML = html;
    results.style.display = 'block';
  }

  function search(q){
    q = norm(q).trim();
    if (!q){ results.style.display='none'; results.innerHTML=''; return; }
    if (!data){ return; }
    var scored = [];
    for (var i=0;i<data.length;i++){
      var e = data[i], l = norm(e.l), z = norm(e.z), s = norm(e.s || '');
      var li = l.indexOf(q), zi = z.indexOf(q), si = s.indexOf(q);
      if (li < 0 && zi < 0 && si < 0) continue;
      var score;
      if (l === q || z === q || s === q) score = 0;
      else if (l.indexOf(q) === 0 || z.indexOf(q) === 0 || s.indexOf(q) === 0) score = 1;
      else score = 2;
      scored.push({ score: score, len: Math.min(l.length, z.length), e: e, viaSyn: (li < 0 && zi < 0) });
    }
    scored.sort(function(a,b){ return a.score-b.score || a.len-b.len; });
    render(scored.slice(0, 60));
  }

  var timer;
  input.addEventListener('input', function(){ clearTimeout(timer); var v = input.value; timer = setTimeout(function(){ search(v); }, 140); });
  input.addEventListener('focus', function(){ if (input.value) search(input.value); });
  document.addEventListener('click', function(ev){ if (results.style.display !== 'none' && !ev.target.closest('.search-wrap')) results.style.display = 'none'; });
})();
