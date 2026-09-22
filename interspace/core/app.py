import json,uuid
from datetime import datetime,timezone
from fastapi import FastAPI,HTTPException,Query\nfrom fastapi.middleware.cors import CORSMiddleware
from interspace.agents.models import AgentHeartbeat,AgentRegistration,AgentResponse,utc_now
from interspace.communication.models import EventCreate,EventResponse
from interspace.communication.notifications import ContractSubscriptionCreate,ContractSubscriptionResponse,NotificationResponse
from interspace.communication.messages import MessageCreate,MessageResponse
from interspace.core.contract_diff import diff_contracts
from interspace.core.contracts import ContractDiffResponse,ContractPublish,ContractSummary,ContractVersionResponse
from interspace.core.database import get_connection,initialize_database
from interspace.core.experiences import ExperienceCreate,ExperienceResponse,ExperienceSearch
from interspace.core.verification import VerificationCreate,VerificationResponse,VerificationTransition
from interspace.core.knowledge import ProjectStateUpsert,ProjectStateResponse,KnowledgeCreate,KnowledgeResponse
from interspace.core.qa_models import QARunCreate,QARunResponse
from interspace.core.qa import run_pytest
from interspace.audit.models import AuditEventCreate,AuditEventResponse
from interspace.audit.state import can_transition
from interspace.retrieval.experiences import rank_experiences

app=FastAPI(title="LLM InterSpace Gateway",version="0.5.0")\napp.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
@app.on_event("startup")
def startup(): initialize_database()
def _agent(row): return AgentResponse(agent_id=row["agent_id"],name=row["name"],role=row["role"],model=row["model"],capabilities=json.loads(row["capabilities_json"]),status=row["status"],last_heartbeat=row["last_heartbeat"])
def _audit(conn,event_type,actor_id,entity_type,entity_id,payload):
    now=utc_now(); conn.execute("INSERT INTO audit_log VALUES (?,?,?,?,?,?,?)",(str(uuid.uuid4()),event_type,actor_id,entity_type,entity_id,json.dumps(payload,sort_keys=True),now.isoformat()))
@app.get("/health")
def health(): return {"status":"ok","service":"interspace-gateway"}
@app.get("/network/ping")
def network_ping(): return {"status":"ok","service":"interspace-gateway","gateway_version":app.version,"timestamp":utc_now()}
@app.post("/agents/register",response_model=AgentResponse)
def register_agent(agent:AgentRegistration):
    now=utc_now()
    with get_connection() as c:
        c.execute("INSERT INTO agents VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(agent_id) DO UPDATE SET name=excluded.name,role=excluded.role,model=excluded.model,status='online',capabilities_json=excluded.capabilities_json,last_heartbeat=excluded.last_heartbeat",(agent.agent_id,agent.name,agent.role,agent.model,"online",json.dumps(agent.capabilities),now.isoformat(),now.isoformat()))
        _audit(c,"agent.registered",agent.agent_id,"agent",agent.agent_id,{"role":agent.role,"model":agent.model})
        row=c.execute("SELECT * FROM agents WHERE agent_id=?",(agent.agent_id,)).fetchone()
    return _agent(row)
@app.post("/agents/{agent_id}/heartbeat",response_model=AgentResponse)
def heartbeat(agent_id,heartbeat_data:AgentHeartbeat):
    now=utc_now()
    with get_connection() as c:
        r=c.execute("UPDATE agents SET status=?,last_heartbeat=? WHERE agent_id=?",(heartbeat_data.status,now.isoformat(),agent_id))
        if not r.rowcount: raise HTTPException(404,"Agent not registered")
        row=c.execute("SELECT * FROM agents WHERE agent_id=?",(agent_id,)).fetchone()
    return _agent(row)
@app.get("/agents",response_model=list[AgentResponse])
def list_agents():
    with get_connection() as c: rows=c.execute("SELECT * FROM agents ORDER BY name").fetchall()
    return [_agent(r) for r in rows]
@app.post("/events",response_model=EventResponse)
def create_event(event:EventCreate):
    if event.agent_id:
        with get_connection() as c:
            if not c.execute("SELECT 1 FROM agents WHERE agent_id=?",(event.agent_id,)).fetchone(): raise HTTPException(404,"Agent not registered")
    eid=str(uuid.uuid4()); now=utc_now()
    with get_connection() as c:
        c.execute("INSERT INTO events VALUES (?,?,?,?,?)",(eid,event.event_type,event.agent_id,json.dumps(event.payload),now.isoformat())); _audit(c,event.event_type,event.agent_id,"event",eid,event.payload)
    return EventResponse(event_id=eid,**event.model_dump(),created_at=now)
@app.get("/events",response_model=list[EventResponse])
def list_events(limit:int=100):
    with get_connection() as c: rows=c.execute("SELECT * FROM events ORDER BY created_at DESC LIMIT ?",(max(1,min(limit,500)),)).fetchall()
    return [EventResponse(event_id=r["event_id"],event_type=r["event_type"],agent_id=r["agent_id"],payload=json.loads(r["payload_json"]),created_at=datetime.fromisoformat(r["created_at"])) for r in rows]
@app.post("/contracts/subscribe",response_model=ContractSubscriptionResponse)
def subscribe(s:ContractSubscriptionCreate):
    now=utc_now()
    with get_connection() as c:
        if not c.execute("SELECT 1 FROM agents WHERE agent_id=?",(s.agent_id,)).fetchone(): raise HTTPException(404,"Agent not registered")
        if not c.execute("SELECT 1 FROM contracts WHERE contract_id=?",(s.contract_id,)).fetchone(): raise HTTPException(404,"Contract not found")
        c.execute("INSERT OR IGNORE INTO contract_subscriptions VALUES (?,?,?)",(s.contract_id,s.agent_id,now.isoformat()))
        r=c.execute("SELECT * FROM contract_subscriptions WHERE contract_id=? AND agent_id=?",(s.contract_id,s.agent_id)).fetchone()
    return ContractSubscriptionResponse(contract_id=r["contract_id"],agent_id=r["agent_id"],created_at=datetime.fromisoformat(r["created_at"]))
@app.get("/agents/{agent_id}/notifications",response_model=list[NotificationResponse])
def notifications(agent_id:str,unread_only:bool=False):
    with get_connection() as c:
        if not c.execute("SELECT 1 FROM agents WHERE agent_id=?",(agent_id,)).fetchone(): raise HTTPException(404,"Agent not registered")
        q="SELECT * FROM notifications WHERE agent_id=?"+(" AND status='unread'" if unread_only else "")+" ORDER BY created_at DESC"
        rows=c.execute(q,(agent_id,)).fetchall()
    return [NotificationResponse(notification_id=r["notification_id"],agent_id=r["agent_id"],notification_type=r["notification_type"],contract_id=r["contract_id"],from_version=r["from_version"],to_version=r["to_version"],payload=json.loads(r["payload_json"]),status=r["status"],created_at=datetime.fromisoformat(r["created_at"])) for r in rows]
@app.post("/agents/{agent_id}/notifications/{notification_id}/ack")
def ack(agent_id,notification_id):
    with get_connection() as c:
        r=c.execute("UPDATE notifications SET status='acknowledged' WHERE notification_id=? AND agent_id=?",(notification_id,agent_id))
        if not r.rowcount: raise HTTPException(404,"Notification not found")
    return {"status":"acknowledged","notification_id":notification_id}
@app.post("/contracts/publish",response_model=ContractVersionResponse)
def publish(contract:ContractPublish):
    now=utc_now()
    with get_connection() as c:
        if not c.execute("SELECT 1 FROM agents WHERE agent_id=?",(contract.created_by,)).fetchone(): raise HTTPException(404,"Publishing agent not registered")
        cur=c.execute("SELECT latest_version FROM contracts WHERE contract_id=?",(contract.contract_id,)).fetchone(); version=1 if cur is None else cur["latest_version"]+1
        c.execute("INSERT INTO contracts VALUES (?,?,?,?) ON CONFLICT(contract_id) DO UPDATE SET name=excluded.name,latest_version=excluded.latest_version,updated_at=excluded.updated_at",(contract.contract_id,contract.name,version,now.isoformat()))
        c.execute("INSERT INTO contract_versions VALUES (?,?,?,?,?)",(contract.contract_id,version,json.dumps(contract.definition,sort_keys=True,separators=(",",":")),contract.created_by,now.isoformat()))
        if version>1:
            prev=c.execute("SELECT definition_json FROM contract_versions WHERE contract_id=? AND version=?",(contract.contract_id,version-1)).fetchone()
            changes=diff_contracts(json.loads(prev["definition_json"]),contract.definition)
            if any(changes.values()):
                subs=c.execute("SELECT agent_id FROM contract_subscriptions WHERE contract_id=?",(contract.contract_id,)).fetchall()
                payload={"contract_name":contract.name,"changes":changes,"message":f"Contract {contract.contract_id} changed from v{version-1} to v{version}."}
                for s in subs:
                    nid=str(uuid.uuid4()); c.execute("INSERT INTO notifications VALUES (?,?,?,?,?,?,?,?,?)",(nid,s["agent_id"],"contract_changed",contract.contract_id,version-1,version,json.dumps(payload,sort_keys=True),"unread",now.isoformat()))
                    c.execute("INSERT INTO events VALUES (?,?,?,?,?)",(str(uuid.uuid4()),"contract.changed",s["agent_id"],json.dumps(payload),now.isoformat()))
                _audit(c,"contract.changed",contract.created_by,"contract",contract.contract_id,{"from_version":version-1,"to_version":version,"changes":changes})
        _audit(c,"contract.published",contract.created_by,"contract",contract.contract_id,{"version":version})
    return ContractVersionResponse(contract_id=contract.contract_id,name=contract.name,version=version,definition=contract.definition,created_by=contract.created_by,created_at=now)
@app.get("/contracts",response_model=list[ContractSummary])
def contracts():
    with get_connection() as c: rows=c.execute("SELECT contract_id,name,latest_version,updated_at FROM contracts ORDER BY contract_id").fetchall()
    return [ContractSummary(contract_id=r["contract_id"],name=r["name"],latest_version=r["latest_version"],updated_at=datetime.fromisoformat(r["updated_at"])) for r in rows]
@app.get("/contracts/{contract_id}",response_model=ContractVersionResponse)
def contract(contract_id):
    with get_connection() as c: r=c.execute("SELECT c.contract_id,c.name,v.version,v.definition_json,v.created_by,v.created_at FROM contracts c JOIN contract_versions v ON v.contract_id=c.contract_id AND v.version=c.latest_version WHERE c.contract_id=?",(contract_id,)).fetchone()
    if not r: raise HTTPException(404,"Contract not found")
    return ContractVersionResponse(contract_id=r["contract_id"],name=r["name"],version=r["version"],definition=json.loads(r["definition_json"]),created_by=r["created_by"],created_at=datetime.fromisoformat(r["created_at"]))
@app.get("/contracts/{contract_id}/versions/{version}",response_model=ContractVersionResponse)
def contract_version(contract_id,version):
    with get_connection() as c: r=c.execute("SELECT c.contract_id,c.name,v.version,v.definition_json,v.created_by,v.created_at FROM contracts c JOIN contract_versions v ON v.contract_id=c.contract_id WHERE c.contract_id=? AND v.version=?",(contract_id,version)).fetchone()
    if not r: raise HTTPException(404,"Contract version not found")
    return ContractVersionResponse(contract_id=r["contract_id"],name=r["name"],version=r["version"],definition=json.loads(r["definition_json"]),created_by=r["created_by"],created_at=datetime.fromisoformat(r["created_at"]))
@app.get("/contracts/{contract_id}/diff",response_model=ContractDiffResponse)
def contract_diff(contract_id,from_version:int=Query(ge=1),to_version:int=Query(ge=1)):
    if from_version==to_version: raise HTTPException(400,"Versions must be different")
    with get_connection() as c: rows=c.execute("SELECT version,definition_json FROM contract_versions WHERE contract_id=? AND version IN (?,?) ORDER BY version",(contract_id,from_version,to_version)).fetchall()
    if len(rows)!=2: raise HTTPException(404,"One or both contract versions not found")
    d={r["version"]:json.loads(r["definition_json"]) for r in rows}; return ContractDiffResponse(contract_id=contract_id,from_version=from_version,to_version=to_version,**diff_contracts(d[from_version],d[to_version]))
@app.post("/messages",response_model=MessageResponse)
def create_message(m:MessageCreate):
    with get_connection() as c:
        for aid in (m.sender_id,m.recipient_id):
            if not c.execute("SELECT 1 FROM agents WHERE agent_id=?",(aid,)).fetchone(): raise HTTPException(404,f"Agent not registered: {aid}")
        mid=str(uuid.uuid4()); now=utc_now(); c.execute("INSERT INTO messages VALUES (?,?,?,?,?,?)",(mid,m.sender_id,m.recipient_id,m.message_type,json.dumps(m.payload),now.isoformat())); _audit(c,"message.sent",m.sender_id,"message",mid,m.model_dump())
    return MessageResponse(message_id=mid,**m.model_dump(),created_at=now)
@app.get("/messages",response_model=list[MessageResponse])
def list_messages(agent_id:str|None=None,limit:int=100):
    with get_connection() as c:
        q="SELECT * FROM messages"; args=[]
        if agent_id: q+=" WHERE sender_id=? OR recipient_id=?"; args += [agent_id,agent_id]
        q+=" ORDER BY created_at DESC LIMIT ?"; args.append(max(1,min(limit,500)))
        rows=c.execute(q,args).fetchall()
    return [MessageResponse(message_id=r["message_id"],sender_id=r["sender_id"],recipient_id=r["recipient_id"],message_type=r["message_type"],payload=json.loads(r["payload_json"]),created_at=datetime.fromisoformat(r["created_at"])) for r in rows]
@app.post("/experiences",response_model=ExperienceResponse)
def create_experience(e:ExperienceCreate):
    now=utc_now(); eid=str(uuid.uuid4())
    with get_connection() as c:
        if not c.execute("SELECT 1 FROM agents WHERE agent_id=?",(e.created_by,)).fetchone(): raise HTTPException(404,"Agent not registered")
        c.execute("INSERT INTO experiences VALUES (?,?,?,?,?,?,?,?,?,?)",(eid,e.problem,e.action,e.result,e.verification,e.created_by,e.status,json.dumps(e.metadata),now.isoformat(),now.isoformat())); _audit(c,"experience.created",e.created_by,"experience",eid,{"status":e.status})
    return ExperienceResponse(experience_id=eid,**e.model_dump(),created_at=now,updated_at=now)
@app.get("/experiences",response_model=list[ExperienceResponse])\ndef experiences(limit:int=100):\n    with get_connection() as c: rows=c.execute("SELECT * FROM experiences ORDER BY created_at DESC LIMIT ?",(max(1,min(limit,500)),)).fetchall()\n    return [ExperienceResponse(experience_id=r["experience_id"],problem=r["problem"],action=r["action"],result=r["result"],verification=r["verification"],created_by=r["created_by"],status=r["status"],metadata=json.loads(r["metadata_json"]),created_at=datetime.fromisoformat(r["created_at"]),updated_at=datetime.fromisoformat(r["updated_at"])) for r in rows]\n@app.post("/experiences/search")
def search_experiences(s:ExperienceSearch):
    with get_connection() as c: rows=[dict(r) for r in c.execute("SELECT * FROM experiences WHERE status IN ('VERIFIED','RECONFIRMED') ORDER BY created_at DESC").fetchall()]
    for r in rows: r["metadata"]=json.loads(r.pop("metadata_json")); r["created_at"]=r["created_at"]
    return rank_experiences(rows,s.query,s.limit)
@app.post("/experiences/{experience_id}/transition",response_model=ExperienceResponse)
def transition_experience(experience_id,transition:VerificationTransition):
    with get_connection() as c:
        r=c.execute("SELECT * FROM experiences WHERE experience_id=?",(experience_id,)).fetchone()
        if not r: raise HTTPException(404,"Experience not found")
        if not can_transition(r["status"],transition.target_state): raise HTTPException(409,f"Invalid transition {r['status']} -> {transition.target_state}")
        now=utc_now(); c.execute("UPDATE experiences SET status=?,updated_at=? WHERE experience_id=?",(transition.target_state,now.isoformat(),experience_id)); _audit(c,"experience.transition",transition.actor_id,"experience",experience_id,{"from":r["status"],"to":transition.target_state,"note":transition.note}); r=c.execute("SELECT * FROM experiences WHERE experience_id=?",(experience_id,)).fetchone()
    return ExperienceResponse(experience_id=r["experience_id"],problem=r["problem"],action=r["action"],result=r["result"],verification=r["verification"],created_by=r["created_by"],status=r["status"],metadata=json.loads(r["metadata_json"]),created_at=datetime.fromisoformat(r["created_at"]),updated_at=now)
@app.post("/verifications",response_model=VerificationResponse)
def create_verification(v:VerificationCreate):
    now=utc_now(); vid=str(uuid.uuid4())
    with get_connection() as c:
        if not c.execute("SELECT 1 FROM agents WHERE agent_id=?",(v.created_by,)).fetchone(): raise HTTPException(404,"Agent not registered")
        c.execute("INSERT INTO verifications VALUES (?,?,?,?,?,?,?,?)",(vid,v.fact_type,v.fact_id,v.created_by,json.dumps(v.metadata),"UNVERIFIED",now.isoformat(),now.isoformat())); _audit(c,"verification.created",v.created_by,"verification",vid,{"state":"UNVERIFIED"})
    return VerificationResponse(verification_id=vid,**v.model_dump(),state="UNVERIFIED",created_at=now,updated_at=now)
@app.post("/verifications/{verification_id}/transition",response_model=VerificationResponse)
def transition_verification(verification_id,transition:VerificationTransition):
    with get_connection() as c:
        r=c.execute("SELECT * FROM verifications WHERE verification_id=?",(verification_id,)).fetchone()
        if not r: raise HTTPException(404,"Verification not found")
        if not can_transition(r["state"],transition.target_state): raise HTTPException(409,f"Invalid transition {r['state']} -> {transition.target_state}")
        now=utc_now(); c.execute("UPDATE verifications SET state=?,updated_at=? WHERE verification_id=?",(transition.target_state,now.isoformat(),verification_id)); _audit(c,"verification.transition",transition.actor_id,"verification",verification_id,{"from":r["state"],"to":transition.target_state,"note":transition.note}); r=c.execute("SELECT * FROM verifications WHERE verification_id=?",(verification_id,)).fetchone()
    return VerificationResponse(verification_id=r["verification_id"],fact_type=r["fact_type"],fact_id=r["fact_id"],created_by=r["created_by"],metadata=json.loads(r["metadata_json"]),state=r["state"],created_at=datetime.fromisoformat(r["created_at"]),updated_at=now)
@app.post("/qa/run",response_model=QARunResponse)
def qa_run(q:QARunCreate):
    with get_connection() as c:
        if not c.execute("SELECT 1 FROM agents WHERE agent_id=?",(q.requested_by,)).fetchone(): raise HTTPException(404,"QA agent not registered")
    try: result=run_pytest(q.test_path,q.timeout_seconds); timed=False
    except __import__("subprocess").TimeoutExpired as exc: result={"status":"failed","returncode":124,"stdout":exc.stdout or "","stderr":exc.stderr or "","timed_out":True}; timed=True
    now=utc_now(); qid=str(uuid.uuid4())
    with get_connection() as c:
        c.execute("INSERT INTO qa_runs VALUES (?,?,?,?,?,?,?,?)",(qid,q.requested_by,result["status"],result["returncode"],result["stdout"],result["stderr"],1 if result.get("timed_out") else 0,now.isoformat())); _audit(c,"qa.completed",q.requested_by,"qa_run",qid,result)
        if result["status"]=="passed":
            c.execute("INSERT INTO events VALUES (?,?,?,?,?)",(str(uuid.uuid4()),"qa.passed",q.requested_by,json.dumps({"qa_run_id":qid}),now.isoformat()))
    return QARunResponse(qa_run_id=qid,requested_by=q.requested_by,status=result["status"],returncode=result["returncode"],stdout=result["stdout"],stderr=result["stderr"],timed_out=result.get("timed_out",False),created_at=now)
@app.post("/project-state",response_model=ProjectStateResponse)
def project_state(s:ProjectStateUpsert):
    now=utc_now()
    with get_connection() as c:
        if not c.execute("SELECT 1 FROM agents WHERE agent_id=?",(s.updated_by,)).fetchone(): raise HTTPException(404,"Agent not registered")
        c.execute("INSERT INTO project_state VALUES (?,?,?,?) ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json,updated_by=excluded.updated_by,updated_at=excluded.updated_at",(s.key,json.dumps(s.value),s.updated_by,now.isoformat())); _audit(c,"state.updated",s.updated_by,"project_state",s.key,{"value":s.value})
    return ProjectStateResponse(key=s.key,value=s.value,updated_by=s.updated_by,updated_at=now)
@app.get("/project-state")
def project_state_list():
    with get_connection() as c: rows=c.execute("SELECT * FROM project_state ORDER BY key").fetchall()
    return [ProjectStateResponse(key=r["key"],value=json.loads(r["value_json"]),updated_by=r["updated_by"],updated_at=datetime.fromisoformat(r["updated_at"])) for r in rows]
@app.post("/knowledge",response_model=KnowledgeResponse)
def knowledge(k:KnowledgeCreate):
    now=utc_now(); kid=str(uuid.uuid4())
    with get_connection() as c:
        if not c.execute("SELECT 1 FROM agents WHERE agent_id=?",(k.created_by,)).fetchone(): raise HTTPException(404,"Agent not registered")
        c.execute("INSERT INTO knowledge VALUES (?,?,?,?,?,?,?,?,?)",(kid,k.key,json.dumps(k.value),k.scope,k.created_by,k.status,now.isoformat()))
        _audit(c,"knowledge.created",k.created_by,"knowledge",kid,{"scope":k.scope,"status":k.status})
    return KnowledgeResponse(knowledge_id=kid,**k.model_dump(),created_at=now)
@app.get("/audit",response_model=list[AuditEventResponse])
def audit(limit:int=100):
    with get_connection() as c: rows=c.execute("SELECT * FROM audit_log ORDER BY created_at DESC LIMIT ?",(max(1,min(limit,500)),)).fetchall()
    return [AuditEventResponse(audit_id=r["audit_id"],event_type=r["event_type"],actor_id=r["actor_id"],entity_type=r["entity_type"],entity_id=r["entity_id"],payload=json.loads(r["payload_json"]),created_at=datetime.fromisoformat(r["created_at"])) for r in rows]
