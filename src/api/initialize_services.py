#!/usr/bin/env python3
"""
Service Initialization Script
Initializes all Hearthlink backend services
"""

import asyncio
import sys
import os
from llm_connector import initialize_llm_services
from vault_connector import initialize_vault
from synapse_connector import initialize_synapse

async def main():
    """Initialize all services"""
    print("=" * 60)
    print("HEARTHLINK SERVICE INITIALIZATION")
    print("=" * 60)
    
    services_status = {
        'llm': False,
        'vault': False,
        'synapse': False
    }
    
    # Initialize LLM services
    print("\n1. LLM Services")
    print("-" * 20)
    services_status['llm'] = await initialize_llm_services()
    
    # Initialize Vault
    print("\n2. Vault Database")
    print("-" * 20)
    services_status['vault'] = initialize_vault()
    
    # Initialize Synapse
    print("\n3. Synapse Connections")
    print("-" * 20)
    services_status['synapse'] = await initialize_synapse()
    
    # Summary
    print("\n" + "=" * 60)
    print("INITIALIZATION SUMMARY")
    print("=" * 60)
    
    for service, status in services_status.items():
        icon = "✓" if status else "✗"
        print(f"{icon} {service.upper()}: {'Connected' if status else 'Not Connected'}")
    
    connected_count = sum(services_status.values())
    total_services = len(services_status)
    
    print(f"\nServices Ready: {connected_count}/{total_services}")
    
    if connected_count == 0:
        print("\n⚠️  No services connected. Hearthlink will run in offline mode.")
        print("\nTo connect services:")
        print("1. For LLM: Install and run Ollama (https://ollama.ai)")
        print("2. For Vault: Database auto-created (should work)")
        print("3. For Synapse: Set CLAUDE_API_KEY and GOOGLE_AI_KEY environment variables")
        
    elif connected_count < total_services:
        print(f"\n⚠️  {total_services - connected_count} service(s) not connected.")
        print("Some features may not be available.")
        
    else:
        print("\n🎉 All services connected! Hearthlink is ready.")
    
    print("\n" + "=" * 60)
    return services_status

if __name__ == '__main__':
    try:
        status = asyncio.run(main())
        
        # Start the health API server
        print("\nStarting Health API server...")
        print("Run: python src/api/system_health.py")
        
    except KeyboardInterrupt:
        print("\nInitialization interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nInitialization failed: {e}")
        sys.exit(1)