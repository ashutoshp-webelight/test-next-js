from typing import Optional

from alembic import command
from alembic.config import Config
from alembic.util import AutogenerateDiffsDetected
from rich import print
from rich.panel import Panel
from typer import Typer

from app.server import Application, create_app
from config import settings


cli = Typer(pretty_exceptions_show_locals=False)


@cli.command(
    help="""
    Detect database changes and create migrations.
    Make sure to import all the model classes to the app.models.__init__.py file to detect all the changes.
    """
)
def make_migrations() -> None:
    print(Panel.fit("[bold yellow]Detecting new migrations![/bold yellow]"))
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    alembic_cfg.set_main_option("compare_type", "true")
    try:
        command.check(alembic_cfg)
        print(Panel.fit("[bold green]No changes detected![/bold green]"))
    except AutogenerateDiffsDetected:
        print(Panel.fit("[bold yellow]Changes detected![/bold yellow]"))
        command.revision(alembic_cfg, autogenerate=True)


@cli.command(help="Migrate the database")
def migrate() -> None:
    print(Panel.fit("[bold yellow]Migrating database![/bold yellow]"))
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    command.upgrade(alembic_cfg, "head")


@cli.command(help="Rollback the database by one migration")
def rollback() -> None:
    print(Panel.fit("[bold yellow]Rolling back the database![/bold yellow]"))
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    command.downgrade(alembic_cfg, "-1")


@cli.command(no_args_is_help=True, help="Run the server")
def run(host: str, port: int, workers: Optional[int] = 1, debug: Optional[bool] = False) -> None:
    Application(
        create_app(debug),
        options={
            "bind": f"{host}:{port}",
            "workers": workers,
            "worker_class": "uvicorn.workers.UvicornWorker",
            "reload": True,
            "loglevel": "debug" if debug else "info",
            "preload_app": True,
        },
    ).run()


if __name__ == "__main__":
    cli()
