#!/usr/bin/env python3
"""
Specialized dependency installation script for Dental AI Voice Agent
Handles Python 3.13+ compatibility issues
"""

import subprocess
import sys
import os
from pathlib import Path

def get_pip_cmd():
    """Get the correct pip command based on OS"""
    if os.name == 'nt':  # Windows
        return "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        return "venv/bin/pip"

def run_pip_install(packages, description):
    """Install packages with pip"""
    pip_cmd = get_pip_cmd()
    cmd = f"{pip_cmd} install {' '.join(packages)}"
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def install_dependencies():
    """Install dependencies with Python 3.13+ compatibility handling"""
    
    print("🚀 Installing dependencies for Dental AI Voice Agent...")
    print(f"Python version: {sys.version}")
    
    # Step 1: Install core dependencies first
    core_packages = [
        "python-dotenv>=1.0.0",
        "aiohttp>=3.8.0"
    ]
    
    if not run_pip_install(core_packages, "Installing core dependencies"):
        return False
    
    # Step 2: Try to install pydantic with specific flags for Python 3.13+
    if sys.version_info >= (3, 13):
        print("🐍 Detected Python 3.13+, using compatibility mode...")
        
        # Try installing pydantic with no build isolation first
        pydantic_cmd = f"{get_pip_cmd()} install --no-build-isolation pydantic>=2.6.0"
        print("🔄 Installing pydantic with no build isolation...")
        try:
            subprocess.run(pydantic_cmd, shell=True, check=True)
            print("✅ Pydantic installed successfully")
        except subprocess.CalledProcessError:
            print("⚠️  Trying older pydantic version...")
            if not run_pip_install(["pydantic==1.10.8"], "Installing older pydantic version"):
                return False
    
    # Step 3: Install FastAPI and related packages
    fastapi_packages = [
        "fastapi>=0.95.0",
        "uvicorn[standard]>=0.22.0",
        "python-multipart>=0.0.6"
    ]
    
    if not run_pip_install(fastapi_packages, "Installing FastAPI and related packages"):
        return False
    
    # Step 4: Install MongoDB driver
    if not run_pip_install(["motor>=3.1.0"], "Installing MongoDB driver"):
        return False
    
    print("\n🎉 All dependencies installed successfully!")
    return True

def main():
    """Main installation function"""
    try:
        success = install_dependencies()
        if success:
            print("\n✅ Installation completed successfully!")
            print("You can now run: python main.py")
        else:
            print("\n❌ Installation failed. Please check the errors above.")
            print("Try running: pip install -r requirements-stable.txt")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Installation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
