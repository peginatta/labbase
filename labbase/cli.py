import typer

cli = typer.Typer(
    help="LabBase: check and maintain a lab vault (Obsidian Markdown notes).", no_args_is_help=True
)


@cli.command()
def check(
    vault: str = typer.Argument(".", help="Path to the vault folder"),
    report: bool = typer.Option(True, help="Write _reports/check.md inside the vault"),
) -> None:
    """Check the vault for mistakes and list stocks that need attention."""
    from labbase.vault.check import run_checks, write_report
    from labbase.vault.reader import load_vault

    v = load_vault(vault)
    result = run_checks(v)
    for issue in result.issues:
        typer.echo(str(issue))
    for s in result.attention():
        if s.status != "OUT":
            typer.echo(f"[{s.status}] {s.note.rel}" + (f": {s.reason}" if s.reason else ""))
    for t in result.totals:
        if t.low:
            typer.echo(f"[REORDER] {t.content.rel}: {t.total:g} {t.unit} left")
    typer.echo(
        f"{len(v.notes)} notes, {len(result.statuses)} stocks: "
        f"{len(result.errors)} errors, {len(result.warnings)} warnings."
    )
    if report:
        typer.echo(f"Report: {write_report(v, result)}")
    raise typer.Exit(1 if result.errors else 0)


@cli.command("fill-ids")
def fill_ids_cmd(
    vault: str = typer.Argument(".", help="Path to the vault folder"),
    dry_run: bool = typer.Option(False, help="Only show what would change"),
) -> None:
    """Give every new note (empty `id:`) the next free ID for its type."""
    from labbase.vault.ids import fill_ids
    from labbase.vault.reader import load_vault

    assigned = fill_ids(load_vault(vault), dry_run=dry_run)
    for a in assigned:
        typer.echo(f"{a.new_id}  {a.rel}")
    typer.echo(f"{len(assigned)} IDs {'would be ' if dry_run else ''}assigned.")


@cli.command("new")
def new_cmd(
    type_: str = typer.Argument(..., metavar="TYPE", help="Record type, e.g. stock, cell_line"),
    name: str = typer.Argument(..., help="Note name (becomes the filename and link name)"),
    vault: str = typer.Option(".", help="Path to the vault folder"),
) -> None:
    """Create a new note of TYPE with all its properties listed and an ID assigned."""
    from labbase.vault.reader import load_vault
    from labbase.vault.templates import new_note

    try:
        path = new_note(load_vault(vault), type_, name)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e
    typer.echo(f"Created {path}")


@cli.command("templates")
def templates_cmd(vault: str = typer.Argument(".", help="Path to the vault folder")) -> None:
    """Regenerate _templates/ from _schema/ (for Obsidian's Templates core plugin)."""
    from labbase.vault.reader import load_vault
    from labbase.vault.templates import write_templates

    for path in write_templates(load_vault(vault)):
        typer.echo(f"Wrote {path}")


@cli.command()
def render(vault: str = typer.Argument(".", help="Path to the vault folder")) -> None:
    """Update generated content: locations (`where` + 📍), box maps, canvases, property types."""
    from labbase.vault.reader import load_vault
    from labbase.vault.render import (
        render_box_maps,
        render_usage,
        render_where,
        write_obsidian_types,
    )

    v = load_vault(vault)
    from labbase.vault.canvas import render_canvases

    where = render_where(v)
    maps = render_box_maps(v)
    canvases = render_canvases(load_vault(vault))
    usage = render_usage(load_vault(vault))
    typer.echo(
        f"{len(where)} location properties/lines, {len(maps)} box maps, "
        f"{len(canvases)} canvases and {len(usage)} protocol usage logs updated."
    )
    typer.echo(f"Property types: {write_obsidian_types(v)}")


@cli.command()
def version() -> None:
    """Print the LabBase version."""
    from labbase import __version__

    typer.echo(__version__)


def main() -> None:
    cli()
