#!/usr/bin/env python3
"""
Test connectivity to Hearthlink database services
"""

import sys
import time
import requests
import socket

def test_port(host, port, timeout=5):
    """Test if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def test_neo4j():
    """Test Neo4j connectivity"""
    print("Testing Neo4j...")
    
    # Test Bolt port
    if test_port('localhost', 7687):
        print("✓ Neo4j Bolt port (7687) is open")
    else:
        print("✗ Neo4j Bolt port (7687) is not accessible")
        return False
    
    # Test HTTP port
    if test_port('localhost', 7474):
        print("✓ Neo4j HTTP port (7474) is open")
        try:
            response = requests.get('http://localhost:7474', timeout=5)
            print(f"✓ Neo4j HTTP service responding (status: {response.status_code})")
        except Exception as e:
            print(f"✗ Neo4j HTTP service error: {e}")
    else:
        print("✗ Neo4j HTTP port (7474) is not accessible")
    
    return True

def test_redis():
    """Test Redis connectivity"""
    print("\nTesting Redis...")
    
    if test_port('localhost', 6379):
        print("✓ Redis port (6379) is open")
        
        # Try to connect with Python redis client if available
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, password='hearthlink_redis_2025', decode_responses=True)
            r.ping()
            print("✓ Redis authentication successful")
        except ImportError:
            print("! Redis client not installed, install with: pip install redis")
        except Exception as e:
            print(f"✗ Redis connection error: {e}")
    else:
        print("✗ Redis port (6379) is not accessible")

def test_qdrant():
    """Test Qdrant connectivity"""
    print("\nTesting Qdrant...")
    
    if test_port('localhost', 6333):
        print("✓ Qdrant HTTP port (6333) is open")
        try:
            response = requests.get('http://localhost:6333/health', timeout=5)
            if response.status_code == 200:
                print("✓ Qdrant health check passed")
            else:
                print(f"✗ Qdrant health check failed (status: {response.status_code})")
        except Exception as e:
            print(f"✗ Qdrant health check error: {e}")
    else:
        print("✗ Qdrant port (6333) is not accessible")

def main():
    print("Hearthlink Database Connectivity Test")
    print("=" * 40)
    
    # Test each service
    test_neo4j()
    test_redis()
    test_qdrant()
    
    print("\n" + "=" * 40)
    print("Test completed!")
    print("\nTo start services, run: docker/launch-databases.bat")
    print("To install missing Python packages: pip install redis requests")

if __name__ == "__main__":
    main()