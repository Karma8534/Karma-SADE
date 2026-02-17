#!/usr/bin/env python3
"""
Karma CLI — Talk to Karma from anywhere.
Usage:
    karma chat              Start interactive conversation
    karma status            Quick system status
    karma ask "question"    Single question, get answer, exit
    karma code "prompt"     Run Claude Code through Karma router (no credit use)
    karma goals             Show active goals
    karma graph             Visualize knowledge connections
    karma reflect           Trigger self-reflection
    karma know <topic>      What does Karma know about <topic>?
    karma rel <entity>      Show entity relationships
"""
import asyncio
import json
import sys
import os
import signal

# Default server — override with KARMA_HOST env var
KARMA_HOST = os.getenv("KARMA_HOST", "ws://localhost:8340")
KARMA_HTTP = KARMA_HOST.replace("ws://", "http://").replace("wss://", "https://")


# ─── Colors ───────────────────────────────────────────────────────────────

class C:
    """Terminal colors."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    WHITE = "\033[37m"
    MAGENTA = "\033[95m"

    @staticmethod
    def karma(text):
        return f"{C.PURPLE}{C.BOLD}Karma{C.RESET}{C.DIM} >{C.RESET} {C.WHITE}{text}{C.RESET}"

    @staticmethod
    def neo(text):
        return f"{C.CYAN}{C.BOLD}Neo{C.RESET}{C.DIM}   >{C.RESET} {text}"

    @staticmethod
    def system(text):
        return f"{C.DIM}[{text}]{C.RESET}"

    @staticmethod
    def error(text):
        return f"{C.RED}{text}{C.RESET}"


# ─── Banner ───────────────────────────────────────────────────────────────

BANNER = f"""{C.PURPLE}{C.BOLD}
   ╦╔═┌─┐┬─┐┌┬┐┌─┐
   ╠╩╗├─┤├┬┘│││├─┤
   ╩ ╩┴ ┴┴└─┴ ┴┴ ┴{C.RESET}
{C.DIM}   Terminal Chat v0.1{C.RESET}
"""


# ─── Interactive Chat ─────────────────────────────────────────────────────

async def chat_session():
    """Start an interactive WebSocket chat with Karma."""
    try:
        import websockets
    except ImportError:
        print(C.error("Missing dependency: pip install websockets"))
        sys.exit(1)

    print(BANNER)
    print(C.system(f"Connecting to {KARMA_HOST}/chat ..."))

    try:
        async with websockets.connect(f"{KARMA_HOST}/chat") as ws:
            # Receive welcome message
            welcome = await ws.recv()
            welcome_data = json.loads(welcome)
            print(C.system(welcome_data.get("message", "Connected")))
            print(C.system("Type /help for commands, /quit to exit"))
            print()

            # Handle input/output concurrently
            async def receiver():
                """Listen for messages from Karma."""
                try:
                    async for message in ws:
                        data = json.loads(message)
                        msg_type = data.get("type", "")
                        msg = data.get("message", "")

                        if msg_type == "thinking":
                            print(f"\r{C.DIM}  thinking...{C.RESET}", end="", flush=True)
                        elif msg_type == "response":
                            # Clear the thinking indicator
                            print(f"\r{' ' * 40}\r", end="")
                            print(C.karma(msg))
                            print()
                        elif msg_type == "command_result":
                            print(f"\r{' ' * 40}\r", end="")
                            print(f"{C.GREEN}{msg}{C.RESET}")
                            print()
                        elif msg_type == "system":
                            print(C.system(msg))
                            print()
                        elif msg_type == "error":
                            print(C.error(f"Error: {msg}"))
                            print()
                        elif msg_type == "proactive":
                            # Karma initiating a message
                            print(f"\n{C.MAGENTA}{C.BOLD}Karma{C.RESET}{C.DIM} (proactive) >{C.RESET} {msg}")
                            print()
                except Exception:
                    pass

            async def sender():
                """Read user input and send to Karma."""
                loop = asyncio.get_event_loop()
                try:
                    while True:
                        # Read input in a thread to not block the event loop
                        try:
                            user_input = await loop.run_in_executor(
                                None, lambda: input(f"{C.CYAN}{C.BOLD}Neo{C.RESET}{C.DIM}   > {C.RESET}")
                            )
                        except EOFError:
                            break

                        text = user_input.strip()
                        if not text:
                            continue

                        # Local commands
                        if text.lower() in ("/quit", "/exit", "/q"):
                            print(C.system("Disconnecting..."))
                            return
                        elif text.lower() == "/help":
                            print_help()
                            continue
                        elif text.lower() == "/clear":
                            os.system("cls" if os.name == "nt" else "clear")
                            print(BANNER)
                            continue

                        # Check if it's a server command
                        if text.startswith("/"):
                            cmd = text[1:]
                            await ws.send(json.dumps({"type": "command", "message": cmd}))
                        else:
                            await ws.send(json.dumps({"type": "chat", "message": text}))

                except asyncio.CancelledError:
                    pass

            # Run sender and receiver concurrently
            receiver_task = asyncio.create_task(receiver())
            try:
                await sender()
            finally:
                receiver_task.cancel()
                try:
                    await receiver_task
                except asyncio.CancelledError:
                    pass

    except ConnectionRefusedError:
        print(C.error(f"Cannot connect to Karma at {KARMA_HOST}"))
        print(C.error("Is the server running? Try: ssh vault-neo 'docker logs karma-server'"))
        sys.exit(1)
    except Exception as e:
        print(C.error(f"Connection error: {e}"))
        sys.exit(1)


def print_help():
    """Print available commands."""
    print(f"""
{C.BOLD}Chat Commands:{C.RESET}
  {C.CYAN}/status{C.RESET}       System status (graph, prefs, sessions)
  {C.CYAN}/goals{C.RESET}        Active goals and tasks
  {C.CYAN}/graph{C.RESET}        ASCII knowledge graph visualization
  {C.CYAN}/reflect{C.RESET}      Karma's self-reflection
  {C.CYAN}/know <topic>{C.RESET} What Karma knows about a topic
  {C.CYAN}/rel <entity>{C.RESET} Show entity relationships
  {C.CYAN}/clear{C.RESET}        Clear screen
  {C.CYAN}/help{C.RESET}         This help text
  {C.CYAN}/quit{C.RESET}         Exit chat

{C.DIM}Or just type naturally to chat with Karma.{C.RESET}
""")


# ─── Single Question Mode ─────────────────────────────────────────────────

def single_ask(question: str):
    """Ask a single question via HTTP, print answer, exit."""
    try:
        import httpx
    except ImportError:
        print(C.error("Missing dependency: pip install httpx"))
        sys.exit(1)

    print(C.system(f"Asking Karma: {question}"))

    try:
        resp = httpx.get(f"{KARMA_HTTP}/ask", params={"q": question}, timeout=30.0)
        data = resp.json()
        if "error" in data:
            print(C.error(data["error"]))
        else:
            print()
            print(C.karma(data["answer"]))
    except httpx.ConnectError:
        print(C.error(f"Cannot connect to Karma at {KARMA_HTTP}"))
        sys.exit(1)
    except Exception as e:
        print(C.error(f"Error: {e}"))
        sys.exit(1)


# ─── HTTP Commands ─────────────────────────────────────────────────────────

def http_status():
    """Get system status via HTTP."""
    try:
        import httpx
    except ImportError:
        print(C.error("Missing dependency: pip install httpx"))
        sys.exit(1)

    try:
        resp = httpx.get(f"{KARMA_HTTP}/status", timeout=10.0)
        data = resp.json()

        karma = data.get("karma", {})
        kg = data.get("knowledge_graph", {})
        prefs = data.get("preferences", {})

        print(f"""
{C.PURPLE}{C.BOLD}Karma Status{C.RESET}
{C.DIM}{'─' * 40}{C.RESET}
  State:          {C.GREEN}{karma.get('state', '?')}{C.RESET}
  Consciousness:  {karma.get('consciousness_loop', '?')}
  Uptime:         {karma.get('uptime_seconds', 0)}s

{C.BOLD}Knowledge Graph{C.RESET}
  Entities:       {kg.get('entities', '?')}
  Episodes:       {kg.get('episodes', '?')}
  Relationships:  {kg.get('relationships', '?')}

{C.BOLD}Preferences{C.RESET}
  Total:          {prefs.get('total', '?')}
  Categories:     {prefs.get('by_category', {})}

{C.BOLD}Sessions{C.RESET}
  Active:         {data.get('active_sessions', 0)}
""")
    except Exception as e:
        print(C.error(f"Cannot reach Karma: {e}"))
        sys.exit(1)


# ─── Claude Code Integration ───────────────────────────────────────────────

def code_ask(prompt: str):
    """Ask Claude Code through Karma's router (OpenAI-compatible endpoint)."""
    try:
        import httpx
        import json
    except ImportError:
        print(C.error("Missing dependency: pip install httpx"))
        sys.exit(1)

    print(C.system(f"Routing through Karma → MiniMax/GLM-5"))
    print()

    try:
        # Use the OpenAI-compatible /v1/chat/completions endpoint
        # which routes through Karma's intelligent router
        resp = httpx.post(
            f"{KARMA_HTTP}/v1/chat/completions",
            json={
                "model": "glm-5-coding",
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=120.0,  # Increased timeout for LLM responses
        )
        data = resp.json()

        if "error" in data:
            print(C.error(data["error"]))
        elif "choices" in data and len(data["choices"]) > 0:
            response = data["choices"][0]["message"]["content"]
            model_used = data.get("model", "unknown")
            print(C.karma(response))
            print()
            print(C.system(f"Model: {model_used}"))
        else:
            print(C.error(f"Unexpected response: {data}"))
    except httpx.ConnectError:
        print(C.error(f"Cannot connect to Karma at {KARMA_HTTP}"))
        sys.exit(1)
    except Exception as e:
        print(C.error(f"Error: {e}"))
        sys.exit(1)


# ─── Main ─────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: karma <command> [args]")
        print("Commands: chat, status, ask, code, goals, graph, reflect, know, rel")
        print("Try: karma chat")
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "chat":
        # Handle Ctrl+C gracefully
        signal.signal(signal.SIGINT, lambda *_: (print(f"\n{C.system('Goodbye.')}"), sys.exit(0)))
        asyncio.run(chat_session())

    elif command == "status":
        http_status()

    elif command == "ask":
        if len(sys.argv) < 3:
            print(C.error("Usage: karma ask \"your question here\""))
            sys.exit(1)
        question = " ".join(sys.argv[2:])
        single_ask(question)

    elif command == "code":
        if len(sys.argv) < 3:
            print(C.error("Usage: karma code \"your prompt here\""))
            print(C.system("Example: karma code \"Write a Python function to reverse a list\""))
            print(C.system("This routes through Karma's multi-model router (MiniMax M2.5, GLM-5, Groq, OpenAI)"))
            print(C.system("Zero API credits consumed — uses the $30/mo GLM-5 plan"))
            sys.exit(1)
        prompt = " ".join(sys.argv[2:])
        code_ask(prompt)

    elif command in ("goals", "graph", "reflect"):
        # These commands go through the /ask endpoint with a command prefix
        single_ask(f"/{command}")

    elif command == "know":
        if len(sys.argv) < 3:
            print(C.error("Usage: karma know <topic>"))
            sys.exit(1)
        topic = " ".join(sys.argv[2:])
        single_ask(f"/know {topic}")

    elif command == "rel":
        if len(sys.argv) < 3:
            print(C.error("Usage: karma rel <entity>"))
            sys.exit(1)
        entity = " ".join(sys.argv[2:])
        single_ask(f"/rel {entity}")

    else:
        print(C.error(f"Unknown command: {command}"))
        print("Commands: chat, status, ask, code, goals, graph, reflect, know, rel")
        sys.exit(1)


if __name__ == "__main__":
    main()
