"""Architecture checks for the Milestone 2 boundary."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src" / "hako"
RESERVED_PACKAGES = ("ai", "voice", "memory", "credentials")
RESERVED_PREFIXES = tuple(f"hako.{name}" for name in RESERVED_PACKAGES)
ALLOWED_TOP_LEVEL = frozenset(
    {
        "hako",
        "__future__",
        "argparse",
        "configparser",
        "dataclasses",
        "enum",
        "logging",
        "os",
        "pathlib",
        "platform",
        "re",
        "signal",
        "sys",
        "typing",
    }
)
FORBIDDEN_ATTRIBUTES = frozenset(
    {"urlopen", "urlretrieve", "HTTPConnection", "HTTPSConnection", "create_connection"}
)


def source_files() -> list[Path]:
    return sorted(SOURCE_ROOT.rglob("*.py"))


class ArchitectureTests(unittest.TestCase):
    def test_expected_directory_structure_exists(self) -> None:
        for directory in ("cli", "core", "utils", *RESERVED_PACKAGES):
            package = SOURCE_ROOT / directory
            self.assertTrue(package.is_dir(), f"missing package: {package}")
            self.assertTrue((package / "__init__.py").is_file())

    def test_only_standard_library_and_hako_imports(self) -> None:
        for path in source_files():
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ("hako" if node.level else "")]
                for name in names:
                    top = name.split(".")[0]
                    with self.subTest(path=path.name, import_name=name):
                        self.assertIn(top, ALLOWED_TOP_LEVEL)

    def test_no_later_milestone_packages_are_imported(self) -> None:
        for path in source_files():
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                for name in names:
                    with self.subTest(path=path.name, import_name=name):
                        self.assertFalse(name.startswith(RESERVED_PREFIXES))

    def test_no_network_or_credential_helpers_are_called(self) -> None:
        for path in source_files():
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute):
                    with self.subTest(path=path.name, attribute=node.attr):
                        self.assertNotIn(node.attr, FORBIDDEN_ATTRIBUTES)

    def test_reserved_packages_contain_docstrings_only(self) -> None:
        for name in RESERVED_PACKAGES:
            path = SOURCE_ROOT / name / "__init__.py"
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            unexpected = [
                node
                for node in tree.body
                if not (
                    isinstance(node, ast.Expr)
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                )
            ]
            with self.subTest(package=name):
                self.assertEqual(unexpected, [])

    def test_launcher_does_not_install_or_download(self) -> None:
        text = (PROJECT_ROOT / "scripts" / "hako").read_text(encoding="utf-8").lower()
        for token in ("pip", "apt", "curl", "wget", "install"):
            with self.subTest(token=token):
                self.assertNotIn(token, text)

    def test_requirements_has_no_runtime_dependencies(self) -> None:
        lines = (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        active = [line for line in lines if line.strip() and not line.lstrip().startswith("#")]
        self.assertEqual(active, [])


if __name__ == "__main__":
    unittest.main()
