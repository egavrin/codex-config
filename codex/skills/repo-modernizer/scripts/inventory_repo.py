#!/usr/bin/env python3
"""
Inventory repository structure, agent guidance, and skill systems.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


BUILD_MANIFESTS = {
    "package.json": "npm",
    "pnpm-workspace.yaml": "pnpm",
    "yarn.lock": "yarn",
    "turbo.json": "turbo",
    "nx.json": "nx",
    "pyproject.toml": "python",
    "setup.py": "python",
    "requirements.txt": "python",
    "Pipfile": "python",
    "poetry.lock": "python",
    "Cargo.toml": "cargo",
    "go.mod": "go",
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "build.gradle.kts": "gradle",
    "settings.gradle": "gradle",
    "settings.gradle.kts": "gradle",
    "CMakeLists.txt": "cmake",
    "meson.build": "meson",
    "BUILD": "bazel",
    "BUILD.bazel": "bazel",
    "WORKSPACE": "bazel",
    "Makefile": "make",
    "justfile": "just",
    "composer.json": "composer",
}

LANGUAGE_EXTENSIONS = {
    ".c": "C",
    ".cc": "C++",
    ".cpp": "C++",
    ".cxx": "C++",
    ".h": "C/C++ headers",
    ".hh": "C/C++ headers",
    ".hpp": "C/C++ headers",
    ".hxx": "C/C++ headers",
    ".rs": "Rust",
    ".go": "Go",
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".m": "Objective-C",
    ".mm": "Objective-C++",
    ".cs": "C#",
    ".rb": "Ruby",
    ".php": "PHP",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".ps1": "PowerShell",
    ".lua": "Lua",
    ".scala": "Scala",
    ".sql": "SQL",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".toml": "TOML",
}

README_PREFIXES = ("readme", "contributing", "architecture", "design")
SOURCE_DIR_MARKERS = {"src", "lib", "include", "cmd", "app", "apps", "pkg", "packages", "tests", "test"}
COMPONENT_NAME_HINTS = {
    "app",
    "apps",
    "cli",
    "cmd",
    "component",
    "components",
    "lib",
    "libs",
    "module",
    "modules",
    "package",
    "packages",
    "plugin",
    "plugins",
    "service",
    "services",
    "tool",
    "tools",
}
NON_COMPONENT_DIR_NAMES = {
    "agents",
    "assets",
    "build",
    "dist",
    "docs",
    "doc",
    "examples",
    "example",
    "fixtures",
    "include",
    "references",
    "scripts",
    "src",
    "test",
    "tests",
    "vendor",
}
NON_COMPONENT_SEGMENTS = {"third_party", "vendor", "external"}
DEEMPHASIZED_SEGMENTS = {"test", "tests", "testing", "__tests__", ".claude"}
IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "out",
    "target",
    ".next",
    ".turbo",
    ".cache",
    ".gradle",
    "coverage",
}


@dataclass
class DirInfo:
    rel: str
    manifests: List[str] = field(default_factory=list)
    readmes: List[str] = field(default_factory=list)
    source_examples: List[str] = field(default_factory=list)
    source_counts: Counter = field(default_factory=Counter)
    child_dirs: set = field(default_factory=set)
    files: List[str] = field(default_factory=list)
    tests_present: bool = False
    docs_present: bool = False
    agents_files: List[str] = field(default_factory=list)
    modern_skill_containers: List[str] = field(default_factory=list)
    legacy_skill_containers: List[str] = field(default_factory=list)
    markdown_files: List[str] = field(default_factory=list)


def rel_path(path: Path, root: Path) -> str:
    relative = path.relative_to(root)
    return "." if str(relative) == "." else relative.as_posix()


def parent_rel(path: Path, root: Path) -> str:
    return rel_path(path.parent, root)


def should_ignore_dir(name: str) -> bool:
    return name in IGNORED_DIRS


def is_readme(name: str) -> bool:
    lower = name.lower()
    return any(lower.startswith(prefix) for prefix in README_PREFIXES)


def is_source_marker_dir(name: str) -> bool:
    return name.lower() in SOURCE_DIR_MARKERS


def add_example(bucket: List[str], value: str, limit: int = 5) -> None:
    if value not in bucket and len(bucket) < limit:
        bucket.append(value)


def collect_repo(root: Path) -> Dict[str, DirInfo]:
    info_by_dir: Dict[str, DirInfo] = {}

    def ensure_dir(path: Path) -> DirInfo:
        rel = rel_path(path, root)
        info_by_dir.setdefault(rel, DirInfo(rel=rel))
        return info_by_dir[rel]

    for dirpath, dirnames, filenames in os.walk(root):
        path = Path(dirpath)
        dirnames[:] = sorted(d for d in dirnames if not should_ignore_dir(d))
        info = ensure_dir(path)
        info.child_dirs.update(dirnames)

        for dirname in dirnames:
            child_path = path / dirname
            child_rel = rel_path(child_path, root)
            lower = dirname.lower()
            if dirname == "SKILLS":
                info.legacy_skill_containers.append(child_rel)
            elif dirname == "skills":
                info.modern_skill_containers.append(child_rel)

        for filename in sorted(filenames):
            file_path = path / filename
            rel = rel_path(file_path, root)
            lower = filename.lower()
            suffix = file_path.suffix.lower()

            add_example(info.files, rel, limit=8)

            if filename in BUILD_MANIFESTS:
                info.manifests.append(rel)
            if filename in {"AGENTS.md", "agents.md"}:
                info.agents_files.append(rel)
            if is_readme(filename):
                info.readmes.append(rel)
            if lower.endswith(".md"):
                add_example(info.markdown_files, rel, limit=12)
            if "test" in lower:
                info.tests_present = True
            if lower == "docs" or path.name.lower() == "docs":
                info.docs_present = True

            language = LANGUAGE_EXTENSIONS.get(suffix)
            if language:
                info.source_counts[language] += 1
                add_example(info.source_examples, rel, limit=8)

    return info_by_dir


def summarize_languages(info_by_dir: Dict[str, DirInfo]) -> List[dict]:
    counts = Counter()
    examples = defaultdict(list)

    for info in info_by_dir.values():
        counts.update(info.source_counts)
        for example in info.source_examples:
            suffix = Path(example).suffix.lower()
            language = LANGUAGE_EXTENSIONS.get(suffix)
            if language:
                add_example(examples[language], example, limit=5)

    return [
        {"language": language, "files": count, "evidence": examples[language]}
        for language, count in counts.most_common()
    ]


def summarize_build_systems(info_by_dir: Dict[str, DirInfo]) -> List[dict]:
    evidence = defaultdict(list)
    for info in info_by_dir.values():
        for manifest in info.manifests:
            name = Path(manifest).name
            build_system = BUILD_MANIFESTS[name]
            add_example(evidence[build_system], manifest, limit=8)

    return [
        {"build_system": build_system, "evidence": paths}
        for build_system, paths in sorted(evidence.items())
    ]


def collect_agents_inventory(root: Path) -> dict:
    agents_paths = sorted(
        rel_path(path, root)
        for path in root.rglob("AGENTS.md")
        if not any(part in IGNORED_DIRS for part in path.parts)
    )
    line_counts = {}
    for rel in agents_paths:
        path = root / rel
        try:
            line_counts[rel] = sum(1 for _ in path.open("r", encoding="utf-8", errors="ignore"))
        except OSError:
            continue

    heterogeneous = False
    if line_counts:
        values = list(line_counts.values())
        heterogeneous = max(values) - min(values) >= 80

    return {
        "paths": agents_paths,
        "count": len(agents_paths),
        "quality_signals": {
            "line_counts": line_counts,
            "heterogeneous": heterogeneous,
            "evidence": agents_paths[:5],
        },
    }


def collect_skill_inventory(root: Path) -> dict:
    skill_roots = sorted(
        rel_path(path.parent, root)
        for path in root.rglob("SKILL.md")
        if not any(part in IGNORED_DIRS for part in path.parts)
    )

    modern_containers = sorted(
        rel_path(path, root)
        for path in root.rglob("skills")
        if path.is_dir() and not any(part in IGNORED_DIRS for part in path.parts)
    )
    legacy_containers = sorted(
        rel_path(path, root)
        for path in root.rglob("SKILLS")
        if path.is_dir() and not any(part in IGNORED_DIRS for part in path.parts)
    )

    legacy_patterns = []
    for container in legacy_containers:
        path = root / container
        child_dirs = sorted(
            rel_path(child, root)
            for child in path.iterdir()
            if child.is_dir() and not should_ignore_dir(child.name)
        )
        markdown_commands = []
        for child in path.iterdir():
            if child.is_dir() and not should_ignore_dir(child.name):
                md_files = sorted(f.name for f in child.glob("*.md"))
                if md_files:
                    markdown_commands.append({"path": rel_path(child, root), "markdown_files": md_files[:4]})
        legacy_patterns.append(
            {
                "path": container,
                "pattern": "uppercase-skill-directory",
                "evidence": child_dirs[:8] or [container],
                "markdown_command_dirs": markdown_commands[:8],
            }
        )

    return {
        "modern_skill_containers": modern_containers,
        "modern_skill_roots": skill_roots,
        "legacy_skill_containers": legacy_containers,
        "legacy_skill_patterns": legacy_patterns,
    }


def clear_boundary(rel: str, info: DirInfo) -> tuple[bool, List[str]]:
    if rel == ".":
        return False, []

    path = Path(rel)
    depth = len(path.parts)
    reasons = []
    last = path.name.lower()
    source_total = sum(info.source_counts.values())

    if last in NON_COMPONENT_DIR_NAMES:
        return False, []

    if last in COMPONENT_NAME_HINTS:
        reasons.append("component-name-hint")
    if info.readmes:
        reasons.append("component-readme")
    if any(is_source_marker_dir(name) for name in info.child_dirs):
        reasons.append("source-subtree")
    if source_total >= 20:
        reasons.append("source-density")
    if info.tests_present and source_total >= 20:
        reasons.append("tests-present")

    if info.readmes and ("source-subtree" in reasons or "source-density" in reasons):
        return True, reasons
    if last in COMPONENT_NAME_HINTS and source_total >= 20:
        return True, reasons
    if depth <= 2 and "source-subtree" in reasons and source_total >= 20:
        return True, reasons
    return False, reasons


def detect_component_roots(root: Path, info_by_dir: Dict[str, DirInfo]) -> List[dict]:
    components = []
    for rel, info in sorted(info_by_dir.items()):
        if rel == ".":
            continue

        parts_lower = {part.lower() for part in Path(rel).parts}
        reasons = []
        evidence = []
        build_systems = set()

        if info.manifests:
            reasons.append("build-manifest")
            evidence.extend(info.manifests[:4])
            for manifest in info.manifests:
                build_systems.add(BUILD_MANIFESTS[Path(manifest).name])
        if info.agents_files:
            reasons.append("agents-md")
            evidence.extend(info.agents_files[:2])
        if info.modern_skill_containers:
            reasons.append("modern-skill-dir")
            evidence.extend(info.modern_skill_containers[:2])
        if info.legacy_skill_containers:
            reasons.append("legacy-skill-dir")
            evidence.extend(info.legacy_skill_containers[:2])

        boundary, boundary_reasons = clear_boundary(rel, info)
        if boundary:
            reasons.append("clear-boundary")
            if info.readmes:
                evidence.extend(info.readmes[:2])
            if info.source_examples:
                evidence.extend(info.source_examples[:2])
            else:
                evidence.append(rel)

        if not reasons:
            continue

        strong_signals = {"agents-md", "modern-skill-dir", "legacy-skill-dir"}
        if parts_lower & NON_COMPONENT_SEGMENTS and not (strong_signals & set(reasons)):
            continue
        if parts_lower & DEEMPHASIZED_SEGMENTS and not (strong_signals & set(reasons)):
            continue

        language_counts = [
            {"language": language, "files": count}
            for language, count in info.source_counts.most_common(5)
        ]
        components.append(
            {
                "path": rel,
                "signals": reasons,
                "boundary_reasons": boundary_reasons,
                "evidence": sorted(dict.fromkeys(evidence)),
                "build_systems": sorted(build_systems),
                "languages": language_counts,
                "existing_agents_md": info.agents_files[:1],
                "modern_skill_dirs": info.modern_skill_containers[:4],
                "legacy_skill_dirs": info.legacy_skill_containers[:4],
                "readmes": info.readmes[:4],
            }
        )

    return components


def apply_coverage(components: List[dict], coverage: str) -> List[dict]:
    if coverage == "exhaustive":
        return components
    if coverage == "root-only":
        return []

    def score(component: dict) -> tuple[int, int, str]:
        signals = component["signals"]
        strength = 0
        if "build-manifest" in signals:
            strength += 5
        if "agents-md" in signals:
            strength += 4
        if "modern-skill-dir" in signals or "legacy-skill-dir" in signals:
            strength += 4
        if "clear-boundary" in signals:
            strength += 2
        source_weight = sum(item["files"] for item in component["languages"])
        return (-strength, -source_weight, component["path"])

    mandatory = [
        component
        for component in components
        if {"agents-md", "modern-skill-dir", "legacy-skill-dir"} & set(component["signals"])
    ]
    selected = {component["path"]: component for component in mandatory}
    for component in sorted(components, key=score):
        selected.setdefault(component["path"], component)
        if len(selected) >= 12:
            break
    return [selected[path] for path in sorted(selected)]


def repo_summary(root: Path, info_by_dir: Dict[str, DirInfo]) -> dict:
    top_level = sorted(
        child.name
        for child in root.iterdir()
        if child.exists() and child.name not in IGNORED_DIRS
    )
    root_info = info_by_dir["."]
    docs = sorted(dict.fromkeys(root_info.readmes + root_info.agents_files))[:10]
    return {
        "name": root.name,
        "path": str(root),
        "top_level_entries": top_level[:50],
        "top_level_docs": docs,
        "languages": summarize_languages(info_by_dir)[:12],
        "build_systems": summarize_build_systems(info_by_dir),
    }


def make_report(root: Path, coverage: str) -> dict:
    info_by_dir = collect_repo(root)
    components = detect_component_roots(root, info_by_dir)
    filtered_components = apply_coverage(components, coverage)
    agents_inventory = collect_agents_inventory(root)
    skill_inventory = collect_skill_inventory(root)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "coverage": coverage,
        "repo_profile": repo_summary(root, info_by_dir),
        "component_roots": filtered_components,
        "documentation_inventory": agents_inventory,
        "skill_inventory": skill_inventory,
    }


def to_markdown(report: dict) -> str:
    lines = []
    repo = report["repo_profile"]
    lines.append(f"# Repository Inventory: {repo['name']}")
    lines.append("")
    lines.append("## Repo Profile")
    lines.append(f"- Root: `{report['root']}`")
    lines.append(f"- Coverage: `{report['coverage']}`")
    if repo["build_systems"]:
        lines.append("- Build systems:")
        for item in repo["build_systems"]:
            evidence = ", ".join(f"`{path}`" for path in item["evidence"][:4])
            lines.append(f"  - {item['build_system']}: {evidence}")
    if repo["languages"]:
        lines.append("- Languages:")
        for item in repo["languages"][:8]:
            evidence = ", ".join(f"`{path}`" for path in item["evidence"][:2])
            lines.append(f"  - {item['language']} ({item['files']} files): {evidence}")

    lines.append("")
    lines.append("## Component Roots")
    for component in report["component_roots"]:
        signals = ", ".join(component["signals"])
        evidence = ", ".join(f"`{path}`" for path in component["evidence"][:4])
        lines.append(f"- `{component['path']}`")
        lines.append(f"  - Signals: {signals}")
        lines.append(f"  - Evidence: {evidence}")

    doc_inventory = report["documentation_inventory"]
    lines.append("")
    lines.append("## Documentation Inventory")
    lines.append(f"- AGENTS.md count: {doc_inventory['count']}")
    lines.append(f"- Heterogeneous AGENTS.md sizes: {doc_inventory['quality_signals']['heterogeneous']}")
    for path in doc_inventory["paths"][:12]:
        lines.append(f"  - `{path}`")

    skill_inventory = report["skill_inventory"]
    lines.append("")
    lines.append("## Skill Inventory")
    if skill_inventory["modern_skill_containers"]:
        lines.append("- Modern skill containers:")
        for path in skill_inventory["modern_skill_containers"][:12]:
            lines.append(f"  - `{path}`")
    if skill_inventory["legacy_skill_containers"]:
        lines.append("- Legacy skill containers:")
        for path in skill_inventory["legacy_skill_containers"][:12]:
            lines.append(f"  - `{path}`")
    for item in skill_inventory["legacy_skill_patterns"]:
        evidence = ", ".join(f"`{path}`" for path in item["evidence"][:4])
        lines.append(f"- Legacy pattern at `{item['path']}`: {evidence}")

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inventory repository guidance, components, and skills.")
    parser.add_argument("--root", default=".", help="Repository root to inspect")
    parser.add_argument(
        "--coverage",
        choices=("exhaustive", "key-components", "root-only"),
        default="exhaustive",
        help="Depth of component discovery",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Root does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"Root is not a directory: {root}")

    report = make_report(root, args.coverage)
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=False))
    else:
        print(to_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
