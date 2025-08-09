#!/usr/bin/env python3
"""
Quick Start Script for Dental AI Voice Agent
This script helps you set up the project quickly
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def print_step(step_num, title, description=""):
    """Print a formatted step"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*60}")
    if description:
        print(description)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        return True
    else:
        print("❌ .env file not found")
        print("Please create a .env file with your MongoDB connection string")
        print("You can copy from env.example as a template")
        return False

def run_command(command, description):
    """Run a shell command"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def setup_virtual_environment():
    """Set up Python virtual environment"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")

def install_dependencies():
    """Install Python dependencies using specialized script"""
    print("🔄 Installing dependencies using specialized installer...")
    try:
        # Use the specialized installation script
        result = subprocess.run("python install_deps.py", shell=True, check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Specialized installation failed, trying manual fallback...")
        
        # Manual fallback
        pip_cmd = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip"
        try:
            result = subprocess.run(f"{pip_cmd} install -r requirements-stable.txt", shell=True, check=True, capture_output=True, text=True)
            print("✅ Dependencies installed successfully with stable versions")
            return True
        except subprocess.CalledProcessError as e2:
            print(f"❌ All installation attempts failed")
            print(f"Final error: {e2.stderr}")
            return False

def setup_sample_data():
    """Set up sample data in MongoDB"""
    print("🔄 Setting up sample data...")
    try:
        # Determine the correct python command based on OS
        if os.name == 'nt':  # Windows
            python_cmd = "venv\\Scripts\\python"
        else:  # Unix/Linux/macOS
            python_cmd = "venv/bin/python"
        
        result = subprocess.run(f"{python_cmd} setup_sample_data.py", shell=True, check=True)
        print("✅ Sample data setup completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Sample data setup failed: {e}")
        return False

def test_api():
    """Test the API endpoints"""
    print("🔄 Testing API endpoints...")
    try:
        # Determine the correct python command based on OS
        if os.name == 'nt':  # Windows
            python_cmd = "venv\\Scripts\\python"
        else:  # Unix/Linux/macOS
            python_cmd = "venv/bin/python"
        
        result = subprocess.run(f"{python_cmd} test_api.py", shell=True, check=True)
        print("✅ API tests completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ API tests failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Dental AI Voice Agent - Quick Start Setup")
    print("This script will help you set up the project quickly")
    
    # Step 1: Check Python version
    print_step(1, "Check Python Version", "Verifying Python 3.8+ is installed")
    if not check_python_version():
        return False
    
    # Step 2: Check environment file
    print_step(2, "Check Environment Configuration", "Verifying .env file exists")
    if not check_env_file():
        print("\n📝 To create your .env file:")
        print("1. Copy env.example to .env")
        print("2. Edit .env with your MongoDB Atlas connection string")
        print("3. Run this script again")
        return False
    
    # Step 3: Set up virtual environment
    print_step(3, "Set Up Virtual Environment", "Creating Python virtual environment")
    if not setup_virtual_environment():
        return False
    
    # Step 4: Install dependencies
    print_step(4, "Install Dependencies", "Installing required Python packages")
    if not install_dependencies():
        return False
    
    # Step 5: Set up sample data
    print_step(5, "Set Up Sample Data", "Populating MongoDB with sample patient data")
    if not setup_sample_data():
        print("⚠️  Sample data setup failed. You can run it manually later.")
    
    # Step 6: Test API
    print_step(6, "Test API", "Testing API endpoints")
    if not test_api():
        print("⚠️  API tests failed. You can run them manually later.")
    
    # Final instructions
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. Start the server: python main.py")
    print("2. Open API docs: http://localhost:8000/docs")
    print("3. Test endpoints: python test_api.py")
    print("\n📚 For more information, see README.md")
    print("\n🔗 Useful URLs:")
    print("   - API Documentation: http://localhost:8000/docs")
    print("   - Health Check: http://localhost:8000/health")
    print("   - Root Endpoint: http://localhost:8000/")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Quick start completed successfully!")
        else:
            print("\n❌ Quick start failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
