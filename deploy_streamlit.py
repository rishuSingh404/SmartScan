#!/usr/bin/env python3
"""
Deployment script for Streamlit Resume Parser
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False
    return True

def download_nltk_data():
    """Download required NLTK data"""
    print("Downloading NLTK data...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('wordnet', quiet=True)
        print("✅ NLTK data downloaded successfully!")
    except Exception as e:
        print(f"❌ Error downloading NLTK data: {e}")
        return False
    return True

def run_streamlit():
    """Run the Streamlit app"""
    print("Starting Streamlit app...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")

def main():
    print("🚀 Resume Parser - Streamlit Deployment")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Download NLTK data
    if not download_nltk_data():
        sys.exit(1)
    
    print("\n🎉 Setup complete! Starting the app...")
    print("📱 The app will open in your browser at http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the app")
    print("-" * 50)
    
    # Run the app
    run_streamlit()

if __name__ == "__main__":
    main() 