/*
  文献检索器（/papers/ 三语页面，纯原生 JS，无依赖）
  数据源：OpenAlex（主，CORS）、Crossref（辅，CORS）、本站 papers-index.json（兜底缓存）。
  检索：自由关键词默认限定白蚁（等翅目）范围；多个关键词 AND；常见中英术语互扩（分子↔molecular）。
  摘要：OpenAlex abstract_inverted_index 还原；Crossref JATS 去标签；单 DOI 缺失时可再试 Semantic Scholar。
  注意：所有结果文本都用 textContent 写入，避免把 API 返回的 HTML 当页面 HTML 执行。
*/
(function () {
  'use strict';

  var app = document.getElementById('papers-app');
  if (!app) return;

  var BASE = app.getAttribute('data-base') || '';
  var INDEX_URL = app.getAttribute('data-index-url') || (BASE + '/search-index.json');
  var PAPERS_URL = app.getAttribute('data-papers-url') || (BASE + '/papers-index.json');
  var PER_PAGE = 20;
  var MAILTO = 'bennetgreen-bilibili@users.noreply.github.com';

  var DEFAULTS = {
    placeholder: 'Latin name, Chinese name or keyword',
    search: 'Search',
    hint: '',
    synonyms: 'Include synonyms',
    chineseOnly: 'Chinese-language papers only',
    hasAbstract: 'With abstract only',
    scope: 'Termite literature only',
    fulltext: 'Full-text search',
    sort: 'Sort',
    sortRelevance: 'Relevance',
    sortNewest: 'Newest',
    sortCited: 'Most cited',
    loading: 'Searching…',
    results: 'Found {n} results',
    noResults: 'No matching papers found.',
    error: 'Search failed: {msg}',
    cached: 'Live search is unavailable; showing cached genus-level papers.',
    more: 'Load more',
    abstract: 'Abstract',
    showAbstract: 'Show abstract',
    hideAbstract: 'Hide abstract',
    noAbstract: 'No abstract',
    tryAbstract: 'Try to fetch abstract',
    tryAbstractLoading: 'Fetching…',
    abstractSource: 'Abstract source',
    external: 'Search on other platforms',
    copy: 'Copy citation',
    copied: 'Copied',
    citeGbt: 'GB/T 7714',
    citeBibtex: 'BibTeX',
    citeRis: 'RIS',
    synonymBadge: 'synonym',
    cachedBadge: 'site cache',
    sourceOpenalex: 'OpenAlex',
    sourceCrossref: 'Crossref',
    sourceS2: 'Semantic Scholar',
    sourceCache: 'Site cache',
    abstractNote: '',
    cited: 'cited',
    clear: 'Clear',
    synonymCount: '{n} synonyms'
  };

  var T = DEFAULTS;
  try {
    var i18nNode = document.getElementById('papers-i18n');
    if (i18nNode) {
      var parsed = JSON.parse(i18nNode.textContent || '{}');
      for (var k in parsed) { if (Object.prototype.hasOwnProperty.call(parsed, k)) T[k] = parsed[k]; }
    }
  } catch (e) { /* 文案解析失败时用英文默认值，继续检索 */ }

  var els = {
    q: document.getElementById('papers-q'),
    form: document.getElementById('papers-form'),
    submit: document.getElementById('papers-submit'),
    suggestions: document.getElementById('papers-suggestions'),
    selected: document.getElementById('papers-selected'),
    syn: document.getElementById('papers-syn'),
    zh: document.getElementById('papers-zh'),
    hasAbstract: document.getElementById('papers-has-abstract'),
    scope: document.getElementById('papers-scope'),
    fulltext: document.getElementById('papers-fulltext'),
    sort: document.getElementById('papers-sort'),
    clear: document.getElementById('papers-clear'),
    status: document.getElementById('papers-status'),
    results: document.getElementById('papers-results'),
    more: document.getElementById('papers-more'),
    external: document.querySelectorAll('[data-external]')
  };
  if (!els.q || !els.form || !els.results) return;

  var state = {
    taxa: null,
    taxaPromise: null,
    cache: null,
    cachePromise: null,
    selected: null,
    mode: 'keyword',
    terms: [],
    context: [],
    query: '',
    results: [],
    page: 1,
    total: 0,
    hasMore: false,
    cacheMode: false,
    abort: null,
    synTouched: false,
    abstractFetching: false,
    activeSuggestion: -1
  };

  // ---------------------------------------------------------------- 基础工具
  function node(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = String(text);
    return n;
  }
  function clearNode(n) { while (n.firstChild) n.removeChild(n.firstChild); }
  function text(v) { return String(v === undefined || v === null ? '' : v); }
  function norm(v) { return text(v).toLowerCase(); }
  function compact(v) { return text(v).replace(/[^a-z0-9]/g, ''); }
  function safeStorageGet(key) {
    try { return window.sessionStorage ? window.sessionStorage.getItem(key) : null; } catch (e) { return null; }
  }
  function safeStorageSet(key, val) {
    try { if (window.sessionStorage) window.sessionStorage.setItem(key, val); } catch (e) { /* 忽略配额/隐私模式 */ }
  }
  function setStatus(message, cls) {
    els.status.textContent = message || '';
    els.status.className = 'papers-status' + (cls ? ' ' + cls : '');
  }
  function rankLabel(r) {
    var map = { '支系': 'Clade', '科': 'Family', '亚科': 'Subfamily', '属': 'Genus', '种': 'Species', '亚种': 'Subspecies' };
    return map[r] || r || '';
  }
  function sourceLabel(s) {
    if (s === 'openalex') return T.sourceOpenalex;
    if (s === 'crossref') return T.sourceCrossref;
    if (s === 's2') return T.sourceS2;
    return T.sourceCache;
  }
  function badge(label, cls) {
    var b = node('span', 'papers-badge' + (cls ? ' ' + cls : ''), label);
    return b;
  }

  // ---------------------------------------------------------------- 数据加载
  function fetchJson(url, signal) {
    return fetch(url, { signal: signal, credentials: 'same-origin', headers: { 'Accept': 'application/json' } })
      .then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
      });
  }

  function loadTaxa() {
    if (state.taxaPromise) return state.taxaPromise;
    state.taxaPromise = fetchJson(INDEX_URL, null).then(function (arr) {
      state.taxa = Array.isArray(arr) ? arr : [];
      return state.taxa;
    }).catch(function (err) {
      state.taxaPromise = null;
      throw err;
    });
    return state.taxaPromise;
  }

  function loadCache() {
    if (state.cachePromise) return state.cachePromise;
    state.cachePromise = fetchJson(PAPERS_URL, null).then(function (data) {
      state.cache = data;
      return data;
    }).catch(function (err) {
      state.cachePromise = null;
      throw err;
    });
    return state.cachePromise;
  }

  // ---------------------------------------------------------------- 自动补全
  function searchTaxa(raw) {
    var list = state.taxa || [];
    var q = norm(raw).trim();
    if (!q) return [];
    var qc = compact(q);
    var scored = [];
    for (var i = 0; i < list.length; i++) {
      var e = list[i];
      if (!e || !e.l) continue;
      var l = norm(e.l), z = norm(e.z), s = norm(e.s || ''), zt = norm(e.zt || '');
      var score = -1;
      if (l === q || z === q || zt === q || s === q) score = 0;
      else if (l.indexOf(q) === 0 || z.indexOf(q) === 0 || zt.indexOf(q) === 0) score = 1;
      else if (l.indexOf(q) >= 0 || z.indexOf(q) >= 0 || s.indexOf(q) >= 0 || zt.indexOf(q) >= 0) score = 2;
      else if (/^[a-z0-9][a-z0-9\s.\-'’]*$/.test(q) && qc.length >= 2) {
        var py = e.py || '', pi = e.pi || '';
        if (py && (py === qc || pi === qc)) score = 3;
        else if (py && py.indexOf(qc) >= 0) score = 4;
        else if (pi && qc.length >= 3 && pi.indexOf(qc) === 0) score = 5;
      }
      if (score >= 0) scored.push({ score: score, len: (l.length + z.length), e: e });
    }
    scored.sort(function (a, b) { return a.score - b.score || a.len - b.len; });
    return scored.slice(0, 9).map(function (x) { return x.e; });
  }

  function hideSuggestions() {
    els.suggestions.hidden = true;
    els.suggestions.textContent = '';
    state.activeSuggestion = -1;
    els.q.setAttribute('aria-expanded', 'false');
  }

  function renderSuggestions(list) {
    clearNode(els.suggestions);
    if (!list.length) { hideSuggestions(); return; }
    list.forEach(function (e, i) {
      var li = document.createElement('li');
      li.setAttribute('role', 'presentation');
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.setAttribute('role', 'option');
      btn.setAttribute('data-index', String(i));
      var rank = node('span', 'sug-rank', rankLabel(e.r));
      var latin = node('span', 'sug-latin', e.l);
      var zh = e.z ? node('span', 'sug-zh', e.z) : null;
      btn.appendChild(rank);
      btn.appendChild(latin);
      if (zh) btn.appendChild(zh);
      li.appendChild(btn);
      els.suggestions.appendChild(li);
    });
    els.suggestions.hidden = false;
    els.q.setAttribute('aria-expanded', 'true');
    state.activeSuggestion = -1;
  }

  function selectTaxon(e, fromSubmit) {
    state.selected = e || null;
    if (e) {
      if (els.q.value !== e.l) els.q.value = e.l;
      if (!state.synTouched) els.syn.checked = !!(e.s && e.s.length);
    }
    renderSelected();
    hideSuggestions();
    if (fromSubmit) runSearch(1);
  }

  function clearSelection() {
    state.selected = null;
    renderSelected();
  }

  function renderSelected() {
    var e = state.selected;
    if (!e) { els.selected.hidden = true; els.selected.textContent = ''; return; }
    var syns = e.s ? e.s.split(';').map(cleanSynonym).filter(Boolean) : [];
    var parts = [e.l];
    if (e.z) parts.push(e.z);
    if (e.r) parts.push(rankLabel(e.r));
    if (syns.length) parts.push(T.synonymCount.replace('{n}', String(syns.length)));
    els.selected.textContent = parts.join(' · ');
    els.selected.hidden = false;
  }

  function findExact(raw) {
    var q = norm(raw).trim();
    if (!q) return null;
    return loadTaxa().then(function (list) {
      for (var i = 0; i < list.length; i++) {
        var e = list[i];
        if (e && (norm(e.l) === q || norm(e.z) === q)) return e;
      }
      return null;
    }).catch(function () { return null; });
  }

  // ---------------------------------------------------------------- 查询构造
  function cleanSynonym(raw) {
    var s = text(raw).replace(/\s+/g, ' ').trim();
    if (!s) return '';
    var m = s.match(/^([A-Z][A-Za-z-]+(?:\s*\([^)]*\))?(?:\s+(?!(?:var|subsp|f)\.?\b)[a-z][A-Za-z-]+){1,2}(?:\s+(?:var|subsp|f)\.?\s+[a-z][A-Za-z-]+)*)/);
    var name = m ? m[1] : s.split(',')[0];
    return name.replace(/\s*\(\s*/g, ' (').replace(/\s*\)/g, ') ').replace(/\s+/g, ' ').trim();
  }

  function taxonSynonyms(e) {
    if (!e || !e.s) return [];
    var seen = {};
    return e.s.split(';').map(cleanSynonym).filter(function (s) {
      var key = norm(s);
      if (!s || seen[key]) return false;
      seen[key] = 1;
      return true;
    });
  }

  // 默认只检索白蚁（等翅目）文献；用户可在页面取消勾选。
  var TERMITE_CONTEXT = [
    'termite', 'termites', 'isoptera', '白蚁', '白蟻', '等翅目', '螱',
    'Coptotermes', 'Reticulitermes', 'Odontotermes', 'Macrotermes',
    'Nasutitermes', 'Heterotermes', 'Cryptotermes', 'Kalotermes',
    'Zootermopsis', 'Hodotermopsis', 'Microtermes', 'Trinervitermes',
    'Anoplotermes', 'Neotermes', 'Prorhinotermes', 'Schedorhinotermes',
    'Mastotermes', 'Hodotermes', 'Amitermes', 'Drepanotermes',
    'Microcerotermes', 'Globitermes', 'Hospitalitermes',
    'Termitidae', 'Rhinotermitidae', 'Kalotermitidae', 'Hodotermitidae',
    'Mastotermitidae', 'Termopsidae', 'Archotermopsidae', 'Stolotermitidae',
    'Serritermitidae'
  ];

  // 常见中英术语互扩：中文关键词也能命中英文论文，反之亦然。
  // 只做整词映射，不做语义猜测；每个关键词内部用 OR，关键词之间用 AND。
  var KEYWORD_ALIASES = {
    '分子': ['molecular'], 'molecular': ['分子'],
    '生物学': ['biology'], 'biology': ['生物学'],
    '系统发育': ['phylogeny', 'phylogenetic'], '系统发生': ['phylogeny', 'phylogenetic'],
    'phylogeny': ['系统发育'], 'phylogenetic': ['系统发育'],
    '肠道': ['gut', 'hindgut', 'intestinal'],
    'gut': ['肠道'], 'hindgut': ['肠道'], 'intestinal': ['肠道'],
    '微生物': ['microbiota', 'microbial', 'microbe', 'microorganism'],
    'microbiota': ['微生物'], 'microbial': ['微生物'], 'microbe': ['微生物'], 'microorganism': ['微生物'],
    '共生': ['symbiosis', 'symbiotic'], 'symbiosis': ['共生'], 'symbiotic': ['共生'],
    '基因': ['gene', 'genetic'], 'gene': ['基因'], 'genetic': ['基因'],
    '基因组': ['genome', 'genomic'], 'genome': ['基因组'], 'genomic': ['基因组'],
    '线粒体': ['mitochondrial', 'mitochondrion'],
    'mitochondrial': ['线粒体'], 'mitochondrion': ['线粒体'],
    '转录组': ['transcriptome', 'transcriptomic'],
    'transcriptome': ['转录组'], 'transcriptomic': ['转录组'],
    '蛋白': ['protein'], 'protein': ['蛋白'],
    '酶': ['enzyme'], 'enzyme': ['酶'],
    '分类': ['taxonomy', 'taxonomic'], 'taxonomy': ['分类'], 'taxonomic': ['分类'],
    '进化': ['evolution', 'evolutionary'], 'evolution': ['进化'], 'evolutionary': ['进化'],
    '生态': ['ecology', 'ecological'], 'ecology': ['生态'], 'ecological': ['生态'],
    '行为': ['behavior', 'behaviour'], 'behavior': ['行为'], 'behaviour': ['行为'],
    '食性': ['feeding', 'diet'], 'feeding': ['食性'], 'diet': ['食性'],
    '木材': ['wood'], 'wood': ['木材'],
    '纤维素': ['cellulose'], 'cellulose': ['纤维素'],
    '抗性': ['resistance'], 'resistance': ['抗性'],
    '杀虫剂': ['insecticide'], 'insecticide': ['杀虫剂'],
    '信息素': ['pheromone'], 'pheromone': ['信息素'],
    '菌圃': ['fungus comb'], 'fungus comb': ['菌圃'],
    '品级': ['caste'], 'caste': ['品级'],
    '工蚁': ['worker'], 'worker': ['工蚁'],
    '兵蚁': ['soldier'], 'soldier': ['兵蚁'],
    '繁殖蚁': ['alate', 'reproductive'], 'alate': ['繁殖蚁'], 'reproductive': ['繁殖蚁']
  };

  var MAX_KEYWORDS = 8;

  function scopeOn() { return !els.scope || els.scope.checked; }
  function fulltextOn() { return !!(els.fulltext && els.fulltext.checked); }

  function parseKeywords(raw) {
    var s = text(raw).replace(/[\u201c\u201d]/g, '"');
    var out = [], cur = '', quoted = false;
    for (var i = 0; i < s.length; i++) {
      var ch = s.charAt(i);
      if (ch === '"') { quoted = !quoted; continue; }
      if (!quoted && /[\s,，;；、|]/.test(ch)) {
        if (cur.trim()) out.push(cur.trim());
        cur = '';
      } else {
        cur += ch;
      }
    }
    if (cur.trim()) out.push(cur.trim());
    var seen = {}, terms = [];
    for (var j = 0; j < out.length; j++) {
      var term = out[j].replace(/\s+/g, ' ').trim();
      var key = norm(term);
      if (!term || seen[key]) continue;
      seen[key] = 1;
      terms.push(term);
      if (terms.length >= MAX_KEYWORDS) break;
    }
    return terms;
  }

  function aliasesFor(term) {
    var list = KEYWORD_ALIASES[norm(term).trim()];
    return Array.isArray(list) ? list : [];
  }

  function termGroup(term) {
    var out = [term], seen = {};
    seen[norm(term)] = 1;
    aliasesFor(term).forEach(function (alias) {
      var key = norm(alias);
      if (alias && !seen[key]) { seen[key] = 1; out.push(alias); }
    });
    return out;
  }

  function buildSearch() {
    var raw = text(els.q.value).trim();
    var e = state.selected;
    if (e) {
      var orTerms = [];
      if (els.zh.checked && e.z) {
        orTerms.push(e.z);
      } else {
        orTerms.push(e.l);
        if (els.syn.checked) {
          taxonSynonyms(e).forEach(function (s) {
            if (s && norm(s) !== norm(e.l)) orTerms.push(s);
          });
        }
      }
      var seen = {}, terms = [];
      orTerms.forEach(function (t) {
        var key = norm(t);
        if (t && !seen[key]) { seen[key] = 1; terms.push(t); }
      });
      return { mode: 'taxon', terms: terms, context: [] };
    }
    var keywords = parseKeywords(raw);
    if (!keywords.length) return null;
    return { mode: 'keyword', terms: keywords, context: TERMITE_CONTEXT.slice() };
  }

  function quoteTerm(term) {
    var clean = text(term).replace(/["|,]/g, ' ').replace(/\s+/g, ' ').trim();
    return '"' + clean + '"';
  }

  // 关键词模式：每个关键词生成一个 AND 过滤器；关键词内部与中英别名之间是 OR。
  // 默认搜标题+摘要；勾选“全文检索”后改用 default.search（含全文，召回更高）。
  function openAlexUrl(page) {
    var filters = [];
    var field = fulltextOn() ? 'default.search' : 'title_and_abstract.search';
    if (state.mode === 'taxon') {
      filters.push('title_and_abstract.search:' + state.terms.map(quoteTerm).join('|'));
    } else if (state.mode === 'keyword') {
      state.terms.forEach(function (t) {
        filters.push(field + ':' + termGroup(t).map(quoteTerm).join('|'));
      });
      if (scopeOn() && state.context.length) {
        filters.push('title_and_abstract.search:' + state.context.map(quoteTerm).join('|'));
      }
    }
    if (els.zh.checked) filters.push('language:zh');
    filters.push('type:article|review|book-chapter|preprint');
    var params = new URLSearchParams();
    params.set('filter', filters.join(','));
    params.set('per-page', String(PER_PAGE));
    params.set('page', String(page));
    params.set('select', 'id,doi,title,publication_year,publication_date,authorships,primary_location,type,language,cited_by_count,open_access,biblio,abstract_inverted_index');
    var sort = els.sort.value;
    if (sort === 'newest') params.set('sort', 'publication_year:desc');
    else if (sort === 'cited') params.set('sort', 'cited_by_count:desc');
    return 'https://api.openalex.org/works?' + params.toString();
  }

  function crossrefUrl(page) {
    var parts = [];
    state.terms.forEach(function (t) {
      parts.push(t);
      if (state.mode === 'keyword') aliasesFor(t).forEach(function (a) { parts.push(a); });
    });
    if (state.mode === 'keyword' && scopeOn()) parts.push('termite', 'isoptera', '白蚁');
    var q = parts.join(' ');
    var params = new URLSearchParams();
    params.set('query.bibliographic', q);
    params.set('rows', String(PER_PAGE));
    params.set('offset', String((page - 1) * PER_PAGE));
    params.set('filter', 'type:journal-article');
    params.set('mailto', MAILTO);
    return 'https://api.crossref.org/works?' + params.toString();
  }

  function haystack(p) {
    return norm(text(p.title) + ' ' + text(p.abstract));
  }

  function textHasTerm(hay, term) {
    var t = norm(term).trim();
    if (!t) return true;
    if (hay.indexOf(t) >= 0) return true;
    var aliases = aliasesFor(term);
    for (var i = 0; i < aliases.length; i++) {
      if (hay.indexOf(norm(aliases[i])) >= 0) return true;
    }
    return false;
  }

  function hasTermiteContext(hay) {
    for (var i = 0; i < TERMITE_CONTEXT.length; i++) {
      if (hay.indexOf(norm(TERMITE_CONTEXT[i])) >= 0) return true;
    }
    return false;
  }

  // Crossref 只能做相关性检索，合并前用标题+摘要做一次本地校验，避免把无关结果带进来。
  function crossrefRelevant(p) {
    if (state.mode !== 'keyword') return true;
    var hay = haystack(p);
    for (var i = 0; i < state.terms.length; i++) {
      if (!textHasTerm(hay, state.terms[i])) return false;
    }
    if (scopeOn() && !hasTermiteContext(hay)) return false;
    return true;
  }

  // ---------------------------------------------------------------- 结果规范化
  function reconstructAbstract(inv) {
    if (!inv || typeof inv !== 'object') return '';
    var positions = [];
    Object.keys(inv).forEach(function (word) {
      var idxs = inv[word];
      if (!Array.isArray(idxs)) return;
      idxs.forEach(function (i) { positions.push([i, word]); });
    });
    positions.sort(function (a, b) { return a[0] - b[0]; });
    var out = positions.map(function (p) { return p[1]; }).join(' ');
    return out.replace(/\s+([,.;:!?])/g, '$1').replace(/\s+/g, ' ').trim();
  }

  function stripTags(html) {
    var raw = text(html);
    if (!raw) return '';
    try {
      var doc = new DOMParser().parseFromString(raw, 'text/html');
      return text(doc.body && (doc.body.textContent || doc.body.innerText)).replace(/\s+/g, ' ').trim();
    } catch (e) {
      return raw.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
    }
  }

  function cleanAbstract(value) {
    return text(value).replace(/^\s*Abstract\b[\s:.-]*/i, '').trim();
  }

  function openAlexPages(biblio) {
    if (!biblio) return '';
    if (biblio.first_page && biblio.last_page) return biblio.first_page + '-' + biblio.last_page;
    return biblio.first_page || biblio.last_page || '';
  }

  function fromOpenAlex(w) {
    var loc = w.primary_location || {};
    var src = loc.source || {};
    var biblio = w.biblio || {};
    var authors = (w.authorships || []).map(function (a) {
      return a && a.author ? a.author.display_name : '';
    }).filter(Boolean);
    var doi = text(w.doi).replace(/^https?:\/\/doi.org\//i, '');
    var abs = cleanAbstract(reconstructAbstract(w.abstract_inverted_index));
    return {
      key: w.id || doi || w.title || '',
      id: w.id || '',
      openalex_url: w.id || '',
      doi: doi,
      doi_url: doi ? ('https://doi.org/' + doi) : '',
      title: stripTags(w.title) || 'Untitled',
      year: w.publication_year || '',
      date: w.publication_date || '',
      authors: authors,
      venue: stripTags(src.display_name),
      type: text(w.type),
      language: text(w.language),
      cited_by: w.cited_by_count || 0,
      oa_url: (w.open_access && w.open_access.oa_url) || '',
      volume: text(biblio.volume),
      issue: text(biblio.issue),
      pages: openAlexPages(biblio),
      abstract: abs,
      abstract_source: abs ? 'openalex' : '',
      source: 'openalex'
    };
  }

  function fromCrossref(it) {
    var title = stripTags(Array.isArray(it.title) ? (it.title[0] || '') : it.title);
    var authors = (it.author || []).map(function (a) {
      return [a.given, a.family].filter(Boolean).join(' ').replace(/\s+/g, ' ').trim();
    }).filter(Boolean);
    var year = '';
    var parts = it.issued && it.issued['date-parts'];
    if (parts && parts[0] && parts[0][0]) year = parts[0][0];
    var venue = stripTags(Array.isArray(it['container-title']) ? (it['container-title'][0] || '') : it['container-title']);
    var doi = text(it.DOI);
    var abs = cleanAbstract(stripTags(it.abstract));
    return {
      key: doi || title,
      id: doi ? ('https://doi.org/' + doi) : '',
      openalex_url: '',
      doi: doi,
      doi_url: doi ? ('https://doi.org/' + doi) : '',
      title: title || 'Untitled',
      year: year,
      date: '',
      authors: authors,
      venue: venue,
      type: text(it.type),
      language: text(it.language),
      cited_by: 0,
      oa_url: '',
      volume: text(it.volume),
      issue: text(it.issue),
      pages: text(it.page),
      abstract: abs,
      abstract_source: abs ? 'crossref' : '',
      source: 'crossref'
    };
  }

  function dedupeKey(p) {
    if (p.doi) return 'doi:' + p.doi.toLowerCase();
    return 't:' + norm(p.title).replace(/[^a-z0-9]+/g, ' ').trim();
  }

  function mergeResults(primary, secondary) {
    var out = [];
    var seen = {};
    primary.forEach(function (p) {
      var k = dedupeKey(p);
      if (!seen[k]) { seen[k] = p; out.push(p); }
    });
    secondary.forEach(function (p) {
      var k = dedupeKey(p);
      if (seen[k]) {
        var existing = seen[k];
        if (!existing.abstract && p.abstract) {
          existing.abstract = p.abstract;
          existing.abstract_source = p.abstract_source;
        }
        if (!existing.oa_url && p.oa_url) existing.oa_url = p.oa_url;
      } else {
        seen[k] = p;
        out.push(p);
      }
    });
    return out;
  }

  function normalizeCachePaper(p) {
    var doi = text(p.doi);
    return {
      key: p.id || doi || p.title || '',
      id: text(p.id),
      openalex_url: text(p.openalex_url) || (p.id && /^W/.test(p.id) ? ('https://openalex.org/' + p.id) : ''),
      doi: doi,
      doi_url: doi ? ('https://doi.org/' + doi) : '',
      title: text(p.title) || 'Untitled',
      year: p.year || '',
      date: text(p.date),
      authors: Array.isArray(p.authors) ? p.authors : [],
      venue: text(p.venue),
      type: text(p.type),
      language: text(p.language),
      cited_by: p.cited_by || 0,
      oa_url: text(p.oa_url),
      volume: text(p.volume),
      issue: text(p.issue),
      pages: text(p.pages),
      abstract: text(p.abstract),
      abstract_source: text(p.abstract_source),
      source: 'cache'
    };
  }

  function sortResults(list) {
    var sort = els.sort.value;
    if (sort === 'newest') list.sort(function (a, b) { return (b.year || 0) - (a.year || 0); });
    else if (sort === 'cited') list.sort(function (a, b) { return (b.cited_by || 0) - (a.cited_by || 0); });
    return list;
  }

  // ---------------------------------------------------------------- 渲染
  function renderCard(p) {
    var card = node('article', 'papers-card');
    var head = node('div', 'papers-card-head');
    var h3 = node('h2', 'papers-card-title');
    var title = p.title || 'Untitled';
    var href = p.doi_url || p.openalex_url || '';
    if (href) {
      var a = node('a', null, title);
      a.href = href;
      a.target = '_blank';
      a.rel = 'noopener';
      h3.appendChild(a);
    } else {
      h3.textContent = title;
    }
    head.appendChild(h3);

    var badges = node('div', 'papers-badges');
    badges.appendChild(badge(sourceLabel(p.source), 'is-source'));
    if (p.type) badges.appendChild(badge(p.type));
    if (p.language === 'zh') badges.appendChild(badge('中文'));
    if (p.oa_url) badges.appendChild(badge('OA', 'is-oa'));
    head.appendChild(badges);
    card.appendChild(head);

    var meta = node('p', 'papers-meta');
    var metaParts = [];
    if (p.authors && p.authors.length) {
      metaParts.push(p.authors.slice(0, 6).join(', ') + (p.authors.length > 6 ? ' et al.' : ''));
    }
    if (p.year) metaParts.push(String(p.year));
    if (p.venue) metaParts.push(p.venue);
    meta.textContent = metaParts.join(' · ');
    if (meta.textContent) card.appendChild(meta);

    card.appendChild(renderAbstract(p));

    var foot = node('div', 'papers-card-foot');
    if (p.cited_by) foot.appendChild(node('span', null, String(p.cited_by) + ' ' + T.cited));
    if (p.doi) {
      var doiLink = node('a', null, 'DOI');
      doiLink.href = p.doi_url;
      doiLink.target = '_blank';
      doiLink.rel = 'noopener';
      foot.appendChild(doiLink);
    }
    if (p.oa_url) {
      var oaLink = node('a', null, 'OA');
      oaLink.href = p.oa_url;
      oaLink.target = '_blank';
      oaLink.rel = 'noopener';
      foot.appendChild(oaLink);
    }
    var citeButtons = node('div', 'papers-cite-buttons');
    citeButtons.appendChild(copyButton(T.citeGbt, function () { return citation(p, 'gbt'); }));
    citeButtons.appendChild(copyButton(T.citeBibtex, function () { return citation(p, 'bibtex'); }));
    citeButtons.appendChild(copyButton(T.citeRis, function () { return citation(p, 'ris'); }));
    foot.appendChild(citeButtons);
    card.appendChild(foot);
    return card;
  }

  function renderAbstract(p) {
    if (!p.abstract) {
      var missing = node('p', 'papers-abstract-missing', T.noAbstract);
      if (p.doi) {
        var btn = node('button', null, T.tryAbstract);
        btn.type = 'button';
        btn.addEventListener('click', function () { tryFetchAbstract(p, btn); });
        missing.appendChild(btn);
      }
      return missing;
    }
    var wrap = node('div', 'papers-abstract');
    var full = text(p.abstract);
    var previewText = full.length > 280 ? full.slice(0, 280).replace(/\s+\S*$/, '') + '…' : full;
    var preview = node('p', 'papers-abstract-preview', previewText);
    wrap.appendChild(preview);
    if (full.length > 280) {
      var more = node('button', 'papers-abstract-toggle', T.showAbstract);
      more.type = 'button';
      var fullNode = node('p', 'papers-abstract-full', full);
      fullNode.hidden = true;
      preview.appendChild(more);
      more.addEventListener('click', function () {
        var show = fullNode.hidden;
        fullNode.hidden = !show;
        more.textContent = show ? T.hideAbstract : T.showAbstract;
      });
      wrap.appendChild(fullNode);
    }
    var src = p.abstract_source || p.source;
    if (src) wrap.appendChild(node('span', 'papers-abstract-source', T.abstractSource + ': ' + sourceLabel(src)));
    return wrap;
  }

  function copyButton(label, getText) {
    var b = node('button', 'papers-copy', label);
    b.type = 'button';
    b.addEventListener('click', function () {
      copyText(getText()).then(function () { flash(b); }).catch(function () { /* 文本仍可手动选中 */ });
    });
    return b;
  }

  function flash(button) {
    if (!button.getAttribute('data-label')) button.setAttribute('data-label', button.textContent);
    button.textContent = T.copied;
    button.classList.add('is-copied');
    window.clearTimeout(button._papersTimer);
    button._papersTimer = window.setTimeout(function () {
      button.textContent = button.getAttribute('data-label');
      button.classList.remove('is-copied');
    }, 1600);
  }

  function copyText(value) {
    var raw = text(value);
    if (navigator.clipboard && window.isSecureContext && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(raw).catch(function () { return legacyCopy(raw); });
    }
    return legacyCopy(raw);
  }

  function legacyCopy(raw) {
    return new Promise(function (resolve, reject) {
      var area = document.createElement('textarea');
      area.value = raw;
      area.setAttribute('readonly', 'readonly');
      area.style.position = 'fixed';
      area.style.top = '-1000px';
      area.style.left = '-1000px';
      area.style.opacity = '0';
      document.body.appendChild(area);
      area.select();
      area.setSelectionRange(0, area.value.length);
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(area);
      if (ok) resolve(); else reject(new Error('copy-failed'));
    });
  }

  // ---------------------------------------------------------------- 引用格式
  function bibEscape(s) {
    return text(s).replace(/[\\{}&%$#_~^]/g, function (c) { return '\\' + c; });
  }
  function asciiKey(s) {
    return text(s).normalize ? text(s).normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[^A-Za-z0-9]/g, '') : text(s).replace(/[^A-Za-z0-9]/g, '');
  }
  function bibKey(p) {
    var first = (p.authors && p.authors[0]) ? p.authors[0] : 'anon';
    var last = first.split(/\s+/).pop() || 'anon';
    var titleWord = (p.title || 'untitled').split(/\s+/)[0] || 'untitled';
    return (asciiKey(last) || 'anon') + (p.year || '') + (asciiKey(titleWord) || 'untitled');
  }
  function citation(p, style) {
    var authors = p.authors || [];
    if (style === 'bibtex') {
      var lines = ['@article{' + bibKey(p) + ','];
      if (authors.length) lines.push('  author  = {' + bibEscape(authors.join(' and ')) + '},');
      lines.push('  title   = {' + bibEscape(p.title) + '},');
      if (p.venue) lines.push('  journal = {' + bibEscape(p.venue) + '},');
      if (p.year) lines.push('  year    = {' + p.year + '},');
      if (p.volume) lines.push('  volume  = {' + bibEscape(p.volume) + '},');
      if (p.issue) lines.push('  number  = {' + bibEscape(p.issue) + '},');
      if (p.pages) lines.push('  pages   = {' + bibEscape(p.pages) + '},');
      if (p.doi) lines.push('  doi     = {' + bibEscape(p.doi) + '},');
      lines.push('}');
      return lines.join('\n');
    }
    if (style === 'ris') {
      var ris = ['TY  - JOUR'];
      if (p.title) ris.push('TI  - ' + p.title);
      authors.forEach(function (a) { ris.push('AU  - ' + a); });
      if (p.year) ris.push('PY  - ' + p.year);
      if (p.venue) ris.push('JO  - ' + p.venue);
      if (p.volume) ris.push('VL  - ' + p.volume);
      if (p.issue) ris.push('IS  - ' + p.issue);
      if (p.pages) ris.push('SP  - ' + p.pages);
      if (p.doi) ris.push('DO  - ' + p.doi);
      ris.push('ER  - ');
      return ris.join('\n');
    }
    var gbtAuthors = authors.length ? authors.slice(0, 3).join(', ') + (authors.length > 3 ? ', et al' : '') : '';
    var gbt = [];
    if (gbtAuthors) gbt.push(gbtAuthors + '.');
    gbt.push((p.title || 'Untitled') + '[J].');
    var pub = [];
    if (p.venue) pub.push(p.venue);
    if (p.year) pub.push(String(p.year));
    if (p.volume) pub.push(p.volume + (p.issue ? '(' + p.issue + ')' : ''));
    if (p.pages) pub.push(p.pages);
    if (pub.length) gbt.push(pub.join(', ') + '.');
    if (p.doi) gbt.push('DOI: ' + p.doi + '.');
    return gbt.join(' ');
  }

  // ---------------------------------------------------------------- 摘要补取
  function applyAbstract(p, abs, source, holder, card) {
    p.abstract = text(abs);
    p.abstract_source = source || '';
    var replacement = renderAbstract(p);
    if (holder && holder.parentNode) holder.parentNode.replaceChild(replacement, holder);
  }

  function tryFetchAbstract(p, btn) {
    if (state.abstractFetching || !p.doi) return;
    state.abstractFetching = true;
    var original = btn.textContent;
    btn.disabled = true;
    btn.textContent = T.tryAbstractLoading;
    var key = 'papers-abs:' + p.doi.toLowerCase();
    var cached = safeStorageGet(key);
    if (cached) {
      try {
        var obj = JSON.parse(cached);
        applyAbstract(p, obj.text, obj.source, btn.closest('.papers-abstract-missing'));
        state.abstractFetching = false;
        return;
      } catch (e) { /* 坏缓存继续联网 */ }
    }
    fetchCrossrefAbstract(p.doi).then(function (r) {
      if (r) return r;
      return fetchS2Abstract(p.doi);
    }).then(function (r) {
      if (!r || !r.text) throw new Error('no abstract');
      safeStorageSet(key, JSON.stringify(r));
      applyAbstract(p, r.text, r.source, btn.closest('.papers-abstract-missing'));
    }).catch(function () {
      btn.disabled = false;
      btn.textContent = original;
    }).then(function () {
      state.abstractFetching = false;
    });
  }

  function fetchCrossrefAbstract(doi) {
    var url = 'https://api.crossref.org/works/' + doi.split('/').map(encodeURIComponent).join('/') + '?mailto=' + encodeURIComponent(MAILTO);
    return fetchJson(url, null).then(function (data) {
      var abs = data && data.message && data.message.abstract;
      if (!abs) return null;
      var cleaned = cleanAbstract(stripTags(abs));
      return cleaned ? { text: cleaned, source: 'crossref' } : null;
    }).catch(function () { return null; });
  }

  function fetchS2Abstract(doi) {
    var url = 'https://api.semanticscholar.org/graph/v1/paper/DOI:' + encodeURI(doi) + '?fields=title,abstract';
    return fetchJson(url, null).then(function (data) {
      var abs = cleanAbstract(data && data.abstract);
      return abs ? { text: abs.replace(/\s+/g, ' ').trim(), source: 's2' } : null;
    }).catch(function () { return null; });
  }

  // ---------------------------------------------------------------- 外部链接
  function updateExternalLinks(query) {
    var q = text(query).trim();
    var cnkiQ = (state.selected && state.selected.z) ? state.selected.z : q;
    var links = {
      openalex: 'https://openalex.org/works?search=' + encodeURIComponent(q),
      crossref: 'https://search.crossref.org/?q=' + encodeURIComponent(q),
      scholar: 'https://scholar.google.com/scholar?q=' + encodeURIComponent(q),
      cnki: 'https://kns.cnki.net/kns8s/defaultresult/index?kw=' + encodeURIComponent(cnkiQ),
      wanfang: 'https://s.wanfangdata.com.cn/paper?q=' + encodeURIComponent(cnkiQ),
      baidu: 'https://xueshu.baidu.com/s?wd=' + encodeURIComponent(cnkiQ),
      bhl: 'https://www.biodiversitylibrary.org/search?searchTerm=' + encodeURIComponent(q)
    };
    for (var i = 0; i < els.external.length; i++) {
      var a = els.external[i];
      var key = a.getAttribute('data-external');
      if (links[key]) a.href = links[key];
    }
  }

  // ---------------------------------------------------------------- 检索主流程
  function clearResults() {
    clearNode(els.results);
    state.results = [];
  }

  function renderResults(clearFirst) {
    if (clearFirst) clearNode(els.results);
    var frag = document.createDocumentFragment();
    state.results.forEach(function (p) { frag.appendChild(renderCard(p)); });
    els.results.appendChild(frag);
  }

  function runSearch(page) {
    page = page || 1;
    var built = buildSearch();
    if (!built) {
      setStatus(T.noResults);
      clearResults();
      els.more.hidden = true;
      return;
    }
    if (state.abort) state.abort.abort();
    state.abort = new AbortController();
    var signal = state.abort.signal;
    state.page = page;
    state.mode = built.mode;
    state.terms = built.terms;
    state.context = built.context;
    state.query = state.selected ? state.selected.l : text(els.q.value).trim();
    state.cacheMode = false;
    if (page === 1) { clearResults(); state.total = 0; }
    setStatus(T.loading);
    els.more.hidden = true;
    els.submit.disabled = true;
    updateExternalLinks(state.query);
    syncUrl();

    var oaPromise = fetchJson(openAlexUrl(page), signal).then(function (data) {
      return { ok: true, data: data };
    }).catch(function (err) {
      return { ok: false, err: err };
    });
    var crPromise = (page === 1 && !els.zh.checked) ? fetchJson(crossrefUrl(page), signal).then(function (data) {
      return { ok: true, data: data };
    }).catch(function (err) {
      return { ok: false, err: err };
    }) : Promise.resolve({ ok: false, skip: true });

    Promise.all([oaPromise, crPromise]).then(function (out) {
      if (signal.aborted) return;
      var oa = out[0], cr = out[1];
      if (!oa.ok && !cr.ok) {
        fallbackToCache(oa.err || cr.err);
        return;
      }
      var primary = oa.ok ? ((oa.data.results || []).map(fromOpenAlex)) : [];
      var secondary = cr.ok ? (((cr.data.message && cr.data.message.items) || []).map(fromCrossref).filter(crossrefRelevant)) : [];
      var merged = page === 1 ? mergeResults(primary, secondary) : primary;
      if (els.hasAbstract.checked) merged = merged.filter(function (p) { return !!p.abstract; });
      if (page === 1) {
        state.results = merged;
        state.total = oa.ok ? Math.max((oa.data.meta && oa.data.meta.count) || merged.length, merged.length) : merged.length;
      } else {
        state.results = state.results.concat(merged);
      }
      if (els.hasAbstract.checked) state.total = state.results.length;
      if (page === 1 && els.sort.value !== 'relevance') sortResults(state.results);
      renderResults(page === 1);
      state.hasMore = !els.hasAbstract.checked && state.results.length < state.total;
      els.more.hidden = !state.hasMore;
      if (state.results.length) {
        setStatus(T.results.replace('{n}', String(state.total || state.results.length)));
      } else {
        setStatus(T.noResults);
      }
      if (!oa.ok && cr.ok) {
        setStatus(T.results.replace('{n}', String(state.results.length)) + ' · ' + T.sourceOpenalex + ' unavailable', 'is-cached');
      }
    }).catch(function (err) {
      if (!signal.aborted) fallbackToCache(err);
    }).then(function () {
      els.submit.disabled = false;
    });
  }

  function fallbackToCache(err) {
    if (state.cacheMode) {
      setStatus(T.error.replace('{msg}', (err && err.message) || 'network'), 'is-error');
      els.submit.disabled = false;
      return;
    }
    state.cacheMode = true;
    setStatus(T.loading);
    loadCache().then(function () {
      var list = cacheResults();
      state.results = list;
      state.total = list.length;
      state.page = 1;
      state.hasMore = false;
      renderResults(true);
      els.more.hidden = true;
      if (list.length) setStatus(T.cached, 'is-cached');
      else setStatus(T.noResults);
    }).catch(function (e) {
      setStatus(T.error.replace('{msg}', (e && e.message) || (err && err.message) || 'network'), 'is-error');
    }).then(function () {
      els.submit.disabled = false;
    });
  }

  function cacheResults() {
    var data = state.cache;
    if (!data || !data.genera) return [];
    var q = norm(state.query).trim();
    var genusKey = state.selected ? state.selected.h : null;
    var pool = [];
    if (genusKey && data.genera[genusKey]) {
      pool = data.genera[genusKey].papers || [];
    } else {
      Object.keys(data.genera).forEach(function (k) {
        pool = pool.concat(data.genera[k].papers || []);
      });
    }
    var out = pool.filter(function (p) {
      if (els.zh.checked && p.language !== 'zh' && !/[\u4e00-\u9fff]/.test(text(p.title))) return false;
      if (els.hasAbstract.checked && !p.abstract) return false;
      if (genusKey) return true;
      var hay = norm(text(p.title) + ' ' + text(p.abstract));
      if (state.mode === 'keyword') {
        for (var i = 0; i < state.terms.length; i++) {
          if (!textHasTerm(hay, state.terms[i])) return false;
        }
        return state.terms.length > 0;
      }
      return q && hay.indexOf(q) >= 0;
    }).map(normalizeCachePaper);
    sortResults(out);
    return out;
  }

  // ---------------------------------------------------------------- URL 状态
  function syncUrl() {
    try {
      var params = new URLSearchParams();
      if (els.q.value.trim()) params.set('q', els.q.value.trim());
      if (!els.syn.checked) params.set('syn', '0');
      if (els.zh.checked) params.set('zh', '1');
      if (els.hasAbstract.checked) params.set('abs', '1');
      if (!scopeOn()) params.set('scope', '0');
      if (fulltextOn()) params.set('full', '1');
      if (els.sort.value !== 'relevance') params.set('sort', els.sort.value);
      var qs = params.toString();
      history.replaceState(null, '', location.pathname + (qs ? '?' + qs : ''));
    } catch (e) { /* file:// 或旧浏览器忽略 */ }
  }

  function restoreFromUrl() {
    try {
      var params = new URLSearchParams(location.search);
      var q = params.get('q') || '';
      if (params.get('syn') === '0') { els.syn.checked = false; state.synTouched = true; }
      if (params.get('zh') === '1') els.zh.checked = true;
      if (params.get('abs') === '1') els.hasAbstract.checked = true;
      if (params.get('scope') === '0' && els.scope) els.scope.checked = false;
      if (params.get('full') === '1' && els.fulltext) els.fulltext.checked = true;
      var sort = params.get('sort');
      if (sort && ['relevance', 'newest', 'cited'].indexOf(sort) >= 0) els.sort.value = sort;
      if (!q) return;
      els.q.value = q;
      findExact(q).then(function (entry) {
        if (entry) { state.selected = entry; renderSelected(); }
        runSearch(1);
      });
    } catch (e) { /* 忽略 */ }
  }

  // ---------------------------------------------------------------- 事件绑定
  var sugTimer = null;
  els.q.addEventListener('input', function () {
    clearTimeout(sugTimer);
    var raw = els.q.value;
    if (state.selected && raw !== state.selected.l) clearSelection();
    sugTimer = window.setTimeout(function () {
      if (!raw.trim() || raw.trim().length < 2) { hideSuggestions(); return; }
      loadTaxa().then(function () {
        renderSuggestions(searchTaxa(raw));
      }).catch(function () { hideSuggestions(); });
    }, 140);
  });
  els.q.addEventListener('focus', function () {
    loadTaxa().catch(function () {});
    if (els.q.value.trim().length >= 2) {
      loadTaxa().then(function () { renderSuggestions(searchTaxa(els.q.value)); }).catch(function () {});
    }
  });
  els.q.addEventListener('blur', function () { window.setTimeout(hideSuggestions, 180); });
  els.q.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape') { hideSuggestions(); return; }
    if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') {
      var buttons = els.suggestions.querySelectorAll('button[data-index]');
      if (!buttons.length) return;
      ev.preventDefault();
      if (ev.key === 'ArrowDown') state.activeSuggestion = (state.activeSuggestion + 1) % buttons.length;
      else state.activeSuggestion = state.activeSuggestion <= 0 ? buttons.length - 1 : state.activeSuggestion - 1;
      for (var i = 0; i < buttons.length; i++) buttons[i].classList.toggle('is-active', i === state.activeSuggestion);
      buttons[state.activeSuggestion].scrollIntoView({ block: 'nearest' });
      return;
    }
    if (ev.key === 'Enter' && !els.suggestions.hidden) {
      var active = els.suggestions.querySelector('button.is-active');
      if (active) {
        ev.preventDefault();
        var list = searchTaxa(els.q.value);
        var idx = parseInt(active.getAttribute('data-index'), 10);
        if (list[idx]) selectTaxon(list[idx], true);
      }
    }
  });
  els.suggestions.addEventListener('click', function (ev) {
    var btn = ev.target.closest ? ev.target.closest('button[data-index]') : null;
    if (!btn) return;
    var idx = parseInt(btn.getAttribute('data-index'), 10);
    var list = searchTaxa(els.q.value);
    if (list[idx]) selectTaxon(list[idx], true);
  });
  els.form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var raw = els.q.value.trim();
    if (!raw && state.selected) raw = state.selected.l;
    if (!raw) { setStatus(T.noResults); return; }
    findExact(raw).then(function (entry) {
      if (entry) { state.selected = entry; renderSelected(); if (!state.synTouched) els.syn.checked = !!(entry.s && entry.s.length); }
      else if (state.selected) clearSelection();
      runSearch(1);
    });
  });
  els.more.addEventListener('click', function () { runSearch(state.page + 1); });
  els.clear.addEventListener('click', function () {
    els.q.value = '';
    state.query = '';
    clearSelection();
    clearResults();
    setStatus('');
    els.more.hidden = true;
    els.syn.checked = true;
    els.zh.checked = false;
    els.hasAbstract.checked = false;
    if (els.scope) els.scope.checked = true;
    if (els.fulltext) els.fulltext.checked = false;
    els.sort.value = 'relevance';
    state.synTouched = false;
    hideSuggestions();
    try { history.replaceState(null, '', location.pathname); } catch (e) { /* ignore */ }
  });
  [els.syn, els.zh, els.hasAbstract, els.scope, els.fulltext].forEach(function (cb) {
    if (!cb) return;
    cb.addEventListener('change', function () {
      if (cb === els.syn) state.synTouched = true;
      if (state.query) runSearch(1);
    });
  });
  els.sort.addEventListener('change', function () { if (state.query) runSearch(1); });
  Array.prototype.forEach.call(document.querySelectorAll('[data-example]'), function (btn) {
    btn.addEventListener('click', function () {
      els.q.value = btn.getAttribute('data-example') || '';
      clearSelection();
      findExact(els.q.value).then(function (entry) {
        if (entry) { state.selected = entry; renderSelected(); }
        runSearch(1);
      });
    });
  });

  // ---------------------------------------------------------------- 启动
  // 索引 466 KB，不在首屏无条件下载；输入/聚焦时才加载（带 ?q= 的分享链接仍会立即加载）。
  restoreFromUrl();
  updateExternalLinks('');
})();
