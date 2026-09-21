import argparse

from app.graph.checkpoint import create_checkpointer
from app.graph.graph import build_graph
from app.services.conversation_service import create_conversation_service


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--thread", default="cli-demo")
    parser.add_argument("--message", default="Hello from StateFlow.")
    parser.add_argument("--decision", choices=["approve", "reject"])
    args = parser.parse_args()

    service = create_conversation_service(
        build_graph(create_checkpointer())
    )

    if args.decision:
        result = service.resume(args.thread, args.decision)
    else:
        result = service.chat(args.thread, args.message)

    print("Status:", result["status"])
    print("Thread:", result["thread_id"])
    print("Intent:", result["intent"])
    print("Response:", result["response"])
    print("Trace:")
    for item in result["trace"]:
        print("  -", item)

    if result["pending_interrupt"]:
        print("Pending interrupt:")
        print(result["pending_interrupt"])


if __name__ == "__main__":
    main()
