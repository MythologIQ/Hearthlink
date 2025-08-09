#!/usr/bin/env python3
"""
Claude Code CLI Integration
Provides direct integration with Claude Code CLI for development workflows
"""

import json
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

class ClaudeCodeCLI:
    def __init__(self, cli_path: str = None):
        self.cli_path = cli_path or self._find_claude_code_cli()
        self.session_history = []
        self.current_session = None
        
    def _find_claude_code_cli(self) -> Optional[str]:
        """Try to find Claude Code CLI in common locations"""
        common_paths = [
            '/home/frostwulf/.npm-global/bin/claude',  # Found Claude Code location
            '/usr/local/bin/claude',
            '/usr/bin/claude',
            '~/.local/bin/claude',
            '/usr/local/bin/claude-code',
            '/usr/bin/claude-code',
            '~/.local/bin/claude-code',
            'C:\\Program Files\\Claude Code\\claude-code.exe',
            'C:\\Users\\{}\\AppData\\Local\\Claude Code\\claude-code.exe'.format(os.getenv('USERNAME', '')),
            'claude',      # Try Claude in PATH first
            'claude-code'  # Try claude-code in PATH
        ]
        
        for path in common_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path) and os.access(expanded_path, os.X_OK):
                return expanded_path
        
        return None
    
    def is_available(self) -> bool:
        """Check if Claude Code CLI is available"""
        if not self.cli_path:
            return False
        
        try:
            result = subprocess.run(
                [self.cli_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def get_version(self) -> Optional[str]:
        """Get Claude Code CLI version"""
        if not self.is_available():
            return None
        
        try:
            result = subprocess.run(
                [self.cli_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        
        return None
    
    def start_session(self, project_path: str = None) -> bool:
        """Start a new Claude Code session"""
        self.current_session = {
            'id': f'session_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'project_path': project_path or os.getcwd(),
            'started_at': datetime.now(),
            'commands': []
        }
        return True
    
    def execute_command(self, command: str, context: Dict = None) -> Dict:
        """Execute a command through Claude Code CLI"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Claude Code CLI not available',
                'output': ''
            }
        
        try:
            # Create temporary file for context if provided
            context_file = None
            if context:
                context_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                json.dump(context, context_file)
                context_file.close()
            
            # Build command arguments
            cmd_args = [self.cli_path]
            
            # Add context file if provided
            if context_file:
                cmd_args.extend(['--context-file', context_file.name])
            
            # Add the command
            cmd_args.append(command)
            
            # Execute command
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.current_session['project_path'] if self.current_session else None
            )
            
            # Clean up temp file
            if context_file:
                os.unlink(context_file.name)
            
            command_result = {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode,
                'command': command,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add to session history
            if self.current_session:
                self.current_session['commands'].append(command_result)
            
            self.session_history.append(command_result)
            
            return command_result
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Command timed out',
                'output': '',
                'command': command,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'command': command,
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_code(self, file_path: str, analysis_type: str = 'general') -> Dict:
        """Analyze code using Claude Code"""
        context = {
            'file_path': file_path,
            'analysis_type': analysis_type,
            'project_root': self.current_session['project_path'] if self.current_session else os.getcwd()
        }
        
        command = f"analyze {file_path} --type {analysis_type}"
        return self.execute_command(command, context)
    
    def generate_code(self, prompt: str, file_path: str = None, language: str = None) -> Dict:
        """Generate code using Claude Code"""
        context = {
            'prompt': prompt,
            'file_path': file_path,
            'language': language,
            'project_root': self.current_session['project_path'] if self.current_session else os.getcwd()
        }
        
        command = f"generate --prompt '{prompt}'"
        if file_path:
            command += f" --file {file_path}"
        if language:
            command += f" --language {language}"
        
        return self.execute_command(command, context)
    
    def refactor_code(self, file_path: str, refactor_type: str, target: str = None) -> Dict:
        """Refactor code using Claude Code"""
        context = {
            'file_path': file_path,
            'refactor_type': refactor_type,
            'target': target,
            'project_root': self.current_session['project_path'] if self.current_session else os.getcwd()
        }
        
        command = f"refactor {file_path} --type {refactor_type}"
        if target:
            command += f" --target {target}"
        
        return self.execute_command(command, context)
    
    def explain_code(self, file_path: str, line_range: str = None) -> Dict:
        """Explain code using Claude Code"""
        context = {
            'file_path': file_path,
            'line_range': line_range,
            'project_root': self.current_session['project_path'] if self.current_session else os.getcwd()
        }
        
        command = f"explain {file_path}"
        if line_range:
            command += f" --lines {line_range}"
        
        return self.execute_command(command, context)
    
    def debug_code(self, file_path: str, error_message: str = None) -> Dict:
        """Debug code using Claude Code"""
        context = {
            'file_path': file_path,
            'error_message': error_message,
            'project_root': self.current_session['project_path'] if self.current_session else os.getcwd()
        }
        
        command = f"debug {file_path}"
        if error_message:
            command += f" --error '{error_message}'"
        
        return self.execute_command(command, context)
    
    def get_session_history(self) -> List[Dict]:
        """Get session command history"""
        return self.session_history
    
    def get_current_session(self) -> Optional[Dict]:
        """Get current session info"""
        return self.current_session
    
    def end_session(self) -> Dict:
        """End current session"""
        if self.current_session:
            self.current_session['ended_at'] = datetime.now()
            session_summary = {
                'session_id': self.current_session['id'],
                'duration': (self.current_session['ended_at'] - self.current_session['started_at']).total_seconds(),
                'commands_executed': len(self.current_session['commands']),
                'successful_commands': sum(1 for cmd in self.current_session['commands'] if cmd['success'])
            }
            
            # Archive session
            archived_session = self.current_session.copy()
            self.current_session = None
            
            return {
                'success': True,
                'session_summary': session_summary,
                'archived_session': archived_session
            }
        
        return {'success': False, 'error': 'No active session'}
    
    def get_available_commands(self) -> List[str]:
        """Get list of available Claude Code commands"""
        if not self.is_available():
            return []
        
        try:
            result = subprocess.run(
                [self.cli_path, '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse help output to extract commands
                # This is a simplified parser - actual implementation would be more robust
                lines = result.stdout.split('\n')
                commands = []
                in_commands_section = False
                
                for line in lines:
                    if 'Commands:' in line or 'Available commands:' in line:
                        in_commands_section = True
                        continue
                    
                    if in_commands_section and line.strip():
                        if line.startswith('  '):
                            command = line.strip().split()[0]
                            commands.append(command)
                        elif not line.startswith(' '):
                            break
                
                return commands
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        
        # Return common commands if help parsing fails
        return ['analyze', 'generate', 'refactor', 'explain', 'debug', 'test', 'format']
    
    def get_status(self) -> Dict:
        """Get Claude Code CLI status"""
        return {
            'available': self.is_available(),
            'cli_path': self.cli_path,
            'version': self.get_version(),
            'current_session': self.current_session is not None,
            'session_commands': len(self.session_history),
            'available_commands': self.get_available_commands()
        }

# Global Claude Code CLI instance
claude_code_cli = ClaudeCodeCLI()

def initialize_claude_code_cli(cli_path: str = None) -> bool:
    """Initialize Claude Code CLI integration"""
    global claude_code_cli
    
    print("Initializing Claude Code CLI integration...")
    
    if cli_path:
        claude_code_cli.cli_path = cli_path
    
    status = claude_code_cli.get_status()
    
    if status['available']:
        print(f"✓ Claude Code CLI found: {status['cli_path']}")
        print(f"  Version: {status['version']}")
        print(f"  Available commands: {', '.join(status['available_commands'])}")
        return True
    else:
        print("✗ Claude Code CLI not found")
        print("  Please install Claude Code CLI or provide the correct path")
        print("  Common locations:")
        print("    - /usr/local/bin/claude-code")
        print("    - ~/.local/bin/claude-code")
        print("    - C:\\Program Files\\Claude Code\\claude-code.exe")
        return False

if __name__ == '__main__':
    # Test the CLI integration
    success = initialize_claude_code_cli()
    
    if success:
        print("\nTesting Claude Code CLI...")
        
        # Start a session
        claude_code_cli.start_session()
        
        # Test a simple command
        result = claude_code_cli.execute_command('--version')
        print(f"Test command result: {result}")
        
        # End session
        session_summary = claude_code_cli.end_session()
        print(f"Session summary: {session_summary}")
    else:
        print("\nClaude Code CLI integration not available")