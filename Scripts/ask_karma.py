#!/usr/bin/env python3
"""
Quick script to send tasks to Karma using FREE Ollama models
Instead of burning Claude Code quota, use this for simple tasks

Usage:
    python ask_karma.py "Check system health"
    python ask_karma.py "List all Python files"
    python ask_karma.py "What's using the most memory?"
"""

import sys
import subprocess
import json

def ask_karma_ollama(question: str, model: str = "llama3.1"):
    """
    Send question to Karma via Ollama (100% FREE, local)

    Args:
        question: What you want Karma to do/answer
        model: Which Ollama model to use (llama3.1, deepseek-coder, etc.)
    """

    print(f"[*] Asking Karma (using {model} - FREE)...")
    print(f"[?] Question: {question}\n")

    try:
        # Call Ollama directly
        result = subprocess.run(
            ["ollama", "run", model, question],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            response = result.stdout.strip()
            print(f"[KARMA] Response:\n{response}\n")
            print(f"[COST] $0.00 (Local Ollama)")
            return response
        else:
            print(f"[ERROR] {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        print("[TIMEOUT] Task took too long (>60s)")
        return None
    except FileNotFoundError:
        print("[ERROR] Ollama not found. Is it installed and running?")
        print("   Check with: ollama list")
        return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def ask_karma_openwebui(question: str, model: str = "llama3.1"):
    """
    Send question to Karma via Open WebUI API

    Requires Open WebUI running on port 8080
    """
    import requests

    print(f"[*] Asking Karma via Open WebUI (using {model})...")
    print(f"[?] Question: {question}\n")

    try:
        response = requests.post(
            "http://localhost:8080/api/chat/completions",
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": question}
                ],
                "stream": False
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            karma_response = result["choices"][0]["message"]["content"]
            print(f"[KARMA] Response:\n{karma_response}\n")
            print(f"[COST] $0.00 (Local Ollama via Open WebUI)")
            return karma_response
        else:
            print(f"[ERROR] {response.status_code} - {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print("[ERROR] Can't connect to Open WebUI. Is it running on port 8080?")
        print("   Falling back to direct Ollama...")
        return ask_karma_ollama(question, model)
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python ask_karma.py 'your question or task'")
        print("\nExamples:")
        print("  python ask_karma.py 'Check system health'")
        print("  python ask_karma.py 'List all running services'")
        print("  python ask_karma.py 'Explain what FastAPI is'")
        sys.exit(1)

    question = " ".join(sys.argv[1:])

    # Try Ollama directly first (faster, more reliable)
    response = ask_karma_ollama(question)

    if response is None:
        # Fallback to Open WebUI API
        response = ask_karma_openwebui(question)

    # Log the interaction (for memory system later)
    try:
        with open("karma_interactions.jsonl", "a") as f:
            import datetime
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "question": question,
                "response": response,
                "method": "ollama_direct"
            }
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        pass  # Logging is optional

    return response


if __name__ == "__main__":
    main()
