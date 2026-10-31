/* ============================================================
   现存等翅下目 · 科—亚科级系统发育树（数据驱动渲染）
   数据：_data/phylogeny.json（页面通过 window.PHYLOGENY 注入）
   - 拓扑/名称/支持值/备注全部来自数据文件
   - 两种布局：cladogram（按支序展开）/ rank（按分类阶元分列）
   ============================================================ */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) { module.exports = factory(); }
  else { root.Phylo = factory(); }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var DEFAULTS = {
    rowH: 34,
    edgeLeaf: 34,
    edgeNamed: 112,
    edgeAnon: 15,
    labelGap: 10,
    padTop: 36,
    padLeft: 30,
    padRight: 30,
    padBottom: 28,
    mode: 'cladogram',      // 'cladogram' | 'rank'
    showSupport: true,
    notesLang: 'zh',
    guideLabels: { clade: '', family: '', subfamily: '' }
  };

  var RANK = { family: 210, subfamily: 440, gutter: 230 };

  function textWidth(s) {
    var w = 0;
    for (var i = 0; i < s.length; i++) {
      var c = s.charCodeAt(i);
      if (c > 0x2e80) w += 12.6;
      else if (c >= 0x30 && c <= 0x39) w += 7.0;
      else if (c >= 0x41 && c <= 0x5a) w += 7.8;
      else if (c >= 0x61 && c <= 0x7a) w += 6.5;
      else w += 4.8;
    }
    return w;
  }

  function countTail(node, lang) {
    var c = node.counts;
    if (!c || c.genera == null || c.species == null) return '';
    if (lang === 'zh') return c.genera + ' 属 ' + c.species + ' 种';
    if (lang === 'es') return c.genera + ' gén. / ' + c.species + ' spp.';
    return c.genera + ' gen. / ' + c.species + ' spp.';
  }

  function nameParts(node, zhMode) {
    var zh = node.zh || '';
    var latin = node.latin || '';
    if (node.type === 'family' && latin) latin = latin.toUpperCase();
    if (zhMode === 'zh' || !latin) return zh ? [{ t: zh, cls: 'zh' }] : [{ t: latin, cls: 'lat' }];
    if (zhMode === 'latin' || !zh) return [{ t: latin, cls: 'lat' }];
    return [{ t: zh, cls: 'zh' }, { t: ' ' + latin, cls: 'lat' }];
  }

  function partsWidth(parts) { return parts.reduce(function (a, p) { return a + textWidth(p.t); }, 0); }

  /* 支持值：有数值则 UFB + sCF；否则用定性文本（单系 / monophyletic） */
  function supportInline(node, lang) {
    if (node.support) {
      var s = 'UFB ' + node.support.ufb;
      if (node.support.scf) s += ' · sCF ' + node.support.scf;
      return s;
    }
    if (node.supportText) return node.supportText[lang] || node.supportText.en || '';
    return '';
  }

  function supportFull(node, lang) {
    if (node.support) {
      var s = 'UFB ' + node.support.ufb;
      if (node.support.lpp) s += ' · LPP ' + node.support.lpp;
      if (node.support.scf) s += ' · sCF ' + node.support.scf;
      return s;
    }
    if (node.supportText) return node.supportText[lang] || node.supportText.en || '';
    return '';
  }

  function noteOf(node, lang) {
    if (lang === 'zh') return node.note || '';
    return node.note_en || node.note || '';
  }

  function buildLayout(tree, options) {
    var opts = {};
    for (var k in DEFAULTS) opts[k] = DEFAULTS[k];
    if (options) for (var k2 in options) opts[k2] = options[k2];

    var rankMode = opts.mode === 'rank';
    if (rankMode) { opts.padLeft = RANK.gutter; opts.padTop = Math.max(opts.padTop, 56); }

    var nodes = [], leaves = [];
    var colFamily = opts.padLeft + RANK.family;
    var colSubfamily = opts.padLeft + RANK.subfamily;

    function isNamed(d) { return !!(d.latin || d.zh || d.id); }

    function prep(data, parent) {
      var n = {
        key: nodes.length, data: data, parent: parent, children: [],
        depth: parent ? parent.depth + 1 : 0,
        x: 0, y: 0, y0: 0, y1: 0,
        isLeaf: !(data.children && data.children.length),
        named: isNamed(data)
      };
      nodes.push(n);
      if (parent) parent.children.push(n);
      if (n.isLeaf) leaves.push(n);
      else (data.children || []).forEach(function (c) { prep(c, n); });
      return n;
    }

    function assignX(n) {
      for (var i = 0; i < n.children.length; i++) {
        var c = n.children[i], d = c.data;
        if (rankMode) {
          if (d.type === 'subfamily') c.x = colSubfamily;
          else if (d.type === 'family') c.x = colFamily;
          else if (isNamed(d)) c.x = Math.max(n.x + 2, opts.padLeft);
          else c.x = n.x + 16;
        } else {
          c.x = n.x + edgeWidth(d);
        }
        assignX(c);
      }
    }

    function edgeWidth(d) {
      if (!d.children || !d.children.length) return opts.edgeLeaf;
      return isNamed(d) ? opts.edgeNamed : opts.edgeAnon;
    }

    var rootNode = prep(tree, null);
    rootNode.x = opts.padLeft;
    assignX(rootNode);

    var maxX = 0;
    nodes.forEach(function (n) { if (n.x > maxX) maxX = n.x; });
    if (!rankMode) { leaves.forEach(function (l) { l.x = maxX; }); }

    var cursor = opts.padTop + opts.rowH / 2;
    leaves.forEach(function (l) { l.y = cursor; cursor += opts.rowH; });
    (function assignY(n) {
      if (n.children.length) {
        n.children.forEach(assignY);
        n.y = (n.children[0].y + n.children[n.children.length - 1].y) / 2;
        n.y0 = n.children[0].y;
        n.y1 = n.children[n.children.length - 1].y;
        n.topY = Math.min.apply(null, n.children.map(function (c) { return c.topY; }));
        n.botY = Math.max.apply(null, n.children.map(function (c) { return c.botY; }));
      } else { n.y0 = n.y1 = n.y; n.topY = n.botY = n.y; }
    })(rootNode);

    var height = opts.padTop + leaves.length * opts.rowH + opts.padBottom;

    var lines = [], bands = [], labels = [], guides = [];
    var rightEdge = opts.padLeft + maxX;

    /* --- 分类阶元参考线（rank 模式） --- */
    if (rankMode) {
      guides.push({ x: opts.padLeft, top: opts.padTop * 0.62, bottom: height - opts.padBottom * 0.4, label: opts.guideLabels.clade, labelX: opts.padLeft + 8 });
      guides.push({ x: colFamily, top: opts.padTop * 0.62, bottom: height - opts.padBottom * 0.4, label: opts.guideLabels.family, labelX: colFamily + 8 });
      guides.push({ x: colSubfamily, top: opts.padTop * 0.62, bottom: height - opts.padBottom * 0.4, label: opts.guideLabels.subfamily, labelX: colSubfamily + 8 });
    }

    /* --- 科级背景带 --- */
    (function collectBands(n) {
      if (n.data.type === 'family' && n.children.length) {
        bands.push({
          x: n.x + 3, y: n.y0 - opts.rowH / 2,
          w: Math.max(rightEdge - n.x + opts.labelGap + 220, 240),
          h: (n.y1 - n.y0) + opts.rowH, cls: 'band-family'
        });
      }
      n.children.forEach(collectBands);
    })(rootNode);

    /* --- 分支 --- */
    (function drawBranches(n) {
      var kids = n.children;
      if (kids.length) {
        var vert = (n.data.edgeUncertain || n.data.uncertain) ? 'branch is-uncertain' : 'branch';
        for (var i = 0; i < kids.length; i++) {
          if (kids[i].data.edgeUncertain || kids[i].data.uncertain) { vert = 'branch is-uncertain'; break; }
        }
        if (n.y1 > n.y0 + 0.5) lines.push({ x1: n.x, y1: n.y0, x2: n.x, y2: n.y1, cls: vert });
        for (var j = 0; j < kids.length; j++) {
          var c = kids[j];
          var ecls = (c.data.edgeUncertain || c.data.uncertain) ? 'branch is-uncertain' : 'branch';
          if (Math.abs(c.x - n.x) > 0.5) lines.push({ x1: n.x, y1: c.y, x2: c.x, y2: c.y, cls: ecls });
        }
      }
      kids.forEach(drawBranches);
    })(rootNode);

    /* --- 名称与支持值 --- */
    var maxLabelRight = 0;
    (function collectLabels(n) {
      var d = n.data;
      if (n.isLeaf) {
        if (d.__collapsed) {
          var cp = nameParts(d, opts.zhMode || 'both');
          labels.push({
            x: n.x + opts.labelGap, y: n.y, parts: cp,
            support: opts.showSupport ? supportInline(d, opts.notesLang) : '', suffix: ' ▸ ' + (d.__collapsedCount || ''), tail: '',
            cls: 'tip tip-' + d.type + ' is-collapsed', key: n.key, href: null,
            title: noteOf(d, opts.notesLang), anchor: 'start', bg: 0
          });
          maxLabelRight = Math.max(maxLabelRight, n.x + opts.labelGap + partsWidth(cp));
        } else {
          var parts = nameParts(d, opts.zhMode || 'both');
          var tail = countTail(d, opts.lang || 'zh');
          var tsup = opts.showSupport ? supportInline(d, opts.notesLang) : '';
          labels.push({
            x: n.x + opts.labelGap, y: n.y, parts: parts,
            support: tsup, suffix: '', tail: tail,
            cls: 'tip tip-' + d.type, key: n.key,
            href: opts.linkFor ? opts.linkFor(d) : null,
            title: [noteOf(d, opts.notesLang), supportFull(d, opts.notesLang)].filter(Boolean).join('\n'),
            anchor: 'start', bg: 0
          });
          var tw = partsWidth(parts) + (tsup ? textWidth(' · ' + tsup) + 8 : 0) + (tail ? textWidth(' · ' + tail) + 10 : 0);
          maxLabelRight = Math.max(maxLabelRight, n.x + opts.labelGap + tw);
        }
      } else if (d.latin || d.zh) {
        var cparts = nameParts(d, opts.zhMode || 'both');
        var sup = opts.showSupport ? supportInline(d, opts.notesLang) : '';
        var isFamily = d.type === 'family';
        var isInternalFamily = isFamily && n.children.length > 0;
        var anchor, lx, ly;
        if (isInternalFamily) {
          // 科级内部节点（白蚁科）：放在其亚科之上的一行间隙，避免压住末端名称
          anchor = 'start';
          lx = n.x + 9;
          ly = n.topY - opts.rowH / 2;
        } else if (rankMode) {
          // 层级布局：支系名统一排在左侧「支系」栏，右对齐，垂直居中于该支系的叶范围
          anchor = 'end';
          lx = opts.padLeft - 10;
          ly = n.y;
        } else {
          anchor = 'start';
          lx = n.x + 9;
          ly = n.y;
        }
        var bg = partsWidth(cparts) + (sup ? textWidth(' · ' + sup) + 8 : 0) + 16;
        labels.push({
          x: lx, y: ly, parts: cparts, support: sup,
          suffix: '', tail: '', bg: bg, anchor: anchor,
          cls: 'clade-name ' + (isFamily ? 'clade-family' : 'clade-clade') +
               ((d.edgeUncertain || d.uncertain) ? ' is-uncertain' : ''),
          key: n.key, href: null,
          title: [noteOf(d, opts.notesLang), supportFull(d, opts.notesLang)].filter(Boolean).join('\n')
        });
        if (anchor === 'start') maxLabelRight = Math.max(maxLabelRight, lx + bg);
      }
      n.children.forEach(collectLabels);
    })(rootNode);

    // rank 布局：支系名同处左栏，做最小间距去重叠（保持自上而下的嵌套顺序）
    if (rankMode) {
      var colLabels = labels.filter(function (l) { return l.cls.indexOf('clade-name') === 0; });
      colLabels.sort(function (a, b) { return a.y - b.y; });
      var minGap = 22;
      for (var ci = 1; ci < colLabels.length; ci++) {
        if (colLabels[ci].y < colLabels[ci - 1].y + minGap) colLabels[ci].y = colLabels[ci - 1].y + minGap;
      }
    }

    // 右边界：末端名称与支系名称的最大延伸
    var width = Math.max(opts.padLeft + maxX + opts.labelGap + 40, maxLabelRight + opts.padRight);

    return {
      width: Math.ceil(width), height: Math.ceil(height), maxX: maxX,
      leaves: leaves.length, nodes: nodes, root: rootNode,
      lines: lines, bands: bands, labels: labels, guides: guides, opts: opts, mode: opts.mode
    };
  }

  /* ---------------- DOM 渲染 ---------------- */
  var SVGNS = 'http://www.w3.org/2000/svg';
  function svgEl(tag, attrs) {
    var e = document.createElementNS(SVGNS, tag);
    if (attrs) for (var k in attrs) {
      if (attrs[k] == null) continue;
      if (k === 'text') e.textContent = attrs[k];
      else e.setAttribute(k, attrs[k]);
    }
    return e;
  }

  function render(container, payload, ui) {
    var state = {
      collapsed: {},
      zhMode: ui.defaultNames || 'both',
      view: 'tree',
      mode: 'cladogram',
      showSupport: true
    };
    var toolbar = document.getElementById('phylo-toolbar');
    var treeWrap = document.getElementById('phylo-tree');
    var tableWrap = document.getElementById('phylo-table-wrap');
    if (!treeWrap) return;

    var notesLang = ui.lang === 'zh' ? 'zh' : 'en';

    function linkFor(d) { return d.id ? (ui.listBase || '/list/') + '#' + d.id : null; }

    function countLeaves(d) {
      if (!d.children || !d.children.length) return 1;
      return d.children.reduce(function (a, c) { return a + countLeaves(c); }, 0);
    }

    function nodeKey(data, index) {
      return (data.id || (data.type + ':' + (data.latin || '?'))) + '#' + (index || 0);
    }

    function cloneTree(data, parentKey, index) {
      var copy = {}, k;
      for (k in data) if (k !== 'children') copy[k] = data[k];
      copy.__key = (parentKey ? parentKey + '>' : '') + nodeKey(data, index);
      copy.__collapsed = !!state.collapsed[copy.__key];
      if (data.children && data.children.length) {
        if (copy.__collapsed) {
          copy.__collapsedCount = countLeaves(data) + ' ' + (ui.taxaUnit || '');
          copy.children = null;
        } else {
          copy.children = data.children.map(function (c, i) { return cloneTree(c, copy.__key, i); });
        }
      } else copy.children = null;
      return copy;
    }

    function findKey(data, targetId, parentKey, index) {
      var full = (parentKey ? parentKey + '>' : '') + nodeKey(data, index);
      if (data.id === targetId) return full;
      var kids = data.children || [];
      for (var i = 0; i < kids.length; i++) {
        var found = findKey(kids[i], targetId, full, i);
        if (found) return found;
      }
      return null;
    }

    function draw() {
      var data = cloneTree(payload.tree, null, 0);
      var layout = buildLayout(data, {
        lang: ui.lang, zhMode: state.zhMode, linkFor: linkFor,
        notesLang: notesLang, mode: state.mode, showSupport: state.showSupport,
        guideLabels: { clade: ui.guideClade, family: ui.guideFamily, subfamily: ui.guideSubfamily }
      });
      var keyByIndex = {};
      layout.nodes.forEach(function (n) { keyByIndex[n.key] = n.data.__key; });

      treeWrap.innerHTML = '';
      var svg = svgEl('svg', {
        viewBox: '0 0 ' + layout.width + ' ' + layout.height,
        width: layout.width, height: layout.height,
        role: 'img', 'aria-label': ui.ariaTree || 'phylogenetic tree'
      });
      svg.setAttribute('class', 'phylo-svg ' + (state.mode === 'rank' ? 'is-rank' : 'is-cladogram'));

      // 参考线
      layout.guides.forEach(function (g) {
        svg.appendChild(svgEl('path', { d: 'M' + g.x + ' ' + g.top + 'L' + g.x + ' ' + g.bottom, 'class': 'guide' }));
        if (g.label) {
          svg.appendChild(svgEl('text', { x: g.labelX, y: 22, 'class': 'guide-label', text: g.label }));
        }
      });

      // 背景带
      layout.bands.forEach(function (b) {
        svg.appendChild(svgEl('rect', { x: b.x, y: b.y, width: b.w, height: b.h, rx: 8, 'class': b.cls }));
      });

      // 分支
      layout.lines.forEach(function (l) {
        svg.appendChild(svgEl('path', { d: 'M' + l.x1 + ' ' + l.y1 + 'L' + l.x2 + ' ' + l.y2, 'class': l.cls }));
      });

      // 名称
      layout.labels.forEach(function (lb) {
        var g = svgEl('g', { 'class': 'label ' + lb.cls });
        if (lb.bg) {
          var rx = lb.anchor === 'end' ? lb.x - lb.bg + 8 : lb.x - 8;
          g.appendChild(svgEl('rect', { x: rx, y: lb.y - 10, width: lb.bg, height: 20, rx: 5, 'class': 'label-bg' }));
        }
        var text = svgEl('text', {
          x: lb.x, y: lb.y, 'dominant-baseline': 'central',
          'text-anchor': lb.anchor === 'end' ? 'end' : 'start'
        });
        lb.parts.forEach(function (p) {
          text.appendChild(svgEl('tspan', { 'class': 'part-' + p.cls, text: p.t }));
        });
        if (lb.support) text.appendChild(svgEl('tspan', { 'class': 'part-support', text: ' · ' + lb.support }));
        if (lb.suffix) text.appendChild(svgEl('tspan', { 'class': 'part-suffix', text: lb.suffix }));
        if (lb.tail) text.appendChild(svgEl('tspan', { 'class': 'part-tail', text: ' · ' + lb.tail }));
        if (lb.title) text.appendChild(svgEl('title', { text: lb.title }));

        if (lb.href) {
          var a = svgEl('a', { href: lb.href });
          a.appendChild(text);
          g.appendChild(a);
        } else g.appendChild(text);

        if (lb.cls.indexOf('clade-name') === 0) {
          g.setAttribute('tabindex', '0');
          g.setAttribute('role', 'button');
          g.addEventListener('click', function (ev) { ev.preventDefault(); toggle(keyByIndex[lb.key]); });
          g.addEventListener('keydown', function (ev) {
            if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); toggle(keyByIndex[lb.key]); }
          });
        }
        svg.appendChild(g);
      });

      treeWrap.appendChild(svg);
    }

    function toggle(key) {
      if (!key) return;
      if (state.collapsed[key]) delete state.collapsed[key];
      else state.collapsed[key] = true;
      draw();
    }

    function drawTable() {
      var rows = [];
      (function walk(d, depth) {
        rows.push({ d: d, depth: depth });
        (d.children || []).forEach(function (c) { walk(c, depth + 1); });
      })(payload.tree, 0);

      var esc = function (s) {
        return String(s == null ? '' : s).replace(/[&<>"]/g, function (m) {
          return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[m];
        });
      };
      var html = '<table class="phylo-table"><thead><tr>' +
        '<th>' + esc(ui.colRank) + '</th><th>' + esc(ui.colZh) + '</th><th>' + esc(ui.colLatin) + '</th>' +
        '<th class="num">' + esc(ui.colGenera) + '</th><th class="num">' + esc(ui.colSpecies) + '</th>' +
        '<th>' + esc(ui.colSupport) + '</th><th>' + esc(ui.colNote) + '</th></tr></thead><tbody>';
      rows.forEach(function (r) {
        var d = r.d, c = d.counts || {};
        if (!d.latin && !d.zh) return;
        var rank = d.type === 'clade' ? ui.rankClade : d.type === 'family' ? ui.rankFamily : ui.rankSubfamily;
        var indent = 'style="padding-left:' + (8 + r.depth * 12) + 'px"';
        var sup = supportFull(d, notesLang) || '—';
        html += '<tr class="rank-' + d.type + '">' +
          '<td>' + esc(rank) + '</td>' +
          '<td ' + indent + '>' + esc(d.zh || '—') + '</td>' +
          '<td><i>' + esc(d.latin || '—') + '</i></td>' +
          '<td class="num">' + (c.genera != null ? c.genera : '—') + '</td>' +
          '<td class="num">' + (c.species != null ? c.species : '—') + '</td>' +
          '<td class="support">' + esc(sup) + '</td>' +
          '<td class="note">' + esc(noteOf(d, notesLang)) + '</td></tr>';
      });
      html += '</tbody></table>';
      tableWrap.innerHTML = html;
    }

    function setPressed() {
      if (!toolbar) return;
      toolbar.querySelectorAll('[data-mode]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-mode') === state.zhMode)); });
      toolbar.querySelectorAll('[data-view]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-view') === state.view)); });
      toolbar.querySelectorAll('[data-layout]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-layout') === state.mode)); });
      var sb = toolbar.querySelector('[data-act="toggle-support"]');
      if (sb) sb.setAttribute('aria-pressed', String(state.showSupport));
    }

    if (toolbar) {
      toolbar.querySelectorAll('[data-act]').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var act = btn.getAttribute('data-act');
          if (act === 'expand') { state.collapsed = {}; draw(); }
          else if (act === 'collapse-terminidae') { state.collapsed = {}; var tk = findKey(payload.tree, 'termitidae', null, 0); if (tk) state.collapsed[tk] = true; draw(); }
          else if (act === 'names-both') { state.zhMode = 'both'; draw(); }
          else if (act === 'names-latin') { state.zhMode = 'latin'; draw(); }
          else if (act === 'names-zh') { state.zhMode = 'zh'; draw(); }
          else if (act === 'layout-cladogram') { state.mode = 'cladogram'; draw(); }
          else if (act === 'layout-rank') { state.mode = 'rank'; draw(); }
          else if (act === 'toggle-support') { state.showSupport = !state.showSupport; draw(); }
          else if (act === 'table') { state.view = 'table'; drawTable(); treeWrap.hidden = true; tableWrap.hidden = false; }
          else if (act === 'tree') { state.view = 'tree'; treeWrap.hidden = false; tableWrap.hidden = true; }
          else if (act === 'print') { window.print(); }
          setPressed();
        });
      });
    }

    draw();
    setPressed();
  }

  return { buildLayout: buildLayout, render: render, _textWidth: textWidth };
});