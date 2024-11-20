import asyncio
import os
import shutil
import subprocess
import sys
import time
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

    try:
        with open(SETTINGS_FILE) as f:
            settings = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"❌ Error reading `settings.yaml`: {e}")
        return

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
    if not SETTINGS_FILE.exists():
        print("❌ No `settings.yaml` found. Skipping database access check.")
        return

    try:
        with open(SETTINGS_FILE) as f:
            settings = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"❌ Error reading `settings.yaml`: {e}")
        return

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

    async def test_connection():
        try:
            engine = create_async_engine(db_url)
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                print("✅ Successfully connected to the database.")
        except Exception as e:
            print(f"⚠️ Failed to connect to the database at `{db_url}`:\n  {e}")
            print("  ➡ Attempting to start the database using `docker compose up -d db`...")
            try:
                subprocess.run(["docker", "compose", "up", "-d", "db"], check=True, text=True, capture_output=True)
                print("  ✅ `docker compose up -d db` executed successfully. Retrying connection...")
                time.sleep(1)
                # Retry the database connection after starting the container
                engine = create_async_engine(db_url)
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                    print("  ✅ Successfully connected to the database after starting the container.")
            except subprocess.CalledProcessError as docker_error:
                print(f"❌ Failed to start the database using `docker compose up -d db`:\n  {docker_error}")
            except Exception as retry_error:
                print(f"❌ Retried database connection but failed again:\n  {retry_error}")

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
