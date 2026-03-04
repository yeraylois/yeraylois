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

WIDTH = 1200
HEIGHT = 280

GRADIENTS = [
    ("#0f172a", "#111827", "#f97316"),
    ("#111827", "#1f2937", "#38bdf8"),
    ("#0b1120", "#111827", "#22c55e"),
    ("#1e1b4b", "#0f172a", "#f43f5e"),
]


def wrap_line(text: str, width: int) -> list[str]:
    return textwrap.wrap(text, width=width, break_long_words=False, replace_whitespace=False) or [""]


def build_svg(project: dict, week: int, accent: str, bg_start: str, bg_end: str) -> str:
    name = html.escape(project.get("name", "Project"))
    desc_lines = [html.escape(x) for x in wrap_line(project.get("description", ""), 68)[:2]]
    stack = html.escape(project.get("stack", ""))
    repo = html.escape(project.get("repo", ""))

    desc_y = 136
    lines_svg = []
    for i, line in enumerate(desc_lines):
        lines_svg.append(
            f'<text x="56" y="{desc_y + i * 30}" fill="#e5e7eb" font-size="26" font-family="Inter,Segoe UI,Arial,sans-serif">{line}</text>'
        )

    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{WIDTH}\" height=\"{HEIGHT}\" viewBox=\"0 0 {WIDTH} {HEIGHT}\" role=\"img\" aria-label=\"Weekly project spotlight\">\n  <defs>\n    <linearGradient id=\"bg\" x1=\"0%\" y1=\"0%\" x2=\"100%\" y2=\"100%\">\n      <stop offset=\"0%\" stop-color=\"{bg_start}\"/>\n      <stop offset=\"100%\" stop-color=\"{bg_end}\"/>\n    </linearGradient>\n    <linearGradient id=\"accent\" x1=\"0%\" y1=\"0%\" x2=\"100%\" y2=\"0%\">\n      <stop offset=\"0%\" stop-color=\"{accent}\"/>\n      <stop offset=\"100%\" stop-color=\"#fb923c\"/>\n    </linearGradient>\n    <filter id=\"shadow\" x=\"-20%\" y=\"-20%\" width=\"140%\" height=\"140%\">\n      <feDropShadow dx=\"0\" dy=\"8\" stdDeviation=\"8\" flood-color=\"#000\" flood-opacity=\"0.35\"/>\n    </filter>\n  </defs>\n\n  <rect x=\"0\" y=\"0\" width=\"{WIDTH}\" height=\"{HEIGHT}\" fill=\"url(#bg)\" rx=\"24\"/>\n  <rect x=\"0\" y=\"0\" width=\"{WIDTH}\" height=\"8\" fill=\"url(#accent)\" rx=\"24\"/>\n\n  <rect x=\"44\" y=\"34\" width=\"360\" height=\"36\" rx=\"10\" fill=\"#0b1220\" stroke=\"{accent}\" stroke-width=\"1.5\"/>\n  <text x=\"62\" y=\"58\" fill=\"{accent}\" font-size=\"20\" font-weight=\"700\" font-family=\"Inter,Segoe UI,Arial,sans-serif\">PROJECT SPOTLIGHT · WEEK {week:02d}</text>\n\n  <text x=\"56\" y=\"108\" fill=\"#f8fafc\" font-size=\"42\" font-weight=\"800\" font-family=\"Inter,Segoe UI,Arial,sans-serif\">{name}</text>\n  {''.join(lines_svg)}\n  <text x=\"56\" y=\"228\" fill=\"#cbd5e1\" font-size=\"22\" font-family=\"Inter,Segoe UI,Arial,sans-serif\">STACK · {stack}</text>\n\n  <g filter=\"url(#shadow)\">\n    <rect x=\"770\" y=\"74\" width=\"384\" height=\"132\" rx=\"16\" fill=\"#0b1220\" stroke=\"{accent}\" stroke-width=\"2\"/>\n    <text x=\"794\" y=\"114\" fill=\"#f8fafc\" font-size=\"24\" font-weight=\"700\" font-family=\"Inter,Segoe UI,Arial,sans-serif\">REPOSITORY</text>\n    <text x=\"794\" y=\"148\" fill=\"#e2e8f0\" font-size=\"17\" font-family=\"Inter,Segoe UI,Arial,sans-serif\">{repo}</text>\n    <text x=\"794\" y=\"180\" fill=\"{accent}\" font-size=\"16\" font-weight=\"700\" font-family=\"Inter,Segoe UI,Arial,sans-serif\">Rotates automatically every week</text>\n  </g>\n</svg>\n"""


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

    svg = build_svg(
        project=project,
        week=week,
        accent=palette[2],
        bg_start=palette[0],
        bg_end=palette[1],
    )
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
