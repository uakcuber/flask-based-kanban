#!/usr/bin/env python3
"""
SSL Certificate Generator for Flask Kanban App
Generates self-signed SSL certificates for HTTPS development server
"""

import os
import subprocess
import sys
from pathlib import Path

def create_ssl_certificates():
    """Generate SSL certificates for HTTPS"""
    
    # Create certs directory if it doesn't exist
    certs_dir = Path("certs")
    certs_dir.mkdir(exist_ok=True)
    
    cert_file = certs_dir / "cert.pem"
    key_file = certs_dir / "key.pem"
    
    # Check if certificates already exist
    if cert_file.exists() and key_file.exists():
        print("🔒 SSL certificates already exist!")
        print(f"📁 Certificate: {cert_file}")
        print(f"🔑 Private Key: {key_file}")
        return str(cert_file), str(key_file)
    
    print("🔧 Generating SSL certificates...")
    
    try:
        # Try different OpenSSL paths for Windows
        openssl_paths = [
            "openssl",  # If in PATH
            "C:\\Program Files\\OpenSSL-Win64\\bin\\openssl.exe",
            "C:\\OpenSSL-Win64\\bin\\openssl.exe",
            "C:\\Program Files (x86)\\OpenSSL-Win32\\bin\\openssl.exe"
        ]
        
        openssl_cmd = None
        for path in openssl_paths:
            try:
                # Test if OpenSSL works with this path
                test_cmd = [path, "version"]
                result = subprocess.run(test_cmd, check=True, capture_output=True, text=True)
                openssl_cmd = path
                print(f"🔍 Found OpenSSL: {path}")
                print(f"📋 Version: {result.stdout.strip()}")
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        if not openssl_cmd:
            raise FileNotFoundError("OpenSSL not found in any expected location")
        
        # Create OpenSSL config for SAN (Subject Alternative Names)
        config_file = certs_dir / "openssl.conf"
        config_content = """[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C=TR
ST=Istanbul
L=Istanbul
O=Kanban App
OU=Development
CN=localhost

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = 127.0.0.1
IP.1 = 127.0.0.1
IP.2 = ::1
"""
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        # Generate private key and certificate using OpenSSL with config
        cmd = [
            openssl_cmd, "req", "-x509", "-newkey", "rsa:4096", 
            "-keyout", str(key_file), "-out", str(cert_file), 
            "-days", "365", "-nodes", "-config", str(config_file)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        print("✅ SSL certificates generated successfully!")
        print(f"📁 Certificate: {cert_file}")
        print(f"🔑 Private Key: {key_file}")
        print("🌐 Your Flask app will now run with HTTPS on https://localhost:5001")
        print("⚠️  Browser will show security warning for self-signed certificates")
        
        return str(cert_file), str(key_file)
        
    except subprocess.CalledProcessError as e:
        print("❌ OpenSSL command failed:")
        print(f"Error: {e}")
        print("\n💡 Alternative: Using Flask's adhoc SSL context")
        return None, None
        
    except FileNotFoundError:
        print("❌ OpenSSL not found in expected locations")
        print("� Searched paths:")
        for path in openssl_paths:
            print(f"   - {path}")
        print("\n💡 Alternative: Using Flask's adhoc SSL context")
        return None, None

def create_ssl_config():
    """Create SSL configuration file"""
    
    config_content = """# SSL Configuration for Flask Kanban App

## Development HTTPS Setup

### Option 1: Self-signed certificates (Recommended)
- Certificate: certs/cert.pem
- Private Key: certs/key.pem
- URL: https://localhost:5001

### Option 2: Flask adhoc SSL (Fallback)
- Uses Flask's built-in SSL context
- URL: https://localhost:5001

### Browser Security Warning
- Self-signed certificates will show browser warnings
- Click "Advanced" → "Proceed to localhost (unsafe)" to access
- This is normal for development environments

### Production Deployment
- Use proper SSL certificates from Let's Encrypt or CA
- Configure reverse proxy (nginx/apache) for HTTPS
- Never use self-signed certificates in production
"""
    
    with open("SSL_README.md", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print("📖 SSL configuration guide created: SSL_README.md")

if __name__ == "__main__":
    print("🔐 Flask Kanban App - SSL Certificate Generator")
    print("=" * 50)
    
    cert_file, key_file = create_ssl_certificates()
    create_ssl_config()
    
    if cert_file and key_file:
        print(f"\n🚀 To start your Flask app with HTTPS:")
        print(f"   python api.py")
        print(f"   Then visit: https://localhost:5001")
    else:
        print(f"\n🚀 Flask will use adhoc SSL context")
        print(f"   python api.py")
        print(f"   Then visit: https://localhost:5001")
    
    print("\n⚠️  Remember: Accept browser security warning for self-signed certificates")