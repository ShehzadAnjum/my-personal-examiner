"""
ClamAV daemon verification script.

Feature: 007-resource-bank-files
Created: 2025-12-27

Usage:
    python scripts/verify_clamav.py
"""

import sys

try:
    import pyclamd
    
    # Try to connect to ClamAV daemon
    cd = pyclamd.ClamdUnixSocket()
    
    # Test connection
    if cd.ping():
        print("✅ ClamAV daemon is running and responsive")
        version = cd.version()
        print(f"   Version: {version}")
        sys.exit(0)
    else:
        print("❌ ClamAV daemon is not responding")
        sys.exit(1)
        
except FileNotFoundError:
    print("❌ ClamAV daemon socket not found")
    print("   Expected: /var/run/clamav/clamd.ctl")
    print("   Install: sudo apt-get install clamav clamav-daemon")
    print("   Start: sudo systemctl start clamav-daemon")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error connecting to ClamAV: {e}")
    print("   Make sure clamav-daemon service is running")
    sys.exit(1)
