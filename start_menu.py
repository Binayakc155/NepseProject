#!/usr/bin/env python3
"""
NEPSE Prediction System - Quick Helper Menu
Provides interactive menu for common tasks.
"""

import os
import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent / "scripts"


def print_header():
    print("\n" + "="*60)
    print("  🚀 NEPSE ML PREDICTION SYSTEM")
    print("  Quick Start Helper Menu")
    print("="*60 + "\n")


def print_menu():
    print("What would you like to do?\n")
    print("  1️⃣  Check system status")
    print("  2️⃣  Run complete pipeline (20-30 min)")
    print("  3️⃣  Update now manually (15-20 min)")
    print("  4️⃣  View web dashboard (open browser)")
    print("  5️⃣  Test model accuracy")
    print("  6️⃣  Start auto-updates (3:10 PM daily)")
    print("  7️⃣  View documentation")
    print("  8️⃣  View logs")
    print("  0️⃣  Exit")
    print()


def status_check():
    """Check system health"""
    print("\n📊 Checking system status...\n")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "status_check.py")],
        capture_output=False
    )
    return result.returncode == 0


def run_all():
    """Run complete pipeline"""
    print("\n🔄 Starting complete pipeline...")
    print("This may take 20-30 minutes.\n")
    input("Press Enter to continue...")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "run_all.py")],
        capture_output=False
    )
    return result.returncode == 0


def update_now():
    """Manual update"""
    print("\n⚡ Starting manual update...")
    print("This takes about 15-20 minutes.\n")
    input("Press Enter to continue...")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "update_now.py")],
        capture_output=False
    )
    return result.returncode == 0


def open_dashboard():
    """Open web dashboard"""
    print("\n🌐 Opening web dashboard...")
    print("Starting web server on http://localhost:8000\n")
    
    import webbrowser
    import time
    
    # Start server in background
    web_dir = SCRIPT_DIR.parent / "web"
    print(f"Web directory: {web_dir}")
    
    # Try to open browser
    try:
        webbrowser.open("http://localhost:8000")
        print("\n✅ Browser opened!")
        print("If not, open manually: http://localhost:8000")
    except:
        print("\n⚠️  Could not open browser automatically")
        print("Open manually: http://localhost:8000")
    
    print("\nTo start the web server, run in another terminal:")
    print("  cd web")
    print("  python -m http.server 8000")


def test_accuracy():
    """Test model accuracy"""
    print("\n🧪 Testing model accuracy...")
    print("This compares LSTM vs XGBoost on unseen data.\n")
    input("Press Enter to continue...")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "backtest_comparison.py")],
        capture_output=False
    )
    return result.returncode == 0


def auto_update():
    """Start auto-updates"""
    print("\n🤖 Starting auto-update scheduler...")
    print("Updates will run every weekday at 3:10 PM")
    print("Keep this terminal open 24/7\n")
    input("Press Enter to continue (Ctrl+C to stop)...")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "auto_update.py")],
        capture_output=False
    )
    return result.returncode == 0


def view_docs():
    """View available documentation"""
    print("\n📚 Documentation Files:\n")
    
    docs = {
        "1": ("QUICKSTART.md", "5-minute getting started guide", "⭐ Start here"),
        "2": ("README_USAGE.md", "Complete features and usage guide", "Full reference"),
        "3": ("TROUBLESHOOTING.md", "Problem solving guide", "Fix issues"),
        "4": ("SYSTEM_ARCHITECTURE.md", "Technical architecture details", "Deep dive"),
        "5": ("SCRIPTS_REFERENCE.md", "All scripts explained", "Command reference"),
    }
    
    for key, (file, desc, label) in docs.items():
        print(f"  {key}. {file}")
        print(f"     {desc} ({label})")
    
    choice = input("\nEnter number to view (or press Enter to skip): ").strip()
    
    if choice in docs:
        file = docs[choice][0]
        file_path = SCRIPT_DIR.parent / file
        if file_path.exists():
            try:
                import webbrowser
                webbrowser.open(f"file://{file_path.absolute()}")
                print(f"\nOpened {file} in browser")
            except:
                print(f"\n📄 File: {file}")
                print(f"   Location: {file_path}")
        else:
            print(f"\n❌ File not found: {file}")


def view_logs():
    """View recent log entries"""
    print("\n📋 Recent Log Entries:\n")
    
    logs = [
        ("auto_update.log", SCRIPT_DIR / "auto_update.log"),
        ("export_predictions.log", SCRIPT_DIR / "export_predictions.log"),
    ]
    
    for name, path in logs:
        if path.exists():
            print(f"📄 {name}:")
            print("  Last 5 entries:")
            with open(path, 'r') as f:
                lines = f.readlines()[-5:]
                for line in lines:
                    print(f"    {line.rstrip()}")
            print()
        else:
            print(f"ℹ️  {name}: Not yet created\n")


def main():
    """Main menu loop"""
    os.chdir(SCRIPT_DIR.parent)
    
    while True:
        print_header()
        print_menu()
        
        choice = input("Enter your choice (0-8): ").strip()
        
        if choice == "1":
            status_check()
        elif choice == "2":
            run_all()
        elif choice == "3":
            update_now()
        elif choice == "4":
            open_dashboard()
        elif choice == "5":
            test_accuracy()
        elif choice == "6":
            auto_update()
        elif choice == "7":
            view_docs()
        elif choice == "8":
            view_logs()
        elif choice == "0":
            print("\n👋 Goodbye!\n")
            break
        else:
            print("\n❌ Invalid choice. Please enter 0-8.\n")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
