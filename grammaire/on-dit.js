/* On dit: shared script for every page.
   1. Builds the contents rail and the previous/next links from PAGES.
   2. Turns {spoken|written} tokens into orange <ruby> words: tapping one opens a pop-up with its standard spelling(s);
      the Written forms switch shows them above every orange word. Turns exercise answers into tap-to-show chips.
   3. Runs the Written forms switch (remembered per browser). */

/* Reading order. To add a chapter, add its page here and to the outline in index.html. */
var PAGES = [
  {id:'intro',  href:'index.html',           label:'Introduction'},
  {id:'ch1',    href:'01-sons.html',         label:'1. Sounds and spelling'},
  {id:'ch2',    href:'02-noms.html',         label:'2. Nouns, articles, gender and number'},
  {id:'ch3',    href:'03-pronoms.html',      label:'3. Pronouns'},
  {id:'ch4',    href:'04-present.html',      label:'4. Verbs: the present'},
  {id:'ch5',    href:'05-passe-futur.html',  label:'5. Verbs: the everyday past and future'},
  {id:'ch6',    href:'06-autres-temps.html', label:'6. Verbs: other common forms'},
  {id:'ch7',    href:'07-negation.html',     label:'7. Negation'},
  {id:'ch8',    href:'08-questions.html',    label:'8. Questions'},
  {id:'ch9',    href:'09-forme.html',        label:'9. Sentence shape'},
  {id:'ch10',   href:'10-relier.html',       label:'10. Joining ideas'},
  {id:'ch11',   href:'11-mots.html',         label:'11. Discourse words'},
  {id:'ch12',   href:'12-quotidien.html',    label:'12. Everyday frames'},
  {id:'ch13',   href:'13-lieu-temps.html',   label:'13. Place and time'},
  {id:'annexe', href:'annexe.html',          label:'Appendix: coming from written French'},
  {id:'listes', href:'listes.html',          label:'Appendix: useful lists'}
];

(function(){
  var here = document.body.getAttribute('data-page');
  var main = document.querySelector('main');

  function el(tag, attrs, text){
    var e = document.createElement(tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text) e.textContent = text;
    return e;
  }
  // Headings on this page that get a contents entry: chapter sections (h3 with an id) and h2s with an id.
  function onPage(){
    var ol = el('ol', {'class':'onpage'});
    main.querySelectorAll('h2[id], h3[id]').forEach(function(h){
      var li = el('li'); var a = el('a', {href:'#' + h.id});
      a.textContent = h.textContent.replace(/^Appendix · Coming from written French/, '');
      li.appendChild(a); ol.appendChild(li);
    });
    return ol.children.length ? ol : null;
  }
  function list(cls){
    var ol = el('ol', cls ? {'class':cls} : {});
    PAGES.forEach(function(p){
      var li = el('li'); var a = el('a', {href:p.href}, p.label);
      if (p.id === here){ li.className = 'here'; a.setAttribute('aria-current','page'); }
      li.appendChild(a);
      if (p.id === here){ var sub = onPage(); if (sub) li.appendChild(sub); }
      ol.appendChild(li);
    });
    return ol;
  }
  var toc = document.getElementById('toc');
  if (toc){ toc.appendChild(el('p', {}, 'Contents')); toc.appendChild(list()); }
  var mob = document.getElementById('toc-mobile');
  if (mob) mob.appendChild(list());

  var i = PAGES.map(function(p){ return p.id; }).indexOf(here);
  if (i !== -1){
    var pager = el('nav', {'class':'pager', 'aria-label':'Previous and next'});
    [[i - 1, 'prev', 'Previous'], [i + 1, 'next', 'Next']].forEach(function(x){
      var p = PAGES[x[0]]; if (!p) return;
      var a = el('a', {href:p.href, 'class':x[1], rel:x[1]});
      a.appendChild(el('small', {}, x[2])); a.appendChild(document.createTextNode(p.label));
      pager.appendChild(a);
    });
    main.appendChild(pager);
  }
})();

(function(){
  var TOK = /\{([^|{}]+)\|([^{}]+)\}/g;
  var root = document.querySelector('main');

  function makeRuby(say, written){
    var r = document.createElement('ruby');
    r.className = 'r';
    r.tabIndex = 0;
    r.setAttribute('role','button');
    r.setAttribute('aria-label', say + ', written: ' + written);
    r.setAttribute('data-w', written);
    var sw = document.createElement('span');
    sw.textContent = say;
    r.appendChild(sw);
    var rt = document.createElement('rt');
    rt.textContent = written;
    r.appendChild(rt);
    return r;
  }

  var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
  var nodes = [];
  while (walker.nextNode()){ if (walker.currentNode.nodeValue.indexOf('{') !== -1) nodes.push(walker.currentNode); }
  nodes.forEach(function(n){
    var text = n.nodeValue, frag = document.createDocumentFragment(), last = 0, m;
    TOK.lastIndex = 0;
    while ((m = TOK.exec(text))){
      if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
      frag.appendChild(makeRuby(m[1], m[2]));
      last = TOK.lastIndex;
    }
    if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
    n.parentNode.replaceChild(frag, n);
  });

  // Exercise answers: <span class="a">…</span> shows as an "answer" chip until tapped.
  root.querySelectorAll('.a').forEach(function(a){
    var inner = document.createElement('span');
    while (a.firstChild) inner.appendChild(a.firstChild);
    a.appendChild(inner);
    a.tabIndex = 0;
    a.setAttribute('role','button');
    a.setAttribute('aria-expanded','false');
  });
  // One pop-up for the whole page, attached to <body> so scrolling tables can't clip it.
  // A token standing for several persons ("je pars · tu pars · il part") gets one line per form.
  var pop = document.createElement('div');
  pop.className = 'pop'; pop.hidden = true; pop.setAttribute('role','status');
  document.body.appendChild(pop);
  var current = null;
  function hidePop(){
    if (current) current.classList.remove('open');
    current = null; pop.hidden = true;
  }
  function showPop(r){
    if (current === r){ hidePop(); return; }
    hidePop();
    current = r; r.classList.add('open');
    pop.textContent = '';
    r.getAttribute('data-w').split(' · ').forEach(function(w){
      var line = document.createElement('span'); line.textContent = w; pop.appendChild(line);
    });
    pop.hidden = false;
    var b = r.getBoundingClientRect(), maxLeft = document.documentElement.clientWidth - pop.offsetWidth - 8;
    pop.style.left = (window.scrollX + Math.max(8, Math.min(b.left, maxLeft))) + 'px';
    pop.style.top = (window.scrollY + b.bottom + 6) + 'px';
  }
  function toggle(el){
    if (el.matches('ruby.r')) showPop(el);
    else el.setAttribute('aria-expanded', el.getAttribute('aria-expanded') === 'true' ? 'false' : 'true');
  }
  // An orange word inside an open answer toggles itself, not the answer.
  function target(e){ return e.target.closest && e.target.closest('ruby.r, .a'); }
  document.addEventListener('click', function(e){
    var t = root.contains(e.target) ? target(e) : null;
    if (t) toggle(t); else if (!pop.contains(e.target)) hidePop();
  });
  document.addEventListener('keydown', function(e){ if (e.key === 'Escape') hidePop(); });
  window.addEventListener('resize', hidePop);
  root.addEventListener('keydown', function(e){
    if ((e.key === 'Enter' || e.key === ' ') && e.target.matches && e.target.matches('ruby.r, .a')){
      e.preventDefault(); toggle(e.target);
    }
  });

  var btn = document.getElementById('wswitch'), state = document.getElementById('wstate');
  function set(on){
    document.body.classList.toggle('show-written', on);
    btn.setAttribute('aria-checked', on ? 'true' : 'false');
    state.textContent = on ? 'shown' : 'hidden';
  }
  var saved = false;
  try { saved = localStorage.getItem('ondit-written') === '1'; } catch(e){}
  set(saved);
  btn.addEventListener('click', function(){
    var on = !document.body.classList.contains('show-written');
    set(on);
    try { localStorage.setItem('ondit-written', on ? '1' : '0'); } catch(e){}
  });
})();
