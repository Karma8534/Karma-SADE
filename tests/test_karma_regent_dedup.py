import ast
from pathlib import Path


def _load_normalizer():
    source = Path("Scripts/karma_regent.py").read_text(encoding="utf-8")
    module = ast.parse(source, filename="Scripts/karma_regent.py")
    func = next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == "_normalized_recent_ids")
    mini_module = ast.Module(body=[func], type_ignores=[])
    ast.fix_missing_locations(mini_module)
    namespace = {"MAX_PROCESSED_CACHE": 500}
    exec(compile(mini_module, "karma_regent_normalizer", "exec"), namespace)
    return namespace["_normalized_recent_ids"]


def test_normalized_recent_ids_accepts_list_and_bounds():
    normalizer = _load_normalizer()
    ids = [f"id-{i}" for i in range(600)]
    out = normalizer(ids)
    assert len(out) == 500
    assert out[0] == "id-100"
    assert out[-1] == "id-599"


def test_normalized_recent_ids_accepts_set_without_crashing():
    normalizer = _load_normalizer()
    out = normalizer({"a", "b", "c"})
    assert set(out) == {"a", "b", "c"}


def test_karma_regent_avoids_deprecated_utc_helpers():
    source = Path("Scripts/karma_regent.py").read_text(encoding="utf-8")
    assert "datetime.datetime.utcnow(" not in source
    assert "datetime.datetime.utcfromtimestamp(" not in source
