(function(){
  var toggle=document.getElementById('menu-toggle'),sb=document.getElementById('sidebar');
  if(toggle&&sb){
    // mobile menu: announces its state, moves focus in, closes on Escape and returns focus to the button
    toggle.setAttribute('aria-controls','sidebar');toggle.setAttribute('aria-expanded','false');
    function setMenu(open,refocus){
      sb.classList.toggle('open',open);toggle.setAttribute('aria-expanded',String(open));
      toggle.setAttribute('aria-label',open?'Close menu':'Open menu');
      if(open){var f=sb.querySelector('#search')||sb.querySelector('a');if(f)f.focus();}
      else if(refocus){toggle.focus();}
    }
    toggle.addEventListener('click',function(){setMenu(!sb.classList.contains('open'),false);});
    var st=document.getElementById('search-toggle');
    if(st)st.addEventListener('click',function(){setMenu(true,false);var s=document.getElementById('search');if(s)s.focus();});
    document.querySelector('.content').addEventListener('click',function(){if(sb.classList.contains('open'))setMenu(false,false);});
    document.addEventListener('keydown',function(e){
      if(e.key==='Escape'&&sb.classList.contains('open')&&getComputedStyle(toggle).display!=='none')setMenu(false,true);});
  }

  var box=document.getElementById('search'),out=document.getElementById('search-results'),idx=null;
  if(box){
    function load(){if(idx)return Promise.resolve(idx);
      return fetch('assets/search.json?v=36').then(function(r){return r.json();}).then(function(d){idx=d;return d;});}
    function esc(s){return s.replace(/[&<>]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});}
    function run(){
      var q=box.value.trim().toLowerCase();
      if(q.length<2){out.classList.remove('show');out.innerHTML='';return;}
      load().then(function(data){
        var res=[],seen={};
        for(var i=0;i<data.length&&res.length<300;i++){
          var t=data[i].t.toLowerCase(),p=data[i].p.toLowerCase(),b=(data[i].b||'').toLowerCase();
          var ti=t.indexOf(q);
          var hit=ti>-1||p.indexOf(q)>-1?1:(b.indexOf(q)>-1?2:0);
          if(hit&&!seen[data[i].u]){seen[data[i].u]=1;
            var r={t:data[i].t,p:data[i].p,u:data[i].u,s:'',o:i,rank:ti===0?0:ti>0?1:p.indexOf(q)>-1?2:3};
            if(hit===2){var k=b.indexOf(q);r.s=(k>40?'\u2026':'')+((data[i].b||'').substring(Math.max(0,k-40),k+60))+'\u2026';}
            res.push(r);}
        }
        res.sort(function(a,b){return a.rank-b.rank||a.o-b.o;});res=res.slice(0,40);
        if(!res.length){out.innerHTML='<div class="nores" role="status">No matches for &ldquo;'+esc(box.value)+'&rdquo;. Try a shorter word, a character or story name (Tessie, Miranda, &lsquo;The Witch&rsquo;) or a skill (symbols, contention, Section C).</div>';out.classList.add('show');return;}
        function hl(s){var e=esc(s),i=e.toLowerCase().indexOf(q);if(i<0)return e;
          return e.substring(0,i)+'<b>'+e.substring(i,i+q.length)+'</b>'+e.substring(i+q.length);}
        out.innerHTML=res.map(function(r){
          return '<a href="'+r.u+'">'+hl(r.t)+'<small>'+esc(r.p)+(r.s?' \u2014 '+hl(r.s):'')+'</small></a>';
        }).join('');
        out.classList.add('show');
      });
    }
    box.addEventListener('input',run);
    box.addEventListener('focus',run);
    document.addEventListener('click',function(e){
      if(!out.contains(e.target)&&e.target!==box)out.classList.remove('show');});
    // keyboard: arrow keys move through results, Enter opens the highlighted (or first) result, Escape closes
    var cur=-1;
    function items(){return [].slice.call(out.querySelectorAll('a'));}
    function mark(i){var a=items();a.forEach(function(x,j){x.classList.toggle('kb',j===i);x.setAttribute('aria-selected',String(j===i));});
      if(a[i])a[i].scrollIntoView({block:'nearest'});cur=i;}
    out.setAttribute('role','listbox');
    box.addEventListener('input',function(){cur=-1;});
    box.addEventListener('keydown',function(e){
      var a=items();
      if(e.key==='ArrowDown'&&a.length){e.preventDefault();mark(Math.min(cur+1,a.length-1));}
      else if(e.key==='ArrowUp'&&a.length){e.preventDefault();mark(Math.max(cur-1,0));}
      else if(e.key==='Enter'&&a.length){e.preventDefault();location.href=(a[cur]||a[0]).getAttribute('href');}
      else if(e.key==='Escape'){out.classList.remove('show');cur=-1;}
    });
  }
})();
(function(){
  var el=document.getElementById('countdown');
  if(!el)return;
  var target=new Date(el.getAttribute('data-target')).getTime();
  var d=document.getElementById('cd-d'),h=document.getElementById('cd-h'),
      m=document.getElementById('cd-m'),s=document.getElementById('cd-s');
  function pad(n){return n<10?'0'+n:''+n;}
  function tick(){
    var diff=target-Date.now();
    if(diff<=0){
      el.classList.add('cd-done');
      el.querySelector('.eb-label').textContent='The English exam is here. Good luck!';
      el.querySelector('.eb-time').style.display='none';
      clearInterval(iv);return;
    }
    var days=Math.floor(diff/86400000);
    d.textContent=days;
    h.textContent=pad(Math.floor(diff/3600000)%24);
    m.textContent=pad(Math.floor(diff/60000)%60);
    s.textContent=pad(Math.floor(diff/1000)%60);
    var u=days<=7?'cd-final':days<=30?'cd-near':days<=100?'cd-mid':'';
    ['cd-mid','cd-near','cd-final'].forEach(function(c){el.classList.remove(c);});
    if(u)el.classList.add(u);
  }
  var iv=setInterval(tick,1000);tick();
})();
(function(){
  var foot=document.querySelector('.side-foot');
  if(foot){
    var b=document.createElement('button');b.className='theme-toggle';b.id='theme-toggle';
    b.textContent=document.documentElement.getAttribute('data-theme')==='dark'?'Light mode':'Dark mode';
    b.addEventListener('click',function(){
      var d=document.documentElement.getAttribute('data-theme')==='dark';
      document.documentElement.setAttribute('data-theme',d?'':'dark');
      try{localStorage.setItem('siteTheme',d?'light':'dark');}catch(e){}
      b.textContent=d?'Dark mode':'Light mode';
    });
    foot.insertBefore(b,foot.firstChild);
  }
  var t=document.createElement('button');t.id='to-top';t.setAttribute('aria-label','Back to top');t.innerHTML='&#8593;';
  t.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});});
  document.body.appendChild(t);
  window.addEventListener('scroll',function(){t.classList.toggle('show',window.scrollY>600);},{passive:true});
})();

(function(){
  var bar=document.createElement('div');bar.id='progress-bar';document.body.appendChild(bar);
  function upd(){var h=document.documentElement.scrollHeight-window.innerHeight;
    bar.style.width=(h>200?Math.min(100,window.scrollY/h*100):0)+'%';}
  window.addEventListener('scroll',upd,{passive:true});upd();


  document.addEventListener('click',function(e){
    var img=e.target.closest&&e.target.closest('img.content-img');
    if(!img)return;
    var ov=document.createElement('div');ov.className='lb-overlay';
    var big=document.createElement('img');big.src=img.src;big.alt=img.alt||'';
    ov.appendChild(big);ov.addEventListener('click',function(){ov.remove();});
    document.addEventListener('keydown',function esc2(ev){if(ev.key==='Escape'){ov.remove();document.removeEventListener('keydown',esc2);}});
    document.body.appendChild(ov);
  });

  var sb=document.getElementById('sidebar');
  var act=sb&&(sb.querySelector('.subnav li.active')||sb.querySelector('.toc li.active'));
  if(sb&&act){var r=act.getBoundingClientRect(),rs=sb.getBoundingClientRect();
    if(r.top>rs.bottom-80||r.top<rs.top)sb.scrollTop+=r.top-rs.top-sb.clientHeight/2;}

  try{
    var here=location.pathname.split('/').pop()||'index.html';
    if(here!=='index.html'&&here!=='404.html'){
      var tt=(document.title||'').split(' · ')[0];
      localStorage.setItem('lastPage',JSON.stringify({u:here,t:tt}));
    }else if(here==='index.html'){
      var lp=JSON.parse(localStorage.getItem('lastPage')||'null');
      var slot=document.getElementById('resume-slot');
      var hero=document.querySelector('.hero');
      if(lp&&lp.u&&(slot||hero)){
        var a=document.createElement('a');a.className='resume-chip';a.href=lp.u;
        a.innerHTML='<span class="rc-label">Resume</span> '+lp.t.replace(/[<>&]/g,'')+' →';
        if(slot){slot.appendChild(a);}else{hero.parentNode.insertBefore(a,hero.nextSibling);}
      }
    }
  }catch(e){}
})();
(function(){
  document.addEventListener('click',function(e){
    var mk=e.target.closest&&e.target.closest('mark.anno');
    document.querySelectorAll('mark.anno.open').forEach(function(m){if(m!==mk)m.classList.remove('open');});
    if(mk){
      mk.classList.toggle('open');
      if(mk.classList.contains('open')){
        var r=mk.getBoundingClientRect();
        mk.classList.toggle('tip-up',r.bottom>window.innerHeight-260);
      }
      e.stopPropagation();
    }
    var lg=e.target.closest&&e.target.closest('.lg[data-cat]');
    if(lg){
      var cat=lg.dataset.cat,was=lg.classList.contains('active');
      document.querySelectorAll('.lg').forEach(function(b){b.classList.remove('active');});
      document.querySelectorAll('mark.anno').forEach(function(m){m.classList.remove('anno-match');});
      document.querySelectorAll('.lg').forEach(function(b){b.setAttribute('aria-pressed',String(b===lg&&!was));});
      if(was){document.body.classList.remove('anno-filtered');}
      else{
        lg.classList.add('active');
        document.body.classList.add('anno-filtered');
        document.querySelectorAll('mark.anno-'+cat).forEach(function(m){m.classList.add('anno-match');});
      }
    }
  });
})();
(function(){
  console.log('%cInspecting the page instead of studying?','font-size:16px;font-weight:bold;color:#7a1f2b');
  console.log('%cVery Section C of you — now analyse how this site positions its audience.','font-size:13px;color:#b7892f');

  function toast(msg,ms){
    var t=document.createElement('div');t.className='egg-toast';t.textContent=msg;
    document.body.appendChild(t);
    requestAnimationFrame(function(){t.classList.add('show');});
    setTimeout(function(){t.classList.remove('show');setTimeout(function(){t.remove();},450);},ms||7000);
  }

  var h=new Date().getHours();
  if(h>=0&&h<4){
    try{
      if(!sessionStorage.getItem('midnightNudge')){
        sessionStorage.setItem('midnightNudge','1');
        setTimeout(function(){toast("It's past midnight. Mrs Appleyard would have had you in bed hours ago. The quote banks will still be here tomorrow.",10000);},2500);
      }
    }catch(e){}
  }

  var sb=document.getElementById('search');
  if(sb){
    sb.addEventListener('input',function(){
      var q=sb.value.trim().toLowerCase().replace(/[^a-z ]/g,'');
      var still=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
      if(q==='a dream within a dream'||q==='dream within a dream'){
        sb.value='';
        if(!still){document.body.classList.add('dream-blur');setTimeout(function(){document.body.classList.remove('dream-blur');},2600);}
        toast("\u2018What we see and what we seem are but a dream, a dream within a dream.\u2019",6000);
      }
      if(q==='the lottery'){
        toast("You drew a blank slip. Lucky. Keep revising.",5000);
      }
      if(/^(do a )?barr?ell? ?roll$/.test(q)&&!still){
        sb.value='';
        document.body.classList.remove('barrel-roll');
        void document.body.offsetWidth;
        document.body.classList.add('barrel-roll');
        setTimeout(function(){document.body.classList.remove('barrel-roll');},1400);
      }
    });
  }
})();


/* Exam checklists: clickable tick boxes, remembered per browser */
(function(){
  var f=(location.pathname.split('/').pop()||'');
  if(!/^(p10-|r25-checklist|p11-final-exam-checklist)/.test(f))return;
  var main=document.getElementById('main');if(!main)return;
  var key='av-check:'+f,state={};
  try{state=JSON.parse(localStorage.getItem(key)||'{}');}catch(e){}
  main.querySelectorAll('section li').forEach(function(li,i){
    if(li.querySelector('ul,ol'))return;
    var cb=document.createElement('input');cb.type='checkbox';cb.checked=!!state[i];
    li.classList.add('chk');if(cb.checked)li.classList.add('done');
    li.insertBefore(cb,li.firstChild);
    li.addEventListener('click',function(e){
      if(e.target.tagName==='A')return;
      if(e.target!==cb)cb.checked=!cb.checked;
      state[i]=cb.checked;li.classList.toggle('done',cb.checked);
      try{localStorage.setItem(key,JSON.stringify(state));}catch(e){}
    });
  });
})();

/* Quote Banks: toggle between grouping by theme and by story (Lottery) or character (Picnic).
   Each item starts with an <em> naming its story/speaker; that is the grouping key. */
(function(){
  var sec=document.querySelector('.quotes-page[data-sortable]');
  if(!sec) return;
  var INV="The Investigators and the Town";
  var MODES={
    story:{label:"Story",strip:true,alias:{},
      order:["The Daemon Lover","Like Mother Used to Make","The Villager","The Witch","The Renegade",
        "After You, My Dear Alphonse","Charles","Flower Garden","Elizabeth","Of Course","The Tooth","The Lottery"]},
    character:{label:"Character",strip:false,
      alias:{"Mademoiselle":"Mademoiselle de Poitiers","Michael":"Michael Fitzhubert","Albert":"Albert Crundall",
        "Sara":"Sara Waybourne","Mr Hussey":INV,"Sergeant Bumpher":INV,"Mrs Bumpher":INV,"A townsman":INV,
        "The doctor":INV,"The head gardener":INV},
      order:["Miranda","Marion","Irma","Edith","Mrs Appleyard","Sara Waybourne","Miss McCraw",
        "Mademoiselle de Poitiers","Miss Lumley","Michael Fitzhubert","Albert Crundall",INV]}
  };
  var mode=MODES[sec.dataset.sortable]||MODES.story, ORDER=mode.order;
  var themes=[].slice.call(sec.querySelectorAll(':scope > section'));
  var groups={};
  themes.forEach(function(ts){
    var h=ts.querySelector('h2,h3,h4,h5'); var theme=h?h.textContent.trim():'';
    ts.querySelectorAll('li').forEach(function(li){
      var em=li.querySelector('p > em:first-child, :scope > em:first-child');
      var key=em?em.textContent.trim():'Other', story=mode.alias[key]||key;
      var c=li.cloneNode(true), cem=c.querySelector('em');
      if(mode.strip&&em&&cem){ // drop the now-redundant "Title:" prefix
        var p=cem.parentNode; p.removeChild(cem);
        if(p.firstChild&&p.firstChild.nodeType===3) p.firstChild.nodeValue=p.firstChild.nodeValue.replace(/^\s*:\s*/,'');
      }
      var tag=document.createElement('span'); tag.className='qb-tag'; tag.textContent=theme;
      (c.querySelector('p')||c).appendChild(tag);
      (groups[story]=groups[story]||[]).push(c);
    });
  });
  var view=document.createElement('div'); view.className='qb-by-story'; view.hidden=true;
  ORDER.concat(Object.keys(groups).filter(function(k){return ORDER.indexOf(k)<0;})).forEach(function(s){
    if(!groups[s]) return;
    var h=document.createElement('h2'); h.className='hl4'; var em=document.createElement('em'); em.textContent=s; h.appendChild(em);
    var ul=document.createElement('ul'); groups[s].forEach(function(li){ul.appendChild(li);});
    view.appendChild(h); view.appendChild(ul);
  });
  var bar=document.createElement('div'); bar.className='qb-sort'; bar.setAttribute('role','group');
  bar.innerHTML='<span>Sort by</span><button type="button" data-v="theme" aria-pressed="true">Theme</button><button type="button" data-v="story" aria-pressed="false">'+mode.label+'</button>';
  var toc=sec.querySelector('.page-toc'), anchor=toc||sec.querySelector('h1');
  anchor.parentNode.insertBefore(bar,anchor.nextSibling);
  sec.appendChild(view);
  function show(v){
    var story=v==='story';
    themes.forEach(function(t){t.hidden=story;}); view.hidden=!story; if(toc) toc.hidden=story;
    bar.querySelectorAll('button').forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.v===v));});
    try{localStorage.setItem('qb-sort',v);}catch(e){}
  }
  bar.addEventListener('click',function(e){var b=e.target.closest('button'); if(b) show(b.dataset.v);});
  try{ if(localStorage.getItem('qb-sort')==='story') show('story'); }catch(e){}
})();

/* Long pages: an "On this page" button appears once the inline contents box has scrolled away */
(function(){
  var toc=document.querySelector('.content .page-toc');
  if(!toc||document.documentElement.scrollHeight<window.innerHeight*3) return;
  var links=toc.querySelector('ul'); if(!links) return;
  var btn=document.createElement('button');btn.id='toc-fab';btn.type='button';
  btn.textContent='On this page';btn.setAttribute('aria-expanded','false');btn.setAttribute('aria-controls','toc-pop');
  var pop=document.createElement('nav');pop.id='toc-pop';pop.setAttribute('aria-label','On this page');pop.hidden=true;
  pop.appendChild(links.cloneNode(true));
  document.body.appendChild(pop);document.body.appendChild(btn);
  function set(open,refocus){pop.hidden=!open;btn.setAttribute('aria-expanded',String(open));
    if(open){var a=pop.querySelector('a');if(a)a.focus();}else if(refocus){btn.focus();}}
  btn.addEventListener('click',function(){set(pop.hidden,false);});
  pop.addEventListener('click',function(e){if(e.target.closest('a'))set(false,false);});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!pop.hidden)set(false,true);});
  document.addEventListener('click',function(e){if(!pop.hidden&&!pop.contains(e.target)&&e.target!==btn)set(false,false);});
  if('IntersectionObserver' in window){
    new IntersectionObserver(function(en){btn.classList.toggle('show',!en[0].isIntersecting&&en[0].boundingClientRect.top<0);
      if(en[0].isIntersecting)set(false,false);}).observe(toc);
  }else{btn.classList.add('show');}
})();


/* Section links: a small link beside each section heading copies a direct link to it */
(function(){
  var content=document.querySelector('.content'); if(!content) return;
  function note(msg){var n=document.createElement('div');n.className='mini-toast';n.setAttribute('role','status');n.textContent=msg;
    document.body.appendChild(n);setTimeout(function(){n.remove();},2200);}
  content.querySelectorAll('section[id] > h2, section[id] > h3').forEach(function(h){
    if(h.closest('.page-toc,.exam-band,.sc-paper')) return;
    var id=h.parentNode.id, a=document.createElement('a');
    a.className='anchor-link';a.href='#'+id;a.setAttribute('aria-label','Copy link to '+h.textContent.trim());a.textContent='#';
    a.addEventListener('click',function(e){
      e.preventDefault();var url=location.href.split('#')[0]+'#'+id;
      history.replaceState(null,'','#'+id);
      if(navigator.clipboard){navigator.clipboard.writeText(url).then(function(){note('Link copied');},function(){note('Link: '+url);});}
      else{note('Link: '+url);}
    });
    h.appendChild(a);
  });
})();

/* Mark chapters as done: saved in this browser, shown in the sidebar and on part pages */
(function(){
  var KEY='donePages',done={};
  try{done=JSON.parse(localStorage.getItem(KEY)||'{}');}catch(e){}
  function save(){try{localStorage.setItem(KEY,JSON.stringify(done));}catch(e){}}
  var here=location.pathname.split('/').pop()||'index.html';
  function paint(){
    document.querySelectorAll('.subnav a, .ch-card').forEach(function(a){
      var f=(a.getAttribute('href')||'').split('#')[0];
      var on=!!done[f];a.classList.toggle('is-done',on);
      var sr=a.querySelector('.done-sr');
      if(on&&!sr){sr=document.createElement('span');sr.className='vh done-sr';sr.textContent=' (done)';a.appendChild(sr);}
      if(!on&&sr)sr.remove();
    });
    document.querySelectorAll('.toc li.grp').forEach(function(g){
      var links=g.querySelectorAll('.subnav a'),n=0;
      links.forEach(function(a){if(done[(a.getAttribute('href')||'').split('#')[0]])n++;});
      var b=g.querySelector('.done-count');
      if(!b){b=document.createElement('span');b.className='done-count';var s=g.querySelector('summary a');if(s)s.appendChild(b);}
      b.textContent=n?n+'/'+links.length:'';
      if(n)b.setAttribute('aria-label',n+' of '+links.length+' chapters done');else b.removeAttribute('aria-label');
    });
  }
  var pos=document.querySelector('.content .ch-pos'), pn=document.querySelector('.content .prevnext');
  if(pos&&pn){
    var btn=document.createElement('button');btn.type='button';btn.className='done-btn';
    function label(){var on=!!done[here];btn.setAttribute('aria-pressed',String(on));
      btn.textContent=on?'✓ Done. Select to undo':'Mark this chapter as done';}
    btn.addEventListener('click',function(){if(done[here])delete done[here];else done[here]=1;save();label();paint();});
    label();pn.parentNode.insertBefore(btn,pn);
  }
  paint();
})();
