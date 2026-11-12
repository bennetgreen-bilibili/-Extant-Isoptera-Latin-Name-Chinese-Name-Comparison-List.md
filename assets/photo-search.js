/* 「全部图片」页（科 / 亚科 / 属 / 种四级，_layouts/photos.html）的本页检索：
   只筛选当前页已经渲染出的 .gallery-card，不发任何请求。
   检索串来自 _includes/photo-card.html 写在 figure 上的 data-label（「拉丁 中文」，
   按种分组时即该种的学名与中文名）与 data-credit（摄影师 / 作者）。
   被筛掉的卡片加 [hidden]；assets/gallery.js 里 PhotoSwipe 的 children 选择器是
   .gallery-card:not([hidden]) a.gallery-item，所以灯箱里也只会翻到匹配的照片。
   输入会同步到 ?q=，便于把筛选结果直接分享出去。
   样式见 assets/gallery.css 的 .photo-search 段；框体由 _includes/photo-search.html 渲染。 */
(function () {
  'use strict';

  var box = document.querySelector('.photo-search');
  if (!box) return;

  var input = box.querySelector('.photo-search-input');
  var clearBtn = box.querySelector('.photo-search-clear');
  var status = box.querySelector('.photo-search-status');
  var empty = box.querySelector('.photo-search-empty');
  var countEl = box.querySelector('.photo-search-count');
  if (!input) return;

  var pageEl = box.closest ? (box.closest('.photo-page') || document) : document;
  var cards = Array.prototype.slice.call(pageEl.querySelectorAll('.gallery-card'));
  if (!cards.length) return;

  // 「在本页 N 张照片中检索」的 N 取实际渲染的卡片数：科 / 亚科 / 属页只渲染
  // 每种前 6 张，front matter 的 photo_count 是全部照片总数，不能直接用它。
  if (countEl) {
    countEl.textContent = cards.length + ' 张 / ' + cards.length + ' photos / ' + cards.length + ' fotos';
    countEl.hidden = false;
  }
  var groups = Array.prototype.slice.call(pageEl.querySelectorAll('.species-gallery'));
  var total = cards.length;
  var searchPage = box.getAttribute('data-search-page') || '/search/';

  function fold(s) {
    s = String(s == null ? '' : s).toLowerCase();
    if (s.normalize) s = s.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    return s;
  }

  // 去掉空格与标点后的紧凑串：让 "amitermesabruptus" 也能命中 "Amitermes abruptus"
  function compact(s) { return s.replace(/[^a-z0-9\u3400-\u9fff]+/g, ''); }

  // 预处理一次：每张卡片的检索串 + 所属种（data-label 去重后就是「种」）
  for (var i = 0; i < cards.length; i++) {
    var card = cards[i];
    var hay = fold(card.getAttribute('data-label')) + ' ' + fold(card.getAttribute('data-credit'));
    card.__psHay = hay;
    card.__psHayCompact = compact(hay);
    card.__psLabel = card.getAttribute('data-label') || '';
  }

  // 组标题上的「N 张」徽标：筛选时改成「匹配 / 总数」，清空后按原文还原
  for (var j = 0; j < groups.length; j++) {
    var badge = groups[j].querySelector('.gallery-count');
    if (!badge) continue;
    groups[j].__psBadge = badge;
    groups[j].__psBadgeText = badge.textContent;
  }

  // 多个词之间是 AND：「amitermes lindqvist」= 该属里这位摄影师的照片
  function matchTokens(card, tokens) {
    var hay = card.__psHay;
    var chay = card.__psHayCompact;
    for (var i = 0; i < tokens.length; i++) {
      var t = tokens[i];
      if (hay.indexOf(t) !== -1) continue;
      var c = compact(t);
      if (c.length >= 3 && chay.indexOf(c) !== -1) continue;
      return false;
    }
    return true;
  }

  function syncUrl(q) {
    if (!window.history || !window.history.replaceState) return;
    var params = null;
    try { params = new URLSearchParams(window.location.search); } catch (e) { params = null; }
    if (!params) return;
    if (q) params.set('q', q); else params.delete('q');
    var query = params.toString();
    window.history.replaceState(null, '',
      window.location.pathname + (query ? '?' + query : '') + window.location.hash);
  }

  function apply(raw) {
    var q = String(raw == null ? '' : raw).trim();
    var tokens = fold(q).split(/\s+/).filter(function (t) { return t.length > 0; });
    var active = tokens.length > 0;
    var shown = 0;
    var species = Object.create(null);
    var speciesCount = 0;

    for (var i = 0; i < cards.length; i++) {
      var card = cards[i];
      var hit = !active || matchTokens(card, tokens);
      card.hidden = !hit;
      if (!hit) continue;
      shown++;
      if (card.__psLabel && !species[card.__psLabel]) {
        species[card.__psLabel] = 1;
        speciesCount++;
      }
    }

    // 一个种的照片全被筛掉时，整组（标题 + 网格 + 「该种全部 N 张」）一起收起
    for (var j = 0; j < groups.length; j++) {
      var group = groups[j];
      var visible = group.querySelectorAll('.gallery-card:not([hidden])').length;
      group.hidden = active && visible === 0;
      if (group.__psBadge) {
        var groupTotal = group.querySelectorAll('.gallery-card').length;
        group.__psBadge.textContent = active
          ? (visible + ' / ' + groupTotal + ' 张 / photos / fotos')
          : group.__psBadgeText;
      }
    }

    if (status) {
      status.hidden = !active;
      status.textContent = !active ? ''
        : shown === 0 ? '没有匹配的照片（共 ' + total + ' 张）· No matching photos (' + total + ' in total) · No hay fotos coincidentes (' + total + ' en total)'
        : '匹配 ' + shown + ' / ' + total + ' 张 · ' + shown + ' / ' + total + ' photos · ' + shown + ' / ' + total + ' fotos' + (speciesCount > 1 ? ' · ' + speciesCount + ' 种 · ' + speciesCount + ' species · ' + speciesCount + ' especies' : '');
    }
    if (empty) {
      empty.hidden = !(active && shown === 0);
      var link = empty.querySelector('a');
      if (link) link.href = searchPage + (q ? '?q=' + encodeURIComponent(q) : '');
    }
    if (clearBtn) clearBtn.hidden = !active;
    box.classList.toggle('is-filtering', active);
    syncUrl(q);
  }

  var timer = null;
  function schedule() {
    clearTimeout(timer);
    var value = input.value;
    timer = setTimeout(function () { apply(value); }, 140);
  }

  input.addEventListener('input', schedule);
  input.addEventListener('search', schedule); // 部分浏览器原生「清空」只发 search
  input.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && input.value) {
      ev.preventDefault();
      input.value = '';
      apply('');
    }
  });

  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      input.value = '';
      apply('');
      input.focus();
    });
  }

  // ?q= 预填：从站内 / 外部链接进来时直接按该词筛选
  var initial = '';
  try { initial = new URLSearchParams(window.location.search).get('q') || ''; } catch (e) { initial = ''; }
  if (initial) {
    input.value = initial;
    apply(initial);
  }
})();
