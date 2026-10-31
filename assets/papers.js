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
    synonymCount: '{n} synonyms',
    translate: 'Translate abstract',
    translateTo: 'Translate to',
    translating: 'Translating…',
    translateProgress: 'Translating… {n}%',
    translateShow: 'Show translation',
    translateHide: 'Hide translation',
    translateSame: 'The abstract is already in this language.',
    translateQuota: 'Today’s free translation quota is used up; use an external translator below.',
    translateError: 'Translation is unavailable right now; use an external translator below.',
    translateMachine: 'Machine translation for reference only; scientific names and technical terms may be inaccurate.',
    translateFallback: 'External translator',
    langZh: '中文',
    langEn: 'English',
    langEs: 'Español'
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

  // ---------------------------------------------------------------- 摘要翻译
  // 纯前端、无后端、无 API Key。默认提供方 MyMemory：CORS 开放，单次最多 500 字符，
  // 匿名额度按访客 IP 计（约 5000 字符/天），用尽后改用站点联系邮箱的额度重试；
  // 仍失败则退到 Google 翻译的非官方接口（部分地区网络不可达）。
  // 也可在 #papers-app 上配置 data-translate-url（LibreTranslate 兼容服务，可选
  // data-translate-key）优先使用，适合自建或 Cloudflare Worker 代理。
  // 译文写入 localStorage（按 原文+目标语言 哈希缓存），重复浏览不再消耗额度。
  var TRANSLATE_TIMEOUT = 15000;
  var TRANSLATE_TARGETS = ['zh-CN', 'en', 'es'];
  var TRANSLATE_LABELS = { 'zh-CN': 'langZh', 'en': 'langEn', 'es': 'langEs' };
  var TR_CACHE_PREFIX = 'papers-tr:v1:';
  var TR_CACHE_MAX = 40;
  var translateUid = 0;

  function translateError(code, detail) {
    var err = new Error(text(detail) || code);
    err.translateCode = code;
    return err;
  }
  function delay(ms) {
    return new Promise(function (resolve) { window.setTimeout(resolve, ms); });
  }
  function clip(value, max) {
    var s = text(value);
    return s.length > max ? s.slice(0, max) : s;
  }
  function byteLength(value) {
    var s = text(value);
    if (typeof window.TextEncoder === 'function') {
      try { return new window.TextEncoder().encode(s).length; } catch (e) { /* 回退按字符数 */ }
    }
    return s.length;
  }
  function hashText(value) {
    var s = text(value), h = 5381;
    for (var i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0;
    return (h >>> 0).toString(36);
  }
  function pageTargetLang() {
    var l = norm(app.getAttribute('data-lang') || '');
    if (l === 'en') return 'en';
    if (l === 'es') return 'es';
    return 'zh-CN';
  }
  // 摘要语种：先看中日韩字符占比（最可靠），再看元数据 language，最后按重音符号猜西语。
  function detectLang(sample, hint) {
    var s = text(sample);
    var cjk = (s.match(/[\u3400-\u9fff]/g) || []).length;
    if (cjk >= 8 && cjk / (s.length || 1) > 0.06) return 'zh-CN';
    // 西语特征优先于 language 元数据：英文里几乎不出现的西语功能词更有辨识度，
    // 可避免元数据缺失或标错时把西语摘要当英语送翻译。
    var esWords = (s.match(/\b(?:el|los|las|una|del|por|para|al|es|son|como|este|esta|entre|desde|más)\b/gi) || []).length;
    if (esWords >= 4) return 'es';
    var marks = (s.match(/[áéíóúüñ¿¡]/gi) || []).length;
    if (marks >= 3) return 'es';
    var h = norm(hint).replace(/_/g, '-');
    if (h.indexOf('zh') === 0) return 'zh-CN';
    if (h.indexOf('es') === 0) return 'es';
    if (h.indexOf('en') === 0) return 'en';
    return 'en';
  }
  // 机器翻译常把拉丁学名翻成无关词（Coptotermes formosanus → “台湾黄百合”）。
  // 翻译前把已知分类群名换成 [[n]] 占位符，译完再还原；实测该接口会原样保留占位符。
  var latinRegexCache = null, latinRegexSig = '';
  function latinNameList() {
    var seen = {}, out = [];
    function add(value) {
      var s = text(value).trim();
      if (!s || seen[norm(s)]) return;
      if (!/^[A-Z][a-z]{2,}(?:\s+[a-z][a-z-]+)?$/.test(s)) return;
      seen[norm(s)] = 1;
      out.push(s);
    }
    TERMITE_CONTEXT.forEach(add);
    if (state.selected) {
      add(state.selected.l);
      taxonSynonyms(state.selected).forEach(add);
    }
    if (state.taxa) {
      for (var i = 0; i < state.taxa.length; i++) {
        var entry = state.taxa[i];
        if (entry && entry.r === '属') add(entry.l);
      }
    }
    out.sort(function (a, b) { return b.length - a.length; });
    return out;
  }
  function latinRegex() {
    var sig = (state.selected ? state.selected.l : '') + '|' + (state.taxa ? '1' : '0');
    if (latinRegexSig === sig) return latinRegexCache;
    latinRegexSig = sig;
    var names = latinNameList();
    latinRegexCache = names.length
      ? new RegExp('\\b(?:' + names.map(function (n) {
        return n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\s+/g, '\\s+');
      }).join('|') + ')(?:\\s+[a-z][a-z-]+)?\\b', 'g')
      : null;
    return latinRegexCache;
  }
  function protectNames(chunk) {
    var re = latinRegex();
    var plain = { text: chunk, restore: function (v) { return text(v); } };
    if (!re) return plain;
    var map = [];
    re.lastIndex = 0;
    var masked = chunk.replace(re, function (match) {
      map.push({ token: '[[' + map.length + ']]', value: match });
      return map[map.length - 1].token;
    });
    if (!map.length) return plain;
    if (byteLength(masked) > 495) return plain;   // 占位符撑破单次上限时放弃保护
    return {
      text: masked,
      restore: function (translated) {
        var out = text(translated);
        for (var i = 0; i < map.length; i++) {
          if (out.indexOf(map[i].token) < 0) continue;
          out = out.split(map[i].token).join(map[i].value);
        }
        // 兼容接口给占位符加空格或换成全角方括号的情况
        out = out.replace(/\[\s*\[\s*(\d+)\s*\]\s*\]/g, function (whole, idx) {
          var item = map[Number(idx)];
          return item ? item.value : whole;
        });
        return out;
      }
    };
  }

  // 按制表符/空白边界切块，保持每块不超过接口字节上限；超长单词硬切。
  function splitChunks(raw, limit) {
    var s = text(raw).replace(/\s+/g, ' ').trim();
    if (!s) return [];
    var cap = limit || 480;
    if (byteLength(s) <= cap) return [s];
    var out = [], cur = '', words = s.split(' ');
    for (var i = 0; i < words.length; i++) {
      var w = words[i];
      if (!w) continue;
      if (cur && byteLength(cur + ' ' + w) > cap) { out.push(cur); cur = ''; }
      if (byteLength(w) > cap) {
        var rest = w;
        while (byteLength(rest) > cap) {
          var piece = rest.slice(0, cap);
          while (piece.length > 1 && byteLength(piece) > cap) piece = piece.slice(0, -1);
          out.push(piece);
          rest = rest.slice(piece.length);
        }
        cur = rest;
      } else {
        cur = cur ? cur + ' ' + w : w;
      }
    }
    if (cur) out.push(cur);
    return out;
  }
  function decodeEntities(value) {
    var s = text(value);
    if (!s || s.indexOf('&') < 0) return s;
    try {
      var doc = new DOMParser().parseFromString('<span>' + s.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</span>', 'text/html');
      return text(doc.body && doc.body.textContent).replace(/\u00a0/g, ' ').trim();
    } catch (e) {
      return s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"')
        .replace(/&#0?39;/g, "'").replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').trim();
    }
  }
  function fetchJsonTimeout(url, signal, ms) {
    var ctrl = new AbortController();
    var timedOut = false;
    var timer = window.setTimeout(function () { timedOut = true; ctrl.abort(); }, ms || TRANSLATE_TIMEOUT);
    function forward() { ctrl.abort(); }
    if (signal) {
      if (signal.aborted) ctrl.abort();
      else if (signal.addEventListener) signal.addEventListener('abort', forward);
    }
    function cleanup() {
      window.clearTimeout(timer);
      if (signal && signal.removeEventListener) signal.removeEventListener('abort', forward);
    }
    return fetchJson(url, ctrl.signal).then(function (data) {
      cleanup();
      return data;
    }, function (err) {
      cleanup();
      if (timedOut) throw translateError('error', 'timeout');
      throw err;
    });
  }

  function myMemoryRequest(chunk, from, to, withEmail) {
    var url = 'https://api.mymemory.translated.net/get?q=' + encodeURIComponent(chunk) +
      '&langpair=' + encodeURIComponent(from) + '%7C' + encodeURIComponent(to) + '&mt=1';
    if (withEmail) url += '&de=' + encodeURIComponent(MAILTO);
    return fetchJsonTimeout(url, null, TRANSLATE_TIMEOUT).then(function (data) {
      var detail = text(data && data.responseDetails);
      var status = text(data && data.responseStatus);
      if (data && data.quotaFinished) throw translateError('quota', detail || 'quota finished');
      if (status && status !== '200') {
        var quota = /quota|limit exceeded|all available|mymemory warning/i.test(detail);
        throw translateError(quota ? 'quota' : 'error', detail || ('status ' + status));
      }
      var out = decodeEntities(data && data.responseData && data.responseData.translatedText);
      if (!out) throw translateError('error', 'empty translation');
      return out;
    });
  }

  function gtxRequest(chunk, from, to) {
    var url = 'https://translate.googleapis.com/translate_a/single?client=gtx&dt=t&sl=' +
      encodeURIComponent(from) + '&tl=' + encodeURIComponent(to) + '&q=' + encodeURIComponent(chunk);
    return fetchJsonTimeout(url, null, 8000).then(function (data) {
      var segs = (Array.isArray(data) && Array.isArray(data[0])) ? data[0] : [];
      var out = segs.map(function (seg) { return Array.isArray(seg) ? text(seg[0]) : ''; }).join('');
      out = text(out).replace(/\s+/g, ' ').trim();
      if (!out) throw translateError('error', 'empty translation');
      return out;
    });
  }

  function libreRequest(provider, chunk, from, to) {
    var body = { q: chunk, source: from === 'zh-CN' ? 'zh' : from, target: to === 'zh-CN' ? 'zh' : to, format: 'text' };
    if (provider.key) body.api_key = provider.key;
    var ctrl = new AbortController();
    var timer = window.setTimeout(function () { ctrl.abort(); }, TRANSLATE_TIMEOUT);
    return fetch(provider.url, {
      method: 'POST',
      credentials: 'omit',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(body),
      signal: ctrl.signal
    }).then(function (res) {
      window.clearTimeout(timer);
      if (!res.ok) throw translateError(res.status === 429 ? 'quota' : 'error', 'HTTP ' + res.status);
      return res.json();
    }).then(function (data) {
      var out = text(data && data.translatedText).replace(/\s+/g, ' ').trim();
      if (!out) throw translateError('error', 'empty translation');
      return out;
    }).catch(function (err) {
      window.clearTimeout(timer);
      throw err && err.translateCode ? err : translateError('error', err && err.message);
    });
  }

  function translateProviderList() {
    var list = [];
    var customUrl = text(app.getAttribute('data-translate-url')).trim();
    if (customUrl) {
      list.push({ name: 'LibreTranslate', kind: 'libre', url: customUrl, key: text(app.getAttribute('data-translate-key')).trim(), chunk: 1200 });
    }
    // 420 字节留给 [[n]] 学名占位符，保证单次请求仍在接口 500 字符上限内。
    list.push({ name: 'MyMemory', kind: 'mymemory', chunk: 420 });
    list.push({ name: 'Google', kind: 'gtx', chunk: 1600 });
    return list;
  }

  // 同一时间只发一个翻译请求，避免多个卡片并发触发免费接口的速率限制。
  var translateQueue = Promise.resolve();
  function serialiseTranslate(task) {
    var run = translateQueue.then(function () { return task(); }, function () { return task(); });
    translateQueue = run.then(function () { return delay(160); }, function () { return delay(160); });
    return run;
  }
  function translateChunk(provider, chunk, from, to, withEmail) {
    return serialiseTranslate(function () {
      if (provider.kind === 'libre') return libreRequest(provider, chunk, from, to);
      if (provider.kind === 'gtx') return gtxRequest(chunk, from, to);
      return myMemoryRequest(chunk, from, to, withEmail);
    });
  }

  // 中文译文块之间直接相接；英/西语或 ASCII 边界再补空格。
  function joinChunks(parts, target) {
    var out = '';
    for (var i = 0; i < parts.length; i++) {
      var part = text(parts[i]).replace(/^\s+|\s+$/g, '');
      if (!part) continue;
      if (!out) { out = part; continue; }
      var needSpace = target !== 'zh-CN' || /[A-Za-z0-9)\]}.,;:]$/.test(out) || /^[A-Za-z0-9(\[{]/.test(part);
      out += (needSpace && !/\s$/.test(out) ? ' ' : '') + part;
    }
    return out.replace(/\s{2,}/g, ' ').trim();
  }

  // 按提供方顺序逐个尝试；每块单独请求，进度回调 (已完成块数, 总块数)。
  function translateText(fullText, from, to, onProgress) {
    // 顺手加载分类群索引：拿到全部属名后，学名保护能覆盖更多属（拿不到也不影响翻译）。
    if (!state.taxa && typeof loadTaxa === 'function') loadTaxa().catch(function () {});
    var providers = translateProviderList();
    var index = 0;
    var lastError = null;
    function attempt() {
      if (index >= providers.length) {
        return Promise.reject(lastError || translateError('error', 'no provider'));
      }
      var provider = providers[index++];
      var chunks = splitChunks(fullText, provider.chunk);
      if (!chunks.length) return Promise.reject(translateError('error', 'empty abstract'));
      var parts = [], pos = 0, withEmail = false;
      function step() {
        if (pos >= chunks.length) {
          return Promise.resolve({ text: joinChunks(parts, to), provider: provider.name });
        }
        var chunk = chunks[pos];
        var guarded = protectNames(chunk);
        return translateChunk(provider, guarded.text, from, to, withEmail).then(function (out) {
          parts.push(guarded.restore(out));
          pos += 1;
          if (onProgress) onProgress(pos, chunks.length);
          return step();
        }, function (err) {
          // 匿名额度用尽：改用站点邮箱额度重试同一块（每块只重试一次）。
          if (err && err.translateCode === 'quota' && provider.kind === 'mymemory' && !withEmail) {
            withEmail = true;
            return step();
          }
          throw err;
        });
      }
      return step().catch(function (err) {
        lastError = err;
        return attempt();
      });
    }
    return attempt();
  }

  function translateCacheKey(p, target) {
    return TR_CACHE_PREFIX + target + ':' + hashText(p.doi || p.title) + ':' + hashText(p.abstract);
  }
  function translateCacheGet(key) {
    try {
      var raw = window.localStorage ? window.localStorage.getItem(key) : null;
      if (!raw) return null;
      var obj = JSON.parse(raw);
      return obj && obj.t ? obj : null;
    } catch (e) { return null; }
  }
  function translateCachePrune() {
    try {
      var keys = [], i;
      for (i = 0; i < window.localStorage.length; i++) {
        var key = window.localStorage.key(i);
        if (key && key.indexOf(TR_CACHE_PREFIX) === 0) keys.push(key);
      }
      if (keys.length <= TR_CACHE_MAX) return;
      var rows = keys.map(function (k) {
        var ts = 0;
        try { ts = (JSON.parse(window.localStorage.getItem(k)) || {}).s || 0; } catch (e) { ts = 0; }
        return { k: k, ts: ts };
      }).sort(function (a, b) { return a.ts - b.ts; });
      for (i = 0; i < rows.length - TR_CACHE_MAX; i++) window.localStorage.removeItem(rows[i].k);
    } catch (e) { /* 隐私模式 / 配额异常：跳过清理 */ }
  }
  function translateCacheSet(key, translated, provider) {
    try {
      if (!window.localStorage) return;
      window.localStorage.setItem(key, JSON.stringify({ t: translated, p: provider || '', s: Date.now() }));
      translateCachePrune();
    } catch (e) { /* 存不下就不缓存，不影响本次显示 */ }
  }

  function translateFallbackUrl(kind, target, sample) {
    var chunk = clip(sample, 1800);
    if (kind === 'google') {
      return 'https://translate.google.com/?op=translate&sl=auto&tl=' + encodeURIComponent(target) +
        '&text=' + encodeURIComponent(chunk);
    }
    var bing = target === 'zh-CN' ? 'zh-Hans' : target;
    return 'https://www.bing.com/translator?ref=TThis&from=auto&to=' + encodeURIComponent(bing) +
      '&text=' + encodeURIComponent(chunk);
  }

  // 摘要卡里的翻译控件：目标语言（中/英/西，与站点三语一致）+ 翻译按钮 + 译文区。
  function renderTranslate(p) {
    var box = node('div', 'papers-translate');
    var row = node('div', 'papers-translate-row');
    var source = detectLang(p.abstract, p.language);
    var defaultTarget = pageTargetLang();
    if (defaultTarget === source) defaultTarget = defaultTarget === 'zh-CN' ? 'en' : 'zh-CN';
    translateUid += 1;
    var outId = 'papers-translate-out-' + translateUid;

    var select = document.createElement('select');
    select.className = 'papers-translate-select';
    select.setAttribute('aria-label', T.translateTo);
    TRANSLATE_TARGETS.forEach(function (code) {
      var option = document.createElement('option');
      option.value = code;
      option.textContent = T[TRANSLATE_LABELS[code]] || code;
      if (code === defaultTarget) option.selected = true;
      select.appendChild(option);
    });

    var button = node('button', 'papers-translate-btn', T.translate);
    button.type = 'button';
    button.setAttribute('aria-controls', outId);
    button.setAttribute('aria-expanded', 'false');

    var status = node('span', 'papers-translate-status');
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');

    var out = node('div', 'papers-translate-output');
    out.id = outId;
    out.hidden = true;
    var outText = node('p', 'papers-translate-text');
    var outMeta = node('p', 'papers-translate-meta');
    out.appendChild(outText);
    out.appendChild(outMeta);

    var fallback = node('p', 'papers-translate-fallback');
    fallback.hidden = true;

    row.appendChild(select);
    row.appendChild(button);
    row.appendChild(status);
    box.appendChild(row);
    box.appendChild(out);
    box.appendChild(fallback);

    var view = { busy: false, shown: false, text: '', provider: '', lang: '', token: 0 };

    function showTranslation() {
      view.shown = true;
      out.hidden = false;
      outText.hidden = !view.text;
      outText.textContent = view.text;
      if (view.text) outText.setAttribute('lang', view.lang);
      outMeta.textContent = view.text
        ? ((view.provider ? view.provider + ' · ' : '') + T.translateMachine)
        : T.translateSame;
      fallback.hidden = true;
      status.textContent = '';
      status.className = 'papers-translate-status';
      button.disabled = false;
      select.disabled = false;
      button.textContent = T.translateHide;
      button.setAttribute('aria-expanded', 'true');
    }
    function hideTranslation() {
      view.shown = false;
      out.hidden = true;
      button.textContent = view.text ? T.translateShow : T.translate;
      button.setAttribute('aria-expanded', 'false');
    }
    function renderFallback(target) {
      clearNode(fallback);
      fallback.appendChild(node('span', 'papers-translate-fallback-label', T.translateFallback));
      [['google', 'Google'], ['bing', 'Bing']].forEach(function (item) {
        var link = node('a', null, item[1]);
        link.href = translateFallbackUrl(item[0], target, p.abstract);
        link.target = '_blank';
        link.rel = 'noopener';
        fallback.appendChild(link);
      });
    }
    function fail(err) {
      view.busy = false;
      view.shown = false;
      button.disabled = false;
      select.disabled = false;
      button.textContent = T.translate;
      button.setAttribute('aria-expanded', 'false');
      out.hidden = true;
      status.textContent = (err && err.translateCode === 'quota') ? T.translateQuota : T.translateError;
      status.className = 'papers-translate-status is-error';
      renderFallback(select.value);
      fallback.hidden = false;
    }
    function start(target) {
      if (view.busy) return;
      // 换目标语言时丢掉上一语言的译文，避免失败后仍显示旧语言内容
      if (view.lang && view.lang !== target) { view.text = ''; view.provider = ''; }
      view.busy = true;
      view.shown = false;
      var token = ++view.token;
      view.lang = target;
      fallback.hidden = true;
      status.className = 'papers-translate-status';
      if (source === target) {
        view.busy = false;
        view.text = '';
        view.provider = '';
        showTranslation();
        return;
      }
      var cacheKey = translateCacheKey(p, target);
      var cached = translateCacheGet(cacheKey);
      if (cached) {
        view.busy = false;
        view.text = text(cached.t);
        view.provider = text(cached.p);
        showTranslation();
        return;
      }
      button.disabled = true;
      select.disabled = true;
      button.textContent = T.translating;
      status.textContent = T.translating;
      out.hidden = true;
      translateText(p.abstract, source, target, function (done, total) {
        if (token !== view.token) return;
        if (total > 1) status.textContent = T.translateProgress.replace('{n}', String(Math.round(done / total * 100)));
      }).then(function (res) {
        if (token !== view.token) return;
        view.busy = false;
        view.text = res.text;
        view.provider = res.provider;
        translateCacheSet(cacheKey, res.text, res.provider);
        showTranslation();
      }).catch(function (err) {
        if (token !== view.token) return;
        fail(err);
      });
    }

    button.addEventListener('click', function () {
      if (view.busy) return;
      if (view.shown) { hideTranslation(); return; }
      if (view.text) { showTranslation(); return; }
      start(select.value);
    });
    select.addEventListener('change', function () {
      if (view.busy) return;
      if (view.shown || view.text) start(select.value);
    });
    return box;
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
    wrap.appendChild(renderTranslate(p));
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
