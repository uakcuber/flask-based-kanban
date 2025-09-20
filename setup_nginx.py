#!/usr/bin/env python3
"""
Nginx Setup Script for Flask Kanban App
Downloads and configures Nginx for Windows HTTPS proxy
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path

def download_nginx():
    """Download Nginx for Windows"""
    
    nginx_version = "1.25.3"
    nginx_url = f"http://nginx.org/download/nginx-{nginx_version}.zip"
    nginx_zip = f"nginx-{nginx_version}.zip"
    nginx_dir = f"nginx-{nginx_version}"
    
    print("Downloading Nginx for Windows...")
    print(f"URL: {nginx_url}")
    
    try:
        # Download Nginx
        urllib.request.urlretrieve(nginx_url, nginx_zip)
        print(f"Downloaded: {nginx_zip}")
        
        # Extract
        with zipfile.ZipFile(nginx_zip, 'r') as zip_ref:
            zip_ref.extractall('.')
        
        # Rename to nginx
        if os.path.exists("nginx"):
            shutil.rmtree("nginx")
        os.rename(nginx_dir, "nginx")
        
        # Cleanup
        os.remove(nginx_zip)
        
        print("Nginx extracted successfully!")
        return True
        
    except Exception as e:
        print(f"Failed to download Nginx: {e}")
        return False

def configure_nginx():
    """Configure Nginx with our config"""
    
    if not os.path.exists("nginx"):
        print("Nginx directory not found!")
        return False
    
    # Copy our config
    nginx_conf = "nginx/conf/nginx.conf"
    
    # Backup original
    if os.path.exists(nginx_conf):
        shutil.copy2(nginx_conf, nginx_conf + ".backup")
    
    # Copy our config
    shutil.copy2("nginx.conf", nginx_conf)
    
    print("Nginx configured with HTTPS proxy!")
    return True

def update_flask_for_nginx():
    """Update Flask to run on HTTP behind Nginx"""
    
    # Read current api.py
    with open("api.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace the final app.run with HTTP version
    old_run = """    app.run(debug=True, host='127.0.0.1', port=5001, ssl_context=ssl_context)
    
    if not use_ssl:
        # HTTP Configuration (fallback)
        print("🌐 Server will start at: http://localhost:5001")
        print("⚠️  Running in HTTP mode (not secure)")
        print("💡 Set FLASK_SSL=false to suppress SSL warnings")
        app.run(debug=True, host='127.0.0.1', port=5001)"""
    
    new_run = """    # Run Flask on HTTP behind Nginx HTTPS proxy
    print("🔄 Running Flask on HTTP (behind Nginx HTTPS proxy)")
    print("🌐 Flask server: http://127.0.0.1:5000")
    print("🔒 Nginx HTTPS: https://localhost")
    print("💡 Access via: https://localhost")
    app.run(debug=True, host='127.0.0.1', port=5000)"""
    
    # Update content
    content = content.replace(old_run, new_run)
    
    # Write back
    with open("api.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("Flask configured for Nginx proxy!")

def create_nginx_scripts():
    """Create start/stop scripts for Nginx"""
    
    # Start script
    start_script = """@echo off
echo Starting Nginx HTTPS Proxy...
cd nginx
start nginx.exe
cd ..
echo Nginx started!
echo HTTPS URL: https://localhost
echo To stop: run stop_nginx.bat
pause
"""
    
    with open("start_nginx.bat", "w", encoding="utf-8") as f:
        f.write(start_script)
    
    # Stop script
    stop_script = """@echo off
echo Stopping Nginx...
cd nginx
nginx.exe -s quit
cd ..
echo Nginx stopped!
pause
"""
    
    with open("stop_nginx.bat", "w", encoding="utf-8") as f:
        f.write(stop_script)
    
    print("Nginx control scripts created!")
    print("  - start_nginx.bat: Start Nginx HTTPS proxy")
    print("  - stop_nginx.bat: Stop Nginx")

def main():
    print("Flask Kanban App - Nginx HTTPS Setup")
    print("=" * 50)
    
    # Check if already setup
    if os.path.exists("nginx/nginx.exe"):
        print("Nginx already installed!")
    else:
        if not download_nginx():
            return
    
    if not configure_nginx():
        return
    
    update_flask_for_nginx()
    create_nginx_scripts()
    
    print("\nNginx HTTPS setup complete!")
    print("\nNext steps:")
    print("1. Run: start_nginx.bat (start Nginx HTTPS proxy)")
    print("2. Run: python api.py (start Flask on HTTP)")
    print("3. Visit: https://localhost (secure HTTPS access)")
    print("\nMake sure to run both Nginx and Flask!")
    print("Flask runs on HTTP:5000, Nginx proxies to HTTPS:443")

if __name__ == "__main__":
    main()