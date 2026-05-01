"""Render borrower notices from Jinja2 templates."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from .paths import deal_outputs_dir, templates_dir


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(templates_dir())),
        autoescape=select_autoescape(["html", "xml"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _money(value: Any, currency: str = "CAD") -> str:
    if value is None:
        return "—"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{currency} {v:,.2f}"


def _ratio(value: Any, places: int = 2) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):.{places}f}x"
    except (TypeError, ValueError):
        return str(value)


def _pct(value: Any, places: int = 2) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value)*100:.{places}f}%"
    except (TypeError, ValueError):
        return str(value)


def list_templates() -> list[str]:
    # Strip both `.md.j2` suffixes — `Path.stem` only strips one.
    return sorted(p.name.removesuffix(".md.j2") for p in templates_dir().glob("*.md.j2"))


def _build_env() -> Environment:
    env = _env()
    env.filters["money"] = _money
    env.filters["ratio"] = _ratio
    env.filters["pct"] = _pct
    return env


def render(deal_id: str, template: str, context: dict[str, Any], draft: bool = True) -> Path:
    """Render a template into the deal's outputs/ directory."""
    env = _build_env()
    tmpl = env.get_template(f"{template}.md.j2")
    rendered = tmpl.render(**context, today=date.today().isoformat())

    today = date.today().strftime("%Y%m%d")
    prefix = "DRAFT_" if draft else ""
    out = deal_outputs_dir(deal_id) / f"{prefix}{today}_{template}.md"
    out.write_text(rendered)
    return out


def render_to_path(template: str, context: dict[str, Any], out_path: Path) -> Path:
    """Render a template to an arbitrary path (used for portfolio-level reports)."""
    env = _build_env()
    tmpl = env.get_template(f"{template}.md.j2")
    rendered = tmpl.render(**context, today=date.today().isoformat())
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered)
    return out_path
