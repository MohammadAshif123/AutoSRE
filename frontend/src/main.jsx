import React,{useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';

const API='http://127.0.0.1:8000';
function App(){
 const [health,setHealth]=useState({}); const [cluster,setCluster]=useState({}); const [inc,setInc]=useState([]);
 const [msg,setMsg]=useState('');
 const load=async()=>{try{setHealth(await (await fetch(API+'/health')).json());setCluster(await (await fetch(API+'/cluster/status')).json());setInc(await (await fetch(API+'/incidents')).json())}catch(e){setMsg('Backend unavailable. Start FastAPI first.')}};
 useEffect(()=>{load();const t=setInterval(load,3000);return()=>clearInterval(t)},[]);
 const action=async(path,body)=>{let r=await fetch(API+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body||{})});let x=await r.json();setMsg(JSON.stringify(x));load()};
 const simulate=()=>action('/simulate/failure',{type:'crash'});
 const analyze=async()=>{await fetch(API+'/incidents/analyze',{method:'POST'});load()};
 return <div className="app">
  <header><div><h1>AutoSRE</h1><p>Agentic Self-Healing Kubernetes Operations</p></div><span className={health.safe_mode?'pill warn':'pill ok'}>{health.safe_mode?'SAFE MODE':'AUTONOMOUS MODE'}</span></header>
  <section className="grid stats"><Card t="Cluster" v={health.status||'—'} s={health.namespace}/><Card t="Pods" v={cluster.pods?.ready+'/'+cluster.pods?.total||'—'} s="running / total"/><Card t="Incidents" v={inc.length} s="latest first"/><Card t="Recovery" v={inc[0]?.recovery_succeeded?'VERIFIED':'—'} s={inc[0]?.service||'No completed incident'}/></section>
  <div className="actions"><button onClick={simulate}>Trigger Payment Crash</button><button onClick={analyze}>Observe + Diagnose</button><button onClick={()=>action('/actions/restart',{service:'payment-service'})}>Restart Payment</button></div>
  {msg&&<pre className="message">{msg}</pre>}
  <section className="grid main">
   <div className="panel"><h2>Service Dependency Graph</h2><div className="graph"><Node n="frontend"/><Arrow/><Node n="payment-service" hot={inc[0]?.service==='payment-service'}/><Arrow/><Node n="database"/></div><p className="muted">Observed/modelled dependency path for the demo workload.</p></div>
   <div className="panel"><h2>Agent Activity</h2><Log label="Observer" text={inc[0]?'Incident detected':'Waiting for incident'}/><Log label="Diagnoser" text={inc[0]?.root_cause||'Waiting'}/><Log label="Memory" text={inc[0]?`Similar incidents: ${inc[0].similar_incidents?.length||0}`:'Waiting'}/><Log label="Governor" text={inc[0]?`${inc[0].governor_confidence} — ${inc[0].decision}`:'Waiting'}/><Log label="Executor" text={inc[0]?.result||'Waiting'}/></div>
  </section>
  <section className="panel"><h2>Latest Incident / Root Cause</h2>{inc[0]?<><div className="incidentHead"><b>{inc[0].id}</b><span>{inc[0].service}</span><span>{inc[0].symptom}</span></div><p><b>Root cause:</b> {inc[0].root_cause}</p><p><b>Evidence:</b></p><ul>{inc[0].evidence?.map((e,i)=><li key={i}>{e.source}: {e.message}</li>)}</ul><div className="decision"><b>Confidence:</b> {inc[0].governor_confidence} &nbsp; <b>Risk:</b> {inc[0].risk} &nbsp; <b>Decision:</b> {inc[0].decision} &nbsp; <b>Action:</b> {inc[0].action||'none'}</div><p><b>Result:</b> {inc[0].result||'Not executed'}</p></>:<p className="muted">No incident yet. Trigger the failure to begin the end-to-end demo.</p>}</section>
  <section className="panel"><h2>Incident History</h2>{inc.map(x=><div className="history" key={x.id}><b>{x.id}</b><span>{x.service}</span><span>{x.symptom}</span><span>{x.decision||'—'}</span><span>{x.result||'analyzed'}</span></div>)}</section>
 </div>
}
function Card({t,v,s}){return <div className="card"><span>{t}</span><strong>{v}</strong><small>{s}</small></div>}
function Node({n,hot}){return <div className={hot?'node hot':'node'}>{n}</div>}
function Arrow(){return <div className="arrow">→</div>}
function Log({label,text}){return <div className="log"><b>[{label}]</b><span>{text}</span></div>}
createRoot(document.getElementById('root')).render(<App/>)
