#!/usr/bin/env python3
"""
Setup script for agents app
"""

import os
import sys
from pathlib import Path

def setup_agents():
    """Setup the agents app with required dependencies and configuration"""
    
    print("Setting up Billnet Agents App...")
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Install dependencies
    print("\n1. Installing dependencies...")
    os.system("poetry install")
    
    # Check for required environment variables
    print("\n2. Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file template...")
        with open(".env", "w") as f:
            f.write("""# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Gemini API Configuration
GEMINI_API_KEY=your-gemini-api-key-here

# App Configuration
APP_NAME=billnet
""")
        print("Please update the .env file with your actual configuration values")
    
    # Check for Gemini API key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("Warning: GEMINI_API_KEY not found in environment variables")
        print("Please add your Gemini API key to the .env file")
    
    # Run migrations
    print("\n3. Running database migrations...")
    os.system("python manage.py makemigrations")
    os.system("python manage.py migrate")
    
    # Test the setup
    print("\n4. Testing the setup...")
    try:
        from apps.agents.service import workspace_agent_service
        print("✓ Agents service imported successfully")
        
        from apps.agents.config import llm_config
        print("✓ LLM configuration loaded successfully")
        
        print("\n✓ Agents app setup completed successfully!")
        print("\nNext steps:")
        print("1. Add your GEMINI_API_KEY to the .env file")
        print("2. Start the development server: python manage.py runserver")
        print("3. Visit http://localhost:8000/api/v1/docs/ to see the API documentation")
        
    except ImportError as e:
        print(f"Error: Failed to import agents modules: {e}")
        print("Please check that all dependencies are installed correctly")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_agents()
