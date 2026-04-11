import os
import sys
import subprocess

def setup_environment():
    print("Setting up School Library System...")
    print("=" * 50)
    
    # Create necessary directories
    directories = ['templates', 'static/css', 'static/js']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Install requirements
    print("\nInstalling dependencies...")
    requirements = [
        'Flask==2.3.3',
        'Flask-SQLAlchemy==3.0.5',
        'Flask-Login==0.6.2',
        'Flask-WTF==1.1.1',
        'WTForms==3.0.1',
        'openpyxl==3.1.2',
        'reportlab==4.0.4',
        'werkzeug==2.3.7',
        'python-dotenv==1.0.0'
    ]
    
    for req in requirements:
        print(f"Installing {req}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", req])
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("\nTo run the application:")
    print("1. Make sure you're in the project directory")
    print("2. Run: python app.py")
    print("3. Open browser to: http://localhost:5000")
    print("4. Login with: admin / admin123")
    print("\nNote: Create HTML templates in the 'templates' folder")

if __name__ == "__main__":
    setup_environment()