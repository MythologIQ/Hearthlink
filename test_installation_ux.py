#!/usr/bin/env python3
"""
Test script for Installation UX & Persona Introduction system.

Demonstrates the complete installation and onboarding experience
with persona introductions, accessibility features, and configuration.
"""

import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from installation_ux import InstallationUX

def setup_logging():
    """Setup logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('installation_ux_test.log')
        ]
    )
    return logging.getLogger(__name__)

def main():
    """Run the Installation UX test."""
    logger = setup_logging()
    
    print("🧪 Installation UX & Persona Introduction Test")
    print("=" * 60)
    
    try:
        # Initialize Installation UX system
        logger.info("Initializing Installation UX system...")
        installation_ux = InstallationUX(logger=logger)
        
        # Run the complete installation process
        logger.info("Starting installation process...")
        result = installation_ux.run_installation()
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 Installation Results")
        print("=" * 60)
        
        if result.success:
            print("✅ Installation completed successfully!")
            print(f"📁 Installation path: {result.installation_path}")
            print(f"⚙️  Config path: {result.config_path}")
            print(f"⏰ Completion time: {result.completion_time}")
            
            if result.warnings:
                print("\n⚠️  Warnings:")
                for warning in result.warnings:
                    print(f"   - {warning}")
        else:
            print("❌ Installation failed!")
            print("\nErrors:")
            for error in result.errors:
                print(f"   - {error}")
        
        print("\n" + "=" * 60)
        print("🎉 Test completed!")
        print("=" * 60)
        
        return 0 if result.success else 1
        
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        print(f"\n❌ Test failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 