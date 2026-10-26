(() => {
  'use strict';
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  const panels = [...document.querySelectorAll('[role="tabpanel"]')];
  const lessons = [...document.querySelectorAll('.lesson')];
  const links = [...document.querySelectorAll('[data-route]')];
  const sidebar = document.querySelector('.sidebar');
  const menu = document.querySelector('#menu');
  const scrim = document.querySelector('.scrim');
  const remembered = {learn:'learn-roles',practice:'practice-start',projects:'projects-cases'};
  const syncSidebar = () => {sidebar.inert=matchMedia('(max-width:760px)').matches&&!sidebar.classList.contains('open');};
  const closeMenu = () => {sidebar.classList.remove('open');scrim.classList.remove('open');menu.setAttribute('aria-expanded','false');syncSidebar();};
  function route(focus = true) {
    let id;try{id = decodeURIComponent(location.hash.slice(1));}catch{ id = ''; }
    const lesson = lessons.find(x=>x.id===id)||lessons[0];
    const group = lesson.dataset.group; remembered[group]=lesson.id;
    panels.forEach(x=>x.hidden=x.id!==`panel-${group}`);
    lessons.forEach(x=>x.hidden=x!==lesson);
    tabs.forEach(x=>{const on=x.dataset.group===group;x.setAttribute('aria-selected',String(on));x.tabIndex=on?0:-1;});
    document.querySelectorAll('[data-trail]').forEach(x=>x.hidden=x.dataset.trail!==group);
    links.forEach(x=>{if(x.dataset.route===lesson.id)x.setAttribute('aria-current','page');else x.removeAttribute('aria-current');});
    document.title=lesson.querySelector('h1').innerText.replace(/\s+/g,' ')+' · Part 5';closeMenu();hideTip();
    if(focus){lesson.focus({preventScroll:true});window.scrollTo({top:0,behavior:'instant'});}
  }
  function activateTab(tab) {
    const hash='#'+remembered[tab.dataset.group];
    if(location.hash!==hash)history.pushState(null,'',hash);
    route(false);
    tab.focus({preventScroll:true});window.scrollTo({top:0,behavior:'instant'});
  }
  tabs.forEach((tab,i)=>{
    tab.addEventListener('click',()=>activateTab(tab));
    tab.addEventListener('keydown',e=>{
      let next;if(e.key==='ArrowRight')next=(i+1)%tabs.length;else if(e.key==='ArrowLeft')next=(i-1+tabs.length)%tabs.length;else if(e.key==='Home')next=0;else if(e.key==='End')next=tabs.length-1;else return;
      e.preventDefault();activateTab(tabs[next]);
    });
  });
  menu.addEventListener('click',()=>{const open=!sidebar.classList.contains('open');sidebar.classList.toggle('open',open);scrim.classList.toggle('open',open);menu.setAttribute('aria-expanded',String(open));syncSidebar();if(open)sidebar.querySelector('[aria-current="page"]').focus();});
  scrim.addEventListener('click',closeMenu);
  const tip=document.querySelector('#tooltip');let activeTip=null;let pinned=false;
  function hideTip(){if(activeTip)activeTip.setAttribute('aria-expanded','false');activeTip=null;pinned=false;tip.hidden=true;}
  function showTip(button,pin=false){activeTip=button;pinned=pin;tip.textContent=button.dataset.definition;tip.hidden=false;button.setAttribute('aria-expanded','true');const box=button.getBoundingClientRect();const t=tip.getBoundingClientRect();tip.style.left=Math.max(12,Math.min(box.left,innerWidth-t.width-12))+'px';tip.style.top=(box.bottom+t.height+12<innerHeight?box.bottom+8:Math.max(12,box.top-t.height-8))+'px';}
  document.querySelectorAll('.term').forEach(button=>{
    button.setAttribute('aria-describedby','tooltip');button.setAttribute('aria-expanded','false');
    button.addEventListener('mouseenter',()=>{if(!pinned)showTip(button);});
    button.addEventListener('mouseleave',()=>{if(!pinned&&document.activeElement!==button)hideTip();});
    button.addEventListener('focus',()=>showTip(button));button.addEventListener('blur',hideTip);
    button.addEventListener('click',()=>{if(activeTip===button&&pinned)hideTip();else showTip(button,true);});
  });
  document.addEventListener('pointerdown',e=>{if(!e.target.closest('.term')&&!tip.contains(e.target))hideTip();});
  document.addEventListener('keydown',e=>{
    if(e.key==='Escape'){hideTip();if(sidebar.classList.contains('open')){closeMenu();menu.focus();}}
    if(e.key==='Tab'&&sidebar.classList.contains('open')&&matchMedia('(max-width:760px)').matches){const available=[menu,...sidebar.querySelectorAll('a')].filter(x=>x.getClientRects().length);const i=available.indexOf(document.activeElement);if(e.shiftKey&&i===0){e.preventDefault();available.at(-1).focus();}else if(!e.shiftKey&&i===available.length-1){e.preventDefault();menu.focus();}}
  });
  addEventListener('resize',()=>{hideTip();syncSidebar();});addEventListener('scroll',hideTip,{passive:true});
  const status=document.querySelector('#status');
  document.querySelectorAll('.copy').forEach(button=>button.addEventListener('click',async()=>{
    const code=button.closest('.prompt').querySelector('code');
    try{await navigator.clipboard.writeText(code.textContent);button.textContent='복사됨';status.textContent='코드를 복사했습니다.';setTimeout(()=>button.textContent='복사',1500);}
    catch{const range=document.createRange();range.selectNodeContents(code);const s=getSelection();s.removeAllRanges();s.addRange(range);status.textContent='자동 복사를 사용할 수 없습니다. 선택된 코드를 복사해 주세요.';}
  }));
  const quiz=document.querySelector('#review-exercise');
  if(quiz){quiz.addEventListener('submit',e=>{
    e.preventDefault();let count=0;
    quiz.querySelectorAll('.question').forEach(q=>{const select=q.querySelector('select');const feedback=q.querySelector('.feedback');const correct=select.value===q.dataset.answer;if(correct)count++;feedback.textContent=!select.value?'판정을 하나 선택해 주세요.':(correct?'맞습니다. ':'다시 확인해 보세요. ')+q.dataset.explanation;feedback.className='feedback '+(correct?'good':'bad');select.setAttribute('aria-invalid',String(!correct));});
    const result=document.querySelector('#review-result');result.textContent=count===3?'3개 판단을 모두 확인했습니다. 이제 검토자가 원고를 직접 고쳐도 되는지 아래에서 확인하세요.':`${count}/3개를 확인했습니다. 근거의 조건과 범위를 다시 비교해 보세요.`;result.focus();
  });document.querySelector('#reset-exercise').addEventListener('click',()=>{quiz.reset();quiz.querySelectorAll('.feedback').forEach(x=>x.textContent='');quiz.querySelectorAll('select').forEach(x=>x.removeAttribute('aria-invalid'));document.querySelector('#review-result').textContent='';quiz.querySelector('select').focus();});}
  document.querySelector('.skip').addEventListener('click',e=>{e.preventDefault();document.querySelector('.lesson:not([hidden])').focus();});
  addEventListener('hashchange',()=>route());route(false);
})();
