#!/usr/bin/env python3
"""
/*************************************************************
 *   PROJECT : YERAYLOIS GITHUB PROFILE                      *
 *   FILE    : .github/scripts/generate_spotlight.py         *
 *   PURPOSE : GENERATE WEEKLY PROJECT SPOTLIGHT SVG CARD    *
 *   AUTHOR  : Yeray Lois Sanchez                            *
 *   EMAIL   : yeray.lois@udc.es                             *
 *************************************************************/
"""

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
HEIGHT = 195

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "border": "#30363d",
        "text1": "#e6edf3",
        "text2": "#7d8590",
        "link": "#58a6ff",
    },
    "light": {
        "bg": "#ffffff",
        "border": "#d1d9e0",
        "text1": "#1f2328",
        "text2": "#656d76",
        "link": "#0969da",
    },
}

TECH_COLORS = {
    "ionic": "#3880FF",
    "android": "#3DDC84",
    "sqlite": "#0F80CC",
    "ansible": "#EE0000",
    "docker": "#2496ED",
    "python": "#3572A5",
    "angular": "#DD0031",
    "prometheus": "#E6522C",
    "grafana": "#F46800",
    "c": "#555555",
    "microchip": "#A22846",
    "embedded": "#F5822A",
}


def short_repo(url: str) -> str:
    path = url.replace("https://github.com/", "").replace("http://github.com/", "")
    if "/tree/" in path:
        repo, branch = path.split("/tree/", 1)
        return f"{repo} @ {branch}"
    return path


def wrap_desc(text: str, max_chars: int = 75, max_lines: int = 2) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if len(test) <= max_chars:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
            if len(lines) >= max_lines:
                break
    if current and len(lines) < max_lines:
        lines.append(current)
    elif current and lines:
        last = lines[-1]
        if len(last) > 3:
            lines[-1] = last[:-3] + "..."
    return lines or [""]


def accent_gradient(tech_items: list[dict]) -> str:
    colors = [TECH_COLORS.get(t.get("id", "").lower(), "#8b949e") for t in tech_items]
    if not colors:
        colors = ["#8b949e"]
    if len(colors) == 1:
        colors = colors * 2
    stops = "".join(
        f'<stop offset="{i / (len(colors) - 1) * 100:.0f}%" stop-color="{c}"/>'
        for i, c in enumerate(colors)
    )
    return f'<linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">{stops}</linearGradient>'


def tech_dots(tech_items: list[dict], x0: int, y: int, text_fill: str) -> str:
    parts: list[str] = []
    x = x0
    for item in tech_items:
        label = html.escape(item.get("label", ""))
        color = TECH_COLORS.get(item.get("id", "").lower(), "#8b949e")
        parts.append(f'<circle cx="{x}" cy="{y - 4}" r="5" fill="{color}"/>')
        parts.append(
            f'<text x="{x + 13}" y="{y}" fill="{text_fill}" '
            f'font-size="12.5" font-weight="500" font-family="{FONT}">'
            f"{label}</text>"
        )
        text_w = max(len(label) * 7.5, 18)
        x += 13 + int(text_w) + 22
    return "".join(parts)


def build_svg(project: dict, week: int, theme: str) -> str:
    t = THEMES[theme]
    name = html.escape(project.get("name", ""))
    desc_lines = [html.escape(ln) for ln in wrap_desc(project.get("description", ""))]
    repo = html.escape(short_repo(project.get("repo", "")))
    tech_items = project.get("tech") if isinstance(project.get("tech"), list) else []

    name_len = len(project.get("name", ""))
    name_size = min(28, max(20, int(700 / max(name_len * 0.62, 1))))

    desc_svg = "\n  ".join(
        f'<text x="32" y="{100 + i * 19}" fill="{t["text2"]}" '
        f'font-size="14" font-family="{FONT}">{line}</text>'
        for i, line in enumerate(desc_lines)
    )

    tech_y = 163
    tech_svg = tech_dots(tech_items, 32, tech_y, t["text1"])
    accent_grad = accent_gradient(tech_items)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Project spotlight: {html.escape(project.get('name', ''))}">
  <defs>
    {accent_grad}
    <clipPath id="card"><rect width="{WIDTH}" height="{HEIGHT}" rx="12"/></clipPath>
  </defs>

  <rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="{t['bg']}" stroke="{t['border']}" stroke-width="1"/>
  <rect width="{WIDTH}" height="3" fill="url(#accent)" clip-path="url(#card)"/>

  <text x="32" y="34" fill="{t['text2']}" font-size="11" font-weight="600" font-family="{FONT}" letter-spacing="1">WEEK {week:02d}</text>
  <text x="{WIDTH - 32}" y="34" fill="{t['link']}" font-size="12" font-weight="400" font-family="{FONT_MONO}" text-anchor="end">{repo}</text>

  <text x="32" y="72" fill="{t['text1']}" font-size="{name_size}" font-weight="700" font-family="{FONT}">{name}</text>

  {desc_svg}

  {tech_svg}
</svg>
"""


def main() -> None:
    if not PROJECTS_FILE.exists():
        raise FileNotFoundError(f"Missing projects file: {PROJECTS_FILE}")

    projects = json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
    if not isinstance(projects, list) or not projects:
        raise RuntimeError("projects.json must contain a non-empty array")

    week = dt.date.today().isocalendar().week
    manual = os.getenv("SPOTLIGHT_INDEX", "").strip()
    if manual:
        index = max(0, min(len(projects) - 1, int(manual)))
    else:
        index = (week - 1) % len(projects)

    project = projects[index]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    META_FILE.parent.mkdir(parents=True, exist_ok=True)

    for theme in ("dark", "light"):
        svg = build_svg(project=project, week=week, theme=theme)
        out = OUTPUT_DIR / f"current-{theme}.svg"
        out.write_text(svg, encoding="utf-8")

    meta = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "iso_week": week,
        "index": index,
        "project": project,
    }
    META_FILE.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
