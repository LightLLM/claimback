const $ = s => document.querySelector(s);
let state, view = 'overview', busy = false;
const money = cents => new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(cents/100);
const esc = value => String(value ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const labels = {ready:'Ready to recover',submitted:'Tracking response',waiting:'Following up',decision:'Your decision needed',resolved:'Resolved',settled:'Partial settlement'};
function toast(message){$('#toast').textContent=message;$('#toast').style.display='block';setTimeout(()=>$('#toast').style.display='none',5000)}
async function api(path,body){const response=await fetch('/api'+path,{method:body===undefined?'GET':'POST',headers:{'Content-Type':'application/json','X-ClaimBack':'1'},...(body===undefined?{}:{body:JSON.stringify(body)})});if(!response.ok){let error=await response.json();throw Error(error.detail||'Request failed')}return response.json()}
async function load(){state=await api('/state');render()}
function render(){
  const pending=state.cases.filter(c=>c.decision).length;
  $('#decision-count').textContent=pending;
  $('#mode').textContent=state.mode==='bedrock'?'● Bedrock · simulated merchants':'● Synthetic demo';
  $('#stats').innerHTML=[['Recovery in progress',money(state.cases.filter(c=>!['resolved','settled'].includes(c.status)).reduce((s,c)=>s+c.amount_cents,0)),'Refund + replacement value','↗','primary'],['Cash recovered',money(state.cases.reduce((s,c)=>s+c.paid_cents,0)),'Confirmed in this simulation','↶',''],['Replacement value',money(state.cases.reduce((s,c)=>s+c.replacement_cents,0)),'Non-cash · kept separate','◇',''],['Your decisions',String(pending).padStart(2,'0'),pending?'Only where your judgment matters':'We’ll ask when it matters','◷','']].map(([label,value,caption,icon,cls])=>`<article class="stat ${cls}"><div class="stat-label">${label}<span class="stat-icon">${icon}</span></div><strong>${value}</strong><small>${caption}</small></article>`).join('');
  const titles={overview:['Your recovery desk','Two loose ends. One agent on your side.'],decisions:['You have the final say','Consequential choices stay with you. Always.'],evidence:['The evidence vault','Every source, every draft, every reason.'],activity:['Your agent’s paper trail','A timestamped record of what happened and why.']};
  $('#page-name').textContent={overview:'Overview',decisions:'Decisions',evidence:'Evidence vault',activity:'Agent activity'}[view];
  $('#section-title').textContent=titles[view][0];$('#section-caption').textContent=titles[view][1];
  document.querySelectorAll('[data-view]').forEach(el=>el.classList.toggle('active',el.dataset.view===view));
  if(view==='overview'||view==='decisions'){
    const cases=view==='decisions'?state.cases.filter(c=>c.decision):state.cases;
    $('#content').innerHTML=cases.length?`<div class="cases">${cases.map(card).join('')}</div>`:'<div class="panel empty"><b>✓</b>No decisions waiting.<br>Your agent will pause here when a choice needs your judgment.</div>';
  }else if(view==='evidence'){
    $('#content').innerHTML=`<div class="cases">${state.cases.map(c=>`<section class="panel"><h3>${esc(c.merchant)}</h3>${c.evidence.map(e=>`<div class="evidence-row"><div><p>${esc(e.name)}</p><small>${esc(e.type)} · Synthetic source</small></div><button class="secondary" data-source="${e.id}" data-case="${c.id}">Read</button></div>`).join('')}<div class="evidence-row"><button class="link-button" data-draft="${c.id}">View claim draft</button><a class="link-button" href="/api/cases/${c.id}/evidence">Export evidence ↓</a></div></section>`).join('')}</div>`;
  }else{
    $('#content').innerHTML=`<div class="cases">${state.cases.map(c=>`<section class="panel"><h3>${esc(c.merchant)}</h3><p class="subtitle">Hash-linked event trail · export to verify</p>${c.audit.map(e=>`<div class="activity-row"><strong>${esc(e.action.replaceAll('_',' '))}</strong><small>${new Date(e.at).toLocaleTimeString()} · ${esc(e.actor)}</small><details><summary>Evidence & details</summary><pre>${esc(typeof e.detail==='string'?e.detail:JSON.stringify(e.detail,null,2))}</pre><small>SHA-256 ${esc(e.hash.slice(0,20))}…</small></details></div>`).join('')}</section>`).join('')}</div>`;
  }
  document.querySelectorAll('button').forEach(b=>b.disabled=busy);
}
function card(c){
  const complete=['resolved','settled'].includes(c.status);
  let summary=c.description;
  if(c.status==='waiting')summary='Your agent submitted the evidence package and sent a routine follow-up. Advance the demo to check the merchant’s response.';
  if(c.status==='submitted')summary='Your challenge is submitted. No settlement was accepted. Check the next simulated merchant response.';
  if(complete)summary=c.kind==='refund'?`${money(c.paid_cents)} confirmed to the original payment method in this simulation.`:'A no-cost replacement is confirmed. $349 in replacement value protected; no cash refund claimed.';
  return `<article class="case"><div class="case-main"><div class="case-top"><div class="merchant"><span class="merchant-logo ${c.kind}">${c.kind==='refund'?'✧':'f.'}</span>${esc(c.merchant)}</div><span class="pill ${c.status}">${labels[c.status]}</span></div><h3>${esc(c.title)}</h3><div class="subtitle">${esc(c.subtitle)}</div><div class="amount">${money(c.amount_cents)}<span class="amount-caption"> USD</span></div><div class="amount-caption">${c.kind==='refund'?'Refund requested':'Potential replacement value · non-cash'}</div><div class="steps">${[['Evidence',c.gathered],['Claim built',c.draft],['Submitted',c.submission_id],['Resolved',complete]].map(([l,d])=>`<div class="step ${d?'done':''}">${l}</div>`).join('')}</div><div class="case-summary">${esc(summary)}</div>${c.decision?decisionCard(c):''}</div><div class="case-foot"><button class="link-button" data-detail="${c.id}">${c.evidence.length} evidence sources ↗</button>${complete?`<a class="link-button" href="/api/cases/${c.id}/evidence">Export case ↓</a>`:c.decision?'<span class="quiet-label">Paused for your decision</span>':`<button class="primary-button" data-run="${c.id}">${!c.authorized?'Review & start →':c.status==='waiting'?'Check response →':'Run agent →'}</button>`}</div></article>`;
}
function decisionCard(c){const d=c.decision;return `<section class="decision-card"><div class="eyebrow">HUMAN DECISION REQUIRED</div><h4>A partial offer. A choice for you.</h4><div class="decision-money"><div>Merchant offered<b>${money(d.offered_cents)}</b></div><div>Still unaccounted for<b>${money(d.gap_cents)}</b></div></div><p>${esc(d.recommendation)}</p><div class="decision-actions"><button class="primary-button" data-challenge="${c.id}">Authorize challenge →</button><button class="link-button" data-accept="${c.id}">Review partial settlement</button></div></section>`}
function modal(html){$('#detail-body').innerHTML=html;$('#detail').showModal()}
async function act(fn){if(busy)return;busy=true;render();try{await fn();await load()}catch(e){toast(e.message);await load().catch(()=>{})}finally{busy=false;render()}}
async function run(id){await act(async()=>{toast('Agent is gathering evidence and working through the case…');await api(`/cases/${id}/run`,{});toast('Agent run complete. Your recovery desk is up to date.');})}
document.addEventListener('click',async event=>{
  const b=event.target.closest('button');if(!b||busy)return;
  if(b.dataset.view){view=b.dataset.view;render();return}
  const find=id=>state.cases.find(c=>c.id===id);
  if(b.dataset.run){const c=find(b.dataset.run);if(!c.authorized){modal(`<div class="eyebrow">SCOPED AUTHORIZATION</div><h2>Let’s take this off your list.</h2><p>For ${esc(c.merchant)}, authorize ClaimBack to gather these synthetic sources, prepare and submit the original claim, check status, and send one routine follow-up to the simulated merchant.</p><p><strong>You retain control over settlements, compromises, and any waiver of rights.</strong> No real messages are sent. All data and merchant responses are synthetic.</p><button class="primary-button" data-authorize="${c.id}">Authorize & start simulation →</button>`)}else await run(c.id)}
  if(b.dataset.authorize){const id=b.dataset.authorize;$('#detail').close();await act(async()=>{await api(`/cases/${id}/authorize`,{});await api(`/cases/${id}/run`,{});toast('Case processed. Review your recovery desk.');})}
  if(b.dataset.challenge){const c=find(b.dataset.challenge);await act(async()=>{await api(`/cases/${c.id}/decision`,{decision_id:c.decision.id,choice:'challenge'});toast('Challenge authorized and submitted to the simulated merchant.');})}
  if(b.dataset.accept){const c=find(b.dataset.accept);modal(`<div class="eyebrow">YOUR DECISION · PARTIAL SETTLEMENT</div><h2>Accept ${money(c.decision.offered_cents)}?</h2><p>${esc(c.decision.terms)}</p><p>You can close this dialog to keep reviewing, or authorize a challenge on the case card.</p><label><input type="checkbox" id="ack">I understand that accepting $880 closes this simulated case and gives up pursuing the remaining $528.</label><button class="primary-button" data-confirm="${c.id}">Accept $880 & close simulated case</button>`)}
  if(b.dataset.confirm){if(!$('#ack').checked){toast('Acknowledge the shortfall and closure before accepting.');return}const c=find(b.dataset.confirm);$('#detail').close();await act(()=>api(`/cases/${c.id}/decision`,{decision_id:c.decision.id,choice:'accept_partial',acknowledge:true}))}
  if(b.dataset.detail){const c=find(b.dataset.detail);modal(`<h2>${esc(c.merchant)} · Evidence</h2>${c.evidence.map(e=>`<details class="evidence-row"><summary>${esc(e.name)}</summary><pre>${esc(e.text)}</pre><small>${esc(e.source)}<br>SHA-256: ${esc(e.sha256)}</small></details>`).join('')}<h3>Claim draft</h3><p>${esc(c.draft||'Your agent will prepare a source-backed draft after you authorize the simulation.')}</p><a class="link-button" href="/api/cases/${c.id}/evidence">Download full evidence & audit trail ↓</a>`)}
  if(b.dataset.source){const e=find(b.dataset.case).evidence.find(e=>e.id===b.dataset.source);modal(`<h2>${esc(e.name)}</h2><pre>${esc(e.text)}</pre><p>${esc(e.source)}</p><pre>SHA-256: ${esc(e.sha256)}</pre>`)}
  if(b.dataset.draft){const c=find(b.dataset.draft);modal(`<h2>Source-backed claim draft</h2><p>${esc(c.draft||'Run the agent to prepare this claim.')}</p>`)}
});
$('#close-detail').addEventListener('click',()=>$('#detail').close());
$('#reset').addEventListener('click',()=>{if(!busy)modal('<h2>Start a fresh demo?</h2><p>This resets both synthetic cases and their audit histories in this browser session. Export any evidence you want to keep first.</p><button class="primary-button" id="confirm-reset">Reset this demo</button>')});
document.addEventListener('click',e=>{if(e.target.id==='confirm-reset'){$('#detail').close();act(()=>api('/reset',{}))}});
load().catch(e=>{$('#content').innerHTML='<div class="panel empty">Could not connect to ClaimBack. Refresh to try again.</div>';toast(e.message)});
