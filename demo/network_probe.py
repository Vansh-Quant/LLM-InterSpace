import argparse

from interspace.agents.models import AgentRegistration
from interspace.communication.client import InterSpaceClient, InterSpaceConnectionError


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe an InterSpace gateway from another device.")
    parser.add_argument("gateway_url", help="Example: http://192.168.1.10:8000")
    parser.add_argument("--agent-id", default="network-test-agent")
    parser.add_argument("--name", default="Network Test Agent")
    args = parser.parse_args()

    client = InterSpaceClient(args.gateway_url)

    try:
        print("1. Pinging InterSpace...")
        print(client.ping())

        print("2. Registering test agent...")
        agent = AgentRegistration(
            agent_id=args.agent_id,
            name=args.name,
            role="network-test",
            model="connection-check",
            capabilities=["network_probe"],
        )
        print(client.register(agent))

        print("3. Sending heartbeat...")
        print(client.heartbeat(args.agent_id))

        print("4. Sending test event...")
        print(client.send_event(
            "network.test",
            {"message": "Hello from a second device"},
            agent_id=args.agent_id,
        ))

        print("CONNECTION TEST PASSED")
    except InterSpaceConnectionError as exc:
        print(f"CONNECTION TEST FAILED: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
