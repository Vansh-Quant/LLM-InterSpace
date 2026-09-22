import {useEffect,useState} from "react";
const API=import.meta.env.VITE_INTERSPACE_API||"http://127.0.0.1:8000";
async function get(path:string){const r=await fetch(API+path);if(!r.ok)throw new Error(await r.text());return r.json();}
type Agent={agent_id:string;name:string;role:string;model:string;status:string};
type Contract={contract_id:string;name:string;latest_version:number};
type Audit={audit_id:string;event_type:string;actor_id?:string;created_at:string;payload:Record<string,unknown>};

export default function App(){
 const [agents,setAgents]=useState<Agent[]>([]),[contracts,setContracts]=useState<Contract[]>([]),[messages,setMessages]=useState<any[]>([]),[audit,setAudit]=useState<Audit[]>([]),[experiences,setExperiences]=useState<any[]>([]),[qa,setQa]=useState<any[]>([]),[state,setState]=useState<any[]>([]),[error,setError]=useState("");
 async function refresh(){try{const [a,c,m,au,e,q,s]=await Promise.all([get("/agents"),get("/contracts"),get("/messages?limit=30"),get("/audit?limit=40"),get("/experiences?limit=20"),get("/qa/runs?limit=10"),get("/project-state")]);setAgents(a);setContracts(c);setMessages(m);setAudit(au);setExperiences(e);setQa(q);setState(s);setError("");}catch(e){setError(String(e));}}
 useEffect(()=>{refresh();const id=setInterval(refresh,1500);return()=>clearInterval(id)},[]);
 return <main>
  <header><div><div className="eyebrow">LLM INTERSPACE</div><h1>Agent Galaxy</h1><p>The models stay independent. The experience becomes collective.</p></div><button onClick={refresh}>Refresh</button></header>
  {error&&<div className="error">{error}</div>}
  <section className="galaxy">{agents.map(a=><div className={"agent "+a.status} key={a.agent_id}><div className="orb">{a.role[0]?.toUpperCase()}</div><strong>{a.name}</strong><span>{a.role}</span><small>{a.model} · {a.status}</small></div>)}{!agents.length&&<div className="empty">Waiting for agents…</div>}</section>
  <div className="grid">
   <Panel title="Contract Monitor"><div className="rows">{contracts.map(c=><div className="row" key={c.contract_id}><span>{c.name}<small>{c.contract_id}</small></span><b>V{c.latest_version}</b></div>)}</div></Panel>
   <Panel title="Experience Library"><div className="rows">{experiences.map((e,i)=><div className="row" key={i}><span>{e.problem}<small>{e.action}</small></span><b>{e.status}</b></div>)}{!experiences.length&&<div className="empty">No experiences yet.</div>}</div></Panel>
   <Panel title="QA Verification"><div className="rows">{qa.map(q=><div className="row" key={q.qa_run_id}><span>{q.requested_by}<small>{q.stdout?.split("\n").slice(-2).join(" ")}</small></span><b>{q.status.toUpperCase()}</b></div>)}{!qa.length&&<div className="empty">No QA runs yet.</div>}</div></Panel>
   <Panel title="Project State"><div className="rows">{state.map(s=><div className="row" key={s.key}><span>{s.key}<small>{JSON.stringify(s.value)}</small></span><b>VERIFIED</b></div>)}{!state.length&&<div className="empty">No project state yet.</div>}</div></Panel>
   <Panel title="Communication Feed"><div className="feed">{messages.slice(0,12).map(m=><div key={m.message_id}><b>{m.sender_id}</b> → <b>{m.recipient_id}</b><span>{m.message_type}</span></div>)}</div></Panel>
   <Panel title="Audit Timeline"><div className="feed">{audit.slice(0,16).map(a=><div key={a.audit_id}><b>{a.event_type}</b><span>{a.actor_id||"system"} · {new Date(a.created_at).toLocaleTimeString()}</span></div>)}</div></Panel>
  </div>
 </main>
}
function Panel(p:{title:string;children:any}){return <section className="panel"><h2>{p.title}</h2>{p.children}</section>}
