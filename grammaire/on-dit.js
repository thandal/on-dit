/* On dit: shared script for every page.
   1. Builds the contents rail and the previous/next links from PAGES.
   2. Turns {spoken*|written} tokens into <ruby> annotations, and exercise answers into tap-to-show chips.
   3. Runs the Written forms switch (remembered per browser). */

/* Reading order. To add a chapter, add its page here and to the outline in index.html. */
var PAGES = [
  {id:'intro',  href:'index.html',          label:'Introduction'},
  {id:'ch1',    href:'01-sons.html',        label:'1. Sounds and spelling'},
  {id:'ch2',    href:'02-noms.html',        label:'2. Nouns, articles, gender and number'},
  {id:'ch3',    href:'03-pronoms.html',     label:'3. Pronouns'},
  {id:'ch4',    href:'04-present.html',     label:'4. Verbs: the present'},
  {id:'ch5',    href:'05-passe-futur.html', label:'5. Verbs: past, future and possibility'},
  {id:'ch6',    href:'06-negation.html',    label:'6. Negation'},
  {id:'ch7',    href:'07-questions.html',   label:'7. Questions'},
  {id:'ch8',    href:'08-forme.html',       label:'8. Sentence shape'},
  {id:'ch9',    href:'09-relier.html',      label:'9. Joining ideas'},
  {id:'ch10',   href:'10-mots.html',        label:'10. Discourse words'},
  {id:'ch11',   href:'11-quotidien.html',   label:'11. Everyday frames'},
  {id:'annexe', href:'annexe.html',         label:'Appendix: coming from written French'}
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
    var clean = say.replace(/\*/g,'');
    r.setAttribute('aria-label', clean + ', written: ' + written);
    r.title = 'Written: ' + written;
    var sw = document.createElement('span');
    var parts = say.split('*');
    parts.forEach(function(p, i){
      sw.appendChild(document.createTextNode(p));
      if (i < parts.length - 1){
        var st = document.createElement('span');
        st.className = 'star'; st.textContent = '*'; st.setAttribute('aria-hidden','true');
        sw.appendChild(st);
      }
    });
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
  function toggle(el){
    if (el.matches('ruby.r')) el.classList.toggle('open');
    else el.setAttribute('aria-expanded', el.getAttribute('aria-expanded') === 'true' ? 'false' : 'true');
  }
  // A starred word inside an open answer toggles itself, not the answer.
  function target(e){ return e.target.closest && e.target.closest('ruby.r, .a'); }
  root.addEventListener('click', function(e){
    var t = target(e); if (t) toggle(t);
  });
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
    if (!on) document.querySelectorAll('ruby.r.open').forEach(function(r){ r.classList.remove('open'); });
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
