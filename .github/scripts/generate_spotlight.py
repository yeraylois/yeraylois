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
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTS_FILE = ROOT / ".github" / "spotlight" / "projects.json"
OUTPUT_FILE = ROOT / "assets" / "spotlight" / "current.svg"
META_FILE = ROOT / ".github" / "spotlight" / "current.json"

WIDTH = 1400
HEIGHT = 440

LEFT_X = 56
RIGHT_X = 905
RIGHT_W = 440
CARD_TOP = 24

FONT_TITLE = "Space Grotesk, Inter, Segoe UI, Arial, sans-serif"
FONT_BODY = "Inter, Segoe UI, Arial, sans-serif"
FONT_MONO = "JetBrains Mono, Menlo, Consolas, monospace"

GRADIENTS = [
    ("#050b16", "#0f1c35", "#ff7a18", "#ffd29d"),
    ("#07111f", "#12223a", "#00b8d9", "#8ee8ff"),
    ("#081119", "#152430", "#22c55e", "#b2f5c9"),
    ("#140f24", "#1e293b", "#f43f5e", "#fecdd3"),
]

TECH_ICON_URLS = {
    "ionic": "https://cdn.simpleicons.org/ionic/3880FF",
    "android": "https://cdn.simpleicons.org/android/3DDC84",
    "sqlite": "https://cdn.simpleicons.org/sqlite/003B57",
    "ansible": "https://cdn.simpleicons.org/ansible/EE0000",
    "docker": "https://cdn.simpleicons.org/docker/2496ED",
    "python": "https://cdn.simpleicons.org/python/3776AB",
    "angular": "https://cdn.simpleicons.org/angular/DD0031",
    "prometheus": "https://cdn.simpleicons.org/prometheus/E6522C",
    "grafana": "https://cdn.simpleicons.org/grafana/F46800",
    "c": "https://cdn.simpleicons.org/c/00599C",
    "microchip": "https://cdn.simpleicons.org/raspberrypi/A22846",
    "embedded": "https://cdn.simpleicons.org/platformio/F5822A",
}


def short_repo(url: str, max_len: int = 36) -> str:
    clean = str(url or "").replace("https://", "").replace("http://", "")
    if len(clean) <= max_len:
        return clean
    if max_len <= 3:
        return clean[:max_len]
    return f"{clean[: max_len - 3]}..."


def sanitize_line(text: str) -> str:
    return " ".join(str(text or "").replace("\n", " ").split()).strip()


def wrap_text(text: str, width: int, max_lines: int) -> list[str]:
    text = sanitize_line(text)
    if not text:
        return [""]
    lines = textwrap.wrap(text, width=width, break_long_words=False, replace_whitespace=False)
    if len(lines) <= max_lines:
        return lines
    trimmed = lines[:max_lines]
    last = trimmed[-1]
    if len(last) >= 3:
        last = f"{last[:-3]}..."
    elif not last.endswith("..."):
        last = f"{last}..."
    trimmed[-1] = last
    return trimmed


def truncate_text(text: str, max_chars: int) -> str:
    text = sanitize_line(text)
    if len(text) <= max_chars:
        return text
    if max_chars <= 3:
        return text[:max_chars]
    return f"{text[: max_chars - 3]}..."


def tech_label_width(label: str) -> int:
    # Approximation for Inter 19px.
    return 74 + int(len(label) * 10.2)


def fit_name_font_size(title: str, max_width: int, base: int = 66, min_size: int = 40) -> int:
    clean = sanitize_line(title)
    if not clean:
        return base
    # Approximation for Space Grotesk width in px.
    size = int(max_width / (len(clean) * 0.58))
    return max(min_size, min(base, size))


def render_tech_chips(tech_items: list[dict], x0: int, y0: int, max_width: int, accent: str) -> str:
    rows = []
    x = x0
    y = y0
    row_limit = 2
    current_row = 0
    hidden = 0

    for item in tech_items:
        label = truncate_text(item.get("label", "Tech"), 20)
        tech_id = str(item.get("id", "")).strip().lower()
        icon_url = TECH_ICON_URLS.get(tech_id, "https://cdn.simpleicons.org/github/9CA3AF")

        chip_w = min(260, max(132, tech_label_width(label)))
        if x + chip_w > x0 + max_width:
            current_row += 1
            x = x0
            y += 56
            if current_row >= row_limit:
                hidden += 1
                continue

        chip = f"""
  <rect x=\"{x}\" y=\"{y}\" width=\"{chip_w}\" height=\"42\" rx=\"12\" fill=\"#0a162c\" stroke=\"#27374f\" stroke-width=\"1.3\"/>
  <image href=\"{icon_url}\" x=\"{x + 12}\" y=\"{y + 9}\" width=\"24\" height=\"24\"/>
  <text x=\"{x + 44}\" y=\"{y + 28}\" fill=\"#e5ecf7\" font-size=\"19\" font-weight=\"600\" font-family=\"{FONT_BODY}\">{html.escape(label)}</text>
"""
        rows.append(chip)
        x += chip_w + 12

    if hidden > 0:
        rows.append(
            f'<text x="{x0}" y="{y + 74}" fill="{accent}" font-size="16" font-weight="700" font-family="{FONT_BODY}">+{hidden} TECHNOLOGIES</text>'
        )

    return "".join(rows)


def build_svg(project: dict, week: int, palette: tuple[str, str, str, str]) -> str:
    bg_start, bg_end, accent, accent_soft = palette

    raw_name = truncate_text(project.get("name", "Project"), 30)
    name = html.escape(raw_name)
    name_size = fit_name_font_size(raw_name, max_width=800)
    desc_lines = [html.escape(x) for x in wrap_text(project.get("description", ""), width=56, max_lines=2)]
    repo_url = str(project.get("repo", "")).strip()
    repo_label = html.escape(short_repo(repo_url, 36))
    tech_items = project.get("tech") if isinstance(project.get("tech"), list) else []

    desc_svg = []
    for idx, line in enumerate(desc_lines):
        desc_svg.append(
            f'<text x="{LEFT_X}" y="{190 + idx * 34}" fill="#dbe6f7" font-size="20" font-weight="500" font-family="{FONT_BODY}">{line}</text>'
        )

    tech_svg = render_tech_chips(
        tech_items=tech_items,
        x0=LEFT_X,
        y0=300,
        max_width=820,
        accent=accent,
    )

    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{WIDTH}\" height=\"{HEIGHT}\" viewBox=\"0 0 {WIDTH} {HEIGHT}\" role=\"img\" aria-label=\"Weekly project spotlight\">\n  <defs>\n    <linearGradient id=\"bg\" x1=\"0%\" y1=\"0%\" x2=\"100%\" y2=\"100%\">\n      <stop offset=\"0%\" stop-color=\"{bg_start}\"/>\n      <stop offset=\"100%\" stop-color=\"{bg_end}\"/>\n    </linearGradient>\n    <linearGradient id=\"acc\" x1=\"0%\" y1=\"0%\" x2=\"100%\" y2=\"0%\">\n      <stop offset=\"0%\" stop-color=\"{accent}\"/>\n      <stop offset=\"100%\" stop-color=\"{accent_soft}\"/>\n    </linearGradient>\n    <filter id=\"softShadow\" x=\"-20%\" y=\"-20%\" width=\"140%\" height=\"140%\">\n      <feDropShadow dx=\"0\" dy=\"10\" stdDeviation=\"12\" flood-color=\"#000\" flood-opacity=\"0.32\"/>\n    </filter>\n    <filter id=\"innerGlow\" x=\"-20%\" y=\"-20%\" width=\"140%\" height=\"140%\">\n      <feDropShadow dx=\"0\" dy=\"0\" stdDeviation=\"6\" flood-color=\"{accent}\" flood-opacity=\"0.35\"/>\n    </filter>\n  </defs>\n\n  <rect x=\"12\" y=\"{CARD_TOP}\" width=\"{WIDTH - 24}\" height=\"{HEIGHT - CARD_TOP - 12}\" rx=\"26\" fill=\"url(#bg)\"/>\n  <rect x=\"12\" y=\"{CARD_TOP}\" width=\"{WIDTH - 24}\" height=\"8\" rx=\"26\" fill=\"url(#acc)\"/>\n\n  <rect x=\"{LEFT_X - 8}\" y=\"52\" width=\"400\" height=\"42\" rx=\"12\" fill=\"#0b1322\" stroke=\"{accent}\" stroke-width=\"1.8\"/>\n  <text x=\"{LEFT_X + 14}\" y=\"80\" fill=\"{accent}\" font-size=\"26\" font-weight=\"700\" font-family=\"{FONT_MONO}\">PROJECT SPOTLIGHT · WEEK {week:02d}</text>\n\n  <text x=\"{LEFT_X}\" y=\"140\" fill=\"#f8fbff\" font-size=\"{name_size}\" font-weight=\"800\" font-family=\"{FONT_TITLE}\">{name}</text>\n  {''.join(desc_svg)}\n\n  <text x=\"{LEFT_X}\" y=\"286\" fill=\"#c8d7ee\" font-size=\"22\" font-weight=\"700\" font-family=\"{FONT_MONO}\">TECH STACK</text>\n  {tech_svg}\n\n  <line x1=\"870\" y1=\"62\" x2=\"870\" y2=\"390\" stroke=\"#20314b\" stroke-width=\"1.5\"/>\n\n  <g filter=\"url(#softShadow)\">\n    <rect x=\"{RIGHT_X}\" y=\"84\" width=\"{RIGHT_W}\" height=\"270\" rx=\"20\" fill=\"#091328\" stroke=\"{accent}\" stroke-width=\"2.2\"/>\n  </g>\n\n  <text x=\"{RIGHT_X + 26}\" y=\"132\" fill=\"#f8fbff\" font-size=\"42\" font-weight=\"800\" font-family=\"{FONT_TITLE}\">REPOSITORY</text>\n  <text x=\"{RIGHT_X + 26}\" y=\"176\" fill=\"#d4e0f5\" font-size=\"19\" font-family=\"{FONT_MONO}\">{repo_label}</text>\n\n  <rect x=\"{RIGHT_X + 24}\" y=\"214\" width=\"{RIGHT_W - 48}\" height=\"54\" rx=\"14\" fill=\"#101f38\" stroke=\"#2a3f60\" stroke-width=\"1.2\"/>\n  <text x=\"{RIGHT_X + 46}\" y=\"249\" fill=\"#dbe6f7\" font-size=\"23\" font-weight=\"600\" font-family=\"{FONT_BODY}\">Preview refreshed every week</text>\n\n  <rect x=\"{RIGHT_X + 24}\" y=\"286\" width=\"{RIGHT_W - 48}\" height=\"48\" rx=\"14\" fill=\"url(#acc)\" filter=\"url(#innerGlow)\"/>\n  <text x=\"{RIGHT_X + 46}\" y=\"317\" fill=\"#0a1020\" font-size=\"24\" font-weight=\"800\" font-family=\"{FONT_TITLE}\">OPEN REPOSITORY</text>\n</svg>\n"""


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
    palette = GRADIENTS[index % len(GRADIENTS)]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    META_FILE.parent.mkdir(parents=True, exist_ok=True)

    svg = build_svg(project=project, week=week, palette=palette)
    OUTPUT_FILE.write_text(svg, encoding="utf-8")

    meta = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "iso_week": week,
        "index": index,
        "project": project,
    }
    META_FILE.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
