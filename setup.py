#!/usr/bin/env python3
"""
Setup script for homeCloud application.
This script initializes the application environment, installs dependencies,
and sets up the database.
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path
from getpass import getpass
from werkzeug.security import generate_password_hash


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


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    print(f"Python version: {sys.version}")


def setup_virtual_environment():
    """Create and activate virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("Creating virtual environment...")
        run_command(f"{sys.executable} -m venv venv")
    else:
        print("Virtual environment already exists.")
    
    # Check if we're in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Already in virtual environment.")
    else:
        print("Please activate the virtual environment:")
        if os.name == 'nt':  # Windows
            print("  venv\\Scripts\\activate")
        else:  # Unix/Linux/macOS
            print("  source venv/bin/activate")
        print("Then run this script again.")
        sys.exit(0)


def install_dependencies():
    """Install Python dependencies from requirements.txt."""
    if not Path("requirements.txt").exists():
        print("Error: requirements.txt not found!")
        sys.exit(1)
    
    print("Installing dependencies...")
    run_command(f"{sys.executable} -m pip install --upgrade pip")
    run_command(f"{sys.executable} -m pip install -r requirements.txt")


def create_directories():
    """Create necessary directories."""
    directories = ["data", "static", "templates"]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"Creating directory: {directory}")
            dir_path.mkdir(parents=True, exist_ok=True)
        else:
            print(f"Directory already exists: {directory}")


def initialize_database():
    """Initialize the database with schema."""
    schema_path = Path("schema.sql")
    db_path = Path("database.db")
    
    if not schema_path.exists():
        print("Error: schema.sql not found!")
        sys.exit(1)
    
    print("Initializing database...")
    
    # Remove existing database if it exists
    if db_path.exists():
        response = input("Database already exists. Recreate it? (y/N): ").lower()
        if response == 'y':
            db_path.unlink()
            print("Existing database removed.")
        else:
            print("Keeping existing database.")
            return
    
    # Create database with schema
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
    
    conn = sqlite3.connect(str(db_path))
    conn.executescript(schema)
    conn.commit()
    conn.close()
    
    print("Database initialized successfully.")


def create_admin_user():
    """Create the first admin user."""
    db_path = Path("database.db")
    
    if not db_path.exists():
        print("Error: Database not found. Please initialize database first.")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check if admin already exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
    admin_count = cursor.fetchone()[0]
    
    if admin_count > 0:
        print("Admin user already exists.")
        conn.close()
        return
    
    print("\nCreating admin user...")
    while True:
        username = input("Enter admin username: ").strip()
        if username:
            break
        print("Username cannot be empty.")
    
    while True:
        password = getpass("Enter admin password: ")
        if len(password) >= 6:
            break
        print("Password must be at least 6 characters long.")
    
    password_hash = generate_password_hash(password)
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)",
            (username, password_hash)
        )
        conn.commit()
        print(f"Admin user '{username}' created successfully.")
    except sqlite3.IntegrityError:
        print(f"Error: Username '{username}' already exists.")
    finally:
        conn.close()


def create_env_file():
    """Create .env file with default configuration."""
    env_path = Path(".env")
    
    if env_path.exists():
        print(".env file already exists.")
        return
    
    print("Creating .env file...")
    env_content = """# homeCloud Configuration
SECRET_KEY=your-secret-key-change-this-in-production
DATABASE=database.db
UPLOAD_FOLDER=data
FLASK_ENV=development
"""
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(".env file created. Please update SECRET_KEY for production use.")


def setup_test_data():
    """Setup test data if requested."""
    response = input("\nDo you want to create test data? (y/N): ").lower()
    if response != 'y':
        return
    
    # Create test directories
    test_dirs = ["data/testshare", "data/testshare2"]
    for test_dir in test_dirs:
        Path(test_dir).mkdir(parents=True, exist_ok=True)
    
    # Create some test files
    test_files = [
        ("data/testshare/test.txt", "This is a test file."),
        ("data/testshare/readme.md", "# Test Share\nThis is a test markdown file."),
        ("data/testshare2/another.txt", "Another test file in second share."),
    ]
    
    for file_path, content in test_files:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("Test data created in data/testshare and data/testshare2")
    print("You can use Flask CLI commands to add these to the database:")
    print("  flask db_testfill")


def main():
    """Main setup function."""
    print("=" * 50)
    print("homeCloud Application Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Setup virtual environment
    setup_virtual_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Create necessary directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Initialize database
    initialize_database()
    
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Update SECRET_KEY in .env file for production")
    print("2. Start the application:")
    print("   python app.py")
    print("3. Or use Flask development server:")
    print("   flask run")
    print("4. Access the application at http://localhost:5000")
    print("\nFor production deployment, consider using gunicorn:")
    print("   gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'")


if __name__ == "__main__":
    main()
