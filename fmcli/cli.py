"""fmcli — CLI entry point."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from . import audit, backup, compute, covenants, excel, notices, portfolio, sensitivity
from .deal import Deal, load_deal
from .excel import CellWrite, read_borrower_submission
from .paths import deal_audit_path, deal_dir, deal_inputs_dir, deal_model_path, deals_dir

console = Console()


def _err(msg: str, code: int = 1) -> None:
    console.print(f"[bold red]error[/]: {msg}")
    sys.exit(code)


def _list_deals() -> list[str]:
    if not deals_dir().exists():
        return []
    return sorted(p.name for p in deals_dir().iterdir() if (p / "deal.yaml").exists())


@click.group(help="Financial Models CLI — agent workbench for project finance.")
@click.version_option()
def main() -> None:
    pass


# ---------------------------------------------------------------------------
# discovery
# ---------------------------------------------------------------------------

@main.command("list", help="List deals in this workspace.")
def cmd_list() -> None:
    deal_ids = _list_deals()
    if not deal_ids:
        console.print("[yellow]No deals found in data/deals/.[/]")
        return
    table = Table(title="Deals", show_lines=False)
    table.add_column("ID", style="cyan")
    table.add_column("Borrower")
    table.add_column("Sector")
    table.add_column("Commitment", justify="right")
    table.add_column("Maturity")
    for did in deal_ids:
        try:
            d = load_deal(did)
            table.add_row(d.id, d.borrower, d.sector, d.commitment_fmt, d.maturity_date)
        except Exception as e:
            table.add_row(did, f"[red]{e}[/]", "", "", "")
    console.print(table)


@main.command("show", help="Show deal metadata, output cells, and covenants.")
@click.argument("deal_id")
def cmd_show(deal_id: str) -> None:
    d = load_deal(deal_id)

    console.rule(f"[bold]{d.project}[/]  ·  {d.id}")
    console.print(f"[bold]Borrower:[/] {d.borrower}")
    console.print(f"[bold]Sector:[/]   {d.sector}")
    console.print(f"[bold]Facility:[/] {d.facility}")
    console.print(f"[bold]Commitment:[/] {d.commitment_fmt}")
    console.print(f"[bold]Closing:[/]  {d.closing_date}    [bold]Maturity:[/] {d.maturity_date}")
    if d.notes:
        console.print(f"\n{d.notes}")

    if d.outputs:
        t = Table(title="Output cells", show_lines=False)
        t.add_column("Name", style="cyan")
        t.add_column("Cell")
        t.add_column("Live value", justify="right")
        try:
            values = excel.read_cells(deal_model_path(deal_id), d.outputs)
        except Exception as e:
            values = {k: f"[red]err: {e}[/]" for k in d.outputs}
        for name, ref in d.outputs.items():
            v = values.get(name)
            t.add_row(name, ref, _fmt(v))
        console.print(t)

    if d.covenants:
        t = Table(title="Covenants")
        t.add_column("Name", style="cyan")
        t.add_column("Test")
        t.add_column("Severity")
        for c in d.covenants:
            t.add_row(c.name, f"{c.output} {c.operator} {c.threshold}", c.severity)
        console.print(t)


def _fmt(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:,.4f}".rstrip("0").rstrip(".")
    return str(v)


def _fmt_covenant_short(c, include_threshold: bool = False) -> str:
    """Render a one-line covenant summary, picking ratio vs money based on threshold magnitude."""
    if c.threshold > 100:
        actual = f"CAD {c.actual:,.0f}"
        thresh = f"CAD {c.threshold:,.0f}"
    else:
        actual = f"{c.actual:.2f}x"
        thresh = f"{c.threshold:.2f}x"
    return f"{c.name} ({actual} vs {thresh})" if include_threshold else f"{c.name} ({actual})"


# ---------------------------------------------------------------------------
# inspect a workbook (used by agents that need orientation)
# ---------------------------------------------------------------------------

@main.command("inspect", help="Print a sheet/label summary of any .xlsx (orientation aid).")
@click.argument("path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def cmd_inspect(path: Path) -> None:
    summary = excel.workbook_summary(path)
    for sheet, labels in summary.items():
        console.print(f"\n[bold cyan]{sheet}[/]")
        for label in labels:
            console.print(f"  · {label}")


# ---------------------------------------------------------------------------
# update — propagate borrower submission into the model
# ---------------------------------------------------------------------------

@main.command("update", help="Propagate a borrower submission into the project model.")
@click.argument("deal_id")
@click.argument("submission", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--sheet", default=None, help="Sheet name in the submission (default: first).")
@click.option("--no-recalc", is_flag=True, help="Skip post-write recompute.")
@click.option("--dry-run", is_flag=True, help="Show what would change without writing.")
def cmd_update(deal_id: str, submission: Path, sheet: str | None, no_recalc: bool, dry_run: bool) -> None:
    d = load_deal(deal_id)
    raw = read_borrower_submission(submission, sheet=sheet)
    if not raw:
        _err(f"No data rows found in {submission}.")

    # Map borrower submission labels -> input cells via deal.input_map.
    writes: list[CellWrite] = []
    unmatched: list[str] = []
    for label, value in raw.items():
        ref = d.input_map.get(label)
        if ref is None:
            unmatched.append(label)
            continue
        writes.append(CellWrite(ref=ref, value=value, label=label))

    if not writes:
        _err(
            f"No labels in submission match deal.input_map. "
            f"Submission keys: {list(raw)[:5]}…  "
            f"Mapped: {list(d.input_map)[:5]}…"
        )

    table = Table(title=f"Updates to {deal_id}/model.xlsx")
    table.add_column("Label", style="cyan")
    table.add_column("Cell")
    table.add_column("New value", justify="right")
    for w in writes:
        table.add_row(w.label, w.ref, _fmt(w.value))
    console.print(table)

    if unmatched:
        console.print(
            f"[yellow]warn:[/] {len(unmatched)} label(s) in submission not mapped — skipping: "
            + ", ".join(unmatched[:5])
            + ("…" if len(unmatched) > 5 else "")
        )

    if dry_run:
        console.print("[bold]Dry run — no changes written.[/]")
        return

    snap = backup.snapshot(deal_id, reason=f"update_{submission.stem}"[:40])
    console.print(f"[dim]backup: {snap.name}[/]")

    results = excel.write_cells(deal_model_path(deal_id), writes)

    if not no_recalc:
        with console.status("Recomputing model outputs…"):
            report = compute.recompute(d)
        console.print(f"[dim]recompute: {report.method} → {len(report.output_writes)} output(s)[/]")

    audit.append(
        deal_id,
        "model.update",
        {
            "submission": str(submission),
            "backup": snap.name,
            "writes": [
                {"ref": r.ref, "label": r.label, "before": r.before, "after": r.after}
                for r in results
            ],
            "unmatched": unmatched,
        },
    )
    console.print(f"[green]✓[/] {len(results)} cell(s) updated. Audit appended.")


# ---------------------------------------------------------------------------
# extract — pull named outputs
# ---------------------------------------------------------------------------

@main.command("extract", help="Extract named output cells from the model.")
@click.argument("deal_id")
@click.option("--outputs", default=None, help="Comma-separated subset of output names (default: all).")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of a table.")
def cmd_extract(deal_id: str, outputs: str | None, as_json: bool) -> None:
    d = load_deal(deal_id)
    refs = d.outputs
    if outputs:
        wanted = [s.strip() for s in outputs.split(",") if s.strip()]
        missing = [w for w in wanted if w not in refs]
        if missing:
            _err(f"Unknown output(s): {', '.join(missing)}. Known: {', '.join(refs)}")
        refs = {k: refs[k] for k in wanted}

    values = excel.read_cells(deal_model_path(deal_id), refs)

    if as_json:
        console.print_json(json.dumps({k: values[k] for k in refs}, default=str))
        return

    t = Table(title=f"{deal_id}: outputs")
    t.add_column("Name", style="cyan")
    t.add_column("Cell")
    t.add_column("Value", justify="right")
    for name in refs:
        t.add_row(name, refs[name], _fmt(values[name]))
    console.print(t)


# ---------------------------------------------------------------------------
# covenant — test
# ---------------------------------------------------------------------------

@main.command("covenant", help="Test all covenants and print a verdict table.")
@click.argument("deal_id")
@click.option("--json", "as_json", is_flag=True)
def cmd_covenant(deal_id: str, as_json: bool) -> None:
    d = load_deal(deal_id)
    results = covenants.test_all(d)

    if as_json:
        console.print_json(json.dumps([r.__dict__ for r in results], default=str))
        return

    t = Table(title=f"{deal_id}: covenant test")
    t.add_column("Covenant", style="cyan")
    t.add_column("Test")
    t.add_column("Actual", justify="right")
    t.add_column("Verdict")
    for r in results:
        verdict = {
            "ok":     "[green]PASS[/]",
            "watch":  "[yellow]WATCH[/]",
            "breach": "[bold red]BREACH[/]",
        }.get(r.severity, r.severity)
        actual = "—" if r.actual is None else f"{r.actual:,.4f}".rstrip("0").rstrip(".")
        t.add_row(r.name, f"{r.output} {r.operator} {r.threshold}", actual, verdict)
    console.print(t)

    audit.append(
        deal_id,
        "covenant.test",
        {"results": [r.__dict__ for r in results]},
    )

    if any(r.severity == "breach" for r in results):
        sys.exit(2)


# ---------------------------------------------------------------------------
# notice — render a borrower notice
# ---------------------------------------------------------------------------

@main.command("notice", help="Draft a borrower notice from a template.")
@click.argument("deal_id")
@click.argument("template")
@click.option("--amount", type=float, default=None, help="Drawdown / payment amount.")
@click.option("--period", default=None, help="Reporting period, e.g. 2026-Q1.")
@click.option("--final", is_flag=True, help="Mark as final (no DRAFT_ prefix).")
def cmd_notice(deal_id: str, template: str, amount: float | None, period: str | None, final: bool) -> None:
    d = load_deal(deal_id)

    # Pull current outputs so the notice can reference live figures.
    output_values = excel.read_cells(deal_model_path(deal_id), d.outputs)

    cov_results = covenants.test_all(d)

    context: dict = {
        "deal": d,
        "outputs": output_values,
        "covenants": cov_results,
        "amount": amount,
        "period": period,
    }

    available = notices.list_templates()
    if template not in available:
        _err(f"Unknown template '{template}'. Available: {', '.join(available)}")

    out_path = notices.render(deal_id, template, context, draft=not final)
    audit.append(
        deal_id,
        "notice.draft",
        {
            "template": template,
            "output": str(out_path),
            "draft": not final,
            "amount": amount,
            "period": period,
        },
    )
    console.print(f"[green]✓[/] Notice drafted: {out_path}")
    if not final:
        console.print("[dim]Filename starts with DRAFT_ — review and remove the prefix to finalize.[/]")


# ---------------------------------------------------------------------------
# report — internal-facing reports (credit memo per deal, portfolio review)
# ---------------------------------------------------------------------------

@main.command("report", help="Generate an internal report (credit memo for one deal, or a portfolio review across all deals).")
@click.argument("kind", type=click.Choice(["credit-memo", "portfolio"]))
@click.argument("deal_id", required=False)
@click.option("--period", default=None, help="Reporting period, e.g. 2026-Q1.")
@click.option("--out", "out_path", type=click.Path(path_type=Path), default=None,
              help="Override output path.")
def cmd_report(kind: str, deal_id: str | None, period: str | None, out_path: Path | None) -> None:
    from datetime import datetime, timedelta, timezone

    if kind == "credit-memo":
        if not deal_id:
            _err("credit-memo requires a deal_id, e.g. `fmcli report credit-memo highway-407-east-extension`.")
        d = load_deal(deal_id)
        outputs_v = excel.read_cells(deal_model_path(deal_id), d.outputs)
        cov_results = covenants.test_all(d)

        # Collect last 10 audit events with a brief detail string.
        ev_raw = audit.read(deal_id)[-10:]
        audit_events = []
        for e in ev_raw:
            if e["event"] == "model.update":
                detail = f"{len(e.get('writes', []))} cell(s) from {Path(e.get('submission','')).name}"
            elif e["event"] == "covenant.test":
                rs = e.get("results", [])
                breach = sum(1 for r in rs if r.get("severity") == "breach")
                watch  = sum(1 for r in rs if r.get("severity") == "watch")
                detail = f"{len(rs)} tests, {breach} breach, {watch} watch"
            elif e["event"] == "notice.draft":
                detail = f"{e.get('template')} → {Path(e.get('output','')).name}"
            else:
                detail = ""
            audit_events.append({
                "ts": e.get("ts", ""),
                "user": e.get("user", ""),
                "event": e.get("event", ""),
                "detail": detail,
            })

        ctx = {
            "deal": d,
            "outputs": outputs_v,
            "covenants": cov_results,
            "period": period,
            "audit_events": audit_events,
        }
        out = notices.render(deal_id, "credit-memo", ctx, draft=True)
        # The credit memo is internal — flag it differently from borrower notices.
        new_path = out.with_name(out.name.replace("DRAFT_", "INTERNAL_"))
        out.rename(new_path)
        audit.append(deal_id, "report.credit_memo", {"output": str(new_path), "period": period})
        console.print(f"[green]✓[/] Internal credit memo: {new_path}")
        return

    # ----- portfolio review -----
    df = portfolio.rollup()
    if df.empty:
        _err("No deals in workspace.")

    deals_ctx: list[dict] = []
    watchlist: list[dict] = []
    breached: list[dict] = []
    sector_totals: dict[str, float] = {}

    for _, row in df.iterrows():
        d = load_deal(row["deal"])
        cov = covenants.test_all(d)
        breaches = [c for c in cov if c.severity == "breach"]
        watches  = [c for c in cov if c.severity == "watch"]
        status = "BREACH" if breaches else ("WATCH" if watches else "OK")
        item = {
            "id": d.id,
            "sector": d.sector,
            "currency": d.currency,
            "commitment": d.commitment,
            "DSCR": row.get("DSCR"),
            "LLCR": row.get("LLCR"),
            "DebtBalance": row.get("DebtBalance"),
            "status": status,
            "watch_summary": ", ".join(_fmt_covenant_short(c) for c in watches if c.actual is not None) or "—",
            "breach_summary": ", ".join(_fmt_covenant_short(c, include_threshold=True) for c in breaches if c.actual is not None) or "—",
        }
        deals_ctx.append(item)
        if breaches:
            breached.append(item)
        elif watches:
            watchlist.append(item)
        sector_totals[d.sector] = sector_totals.get(d.sector, 0.0) + d.commitment

    total_committed = sum(d["commitment"] for d in deals_ctx)
    sector_pairs = sorted(sector_totals.items(), key=lambda kv: -kv[1])

    # 30-day activity rollup across every deal's audit log.
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    activity: dict[str, int] = {}
    for d in deals_ctx:
        for e in audit.read(d["id"]):
            try:
                ts = datetime.strptime(e["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            except (KeyError, ValueError):
                continue
            if ts < cutoff:
                continue
            key = e["event"].replace(".", "_")
            activity[key] = activity.get(key, 0) + 1

    ctx = {
        "deals": deals_ctx,
        "watchlist": watchlist,
        "breached": breached,
        "sectors": sorted({d["sector"] for d in deals_ctx}),
        "sector_totals": sector_pairs,
        "total_committed": total_committed,
        "activity": activity,
    }

    if out_path is None:
        from .paths import repo_root
        out_path = repo_root() / "data" / f"INTERNAL_{__import__('datetime').date.today().strftime('%Y%m%d')}_portfolio-review.md"
    notices.render_to_path("portfolio-review", ctx, out_path)
    console.print(f"[green]✓[/] Portfolio review report: {out_path}")


# ---------------------------------------------------------------------------
# audit — show audit trail
# ---------------------------------------------------------------------------

@main.command("audit", help="Show audit trail for a deal.")
@click.argument("deal_id")
@click.option("--limit", type=int, default=20, help="Most recent N events.")
def cmd_audit(deal_id: str, limit: int) -> None:
    deal_dir(deal_id)  # validate deal exists
    events = audit.read(deal_id)
    if not events:
        console.print("[yellow]No audit events yet.[/]")
        return

    events = events[-limit:]
    t = Table(title=f"{deal_id}: audit trail (last {len(events)})")
    t.add_column("Timestamp", style="dim")
    t.add_column("User")
    t.add_column("Event", style="cyan")
    t.add_column("Detail")
    for e in events:
        if e["event"] == "model.update":
            detail = f"{len(e.get('writes', []))} cell(s) from {Path(e.get('submission','')).name}"
        elif e["event"] == "covenant.test":
            results = e.get("results", [])
            breaches = sum(1 for r in results if r.get("severity") == "breach")
            watches  = sum(1 for r in results if r.get("severity") == "watch")
            detail = f"{len(results)} tests, {breaches} breach, {watches} watch"
        elif e["event"] == "notice.draft":
            detail = f"{e.get('template')} → {Path(e.get('output','')).name}"
        else:
            detail = ""
        t.add_row(e["ts"], e["user"], e["event"], detail)
    console.print(t)


# ---------------------------------------------------------------------------
# reconcile — diff two .xlsx workbooks at the named outputs of a deal
# ---------------------------------------------------------------------------

@main.command("reconcile", help="Diff outputs between the deal model and another workbook.")
@click.argument("deal_id")
@click.argument("other", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def cmd_reconcile(deal_id: str, other: Path) -> None:
    d = load_deal(deal_id)
    a = excel.read_cells(deal_model_path(deal_id), d.outputs)
    b = excel.read_cells(other, d.outputs)

    t = Table(title=f"{deal_id}: reconcile vs {other.name}")
    t.add_column("Output", style="cyan")
    t.add_column("Model", justify="right")
    t.add_column("Other", justify="right")
    t.add_column("Δ", justify="right")
    for name in d.outputs:
        va, vb = a.get(name), b.get(name)
        try:
            delta = float(va) - float(vb)
            d_str = f"{delta:,.4f}".rstrip("0").rstrip(".")
        except (TypeError, ValueError):
            d_str = "—"
        t.add_row(name, _fmt(va), _fmt(vb), d_str)
    console.print(t)


# ---------------------------------------------------------------------------
# templates — list available notice templates
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# backup / restore
# ---------------------------------------------------------------------------

@main.command("backup", help="Take a manual snapshot of the deal's model.xlsx.")
@click.argument("deal_id")
@click.option("--reason", default="manual", help="Short tag (e.g. 'pre-quarter-close').")
def cmd_backup(deal_id: str, reason: str) -> None:
    deal_dir(deal_id)  # validate
    snap = backup.snapshot(deal_id, reason=reason)
    audit.append(deal_id, "model.backup", {"backup": snap.name, "reason": reason})
    console.print(f"[green]✓[/] {snap.name}")


@main.command("backups", help="List snapshots for a deal.")
@click.argument("deal_id")
def cmd_backups(deal_id: str) -> None:
    snaps = backup.list_snapshots(deal_id)
    if not snaps:
        console.print("[yellow]No snapshots yet.[/]")
        return
    t = Table(title=f"{deal_id}: snapshots")
    t.add_column("Snapshot", style="cyan")
    t.add_column("Timestamp")
    t.add_column("Reason")
    t.add_column("SHA", style="dim")
    for s in snaps:
        t.add_row(s.name, s.ts, s.reason, s.sha)
    console.print(t)


@main.command("restore", help="Restore a deal's model from a snapshot.")
@click.argument("deal_id")
@click.argument("snapshot_name")
def cmd_restore(deal_id: str, snapshot_name: str) -> None:
    try:
        snap = backup.restore(deal_id, snapshot_name)
    except (FileNotFoundError, ValueError) as e:
        _err(str(e))
    audit.append(deal_id, "model.restore", {"backup": snap.name})
    console.print(f"[green]✓[/] Restored from {snap.name}. A pre-restore snapshot was also taken.")


# ---------------------------------------------------------------------------
# portfolio rollup across all deals
# ---------------------------------------------------------------------------

@main.command("portfolio", help="Aggregate live KPIs across every deal in the workspace.")
@click.option("--csv", "as_csv", is_flag=True, help="Emit CSV.")
def cmd_portfolio(as_csv: bool) -> None:
    df = portfolio.rollup()
    if as_csv:
        click.echo(df.to_csv(index=False))
        return
    if df.empty:
        console.print("[yellow]No deals in workspace.[/]")
        return
    t = Table(title="Portfolio rollup")
    for col in df.columns:
        t.add_column(str(col))
    for _, row in df.iterrows():
        t.add_row(*[_fmt(v) for v in row.tolist()])
    console.print(t)


# ---------------------------------------------------------------------------
# sensitivity analysis (OAT)
# ---------------------------------------------------------------------------

@main.command("sensitivity", help="Run a one-at-a-time sensitivity on the model.")
@click.argument("deal_id")
@click.option(
    "--shock", "shocks", multiple=True,
    help='Shock spec: "INPUT:OP:VALUE" e.g. "Revenue_Q1:mul:1.10" or "InterestRate:abs:0.065" '
         'or "Opex_Q1:delta:50000". OP is one of mul|abs|delta.',
)
@click.option("--csv", "as_csv", is_flag=True)
def cmd_sensitivity(deal_id: str, shocks: tuple[str, ...], as_csv: bool) -> None:
    d = load_deal(deal_id)
    if not shocks:
        _err("provide at least one --shock spec, e.g. --shock 'Revenue_Q1:mul:1.10'")

    parsed: list[sensitivity.Shock] = []
    for spec in shocks:
        try:
            name, op, val = spec.split(":", 2)
            v = float(val)
        except ValueError:
            _err(f"bad --shock spec {spec!r}, expected INPUT:OP:VALUE")
        kwargs = {"input_name": name, "label": spec}
        if op == "mul":
            kwargs["multiplier"] = v
        elif op == "delta":
            kwargs["delta"] = v
        elif op == "abs":
            kwargs["absolute"] = v
        else:
            _err(f"unknown shock op {op!r} (use mul|delta|abs)")
        parsed.append(sensitivity.Shock(**kwargs))

    df = sensitivity.run(d, parsed)
    audit.append(deal_id, "model.sensitivity", {"shocks": [s.label for s in parsed]})

    if as_csv:
        click.echo(df.to_csv(index=False))
        return
    t = Table(title=f"{deal_id}: sensitivity")
    for col in df.columns:
        t.add_column(str(col))
    for _, row in df.iterrows():
        t.add_row(*[_fmt(v) for v in row.tolist()])
    console.print(t)


@main.command("templates", help="List available notice templates.")
def cmd_templates() -> None:
    names = notices.list_templates()
    if not names:
        console.print("[yellow]No templates in data/templates/.[/]")
        return
    for n in names:
        console.print(f"  · [cyan]{n}[/]")


if __name__ == "__main__":
    main()
