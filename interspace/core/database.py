import sqlite3
from pathlib import Path
from typing import Iterator
from interspace.core.config import settings

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS agents (agent_id TEXT PRIMARY KEY,name TEXT NOT NULL,role TEXT NOT NULL,model TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'offline',capabilities_json TEXT NOT NULL DEFAULT '[]',last_heartbeat TEXT,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY,event_type TEXT NOT NULL,agent_id TEXT,payload_json TEXT NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(agent_id) REFERENCES agents(agent_id));
CREATE TABLE IF NOT EXISTS contracts (contract_id TEXT PRIMARY KEY,name TEXT NOT NULL,latest_version INTEGER NOT NULL DEFAULT 0,updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS contract_versions (contract_id TEXT NOT NULL,version INTEGER NOT NULL,definition_json TEXT NOT NULL,created_by TEXT NOT NULL,created_at TEXT NOT NULL,PRIMARY KEY(contract_id,version),FOREIGN KEY(contract_id) REFERENCES contracts(contract_id),FOREIGN KEY(created_by) REFERENCES agents(agent_id));
CREATE TABLE IF NOT EXISTS contract_subscriptions (contract_id TEXT NOT NULL,agent_id TEXT NOT NULL,created_at TEXT NOT NULL,PRIMARY KEY(contract_id,agent_id),FOREIGN KEY(contract_id) REFERENCES contracts(contract_id),FOREIGN KEY(agent_id) REFERENCES agents(agent_id));
CREATE TABLE IF NOT EXISTS notifications (notification_id TEXT PRIMARY KEY,agent_id TEXT NOT NULL,notification_type TEXT NOT NULL,contract_id TEXT NOT NULL,from_version INTEGER NOT NULL,to_version INTEGER NOT NULL,payload_json TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'unread',created_at TEXT NOT NULL,FOREIGN KEY(agent_id) REFERENCES agents(agent_id),FOREIGN KEY(contract_id) REFERENCES contracts(contract_id));
CREATE TABLE IF NOT EXISTS messages (message_id TEXT PRIMARY KEY,sender_id TEXT NOT NULL,recipient_id TEXT NOT NULL,message_type TEXT NOT NULL,payload_json TEXT NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(sender_id) REFERENCES agents(agent_id),FOREIGN KEY(recipient_id) REFERENCES agents(agent_id));
CREATE TABLE IF NOT EXISTS experiences (experience_id TEXT PRIMARY KEY,problem TEXT NOT NULL,action TEXT NOT NULL,result TEXT NOT NULL,verification TEXT NOT NULL,created_by TEXT NOT NULL,status TEXT NOT NULL,metadata_json TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,FOREIGN KEY(created_by) REFERENCES agents(agent_id));
CREATE TABLE IF NOT EXISTS verifications (verification_id TEXT PRIMARY KEY,fact_type TEXT NOT NULL,fact_id TEXT NOT NULL,created_by TEXT NOT NULL,metadata_json TEXT NOT NULL,state TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,FOREIGN KEY(created_by) REFERENCES agents(agent_id));
CREATE TABLE IF NOT EXISTS project_state (key TEXT PRIMARY KEY,value_json TEXT NOT NULL,updated_by TEXT NOT NULL,updated_at TEXT NOT NULL,FOREIGN KEY(updated_by) REFERENCES agents(agent_id));
CREATE TABLE IF NOT EXISTS knowledge (knowledge_id TEXT PRIMARY KEY,key TEXT NOT NULL,value_json TEXT NOT NULL,scope TEXT NOT NULL,created_by TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(created_by) REFERENCES agents(agent_id));
CREATE TABLE IF NOT EXISTS audit_log (audit_id TEXT PRIMARY KEY,event_type TEXT NOT NULL,actor_id TEXT,entity_type TEXT NOT NULL,entity_id TEXT,payload_json TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS qa_runs (qa_run_id TEXT PRIMARY KEY,requested_by TEXT NOT NULL,status TEXT NOT NULL,returncode INTEGER NOT NULL,stdout TEXT NOT NULL,stderr TEXT NOT NULL,timed_out INTEGER NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(requested_by) REFERENCES agents(agent_id));
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_experiences_status ON experiences(status);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_qa_created_at ON qa_runs(created_at);
"""
def get_connection():
    path=Path(settings.database_path); path.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(path); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys = ON"); return c
def initialize_database():
    with get_connection() as c: c.executescript(SCHEMA)
def connection() -> Iterator[sqlite3.Connection]:
    with get_connection() as c: yield c
