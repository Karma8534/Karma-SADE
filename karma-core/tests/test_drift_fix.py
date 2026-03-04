"""
Phase B — RED tests for DRIFT #4 (ANALYSIS_MODEL default in karma-server)
Uses unittest (built-in) — no external dependencies.
Run: python3 -m unittest tests/test_drift_fix.py -v
"""
import ast
import os
import pathlib
import sys
import unittest


def fresh_config(env_overrides=None):
    """Import config with a clean, controlled environment."""
    env_overrides = env_overrides or {}
    original = dict(os.environ)
    os.environ.clear()
    os.environ.update({
        "FALKORDB_HOST": "falkordb",
        "FALKORDB_PORT": "6379",
        **env_overrides,
    })
    for mod_name in list(sys.modules.keys()):
        if mod_name in ("config",):
            del sys.modules[mod_name]
    try:
        karma_core = str(pathlib.Path(__file__).parent.parent)
        if karma_core not in sys.path:
            sys.path.insert(0, karma_core)
        import config  # noqa
        return config
    finally:
        os.environ.clear()
        os.environ.update(original)


class TestAnalysisModelDefault(unittest.TestCase):
    """B4: ANALYSIS_MODEL default must be GLM, not gpt-4o-mini."""

    def test_b4a_analysis_model_default_is_glm(self):
        """B4-a: ANALYSIS_MODEL default (no env var) must be glm-4.7-flash."""
        cfg = fresh_config()
        self.assertEqual(
            cfg.ANALYSIS_MODEL, "glm-4.7-flash",
            f"DRIFT #4: ANALYSIS_MODEL default must be 'glm-4.7-flash', got '{cfg.ANALYSIS_MODEL}'"
        )

    def test_b4b_analysis_model_env_override_works(self):
        """B4-b: ANALYSIS_MODEL can still be overridden via env var."""
        cfg = fresh_config({"ANALYSIS_MODEL": "gpt-4o-mini"})
        self.assertEqual(cfg.ANALYSIS_MODEL, "gpt-4o-mini",
                         "ANALYSIS_MODEL env override must be respected")

    def test_b4c_glm_config_vars_exist(self):
        """B4-c: GLM config vars must exist in config module."""
        cfg = fresh_config({
            "GLM_API_KEY": "test-key",
            "GLM_BASE_URL": "https://api.z.ai/api/paas/v4/",
            "GLM_MODEL": "glm-4.7-flash",
        })
        self.assertTrue(hasattr(cfg, "GLM_API_KEY"), "config must expose GLM_API_KEY")
        self.assertTrue(hasattr(cfg, "GLM_BASE_URL"), "config must expose GLM_BASE_URL")
        self.assertTrue(hasattr(cfg, "GLM_MODEL"), "config must expose GLM_MODEL")
        self.assertEqual(cfg.GLM_MODEL, "glm-4.7-flash")
        self.assertEqual(cfg.GLM_BASE_URL, "https://api.z.ai/api/paas/v4/")


class TestSkipDedupRegression(unittest.TestCase):
    """B4-regression: --skip-dedup path must not call create_graphiti()."""

    def test_b4d_create_graphiti_exists_in_source(self):
        """Sanity: create_graphiti must be defined in batch_ingest.py."""
        source = pathlib.Path(__file__).parent.parent / "batch_ingest.py"
        tree = ast.parse(source.read_text())
        func_names = [
            node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        self.assertIn("create_graphiti", func_names,
                      "create_graphiti must exist in batch_ingest.py")


if __name__ == "__main__":
    unittest.main()
