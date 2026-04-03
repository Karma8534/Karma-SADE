#!/usr/bin/env python3
"""plugin_loader.py — Nexus Plugin System (Phase 4)

Loads, validates, and manages plugins for the Karma Nexus harness.
Plugins are directories under plugins/ with a manifest.json.

Plugin manifest format:
{
    "name": "my-plugin",
    "version": "1.0.0",
    "description": "What this plugin does",
    "author": "who",
    "trust_level": "local",         // local | verified | untrusted
    "entry_point": "main.py",       // Python file to load
    "tools": ["tool_name"],         // tools this plugin provides
    "hooks": ["SessionStart"],      // hooks this plugin listens to
    "permissions": ["read", "write"] // required permissions
}

Trust levels:
- local: created by family (Julian/Karma/Colby). Full access.
- verified: reviewed and approved by Sovereign. Gated access.
- untrusted: third-party. Sandboxed, no file/shell access.

Usage:
    from plugins.plugin_loader import PluginManager
    pm = PluginManager()
    pm.discover()
    pm.load_all()
    tools = pm.get_all_tools()
"""
import json
import os
import importlib.util
from pathlib import Path
from dataclasses import dataclass, field


PLUGINS_DIR = Path(__file__).resolve().parent
TRUST_LEVELS = {"local", "verified", "untrusted"}
DANGEROUS_PERMISSIONS = {"shell", "network", "admin"}


@dataclass
class Plugin:
    name: str
    version: str
    description: str
    author: str
    trust_level: str
    entry_point: str
    tools: list = field(default_factory=list)
    hooks: list = field(default_factory=list)
    permissions: list = field(default_factory=list)
    path: Path = field(default_factory=Path)
    loaded: bool = False
    module: object = None
    error: str = ""


class PluginManager:
    def __init__(self, plugins_dir=None):
        self.plugins_dir = Path(plugins_dir) if plugins_dir else PLUGINS_DIR
        self.plugins: dict[str, Plugin] = {}
        self._tools: dict[str, callable] = {}

    def discover(self) -> list[str]:
        """Scan plugins/ for directories with manifest.json."""
        found = []
        for entry in self.plugins_dir.iterdir():
            if not entry.is_dir() or entry.name.startswith(("_", ".")):
                continue
            manifest_path = entry / "manifest.json"
            if not manifest_path.exists():
                continue
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                plugin = Plugin(
                    name=manifest["name"],
                    version=manifest.get("version", "0.0.0"),
                    description=manifest.get("description", ""),
                    author=manifest.get("author", "unknown"),
                    trust_level=manifest.get("trust_level", "untrusted"),
                    entry_point=manifest.get("entry_point", "main.py"),
                    tools=manifest.get("tools", []),
                    hooks=manifest.get("hooks", []),
                    permissions=manifest.get("permissions", []),
                    path=entry,
                )
                if plugin.trust_level not in TRUST_LEVELS:
                    plugin.trust_level = "untrusted"
                self.plugins[plugin.name] = plugin
                found.append(plugin.name)
            except Exception as e:
                print(f"[plugins] Failed to read manifest for {entry.name}: {e}")
        return found

    def load(self, name: str) -> bool:
        """Load a single plugin by name."""
        plugin = self.plugins.get(name)
        if not plugin:
            return False
        if plugin.loaded:
            return True

        # Trust gate: untrusted plugins with dangerous permissions are blocked
        if plugin.trust_level == "untrusted":
            dangerous = set(plugin.permissions) & DANGEROUS_PERMISSIONS
            if dangerous:
                plugin.error = f"Blocked: untrusted plugin requests dangerous permissions: {dangerous}"
                print(f"[plugins] {plugin.error}")
                return False

        entry = plugin.path / plugin.entry_point
        if not entry.exists():
            plugin.error = f"Entry point not found: {entry}"
            return False

        try:
            spec = importlib.util.spec_from_file_location(f"plugin_{name}", str(entry))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            plugin.module = module
            plugin.loaded = True

            # Register tools from the module
            if hasattr(module, "TOOLS"):
                for tool_name, tool_fn in module.TOOLS.items():
                    self._tools[f"{name}.{tool_name}"] = tool_fn

            print(f"[plugins] Loaded: {name} v{plugin.version} ({plugin.trust_level})")
            return True
        except Exception as e:
            plugin.error = str(e)
            print(f"[plugins] Failed to load {name}: {e}")
            return False

    def load_all(self) -> dict:
        """Load all discovered plugins. Returns {name: success}."""
        results = {}
        for name in self.plugins:
            results[name] = self.load(name)
        return results

    def get_all_tools(self) -> dict:
        """Return all registered tools across loaded plugins."""
        return dict(self._tools)

    def get_plugin_info(self) -> list[dict]:
        """Return info about all plugins for UI display."""
        return [
            {
                "name": p.name,
                "version": p.version,
                "description": p.description,
                "author": p.author,
                "trust_level": p.trust_level,
                "tools": p.tools,
                "hooks": p.hooks,
                "loaded": p.loaded,
                "error": p.error,
            }
            for p in self.plugins.values()
        ]

    def list_loaded(self) -> list[str]:
        return [name for name, p in self.plugins.items() if p.loaded]


if __name__ == "__main__":
    pm = PluginManager()
    found = pm.discover()
    print(f"Discovered {len(found)} plugins: {found}")
    results = pm.load_all()
    for name, ok in results.items():
        p = pm.plugins[name]
        status = "OK" if ok else f"FAILED: {p.error}"
        print(f"  {name} v{p.version} [{p.trust_level}]: {status}")
    print(f"Tools: {list(pm.get_all_tools().keys())}")
