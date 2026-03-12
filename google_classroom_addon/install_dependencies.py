#!/usr/bin/env python3
"""
Setup script to install Google API dependencies into Blender's Python environment
Run this script to automatically locate and install dependencies
"""

import sys
import subprocess
import os
import platform

def find_blender_python():
    """Try to find Blender's Python executable"""
    system = platform.system()
    
    common_paths = []
    
    if system == "Windows":
        common_paths = [
            r"C:\Program Files\Blender Foundation\Blender 4.5\4.5\python\bin\python.exe",
            r"C:\Program Files\Blender Foundation\Blender\4.5\python\bin\python.exe",
        ]
    elif system == "Darwin":  # macOS
        common_paths = [
            "/Applications/Blender.app/Contents/Resources/4.5/python/bin/python3.11",
            "/Applications/Blender.app/Contents/Resources/4.5/python/bin/python3",
        ]
    elif system == "Linux":
        common_paths = [
            "/usr/share/blender/4.5/python/bin/python3.11",
            "/usr/share/blender/4.5/python/bin/python3",
            "/opt/blender/4.5/python/bin/python3.11",
            "/snap/blender/current/4.5/python/bin/python3.11",
        ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return None

def install_dependencies(python_path, requirements_file):
    """Install dependencies using pip"""
    print(f"Installing dependencies from {requirements_file}...")
    print(f"Using Python: {python_path}")
    
    try:
        result = subprocess.run(
            [python_path, "-m", "pip", "install", "-r", requirements_file],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.returncode != 0:
            print("Error installing dependencies:")
            print(result.stderr)
            return False
        
        print("\n✓ Dependencies installed successfully!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Classroom Blender Add-on - Dependency Installer")
    print("=" * 60)
    print()
    print("NOTE: If you are using GitHub Classroom, no additional")
    print("dependencies are needed. This installer is only required")
    print("for Google Classroom integration.")
    print()
    
    # Find Blender's Python
    python_path = find_blender_python()
    
    if python_path:
        print(f"Found Blender Python at: {python_path}")
        print()
        
        # Get requirements file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        requirements_file = os.path.join(script_dir, "requirements.txt")
        
        if not os.path.exists(requirements_file):
            print(f"Error: requirements.txt not found at {requirements_file}")
            return 1
        
        # Install dependencies
        if install_dependencies(python_path, requirements_file):
            print()
            print("Installation complete! You can now use the add-on in Blender.")
            print("Remember to:")
            print("1. Restart Blender if it's currently running")
            print("2. Enable the add-on in Edit > Preferences > Add-ons")
            print("3. Add your credentials.json file to the config folder")
            return 0
        else:
            return 1
    else:
        print("Could not automatically find Blender's Python executable.")
        print()
        print("Please manually install the dependencies by:")
        print("1. Locating Blender's Python executable")
        print("2. Running: <blender_python> -m pip install -r requirements.txt")
        print()
        print("Common locations:")
        if platform.system() == "Windows":
            print("  Windows: C:\\Program Files\\Blender Foundation\\Blender 4.5\\4.5\\python\\bin\\python.exe")
        elif platform.system() == "Darwin":
            print("  macOS: /Applications/Blender.app/Contents/Resources/4.5/python/bin/python3.11")
        else:
            print("  Linux: /usr/share/blender/4.5/python/bin/python3.11")
        return 1

if __name__ == "__main__":
    sys.exit(main())
