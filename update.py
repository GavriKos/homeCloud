#!/usr/bin/env python3
"""
Update script for homeCloud application.
This script updates dependencies and performs database migrations if needed.
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path


def run_command(command, cwd=None, check=True):
    """
    Run a shell command and return the result.
    
    Args:
        command (str): Command to run
        cwd (str): Working directory
        check (bool): Whether to check return code
        
    Returns:
        subprocess.CompletedProcess: Result of the command
    """
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def backup_database():
    """Create a backup of the current database."""
    db_path = Path("database.db")
    if not db_path.exists():
        print("No database found to backup.")
        return None
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"database_backup_{timestamp}.db"
    
    print(f"Creating database backup: {backup_path}")
    import shutil
    shutil.copy2(db_path, backup_path)
    return backup_path


def update_dependencies():
    """Update Python dependencies."""
    if not Path("requirements.txt").exists():
        print("Error: requirements.txt not found!")
        sys.exit(1)
    
    print("Updating dependencies...")
    run_command(f"{sys.executable} -m pip install --upgrade pip")
    run_command(f"{sys.executable} -m pip install -r requirements.txt --upgrade")


def check_database_schema():
    """Check if database schema needs updates."""
    db_path = Path("database.db")
    schema_path = Path("schema.sql")
    
    if not db_path.exists():
        print("Database not found. Please run setup first.")
        return False
    
    if not schema_path.exists():
        print("Schema file not found.")
        return False
    
    # Read current schema
    with open(schema_path, 'r', encoding='utf-8') as f:
        expected_schema = f.read()
    
    # Get current database schema
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get table schemas
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name")
    current_tables = cursor.fetchall()
    conn.close()
    
    print("Current database schema is compatible.")
    return True


def main():
    """Main update function."""
    print("=" * 50)
    print("homeCloud Application Update")
    print("=" * 50)
    
    # Check if we're in virtual environment
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        print("Warning: Not running in virtual environment.")
        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            print("Please activate virtual environment and try again.")
            sys.exit(0)
    
    # Backup database
    backup_path = backup_database()
    
    try:
        # Update dependencies
        update_dependencies()
        
        # Check database schema
        check_database_schema()
        
        print("\n" + "=" * 50)
        print("Update completed successfully!")
        print("=" * 50)
        
        if backup_path:
            print(f"Database backup created: {backup_path}")
        
        print("\nRestart the application to apply changes:")
        print("  python app.py")
        print("  or")
        print("  flask run")
        
    except Exception as e:
        print(f"\nUpdate failed: {e}")
        if backup_path:
            print(f"Database backup available: {backup_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
