#!/usr/bin/env python3
"""
Install missing dependencies for the backend
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("🔧 Installing missing dependencies for education API...")
    
    # Required packages for the education API
    packages = [
        "aiohttp==3.9.0"
    ]
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installation Results:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Failed: {len(packages) - success_count}")
    
    if success_count == len(packages):
        print("\n🎉 All dependencies installed successfully!")
        print("Your backend is now ready to run the education API.")
        print("\nNext steps:")
        print("1. cd /path/to/backend")
        print("2. python run.py")
        print("3. Test at http://localhost:8000/api/v1/education/metadata")
    else:
        print("\n⚠️ Some dependencies failed to install.")
        print("Please install them manually:")
        for package in packages:
            print(f"   pip install {package}")

if __name__ == "__main__":
    main()