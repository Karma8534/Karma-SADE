"""compiler_in_loop.py — PostToolUse handler (condition: Edit/Write).
Runs syntax/lint checks on edited files immediately after edit.
"""
import json, sys, os, subprocess

# File extensions we can check
CHECKABLE = {
    ".py": ["python", "-m", "py_compile"],
    ".js": ["node", "--check"],
    ".ts": None,  # would need tsc, skip for now
    ".json": None,  # json.loads check
}


def handle(context: dict) -> dict:
    """Run syntax check on the file that was just edited/written."""
    tool_name = context.get("tool_name", "")
    tool_input = context.get("input", {})

    file_path = tool_input.get("file_path", "")
    if not file_path or not os.path.exists(file_path):
        return {}

    ext = os.path.splitext(file_path)[1].lower()

    # Python: py_compile
    if ext == ".py":
        try:
            result = subprocess.run(
                ["python", "-m", "py_compile", file_path],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                return {
                    "systemMessage": f"SYNTAX ERROR in {os.path.basename(file_path)}:\n{result.stderr[:500]}",
                    "permissionDecision": "allow",  # warn but don't block
                }
            return {"systemMessage": f"Syntax OK: {os.path.basename(file_path)}"}
        except Exception as e:
            return {"systemMessage": f"Compile check failed: {e}"}

    # JavaScript: node --check
    if ext == ".js":
        try:
            result = subprocess.run(
                ["node", "--check", file_path],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                return {
                    "systemMessage": f"SYNTAX ERROR in {os.path.basename(file_path)}:\n{result.stderr[:500]}",
                }
            return {"systemMessage": f"Syntax OK: {os.path.basename(file_path)}"}
        except Exception:
            return {}

    # JSON: parse check
    if ext == ".json":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)
            return {"systemMessage": f"JSON valid: {os.path.basename(file_path)}"}
        except json.JSONDecodeError as e:
            return {"systemMessage": f"JSON PARSE ERROR in {os.path.basename(file_path)}: {e}"}

    return {}


if __name__ == "__main__":
    if "--test" in sys.argv:
        # Test with a valid Python file
        test_file = os.path.join(os.path.dirname(__file__), "__init__.py")
        result = handle({"tool_name": "Edit", "input": {"file_path": test_file}})
        assert "Syntax OK" in result.get("systemMessage", ""), f"Expected OK, got: {result}"
        # Test with invalid Python
        bad_file = os.path.join(os.path.dirname(__file__), "..", "..", "tmp", "_test_bad.py")
        os.makedirs(os.path.dirname(bad_file), exist_ok=True)
        with open(bad_file, "w") as f:
            f.write("def broken(\n")
        result = handle({"tool_name": "Edit", "input": {"file_path": bad_file}})
        assert "SYNTAX ERROR" in result.get("systemMessage", ""), f"Expected error, got: {result}"
        os.remove(bad_file)
        print("PASS")
        sys.exit(0)

    ctx = json.loads(sys.stdin.read())
    output = handle(ctx)
    print(json.dumps(output))
