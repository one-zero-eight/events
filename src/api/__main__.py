import asyncio
import os
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

import yaml
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

BASE_DIR = Path(__file__).resolve().parents[2]
os.chdir(BASE_DIR)

SETTINGS_TEMPLATE = BASE_DIR / "settings.example.yaml"
SETTINGS_FILE = BASE_DIR / "settings.yaml"
PRE_COMMIT_CONFIG = BASE_DIR / ".pre-commit-config.yaml"
ACCOUNTS_TOKEN_URL = "https://api.innohassle.ru/accounts/v0/tokens/generate-service-token?sub=events-local-dev&scopes=users&only_for_me=true"
DEFAULT_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"


def get_settings():
    """
    Load and return the settings from `settings.yaml` if it exists.
    """
    if not SETTINGS_FILE.exists():
        raise RuntimeError("❌ No `settings.yaml` found.")

    try:
        with open(SETTINGS_FILE) as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        raise RuntimeError("❌ No `settings.yaml` found.") from e


def ensure_settings_file():
    """
    Ensure `settings.yaml` exists. If not, copy `settings.yaml.example`.
    """
    if not SETTINGS_TEMPLATE.exists():
        print("❌ No `settings.yaml.example` found. Skipping copying.")
        return

    if SETTINGS_FILE.exists():
        print("✅ `settings.yaml` exists.")
        return

    shutil.copy(SETTINGS_TEMPLATE, SETTINGS_FILE)
    print(f"✅ Copied `{SETTINGS_TEMPLATE}` to `{SETTINGS_FILE}`")


def check_and_prompt_api_jwt_token():
    """
    Check if `accounts.api_jwt_token` is set in `settings.yaml`.
    Prompt the user to set it if it is missing, allow them to input it,
    and open the required URL in the default web browser.
    """
    if not SETTINGS_FILE.exists():
        print("❌ No `settings.yaml` found. Skipping JWT token check.")
        return

    settings = get_settings()
    accounts = settings.get("accounts", {})
    api_jwt_token = accounts.get("api_jwt_token")

    if not api_jwt_token or api_jwt_token == "...":
        print("⚠️ `accounts.api_jwt_token` is missing in `settings.yaml`.")
        print(f"  ➡️ Opening the following URL to generate a token:\n  {ACCOUNTS_TOKEN_URL}")

        webbrowser.open(ACCOUNTS_TOKEN_URL)
        print("  🔑 Please paste the generated token below:")

        token = input("  Enter the token here (or press Enter to skip):\n>").strip()

        if token:
            try:
                with open(SETTINGS_FILE) as f:
                    as_text = f.read()
                as_text = as_text.replace("api_jwt_token: null", f"api_jwt_token: {token}")
                as_text = as_text.replace("api_jwt_token: ...", f"api_jwt_token: {token}")
                with open(SETTINGS_FILE, "w") as f:
                    f.write(as_text)
                print("  ✅ `accounts.api_jwt_token` has been updated in `settings.yaml`.")
            except Exception as e:
                print(f"  ❌ Error updating `settings.yaml`: {e}")
        else:
            print("  ⚠️ Token was not provided. Please manually update `settings.yaml` later.")
            print(f"  ➡️ Refer to the URL: {ACCOUNTS_TOKEN_URL}")
    else:
        print("✅ `accounts.api_jwt_token` is specified.")


def ensure_pre_commit_hooks():
    """
    Ensure `pre-commit` hooks are installed.
    """

    def is_pre_commit_installed():
        pre_commit_hook = BASE_DIR / ".git" / "hooks" / "pre-commit"
        return pre_commit_hook.exists() and os.access(pre_commit_hook, os.X_OK)

    if not PRE_COMMIT_CONFIG.exists():
        print("❌ No `.pre-commit-config.yaml` found. Skipping pre-commit setup.")
        return

    if is_pre_commit_installed():
        print("✅ Pre-commit hooks are installed.")
        return

    try:
        subprocess.run(
            ["poetry", "run", "pre-commit", "install", "--install-hooks", "-t", "pre-commit", "-t", "commit-msg"],
            check=True,
            text=True,
        )
        print("✅ Pre-commit hooks installed successfully.")
    except subprocess.CalledProcessError as e:
        print(
            f"❌ Error setting up pre-commit hooks:\n{e.stderr}\nPlease, setup it manually with `poetry run pre-commit install --install-hooks -t pre-commit -t commit-msg`"
        )


def check_database_access():
    """
    Ensure the database is accessible using `db_url` from `settings.yaml`. If missing, set a default value.
    """
    settings = get_settings()
    db_url = settings.get("db_url")

    if not db_url or db_url == "...":
        print("⚠️ `db_url` is missing in `settings.yaml`. Setting default one.")

        try:
            with open(SETTINGS_FILE) as f:
                as_text = f.read()
            as_text = as_text.replace("db_url: null", f"db_url: {DEFAULT_DB_URL}")
            as_text = as_text.replace("db_url: ...", f"db_url: {DEFAULT_DB_URL}")
            with open(SETTINGS_FILE, "w") as f:
                f.write(as_text)
            print("  ✅ `db_url` has been updated in `settings.yaml`.")
            db_url = DEFAULT_DB_URL
        except Exception as e:
            print(f"  ❌ Error updating `settings.yaml`: {e}")
            return

    def get_docker_compose_command():
        commands = ["docker compose", "docker-compose"]

        for cmd in commands:
            try:
                subprocess.run(cmd.split(), check=True, text=True, capture_output=True)
                return cmd
            except subprocess.CalledProcessError:
                # Command not available
                continue
        return None

    def run_alembic_upgrade():
        """
        Run `alembic upgrade head` to apply migrations.
        """
        try:
            print("⚙️ Running Alembic migrations...")
            subprocess.run(["alembic", "upgrade", "head"], check=True, text=True, capture_output=True)
            print("  ✅ Alembic migrations applied successfully.")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Error running Alembic migrations:\n  {e.stderr}")
        except Exception as e:
            print(f"  ❌ Unexpected error running Alembic migrations: {e}")

    async def test_connection():
        try:
            engine = create_async_engine(db_url)
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                print("✅ Successfully connected to the database.")
            run_alembic_upgrade()
        except Exception:
            print(f"⚠️ Failed to connect to the database at `{db_url}`")
            docker_compose = get_docker_compose_command()

            if docker_compose:
                print(f"  ➡ Attempting to start the database using `{docker_compose} up -d db` (wait for it)")
                try:
                    subprocess.run(
                        [*docker_compose.split(), "up", "-d", "--wait", "db"],
                        check=True,
                        text=True,
                        capture_output=True,
                    )
                    print(f"  ✅ `{docker_compose} up -d db` executed successfully. Retrying connection...")
                    # Retry the database connection after starting the container
                    engine = create_async_engine(db_url)
                    async with engine.connect() as conn:
                        await conn.execute(text("SELECT 1"))
                        print("  ✅ Successfully connected to the database after starting the container.")
                    run_alembic_upgrade()
                except subprocess.CalledProcessError as docker_error:
                    print(f"  ❌ Failed to start the database using `{docker_compose} up -d db`:\n  {docker_error}")
                except Exception as retry_error:
                    print(f"  ❌ Retried database connection but failed again:\n  {retry_error}")
            else:
                print("  ❌ Docker Compose is not available, so not able to start db automatically.")

    asyncio.run(test_connection())


ensure_settings_file()
ensure_pre_commit_hooks()
check_and_prompt_api_jwt_token()
check_database_access()

import uvicorn  # noqa: E402

# Get arguments from command
args = sys.argv[1:]
extended_args = [
    "src.api.app:app",
    "--use-colors",
    "--proxy-headers",
    "--forwarded-allow-ips=*",
    *args,
]

print(f"🚀 Starting Uvicorn server: 'uvicorn {' '.join(extended_args)}'")
uvicorn.main.main(extended_args)
