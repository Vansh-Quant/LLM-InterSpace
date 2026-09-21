import argparse
import time

from interspace.agents.models import AgentRegistration
from interspace.communication.client import InterSpaceClient
from interspace.core.contracts import ContractPublish


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a demo InterSpace agent.")
    parser.add_argument("--gateway", required=True, help="InterSpace gateway URL")
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--model", default="demo-model")
    parser.add_argument("--subscribe", help="Contract ID to subscribe to")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--change", action="store_true")
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()

    client = InterSpaceClient(args.gateway)
    agent = AgentRegistration(
        agent_id=args.agent_id,
        name=args.name,
        role=args.role,
        model=args.model,
        capabilities=["demo", "contracts", "notifications"],
    )

    print("PING:", client.ping())
    print("REGISTER:", client.register(agent))

    if args.subscribe:
        print("SUBSCRIBE:", client.subscribe(args.subscribe, args.agent_id))

    if args.publish:
        definition = {"request": {"user_id": "string"}} if not args.change else {"request": {"userId": "string"}}
        contract = ContractPublish(
            contract_id="demo-user-api",
            name="Demo User API",
            definition=definition,
            created_by=args.agent_id,
        )
        print("PUBLISH:", client.publish_contract(contract))

    if args.watch:
        print("Watching notifications. Press Ctrl+C to stop.")
        seen: set[str] = set()
        while True:
            for notification in client.notifications(args.agent_id, unread_only=True):
                if notification["notification_id"] not in seen:
                    print("NOTIFICATION:", notification)
                    seen.add(notification["notification_id"])
            time.sleep(2)


if __name__ == "__main__":
    main()
