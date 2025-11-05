# -*- coding: utf-8 -*-
"""
Migration Helper Script

Provides easy commands for database migrations.
"""
import subprocess
import sys
from pathlib import Path

def run_command(cmd: list[str]):
    """Run a command and print output"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/migrate.py [command]")
        print("\nCommands:")
        print("  init       - Create initial migration")
        print("  upgrade    - Upgrade to latest migration")
        print("  downgrade  - Downgrade one migration")
        print("  current    - Show current migration")
        print("  history    - Show migration history")
        return
    
    command = sys.argv[1]
    
    if command == "init":
        run_command(["alembic", "revision", "--autogenerate", "-m", "Initial migration"])
    elif command == "upgrade":
        run_command(["alembic", "upgrade", "head"])
    elif command == "downgrade":
        run_command(["alembic", "downgrade", "-1"])
    elif command == "current":
        run_command(["alembic", "current"])
    elif command == "history":
        run_command(["alembic", "history"])
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()



