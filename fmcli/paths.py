"""Resolve repo-relative paths."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def deals_dir() -> Path:
    return repo_root() / "data" / "deals"


def templates_dir() -> Path:
    return repo_root() / "data" / "templates"


def deal_dir(deal_id: str) -> Path:
    d = deals_dir() / deal_id
    if not d.exists():
        raise FileNotFoundError(f"Deal not found: {deal_id}. Try `fmcli list`.")
    return d


def deal_model_path(deal_id: str) -> Path:
    return deal_dir(deal_id) / "model.xlsx"


def deal_yaml_path(deal_id: str) -> Path:
    return deal_dir(deal_id) / "deal.yaml"


def deal_audit_path(deal_id: str) -> Path:
    return deal_dir(deal_id) / "audit.log"


def deal_inputs_dir(deal_id: str) -> Path:
    p = deal_dir(deal_id) / "inputs"
    p.mkdir(exist_ok=True)
    return p


def deal_outputs_dir(deal_id: str) -> Path:
    p = deal_dir(deal_id) / "outputs"
    p.mkdir(exist_ok=True)
    return p
