"""TDD tests for k2_tools.py — structured tool registry for Karma MCP Phase 2."""
import os
import sys
import json
import tempfile
import shutil
import unittest

# Module under test — will be created after these tests RED
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestToolRegistry(unittest.TestCase):
    """Tool discovery: /api/tools/list returns all registered tools with schemas."""

    def test_list_tools_returns_list(self):
        from k2_tools import list_tools
        tools = list_tools()
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)

    def test_each_tool_has_required_fields(self):
        from k2_tools import list_tools
        for tool in list_tools():
            self.assertIn("name", tool, f"Tool missing 'name': {tool}")
            self.assertIn("description", tool, f"Tool missing 'description': {tool}")
            self.assertIn("input_schema", tool, f"Tool missing 'input_schema': {tool}")
            self.assertIsInstance(tool["input_schema"], dict)

    def test_tool_names_are_unique(self):
        from k2_tools import list_tools
        names = [t["name"] for t in list_tools()]
        self.assertEqual(len(names), len(set(names)), f"Duplicate tool names: {names}")

    def test_expected_tools_present(self):
        from k2_tools import list_tools
        names = {t["name"] for t in list_tools()}
        expected = {"file_read", "file_write", "file_list", "file_search",
                    "python_exec", "service_status", "service_restart",
                    "scratchpad_read", "scratchpad_write"}
        for name in expected:
            self.assertIn(name, names, f"Expected tool '{name}' not found")


class TestExecuteTool(unittest.TestCase):
    """Tool execution: /api/tools/execute dispatches to handler and returns structured result."""

    def test_execute_unknown_tool_returns_error(self):
        from k2_tools import execute_tool
        result = execute_tool("nonexistent_tool", {})
        self.assertFalse(result["ok"])
        self.assertIn("error", result)

    def test_execute_returns_ok_true_on_success(self):
        from k2_tools import execute_tool
        # scratchpad_read should always work (returns empty if file missing)
        result = execute_tool("scratchpad_read", {})
        self.assertTrue(result["ok"])


class TestFileRead(unittest.TestCase):
    """file_read tool: read file contents with metadata."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.testfile = os.path.join(self.tmpdir, "test.txt")
        with open(self.testfile, "w") as f:
            f.write("hello world")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_read_existing_file(self):
        from k2_tools import execute_tool
        result = execute_tool("file_read", {"path": self.testfile})
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["content"], "hello world")
        self.assertEqual(result["result"]["size"], 11)
        self.assertTrue(result["result"]["exists"])

    def test_read_missing_file(self):
        from k2_tools import execute_tool
        result = execute_tool("file_read", {"path": "/tmp/nonexistent_file_xyz.txt"})
        self.assertTrue(result["ok"])
        self.assertFalse(result["result"]["exists"])
        self.assertIsNone(result["result"]["content"])

    def test_read_requires_path(self):
        from k2_tools import execute_tool
        result = execute_tool("file_read", {})
        self.assertFalse(result["ok"])
        self.assertIn("error", result)


class TestFileWrite(unittest.TestCase):
    """file_write tool: write content to file."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_write_new_file(self):
        from k2_tools import execute_tool
        path = os.path.join(self.tmpdir, "new.txt")
        result = execute_tool("file_write", {"path": path, "content": "test content"})
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["bytes_written"], 12)
        with open(path) as f:
            self.assertEqual(f.read(), "test content")

    def test_write_requires_path_and_content(self):
        from k2_tools import execute_tool
        result = execute_tool("file_write", {"path": "/tmp/x.txt"})
        self.assertFalse(result["ok"])

    def test_write_creates_parent_dirs(self):
        from k2_tools import execute_tool
        path = os.path.join(self.tmpdir, "sub", "dir", "file.txt")
        result = execute_tool("file_write", {"path": path, "content": "nested"})
        self.assertTrue(result["ok"])
        with open(path) as f:
            self.assertEqual(f.read(), "nested")


class TestFileList(unittest.TestCase):
    """file_list tool: list directory contents."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        open(os.path.join(self.tmpdir, "a.txt"), "w").close()
        open(os.path.join(self.tmpdir, "b.py"), "w").close()
        os.mkdir(os.path.join(self.tmpdir, "subdir"))

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_list_directory(self):
        from k2_tools import execute_tool
        result = execute_tool("file_list", {"path": self.tmpdir})
        self.assertTrue(result["ok"])
        names = [e["name"] for e in result["result"]["entries"]]
        self.assertIn("a.txt", names)
        self.assertIn("b.py", names)
        self.assertIn("subdir", names)

    def test_list_with_pattern(self):
        from k2_tools import execute_tool
        result = execute_tool("file_list", {"path": self.tmpdir, "pattern": "*.txt"})
        self.assertTrue(result["ok"])
        names = [e["name"] for e in result["result"]["entries"]]
        self.assertIn("a.txt", names)
        self.assertNotIn("b.py", names)

    def test_list_includes_type(self):
        from k2_tools import execute_tool
        result = execute_tool("file_list", {"path": self.tmpdir})
        entries = {e["name"]: e["type"] for e in result["result"]["entries"]}
        self.assertEqual(entries["a.txt"], "file")
        self.assertEqual(entries["subdir"], "directory")


class TestFileSearch(unittest.TestCase):
    """file_search tool: grep-like search in files."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        with open(os.path.join(self.tmpdir, "a.txt"), "w") as f:
            f.write("line one\nfoo bar\nline three\n")
        with open(os.path.join(self.tmpdir, "b.txt"), "w") as f:
            f.write("no match here\n")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_search_finds_matches(self):
        from k2_tools import execute_tool
        result = execute_tool("file_search", {"path": self.tmpdir, "pattern": "foo"})
        self.assertTrue(result["ok"])
        self.assertGreater(len(result["result"]["matches"]), 0)
        match = result["result"]["matches"][0]
        self.assertIn("file", match)
        self.assertIn("line", match)
        self.assertIn("text", match)

    def test_search_no_matches(self):
        from k2_tools import execute_tool
        result = execute_tool("file_search", {"path": self.tmpdir, "pattern": "zzznomatch"})
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["result"]["matches"]), 0)


class TestPythonExec(unittest.TestCase):
    """python_exec tool: execute Python code and return result."""

    def test_simple_expression(self):
        from k2_tools import execute_tool
        result = execute_tool("python_exec", {"code": "print(2 + 2)"})
        self.assertTrue(result["ok"])
        self.assertIn("4", result["result"]["stdout"])
        self.assertEqual(result["result"]["exit_code"], 0)

    def test_syntax_error(self):
        from k2_tools import execute_tool
        result = execute_tool("python_exec", {"code": "def ("})
        self.assertTrue(result["ok"])  # tool succeeds, code fails
        self.assertNotEqual(result["result"]["exit_code"], 0)

    def test_requires_code(self):
        from k2_tools import execute_tool
        result = execute_tool("python_exec", {})
        self.assertFalse(result["ok"])


class TestScratchpad(unittest.TestCase):
    """scratchpad_read/write tools: working memory persistence."""

    def setUp(self):
        # Override scratchpad path for testing
        import k2_tools
        self._orig_path = k2_tools.SCRATCHPAD_PATH
        self.tmpdir = tempfile.mkdtemp()
        k2_tools.SCRATCHPAD_PATH = os.path.join(self.tmpdir, "scratchpad.md")

    def tearDown(self):
        import k2_tools
        k2_tools.SCRATCHPAD_PATH = self._orig_path
        shutil.rmtree(self.tmpdir)

    def test_read_empty_scratchpad(self):
        from k2_tools import execute_tool
        result = execute_tool("scratchpad_read", {})
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["content"], "")

    def test_write_replace(self):
        from k2_tools import execute_tool
        execute_tool("scratchpad_write", {"content": "hello", "mode": "replace"})
        result = execute_tool("scratchpad_read", {})
        self.assertEqual(result["result"]["content"], "hello")

    def test_write_append(self):
        from k2_tools import execute_tool
        execute_tool("scratchpad_write", {"content": "first", "mode": "replace"})
        execute_tool("scratchpad_write", {"content": "\nsecond", "mode": "append"})
        result = execute_tool("scratchpad_read", {})
        self.assertEqual(result["result"]["content"], "first\nsecond")


if __name__ == "__main__":
    unittest.main()
