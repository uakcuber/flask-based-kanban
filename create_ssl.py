#!/usr/bin/env python3
"""
SSL Certificate Generator
Bu script development için self-signed SSL certificate oluşturur
"""

from OpenSSL import SSL, crypto
import os

def create_self_signed_cert(cert_dir="ssl"):
    """Self-signed SSL certificate oluştur"""
    
    # SSL klasörü oluştur
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
    
    # Key pair oluştur
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    
    # Certificate oluştur
    cert = crypto.X509()
    cert.get_subject().C = "TR"  # Country
    cert.get_subject().ST = "Istanbul"  # State
    cert.get_subject().L = "Istanbul"  # Location
    cert.get_subject().O = "Flask App"  # Organization
    cert.get_subject().OU = "Development"  # Organization Unit
    cert.get_subject().CN = "localhost"  # Common Name
    
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # 1 yıl geçerli
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')
    
    # Dosyalara kaydet
    cert_file = os.path.join(cert_dir, "cert.pem")
    key_file = os.path.join(cert_dir, "key.pem")
    
    with open(cert_file, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    with open(key_file, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
    
    print(f"SSL Certificate created:")
    print(f"  Certificate: {cert_file}")
    print(f"  Private Key: {key_file}")
    print(f"  Valid for: localhost")
    print(f"  Expires: 1 year from now")
    
    return cert_file, key_file

if __name__ == "__main__":
    create_self_signed_cert()