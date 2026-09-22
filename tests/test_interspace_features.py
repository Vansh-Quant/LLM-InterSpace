from fastapi.testclient import TestClient

from interspace.core.app import app

def reg(c, aid, role="test"):
    r=c.post("/agents/register",json={"agent_id":aid,"name":aid,"role":role,"model":"test-model"})
    assert r.status_code==200

def test_messages_memory_verification_and_audit():
    with TestClient(app) as c:
        reg(c,"a"); reg(c,"b","qa")
        r=c.post("/messages",json={"sender_id":"a","recipient_id":"b","message_type":"patch_proposal","payload":{"field":"userId"}})
        assert r.status_code==200
        assert c.get("/messages?agent_id=b").status_code==200

        e=c.post("/experiences",json={"problem":"contract drift","action":"patch consumer","result":"tests pass","verification":"pytest","created_by":"a","status":"UNVERIFIED"})
        assert e.status_code==200; eid=e.json()["experience_id"]
        for target,actor in [("OBSERVED","a"),("TESTED","b"),("VERIFIED","b")]:
            r=c.post(f"/experiences/{eid}/transition",json={"target_state":target,"actor_id":actor})
            assert r.status_code==200
        found=c.post("/experiences/search",json={"query":"contract consumer tests","limit":5})
        assert found.status_code==200 and found.json()

        v=c.post("/verifications",json={"fact_type":"experience","fact_id":eid,"created_by":"b"})
        assert v.status_code==200; vid=v.json()["verification_id"]
        for target in ["OBSERVED","TESTED","VERIFIED"]:
            r=c.post(f"/verifications/{vid}/transition",json={"target_state":target,"actor_id":"b"})
            assert r.status_code==200

        state=c.post("/project-state",json={"key":"demo.status","value":"verified","updated_by":"b"})
        assert state.status_code==200
        assert any(x["event_type"]=="experience.transition" for x in c.get("/audit").json())

def test_invalid_state_transition_rejected():
    with TestClient(app) as c:
        reg(c,"state-agent")
        e=c.post("/experiences",json={"problem":"p","action":"a","result":"r","verification":"v","created_by":"state-agent"}).json()
        r=c.post(f"/experiences/{e['experience_id']}/transition",json={"target_state":"VERIFIED","actor_id":"state-agent"})
        assert r.status_code==409

def test_qa_run_and_record():
    with TestClient(app) as c:
        reg(c,"qa-agent","qa")
        r=c.post("/qa/run",json={"requested_by":"qa-agent","test_path":"tests/test_gateway.py","timeout_seconds":120})
        assert r.status_code==200
        assert r.json()["status"]=="passed"
