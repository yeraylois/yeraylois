#!/usr/bin/env python3
"""Generate the editorial project and contact rows used by the profile README."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / ".github" / "cards"
OUTPUT_DIR = ROOT / "assets" / "cards"

WIDTH = 840
PROJECT_HEIGHT = 68
CONTACT_HEIGHT = 52

THEMES = {
    "dark": {
        "text": "#f0f6fc",
        "muted": "#8b949e",
        "line": "#30363d",
        "quiet": "#6e7681",
    },
    "light": {
        "text": "#1f2328",
        "muted": "#59636e",
        "line": "#d8dee4",
        "quiet": "#8c959f",
    },
}

TECH_COLORS = {
    "ansible": "#ee0000",
    "angular": "#dd0031",
    "c": "#5c6bc0",
    "docker": "#2496ed",
    "githubactions": "#2088ff",
    "python": "#3776ab",
    "zephyr": "#7f4bc4",
}

CONTACT_COLORS = {
    "email": "#ea4335",
    "linkedin": "#0a66c2",
    "github": "#8b949e",
}


def load_json(name: str) -> list[dict]:
    with (DATA_DIR / name).open(encoding="utf-8") as source:
        return json.load(source)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def project_accent(project: dict) -> str:
    technologies = project.get("tech", [])
    if not technologies:
        return "#58a6ff"
    return TECH_COLORS.get(technologies[0].get("id", ""), "#58a6ff")


def project_stack(project: dict) -> str:
    labels = [item.get("label", "") for item in project.get("tech", [])]
    return " / ".join(label.upper() for label in labels if label)


def build_project_row(project: dict, theme_name: str, lang: str, index: int) -> str:
    theme = THEMES[theme_name]
    title = esc(project["name"])
    raw_description = project[f"description_{lang}"]
    description = esc(raw_description)
    stack = esc(project_stack(project))
    accent = project_accent(project)
    number = f"{index:02d}"
    action = "VER REPOSITORIO" if lang == "es" else "VIEW REPOSITORY"
    aria = esc(f"Project {number}: {project['name']} — {raw_description}")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{PROJECT_HEIGHT}" viewBox="0 0 {WIDTH} {PROJECT_HEIGHT}" role="img" aria-label="{aria}">
  <style>
    .sans {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; }}
  </style>
  <line x1="0" y1="1" x2="{WIDTH}" y2="1" stroke="{theme['line']}"/>
  <line x1="0" y1="1" x2="48" y2="1" stroke="{accent}" stroke-width="2"/>
  <text class="mono" x="0" y="30" fill="{theme['quiet']}" font-size="10" letter-spacing="1">{number}</text>
  <text class="sans" x="54" y="30" fill="{theme['text']}" font-size="14" font-weight="650">{title}</text>
  <text class="sans" x="54" y="50" fill="{theme['muted']}" font-size="12">{description}</text>
  <text class="mono" x="790" y="29" fill="{theme['muted']}" font-size="9" text-anchor="end" letter-spacing="0.8">{stack}</text>
  <text class="mono" x="790" y="50" fill="{theme['quiet']}" font-size="9" text-anchor="end" letter-spacing="0.8">{action}</text>
  <text class="sans" x="840" y="51" fill="{accent}" font-size="16" text-anchor="end">↗</text>
</svg>
"""


def build_contact_row(contact: dict, theme_name: str, lang: str, index: int) -> str:
    theme = THEMES[theme_name]
    channel = esc(contact["channel"])
    handle = esc(contact["handle"])
    raw_purpose = contact[f"use_{lang}"]
    purpose = esc(raw_purpose.upper())
    accent = CONTACT_COLORS.get(contact["id"], "#58a6ff")
    number = f"{index:02d}"
    aria = esc(f"{contact['channel']}: {contact['handle']} — {raw_purpose}")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{CONTACT_HEIGHT}" viewBox="0 0 {WIDTH} {CONTACT_HEIGHT}" role="img" aria-label="{aria}">
  <style>
    .sans {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; }}
  </style>
  <line x1="0" y1="1" x2="{WIDTH}" y2="1" stroke="{theme['line']}"/>
  <line x1="0" y1="1" x2="28" y2="1" stroke="{accent}" stroke-width="2"/>
  <text class="mono" x="0" y="32" fill="{theme['quiet']}" font-size="10" letter-spacing="1">{number}</text>
  <circle cx="43" cy="28" r="3.5" fill="{accent}"/>
  <text class="sans" x="58" y="32" fill="{theme['text']}" font-size="14" font-weight="650">{channel}</text>
  <text class="mono" x="178" y="32" fill="{theme['muted']}" font-size="12">{handle}</text>
  <text class="mono" x="790" y="31" fill="{theme['quiet']}" font-size="9" text-anchor="end" letter-spacing="0.8">{purpose}</text>
  <text class="sans" x="840" y="33" fill="{accent}" font-size="16" text-anchor="end">↗</text>
</svg>
"""


def generate_all() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for index, project in enumerate(load_json("projects.json"), start=1):
        for lang in ("es", "en"):
            for theme_name in THEMES:
                filename = f"project-{project['id']}-{theme_name}-{lang}.svg"
                content = build_project_row(project, theme_name, lang, index)
                (OUTPUT_DIR / filename).write_text(content, encoding="utf-8")

    for index, contact in enumerate(load_json("contact.json"), start=1):
        for lang in ("es", "en"):
            for theme_name in THEMES:
                filename = f"contact-{contact['id']}-{theme_name}-{lang}.svg"
                content = build_contact_row(contact, theme_name, lang, index)
                (OUTPUT_DIR / filename).write_text(content, encoding="utf-8")


if __name__ == "__main__":
    generate_all()
