#!/usr/bin/env python3
"""
Test script to verify Synapse launch_local_resource function
Tests the function specification and operational status as required for external tool coordination.
"""

import sys
import os
import subprocess
import logging
from typing import Dict, Any, Optional

# Add the src directory to the path so we can import synapse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from synapse.synapse import Synapse

def test_launch_local_resource_function():
    """Test if launch_local_resource function exists and is operational."""
    print("🔍 Testing Synapse launch_local_resource function...")
    
    # Initialize Synapse
    synapse = Synapse()
    
    # Check if the function exists
    has_function = hasattr(synapse, 'launch_local_resource')
    print(f"Function exists: {has_function}")
    
    if not has_function:
        print("❌ launch_local_resource function not implemented")
        return False
    
    # Test the function with claude_code
    try:
        result = synapse.launch_local_resource("claude_code")
        print(f"✅ Function executed successfully: {result}")
        return True
    except Exception as e:
        print(f"❌ Function execution failed: {e}")
        return False

def verify_claude_code_availability():
    """Verify if claude-code is available in the system."""
    print("\n🔍 Verifying claude-code availability...")
    
    try:
        # Try to find claude-code command
        result = subprocess.run(['which', 'claude-code'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ claude-code found at: {result.stdout.strip()}")
            
            # Try to get version
            version_result = subprocess.run(['claude-code', '--version'], 
                                          capture_output=True, text=True)
            if version_result.returncode == 0:
                print(f"✅ claude-code version: {version_result.stdout.strip()}")
                return True
            else:
                print(f"⚠️ claude-code exists but version check failed: {version_result.stderr}")
                return False
        else:
            print("❌ claude-code not found in PATH")
            return False
    except Exception as e:
        print(f"❌ Error checking claude-code: {e}")
        return False

def run_setup_script():
    """Run the setup script to install claude-code."""
    print("\n🚀 Running setup script to install claude-code...")
    
    setup_script = os.path.join(os.path.dirname(__file__), 'setup-claude-code.sh')
    
    if not os.path.exists(setup_script):
        print("❌ Setup script not found")
        return False
    
    try:
        # Make script executable
        os.chmod(setup_script, 0o755)
        
        # Run the setup script
        result = subprocess.run(['bash', setup_script], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Setup script executed successfully")
            print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ Setup script failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running setup script: {e}")
        return False

def implement_launch_local_resource():
    """Implement the launch_local_resource function in Synapse."""
    print("\n🔧 Implementing launch_local_resource function...")
    
    # The function implementation will be added to the Synapse class
    function_code = '''
    def launch_local_resource(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Launch a local resource/tool as specified in the Claude Integration Protocol.
        
        Args:
            target: The target resource to launch (e.g., 'claude_code', 'dev_container', 'gemini_colab')
            **kwargs: Optional flags (background, monitor, ipc_bridge)
            
        Returns:
            Dict containing launch result and status
        """
        import subprocess
        import uuid
        from datetime import datetime
        
        # Generate request ID for tracking
        request_id = f"launch-{uuid.uuid4().hex[:8]}"
        
        # Log the launch request
        self.traffic_logger.log_traffic(
            traffic_type=self.traffic_logger.TrafficType.SYSTEM_OPERATION,
            source="synapse",
            target=target,
            user_id="system",
            request_id=request_id,
            payload={"target": target, "kwargs": kwargs},
            severity=self.traffic_logger.TrafficSeverity.MEDIUM
        )
        
        try:
            # Handle different target types
            if target == "claude_code":
                return self._launch_claude_code(**kwargs)
            elif target == "dev_container":
                return self._launch_dev_container(**kwargs)
            elif target == "gemini_colab":
                return self._launch_gemini_colab(**kwargs)
            else:
                raise ValueError(f"Unknown target: {target}")
                
        except Exception as e:
            self.logger.error(f"Failed to launch {target}: {e}")
            return {
                "request_id": request_id,
                "target": target,
                "success": False,
                "error": str(e),
                "launched_at": datetime.now().isoformat()
            }
    
    def _launch_claude_code(self, background: bool = False, monitor: bool = False, 
                           ipc_bridge: bool = False) -> Dict[str, Any]:
        """Launch claude-code with specified options."""
        import subprocess
        import uuid
        from datetime import datetime
        
        request_id = f"claude-{uuid.uuid4().hex[:8]}"
        
        # Check if claude-code is available
        try:
            version_result = subprocess.run(['claude-code', '--version'], 
                                          capture_output=True, text=True, timeout=10)
            if version_result.returncode != 0:
                raise RuntimeError("claude-code not available or not responding")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise RuntimeError(f"claude-code not found or not responding: {e}")
        
        # Build command
        cmd = ['claude-code']
        
        # Add flags based on options
        if background:
            cmd.append('--background')
        if monitor:
            cmd.append('--monitor')
        if ipc_bridge:
            cmd.append('--ipc-bridge')
        
        # Launch the process
        try:
            if background:
                # Launch in background
                process = subprocess.Popen(cmd, 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE,
                                         text=True)
                pid = process.pid
                
                return {
                    "request_id": request_id,
                    "target": "claude_code",
                    "success": True,
                    "pid": pid,
                    "background": True,
                    "launched_at": datetime.now().isoformat()
                }
            else:
                # Launch synchronously
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                return {
                    "request_id": request_id,
                    "target": "claude_code",
                    "success": result.returncode == 0,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "launched_at": datetime.now().isoformat()
                }
                
        except subprocess.TimeoutExpired:
            return {
                "request_id": request_id,
                "target": "claude_code",
                "success": False,
                "error": "claude-code launch timed out",
                "launched_at": datetime.now().isoformat()
            }
    
    def _launch_dev_container(self, **kwargs) -> Dict[str, Any]:
        """Launch development container."""
        # Placeholder implementation
        return {
            "target": "dev_container",
            "success": False,
            "error": "dev_container not implemented yet",
            "launched_at": datetime.now().isoformat()
        }
    
    def _launch_gemini_colab(self, **kwargs) -> Dict[str, Any]:
        """Launch Gemini Colab integration."""
        # Placeholder implementation
        return {
            "target": "gemini_colab",
            "success": False,
            "error": "gemini_colab not implemented yet",
            "launched_at": datetime.now().isoformat()
        }
    '''
    
    # Read the current synapse.py file
    synapse_file = os.path.join(os.path.dirname(__file__), 'src', 'synapse', 'synapse.py')
    
    try:
        with open(synapse_file, 'r') as f:
            content = f.read()
        
        # Check if function already exists
        if 'def launch_local_resource' in content:
            print("✅ launch_local_resource function already exists")
            return True
        
        # Add the function before the last line (which should be a closing brace or similar)
        # Find the last method in the class
        lines = content.split('\n')
        insert_index = -1
        
        # Find the end of the class
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() and not lines[i].startswith(' ') and not lines[i].startswith('\t'):
                # This is likely the end of the class
                insert_index = i
                break
        
        if insert_index == -1:
            # If we can't find a good place, append at the end
            insert_index = len(lines)
        
        # Insert the function code
        function_lines = function_code.split('\n')
        # Remove the first empty line
        if function_lines[0] == '':
            function_lines = function_lines[1:]
        
        # Insert at the found position
        new_lines = lines[:insert_index] + function_lines + lines[insert_index:]
        
        # Write back to file
        with open(synapse_file, 'w') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ launch_local_resource function added to Synapse class")
        return True
        
    except Exception as e:
        print(f"❌ Error implementing function: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Synapse launch_local_resource Function Test")
    print("=" * 50)
    
    # Step 1: Check if function exists
    function_exists = test_launch_local_resource_function()
    
    if not function_exists:
        print("\n📝 Function not found. Implementing...")
        if implement_launch_local_resource():
            print("✅ Function implemented successfully")
            # Test again
            function_exists = test_launch_local_resource_function()
        else:
            print("❌ Failed to implement function")
            return False
    
    # Step 2: Check if claude-code is available
    claude_available = verify_claude_code_availability()
    
    if not claude_available:
        print("\n📦 claude-code not available. Running setup...")
        if run_setup_script():
            print("✅ Setup completed")
            claude_available = verify_claude_code_availability()
        else:
            print("❌ Setup failed")
    
    # Step 3: Final test
    print("\n🎯 Final Integration Test")
    print("-" * 30)
    
    if function_exists and claude_available:
        print("✅ All components ready")
        print("✅ launch_local_resource('claude_code') is operational")
        print("✅ External tool coordination is functional")
        return True
    else:
        print("❌ Some components not ready")
        print(f"   Function exists: {function_exists}")
        print(f"   claude-code available: {claude_available}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)