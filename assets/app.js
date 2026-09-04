'use strict';

const $ = id => document.getElementById(id);
const CF_BASE = 'https://speed.cloudflare.com';
const state = { busy:false, history:[], last:null, samples:[], apiBase:null, backend:'detecting' };

try { state.history = JSON.parse(localStorage.getItem('pulsenet-history') || '[]'); if (!Array.isArray(state.history)) state.history=[]; } catch { state.history=[]; }

const toast = msg => { const el=$('toast'); el.textContent=msg; el.classList.add('show'); clearTimeout(toast.t); toast.t=setTimeout(()=>el.classList.remove('show'),2200); };
const progress = (n,label) => { $('bar').style.width=`${Math.max(0,Math.min(100,n))}%`; $('pct').textContent=`${Math.round(n)}%`; $('label').textContent=label; };

function chart(){
  const c=$('chart'),ctx=c.getContext('2d'),w=c.clientWidth||600,h=110,d=devicePixelRatio||1;
  c.width=w*d;c.height=h*d;ctx.setTransform(d,0,0,d,0,0);ctx.clearRect(0,0,w,h);
  if(state.samples.length<2)return;
  const max=Math.max(10,...state.samples);ctx.beginPath();
  state.samples.forEach((v,i)=>{const x=i/(state.samples.length-1)*w,y=h-10-(v/max)*(h-25);i?ctx.lineTo(x,y):ctx.moveTo(x,y)});
  ctx.strokeStyle='#39e6cc';ctx.lineWidth=3;ctx.lineCap='round';ctx.stroke();
}

async function fetchWithTimeout(url,options={},ms=8000){
  const c=new AbortController(),t=setTimeout(()=>c.abort(),ms);
  try{return await fetch(url,{...options,signal:c.signal,cache:'no-store',credentials:'omit'})}finally{clearTimeout(t)}
}

async function detectBackend(){
  try{
    const r=await fetchWithTimeout('/api/health',{},1800);
    if(r.ok){const j=await r.json();if(j&&j.status==='ok'){state.apiBase='';state.backend='PulseNet Python';$('serverName').textContent='PulseNet Python';return;}}
  }catch{}
  state.apiBase=CF_BASE;state.backend='Cloudflare Edge';$('serverName').textContent='Cloudflare Edge';
}

const endpoint = path => state.apiBase ? `${state.apiBase}${path}` : `${CF_BASE}${path}`;

async function latency(){
  const values=[],total=8;
  for(let i=0;i<total;i++){
    const start=performance.now();
    try{
      const r=await fetchWithTimeout(endpoint(`/__down?bytes=0&measId=${Date.now()}-${i}-${Math.random()}`),{},5000);
      if(r.ok){await r.arrayBuffer();values.push(performance.now()-start)}
    }catch{}
    progress(3+(i+1)/total*7,'Measuring latency');
  }
  if(!values.length)throw Error('Latency test could not reach the test server.');
  const ping=values.reduce((a,b)=>a+b,0)/values.length;
  const jitter=values.length>1?values.slice(1).reduce((a,v,i)=>a+Math.abs(v-values[i]),0)/(values.length-1):0;
  return {ping,jitter,loss:(total-values.length)/total*100};
}

async function download(){
  const sizes=[1e6,5e6,10e6,25e6];let bytes=0,start=performance.now(),total=sizes.reduce((a,b)=>a+b,0);
  for(const size of sizes){
    const r=await fetchWithTimeout(endpoint(`/__down?bytes=${size}&measId=${Date.now()}-${Math.random()}`),{},45000);
    if(!r.ok||!r.body)throw Error('Download test failed.');
    const reader=r.body.getReader();
    for(;;){
      const part=await reader.read();if(part.done)break;bytes+=part.value.byteLength;
      const seconds=Math.max(.001,(performance.now()-start)/1000),mbps=bytes*8/1e6/seconds;
      state.samples.push(mbps);if(state.samples.length>60)state.samples.shift();
      $('speed').textContent=mbps<10?mbps.toFixed(2):mbps.toFixed(1);
      progress(10+(bytes/total)*55,'Downloading');chart();
    }
  }
  return bytes*8/1e6/Math.max(.001,(performance.now()-start)/1000);
}

async function upload(){
  const bytes=16*1024*1024,data=new Uint8Array(bytes);
  for(let i=0;i<bytes;i+=65536)crypto.getRandomValues(data.subarray(i,Math.min(i+65536,bytes)));
  return await new Promise((resolve,reject)=>{
    const x=new XMLHttpRequest(),start=performance.now();x.open('POST',endpoint(`/__up?measId=${Date.now()}-${Math.random()}`));x.timeout=45000;
    x.upload.onprogress=e=>{if(e.lengthComputable){const mbps=e.loaded*8/1e6/Math.max(.001,(performance.now()-start)/1000);$('speed').textContent=mbps<10?mbps.toFixed(2):mbps.toFixed(1);progress(65+e.loaded/e.total*35,'Uploading')}};
    x.onload=()=>{if(x.status>=200&&x.status<300)resolve(bytes*8/1e6/Math.max(.001,(performance.now()-start)/1000));else reject(Error('Upload test failed.'))};
    x.onerror=()=>reject(Error('Upload connection failed. Check your network or browser privacy settings.'));
    x.ontimeout=()=>reject(Error('Upload test timed out.'));
    x.send(data);
  });
}

function localScore(ping,jitter,download,upload,loss){
  return Math.max(0,Math.min(100,Math.round(100-Math.min(35,ping/4)-Math.min(20,jitter*1.5)-Math.min(20,loss*2)-Math.max(0,30-Math.min(30,download))/1.5)));
}

async function analyze(r){
  if(state.apiBase===''){
    const res=await fetchWithTimeout('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(r)},5000);
    if(res.ok)return res.json();
  }
  const score=localScore(r.ping,r.jitter,r.download,r.upload,r.loss);
  return {score,grade:grade(score)};
}

function grade(n){return n>=90?'Excellent':n>=75?'Very good':n>=55?'Good':n>=35?'Fair':'Poor'}

function renderHealth(r){
  $('score').textContent=`${r.score}/100`;$('grade').textContent=grade(r.score);
  $('advice').textContent=r.score>=85?'Excellent connection for most everyday uses.':r.score>=65?'Good connection; demanding apps may notice latency or load.':'Connection quality needs attention. Check Wi-Fi placement, VPNs and background traffic.';
  $('gaming').textContent=r.ping<30&&r.jitter<8?'Excellent':r.ping<60&&r.jitter<15?'Good':r.ping<100?'Fair':'Poor';
  $('stream').textContent=r.download>=50?'Excellent':r.download>=15?'Good':r.download>=5?'Fair':'Poor';
  $('calls').textContent=r.ping<60&&r.upload>=5?'Excellent':r.ping<100&&r.upload>=2?'Good':'Fair';
}

function renderHistory(){
  const body=$('history');if(!state.history.length){body.innerHTML='<tr><td colspan="6" class="empty">No tests yet.</td></tr>';return}
  body.textContent='';state.history.slice(0,30).forEach(r=>{const tr=document.createElement('tr');[new Date(r.time).toLocaleString(),`${Number(r.ping).toFixed(1)} ms`,`${Number(r.jitter).toFixed(1)} ms`,`${Number(r.download).toFixed(1)} Mbps`,`${Number(r.upload).toFixed(1)} Mbps`,`${Number(r.score)}/100`].forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.appendChild(td)});body.appendChild(tr)});
}

async function run(){
  if(state.busy)return;if(!navigator.onLine)return toast('You are offline.');
  state.busy=true;state.samples=[];$('gauge').classList.add('testing');$('go').disabled=true;$('go').textContent='TESTING';
  try{
    progress(1,'Connecting');$('phase').textContent='Connecting';await detectBackend();
    $('phase').textContent='Latency';const l=await latency();$('ping').textContent=l.ping.toFixed(1);$('jitter').textContent=l.jitter.toFixed(1);$('loss').textContent=l.loss.toFixed(1);
    $('phase').textContent='Download';const down=await download();$('down').textContent=down.toFixed(1);
    $('phase').textContent='Upload';const up=await upload();$('up').textContent=up.toFixed(1);
    $('phase').textContent='Analyzing';progress(98,'Analyzing');const analysis=await analyze({ping:l.ping,jitter:l.jitter,loss:l.loss,download:down,upload:up});
    const result={time:new Date().toISOString(),ping:l.ping,jitter:l.jitter,loss:l.loss,download:down,upload:up,score:analysis.score,server:state.backend};state.last=result;
    state.history.unshift(result);state.history=state.history.slice(0,30);try{localStorage.setItem('pulsenet-history',JSON.stringify(state.history))}catch{}
    renderHealth(result);renderHistory();$('speed').textContent=down.toFixed(1);$('phase').textContent='Complete';progress(100,'Test complete');toast(`Complete — ${analysis.grade}`);
  }catch(e){$('phase').textContent='Test failed';progress(0,'Ready');toast(e.message||'Test failed. Try again.');}
  finally{state.busy=false;$('gauge').classList.remove('testing');$('go').disabled=false;$('go').textContent='RETEST';}
}

function openModal(title,html){$('modalTitle').textContent=title;$('modalBody').innerHTML=html;$('modal').hidden=false}
$('go').onclick=run;
$('clear').onclick=()=>{state.history=[];try{localStorage.removeItem('pulsenet-history')}catch{}renderHistory();toast('History cleared')};
$('copy').onclick=async()=>{if(!state.last)return toast('Run a test first');try{await navigator.clipboard.writeText(JSON.stringify(state.last,null,2));toast('Result copied')}catch{toast('Clipboard unavailable')}};
$('json').onclick=()=>{if(!state.last)return toast('Run a test first');const url=URL.createObjectURL(new Blob([JSON.stringify(state.last,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='pulsenet-result.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
$('share').onclick=async()=>{if(!state.last)return toast('Run a test first');const r=state.last,text=`PulseNet — ${r.download.toFixed(1)} Mbps down / ${r.upload.toFixed(1)} Mbps up / ${r.ping.toFixed(0)} ms ping / ${r.score}/100`;try{if(navigator.share)await navigator.share({title:'PulseNet result',text});else{await navigator.clipboard.writeText(text);toast('Share text copied')}}catch{}};
$('settings').onclick=()=>openModal('Settings','<p>PulseNet automatically uses the local Python server when available. On GitHub Pages or another static host it automatically falls back to Cloudflare’s public speed-test edge.</p><label for="motion">Motion</label><select id="motion"><option value="auto">Use system preference</option><option value="reduce">Reduce animation</option></select><p>Results stay in this browser. The static fallback sends test traffic to Cloudflare’s speed-test service.</p>');
$('about').onclick=()=>openModal('How PulseNet works','<p>PulseNet measures controlled HTTPS traffic. It first tries the self-hosted Python endpoint; if that endpoint is unavailable, the browser uses Cloudflare’s speed-test endpoints so the GitHub Pages version can still perform real measurements.</p><ul><li>Download and upload are measured from actual transferred bytes and elapsed time.</li><li>Latency and jitter use repeated HTTPS timing probes.</li><li>Packet loss is an HTTP probe failure estimate, not an ICMP measurement.</li><li>No SQL or PHP is required.</li><li>History remains local in your browser.</li></ul>');
$('close').onclick=()=>$('modal').hidden=true;$('modal').onclick=e=>{if(e.target===$('modal'))$('modal').hidden=true};
$('modal').addEventListener('change',e=>{if(e.target.id==='motion'){document.documentElement.style.setProperty('scroll-behavior',e.target.value==='reduce'?'auto':'smooth');try{localStorage.setItem('pulsenet-motion',e.target.value)}catch{}}});

function networkInfo(){const c=navigator.connection||navigator.webkitConnection||navigator.mozConnection;if(c){$('conn').textContent=c.effectiveType||c.type||'Detected';$('net').textContent=c.type||c.effectiveType||'Browser API';$('dl').textContent=c.downlink?`${c.downlink} Mbps`:'—';$('brtt').textContent=c.rtt?`${c.rtt} ms`:'—'}else{$('conn').textContent='Detected';$('net').textContent='Browser'}$('device').textContent=/Android/i.test(navigator.userAgent)?'Android':/iPhone|iPad/i.test(navigator.userAgent)?'iOS':/Windows/i.test(navigator.userAgent)?'Windows':/Mac/i.test(navigator.userAgent)?'macOS':'Browser'}

renderHistory();networkInfo();
window.addEventListener('resize',chart);window.addEventListener('online',()=>{$('online').textContent='Online';$('online2').textContent='Online'});window.addEventListener('offline',()=>{$('online').textContent='Offline';$('online2').textContent='Offline'});chart();
