import argparse
from interspace.agents.models import AgentRegistration
from interspace.communication.client import InterSpaceClient
from interspace.core.contracts import ContractPublish
from interspace.core.experiences import ExperienceCreate
from interspace.core.verification import VerificationCreate, VerificationTransition

def register(client, agent_id, name, role):
    return client.register(AgentRegistration(agent_id=agent_id,name=name,role=role,model="demo-local-model",capabilities=["contracts","messages","qa","memory"]))

def main():
    p=argparse.ArgumentParser(description="Run the complete InterSpace contract-drift demo.")
    p.add_argument("--gateway",default="http://127.0.0.1:8000")
    args=p.parse_args()
    c=InterSpaceClient(args.gateway,timeout=120)
    for spec in [("demo-backend","Backend Agent","backend"),("demo-frontend","Frontend Agent","frontend"),("demo-qa","QA Agent","qa")]:
        print("REGISTER:",register(c,*spec))
    v1=ContractPublish(contract_id="user-api",name="User API",created_by="demo-backend",definition={"endpoint":"/users","request":{"user_id":"string"},"response":{"name":"string"}})
    print("CONTRACT V1:",c.publish_contract(v1))
    print("SUBSCRIBE:",c.subscribe("user-api","demo-frontend"))
    v2=v1.model_copy(update={"definition":{"endpoint":"/users","request":{"userId":"string"},"response":{"name":"string"}}})
    print("CONTRACT V2:",c.publish_contract(v2))
    note=c.notifications("demo-frontend",unread_only=True)[0]
    print("DRIFT NOTIFICATION:",note)
    print("MESSAGE:",c.send_message("demo-backend","demo-frontend","contract_drift",note["payload"]))
    experience=c.create_experience(ExperienceCreate(problem="Frontend contract broke after user_id changed to userId",action="Update consumer field and rerun integration tests",result="Consumer patch proposed for request.userId",verification="QA integration suite",created_by="demo-frontend",status="UNVERIFIED"))
    eid=experience["experience_id"]
    print("EXPERIENCE:",experience)
    print("EXPERIENCE OBSERVED:",c.transition_experience(eid,VerificationTransition(target_state="OBSERVED",actor_id="demo-frontend",note="Agent observed the contract drift.")))
    print("EXPERIENCE TESTED:",c.transition_experience(eid,VerificationTransition(target_state="TESTED",actor_id="demo-qa",note="QA execution started.")))
    qa=c.run_qa("demo-qa")
    print("QA RESULT:",qa)
    if qa["status"]=="passed":
        print("EXPERIENCE VERIFIED:",c.transition_experience(eid,VerificationTransition(target_state="VERIFIED",actor_id="demo-qa",note="Full pytest suite passed.")))
        print("REUSE SEARCH:",c.search_experiences("userId contract frontend pytest",limit=3))
    verification=c.create_verification(VerificationCreate(fact_type="contract_fix",fact_id=eid,created_by="demo-qa",metadata={"qa_run_id":qa["qa_run_id"]}))
    print("VERIFICATION:",verification)
    print("VERIFICATION OBSERVED:",c.transition_verification(verification["verification_id"],VerificationTransition(target_state="OBSERVED",actor_id="demo-qa")))
    print("VERIFICATION TESTED:",c.transition_verification(verification["verification_id"],VerificationTransition(target_state="TESTED",actor_id="demo-qa")))
    if qa["status"]=="passed":
        print("VERIFICATION VERIFIED:",c.transition_verification(verification["verification_id"],VerificationTransition(target_state="VERIFIED",actor_id="demo-qa",note="QA passed.")))
    print("\nFULL INTERSPACE DEMO COMPLETE")
if __name__=="__main__": main()
