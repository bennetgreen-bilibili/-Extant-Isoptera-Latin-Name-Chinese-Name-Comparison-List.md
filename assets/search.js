(function(){
  var BASE = "https://bennetgreen-bilibili.github.io/-Extant-Isoptera-Latin-Name-Chinese-Name-Comparison-List.md";
  var input = document.getElementById('search-input');
  var results = document.getElementById('search-results');
  if (!input || !results) return;
  var data = null;

  function esc(s){ return String(s==null?'':s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function norm(s){ return String(s==null?'':s).toLowerCase(); }

  fetch(BASE + '/search-index.json').then(function(r){ return r.json(); }).then(function(arr){ data = arr; }).catch(function(){});

  function render(list){
    if (!list.length){ results.innerHTML = '<li>无匹配结果</li>'; results.style.display='block'; return; }
    var html = '';
    for (var i=0;i<list.length;i++){
      var e = list[i];
      html += '<li><a href="'+BASE+'/list/#'+esc(e.h)+'"><span class="rank">'+esc(e.r)+'</span>'+esc(e.z)+' <span class="latin">'+esc(e.l)+'</span></a></li>';
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
      var e = data[i], l = norm(e.l), z = norm(e.z);
      var li = l.indexOf(q), zi = z.indexOf(q);
      if (li < 0 && zi < 0) continue;
      var score;
      if (l === q || z === q) score = 0;
      else if (l.indexOf(q) === 0 || z.indexOf(q) === 0) score = 1;
      else score = 2;
      scored.push([score, Math.min(l.length, z.length), e]);
    }
    scored.sort(function(a,b){ return a[0]-b[0] || a[1]-b[1]; });
    render(scored.slice(0, 60).map(function(x){ return x[2]; }));
  }

  var timer;
  input.addEventListener('input', function(){ clearTimeout(timer); var v = input.value; timer = setTimeout(function(){ search(v); }, 140); });
  input.addEventListener('focus', function(){ if (input.value) search(input.value); });
  document.addEventListener('click', function(ev){ if (results.style.display !== 'none' && !ev.target.closest('.search-wrap')) results.style.display = 'none'; });
})();
