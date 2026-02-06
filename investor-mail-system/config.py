"""
Investor Mail System - Configuration

Developed by: emirgunyy & gktrk363
"""
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
DATABASE_PATH = os.path.join(DATA_DIR, "investors.db")

# Gmail SMTP Settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Rate Limiting
RATE_LIMIT_SECONDS = 1.5  # Wait between emails
DAILY_LIMIT = 500  # Gmail free limit

# App Settings
APP_TITLE = "🎮 Yatırımcı Mail Sistemi"
PAGE_ICON = "📧"

# Create directories if not exist
for dir_path in [DATA_DIR, TEMPLATES_DIR, UPLOADS_DIR]:
    os.makedirs(dir_path, exist_ok=True)
