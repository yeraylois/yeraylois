#!/usr/bin/env python3
"""Generate the bilingual editorial weekly-project spotlight."""

from __future__ import annotations

import datetime as dt
import html
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROJECTS_FILE = ROOT / ".github" / "spotlight" / "projects.json"
OUTPUT_DIR = ROOT / "assets" / "spotlight"
META_FILE = ROOT / ".github" / "spotlight" / "current.json"

WIDTH = 840
HEIGHT = 118
ACCENTS = {("es", "dark"): "#d97757", ("es", "light"): "#d97757", ("en", "dark"): "#9be9a8", ("en", "light"): "#5c6bc0"}
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

THEMES = {
    "dark": {
        "line": "#30363d",
        "text1": "#f0f6fc",
        "text2": "#8b949e",
        "quiet": "#6e7681",
    },
    "light": {
        "line": "#d8dee4",
        "text1": "#1f2328",
        "text2": "#59636e",
        "quiet": "#8c959f",
    },
}

TECH_COLORS = {
    "ionic": "#3880ff",
    "android": "#3ddc84",
    "sqlite": "#0f80cc",
    "ansible": "#ee0000",
    "docker": "#2496ed",
    "python": "#3776ab",
    "angular": "#dd0031",
    "prometheus": "#e6522c",
    "grafana": "#f46800",
    "c": "#5c6bc0",
    "microchip": "#a22846",
    "embedded": "#f5822a",
    "zephyr": "#7f4bc4",
}


def short_repo(url: str) -> str:
    path = url.replace("https://github.com/", "").replace("http://github.com/", "")
    if "/tree/" in path:
        repo, branch = path.split("/tree/", 1)
        return f"{repo} @ {branch}"
    return path


def wrap_text(text: str, max_chars: int = 100, max_lines: int = 2) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
        if len(lines) == max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) == max_lines and words and " ".join(lines) != text:
        lines[-1] = lines[-1].rstrip(".") + "…"
    return lines or [""]


def tech_signature(tech_items: list[dict], text_fill: str) -> str:
    x = 132
    parts: list[str] = []
    for item in tech_items:
        label = html.escape(item.get("label", "").upper())
        color = TECH_COLORS.get(item.get("id", "").lower(), "#8b949e")
        parts.append(f'<line x1="{x}" y1="100" x2="{x + 12}" y2="100" stroke="{color}" stroke-width="2"/>')
        parts.append(
            f'<text x="{x + 18}" y="103" fill="{text_fill}" font-size="9" '
            f'font-family="{FONT_MONO}" letter-spacing="0.8">{label}</text>'
        )
        x += 34 + max(34, int(len(item.get("label", "")) * 6.2))
    return "".join(parts)


def build_svg(project: dict, week: int, theme: str, lang: str) -> str:
    colors = THEMES[theme]
    raw_name = project.get("name", "")
    name = html.escape(raw_name)
    raw_description = project.get(f"description_{lang}", project.get("description", ""))
    descriptions = [html.escape(line) for line in wrap_text(raw_description)]
    repo = html.escape(short_repo(project.get("repo", "")))
    tech_items = project.get("tech") if isinstance(project.get("tech"), list) else []
    accent = ACCENTS[(lang, theme)]

    pick_label = "SELECCIÓN ACTUAL" if lang == "es" else "CURRENT PICK"
    action = "ABRIR REPOSITORIO" if lang == "es" else "OPEN REPOSITORY"
    aria_prefix = "Proyecto semanal" if lang == "es" else "Weekly project"
    description_svg = "".join(
        f'<text x="132" y="{58 + index * 17}" fill="{colors["text2"]}" '
        f'font-size="12" font-family="{FONT}">{line}</text>'
        for index, line in enumerate(descriptions)
    )
    technologies = tech_signature(tech_items, colors["text2"])

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{aria_prefix}: {name}">
  <line x1="0" y1="1" x2="{WIDTH}" y2="1" stroke="{colors['line']}"/>
  <line x1="0" y1="1" x2="64" y2="1" stroke="{accent}" stroke-width="2"/>
  <line x1="102" y1="20" x2="102" y2="100" stroke="{colors['line']}"/>

  <text x="0" y="34" fill="{colors['text1']}" font-size="14" font-family="{FONT_MONO}" font-weight="650">W{week:02d}</text>
  <text x="0" y="52" fill="{colors['quiet']}" font-size="9" font-family="{FONT_MONO}" letter-spacing="0.8">{pick_label}</text>

  <text x="132" y="34" fill="{colors['text1']}" font-size="14" font-family="{FONT}" font-weight="650">{name}</text>
  <text x="{WIDTH}" y="33" fill="{colors['quiet']}" font-size="9" font-family="{FONT_MONO}" text-anchor="end" letter-spacing="0.8">{repo}</text>
  {description_svg}
  {technologies}
  <text x="{WIDTH - 24}" y="103" fill="{colors['quiet']}" font-size="9" font-family="{FONT_MONO}" text-anchor="end" letter-spacing="0.8">{action}</text>
  <text x="{WIDTH}" y="105" fill="{accent}" font-size="16" font-family="{FONT}" text-anchor="end">↗</text>
</svg>
"""


def select_project(projects: list[dict], week: int) -> tuple[int, dict]:
    manual = os.getenv("SPOTLIGHT_INDEX", "").strip()
    pinned_id = os.getenv("SPOTLIGHT_PINNED_ID", "").strip()
    if pinned_id:
        try:
            index = next(i for i, project in enumerate(projects) if project.get("id") == pinned_id)
        except StopIteration as error:
            raise RuntimeError(f"Pinned project id not found: {pinned_id}") from error
    elif manual:
        index = max(0, min(len(projects) - 1, int(manual)))
    else:
        index = (week - 1) % len(projects)
    return index, projects[index]


def main() -> None:
    if not PROJECTS_FILE.exists():
        raise FileNotFoundError(f"Missing projects file: {PROJECTS_FILE}")
    projects = json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
    if not isinstance(projects, list) or not projects:
        raise RuntimeError("projects.json must contain a non-empty array")

    week = dt.date.today().isocalendar().week
    index, project = select_project(projects, week)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    META_FILE.parent.mkdir(parents=True, exist_ok=True)

    for theme in THEMES:
        for lang in ("es", "en"):
            svg = build_svg(project=project, week=week, theme=theme, lang=lang)
            (OUTPUT_DIR / f"current-{theme}-{lang}.svg").write_text(svg, encoding="utf-8")

    meta = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "iso_week": week,
        "index": index,
        "project": project,
    }
    META_FILE.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
