"""
Dependency checker script for Diagnosis-AI web application
This script checks if all required dependencies are properly installed and can be imported.
"""

import sys
import importlib.util

def check_dependency(name):
    """Check if a dependency is installed and can be imported"""
    try:
        spec = importlib.util.find_spec(name)
        if spec is None:
            print(f"❌ {name:<20} - NOT FOUND")
            return False
        else:
            module = importlib.import_module(name)
            version = getattr(module, '__version__', 'Unknown version')
            print(f"✅ {name:<20} - INSTALLED (Version: {version})")
            return True
    except ImportError as e:
        print(f"❌ {name:<20} - ERROR: {str(e)}")
        return False

def main():
    print("\n==== DIAGNOSIS-AI DEPENDENCY CHECKER ====\n")
    
    dependencies = [
        "flask",
        "matplotlib",
        "reportlab",
        "json",
        "tempfile",
        "datetime",
        "io",
        "base64"
    ]
    
    # Special case for flask_session
    print("Checking flask_session:")
    try:
        from flask_session import Session
        print("✅ flask_session        - INSTALLED (Session class found)")
    except ImportError as e:
        print(f"❌ flask_session        - ERROR: {str(e)}")
        print("   Note: Your app is configured to use standard Flask sessions instead")
    
    print("\nChecking other dependencies:")
    all_ok = all(check_dependency(dep) for dep in dependencies)
    
    # Check diagnosis_engine and localization modules
    try:
        from diagnosis_engine import DiagnosisEngine
        print("✅ diagnosis_engine     - FOUND")
    except ImportError as e:
        print(f"❌ diagnosis_engine     - ERROR: {str(e)}")
        all_ok = False
    
    try:
        from localization import get_translation, available_languages
        print("✅ localization         - FOUND")
    except ImportError as e:
        print(f"❌ localization         - ERROR: {str(e)}")
        all_ok = False
    
    print("\nSummary:")
    if all_ok:
        print("All core dependencies are properly installed!")
        print("Your web application should be able to run without dependency issues.")
    else:
        print("Some dependencies have issues. Please install the missing packages.")
        print("You can run: pip install -r requirements.txt")
    
    print("\n========================================\n")

if __name__ == "__main__":
    main()