#!/usr/bin/env python3
"""
ScrubPy Modern Web Interface Launcher
Run the enhanced Streamlit interface
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the modern web interface"""
    try:
        # Get the path to the modern app
        app_path = Path(__file__).parent / "modern_app.py"
        
        if not app_path.exists():
            print(f"Error: {app_path} not found")
            sys.exit(1)
        
        print("🧹 Starting ScrubPy Modern Web Interface...")
        print("🌐 Opening in your browser...")
        print("Press Ctrl+C to stop")
        
        # Run Streamlit with the modern app
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(app_path),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false",
            "--theme.base", "light",
            "--theme.primaryColor", "#667eea"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 ScrubPy web interface stopped.")
    except Exception as e:
        print(f"Error starting web interface: {e}")
        sys.exit(1)

# Alias for backward compatibility
def launch_streamlit_app():
    """Launch the streamlit app - alias for main()"""
    return main()

if __name__ == "__main__":
    main()