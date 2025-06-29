# HomeCloud

HomeCloud is a simple and fast folder sharing system designed for home use only. It allows you to quickly share folders from your local machine via a modern web interface, with a focus on ease of use and privacy within your home network.

## Features
- Share any folder from your local storage with a couple of clicks
- Modern admin interface for managing shares
- Folder tree browsing and one-click sharing
- Public links for shared folders
- Multilingual interface (English, Russian)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/homecloud.git
   cd homecloud
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (optional):**
   - You can create a `.env` file to override default settings (see `config.py` for available options).

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Open in your browser:**
   - Go to [http://localhost:5000](http://localhost:5000)

## Project Status

This project is in early development. Features and security are minimal and intended only for home/local network use. Do not expose HomeCloud to the internet or use it for sensitive data.

Contributions and feedback are welcome!
