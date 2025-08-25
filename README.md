# HomeCloud

HomeCloud is a simple and fast folder sharing system designed for home use only. It allows you to quickly share folders from your local machine via a modern web interface, with a focus on ease of use and privacy within your home network.

## Features
- Share any folder from your local storage with a couple of clicks
- Modern admin interface for managing shares
- Folder tree browsing and one-click sharing
- Public links for shared folders
- Multilingual interface (English, Russian)

## Installation

### Quick Setup (Recommended)

The easiest way to get started is using the provided setup scripts that will automatically:
- Create virtual environment
- Install all dependencies
- Initialize the database

#### Using Python setup script (cross-platform):
```bash
python setup.py
```

### Manual Installation

If you prefer to set up manually:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/homecloud.git
   cd homecloud
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database:**
   ```bash
   flask db_init
   ```

5. **Create admin user:**
   ```bash
   python -c "
   from app import create_app
   from scripts.db import create_admin_user
   app = create_app()
   with app.app_context():
       create_admin_user(app, 'admin', 'your_password')
   "
   ```

6. **Set up environment variables (optional):**
   - Create a `.env` file to override default settings (see `config.py` for available options).

7. **Run the application:**
   ```bash
   python app.py
   ```

8. **Open in your browser:**
   - Go to [http://localhost:5000](http://localhost:5000)

## Development Commands

If you're using the Makefile, you have access to additional development commands:

```bash
make help          # Show all available commands
make dev           # Run in development mode with auto-reload
make db-init       # Initialize database
make db-testfill   # Fill database with test data
make db-reset      # Reset database
make clean         # Clean up cache files
make lint          # Run code linting
make format        # Format code with black
make test          # Run tests
```

## Docker Support

You can also run HomeCloud using Docker:

```bash
# Build and run with Docker
make docker-build
make docker-run

# Or use Docker Compose
docker-compose up --build
```

## Configuration

The application can be configured using environment variables or a `.env` file:

```env
SECRET_KEY=your-secret-key-change-this-in-production
DATABASE=database.db
UPLOAD_FOLDER=data
FLASK_ENV=development
```

## Project Status

This project is in early development. Features and security are minimal and intended only for home/local network use. Do not expose HomeCloud to the internet or use it for sensitive data.

Contributions and feedback are welcome!
