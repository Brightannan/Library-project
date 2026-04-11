import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

# Load .env file in development
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(basedir, '.env'))
except ImportError:
    pass


def _get_database_url():
    """Get database URL, fixing Railway's postgres:// -> postgresql:// prefix."""
    url = os.environ.get('DATABASE_URL') or \
          'sqlite:///' + os.path.join(basedir, 'library.db')
    # Railway (and Heroku) return 'postgres://' but SQLAlchemy needs 'postgresql://'
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url


class Config:
    # --- Security ---
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-insecure-key-change-in-production')
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'dev-salt-change-in-production')

    # --- Database ---
    SQLALCHEMY_DATABASE_URI = _get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Session ---
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    IDLE_TIMEOUT = timedelta(minutes=30)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False

    # --- File uploads ---
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    REPORTS_FOLDER = os.path.join(basedir, 'reports')

    # --- Mail ---
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER',
                                          os.environ.get('MAIL_USERNAME', ''))

    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.REPORTS_FOLDER, exist_ok=True)


class DevelopmentConfig(Config):
    DEBUG = True

    @staticmethod
    def init_app(app):
        Config.init_app(app)
        import logging
        logging.basicConfig(level=logging.DEBUG)


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Requires HTTPS (Railway provides this)

    @staticmethod
    def init_app(app):
        Config.init_app(app)
        import logging
        logging.basicConfig(level=logging.WARNING)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
