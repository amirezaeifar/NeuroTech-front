from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "app"


def _python_files(relative: str):
    return list((ROOT / relative).rglob("*.py"))


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def _calls(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            result.add(node.func.attr)
    return result


def test_controllers_do_not_use_sqlalchemy_sessions_or_transactions():
    for path in _python_files("interfaces/http/controllers"):
        imports = _imports(path)
        assert not any(name.startswith("sqlalchemy.orm") for name in imports), path
        assert "commit" not in _calls(path), path
        assert "rollback" not in _calls(path), path


def test_services_are_framework_and_redis_independent():
    for path in _python_files("domain/services"):
        imports = _imports(path)
        assert not any(name == "flask" or name.startswith("flask.") for name in imports), path
        assert not any(name == "redis" or name.startswith("redis.") for name in imports), path
        assert not any(name.startswith("app.infrastructure") for name in imports), path


def test_repository_interfaces_are_framework_and_orm_independent():
    for path in _python_files("domain/repositories"):
        imports = _imports(path)
        assert not any(name == "flask" or name.startswith("flask.") for name in imports), path
        assert not any(name.startswith("sqlalchemy.orm") for name in imports), path


def test_concrete_repositories_live_only_in_infrastructure():
    offenders = [
        path
        for path in ROOT.rglob("*.py")
        if "SqlAlchemy" in path.read_text(encoding="utf-8")
        and "infrastructure" not in path.parts
        and path.name != "main.py"
    ]
    assert offenders == []


def test_composition_root_wires_all_external_adapters():
    source = (ROOT / "main.py").read_text(encoding="utf-8")
    for dependency in (
        "SqlAlchemyUnitOfWork",
        "PyJwtTokenService",
        "WerkzeugPasswordHasher",
        "RedisOtpStore",
        "AuthService",
        "OtpService",
    ):
        assert dependency in source
