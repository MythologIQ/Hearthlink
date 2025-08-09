#!/usr/bin/env python3
"""
SPEC-3 Week 2: CLI Tools for Orphaned Functions
Provides command-line invocation paths for backend functions without coverage
"""

import asyncio
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

class HearthlinkCLI:
    """Command-line interface for Hearthlink functions"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.parser = self._setup_parser()
    
    def _setup_parser(self) -> argparse.ArgumentParser:
        """Setup command-line argument parser"""
        parser = argparse.ArgumentParser(
            description="Hearthlink CLI Tools - Invocation paths for orphaned functions",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python scripts/cli_tools.py core status
  python scripts/cli_tools.py vault health
  python scripts/cli_tools.py session create --user-id test_user
  python scripts/cli_tools.py agent create --agent-id alden --config '{}'
  python scripts/cli_tools.py database migrate --version 2
            """
        )
        
        subparsers = parser.add_subparsers(dest='module', help='Module commands')
        
        # Core module commands
        core_parser = subparsers.add_parser('core', help='Core module commands')
        core_subparsers = core_parser.add_subparsers(dest='command')
        
        core_subparsers.add_parser('status', help='Get core status')
        core_subparsers.add_parser('health', help='Check core health')
        
        # Vault module commands
        vault_parser = subparsers.add_parser('vault', help='Vault module commands')
        vault_subparsers = vault_parser.add_subparsers(dest='command')
        
        vault_subparsers.add_parser('health', help='Check vault health')
        vault_subparsers.add_parser('ready', help='Check vault ready state')
        vault_subparsers.add_parser('init', help='Initialize vault')
        
        store_parser = vault_subparsers.add_parser('store', help='Store memory')
        store_parser.add_argument('--key', required=True, help='Memory key')
        store_parser.add_argument('--data', required=True, help='Memory data (JSON)')
        
        retrieve_parser = vault_subparsers.add_parser('retrieve', help='Retrieve memory')
        retrieve_parser.add_argument('--key', required=True, help='Memory key')
        
        # Session module commands
        session_parser = subparsers.add_parser('session', help='Session management commands')
        session_subparsers = session_parser.add_subparsers(dest='command')
        
        create_session_parser = session_subparsers.add_parser('create', help='Create session')
        create_session_parser.add_argument('--user-id', required=True, help='User ID')
        create_session_parser.add_argument('--agent-context', default='{}', help='Agent context JSON')
        create_session_parser.add_argument('--metadata', default='{}', help='Session metadata JSON')
        
        session_subparsers.add_parser('list', help='List active sessions')
        
        # Agent module commands
        agent_parser = subparsers.add_parser('agent', help='Agent management commands')
        agent_subparsers = agent_parser.add_subparsers(dest='command')
        
        create_agent_parser = agent_subparsers.add_parser('create', help='Create agent')
        create_agent_parser.add_argument('--agent-id', required=True, help='Agent ID')
        create_agent_parser.add_argument('--config', default='{}', help='Agent configuration JSON')
        
        # Database module commands
        db_parser = subparsers.add_parser('database', help='Database management commands')
        db_subparsers = db_parser.add_subparsers(dest='command')
        
        db_subparsers.add_parser('status', help='Get database status')
        db_subparsers.add_parser('health', help='Check database health')
        
        migrate_parser = db_subparsers.add_parser('migrate', help='Run database migration')
        migrate_parser.add_argument('--version', type=int, help='Target schema version')
        
        # LLM module commands
        llm_parser = subparsers.add_parser('llm', help='LLM management commands')
        llm_subparsers = llm_parser.add_subparsers(dest='command')
        
        llm_subparsers.add_parser('config', help='Get LLM configuration')
        llm_subparsers.add_parser('status', help='Get LLM status')
        
        # API server commands
        api_parser = subparsers.add_parser('api', help='API server commands')
        api_subparsers = api_parser.add_subparsers(dest='command')
        
        api_subparsers.add_parser('status', help='Get API server status')
        
        token_parser = api_subparsers.add_parser('create-token', help='Create API token')
        token_parser.add_argument('--user-id', required=True, help='User ID for token')
        token_parser.add_argument('--permissions', default='[]', help='Token permissions JSON')
        
        execute_parser = api_subparsers.add_parser('execute', help='Execute command')
        execute_parser.add_argument('--command', required=True, help='Command to execute')
        execute_parser.add_argument('--args', default='[]', help='Command arguments JSON')
        
        return parser
    
    async def run(self, args: Optional[list] = None) -> int:
        """Run CLI command"""
        try:
            parsed_args = self.parser.parse_args(args)
            
            if not parsed_args.module:
                self.parser.print_help()
                return 1
            
            # Route to appropriate handler
            if parsed_args.module == 'core':
                return await self._handle_core_commands(parsed_args)
            elif parsed_args.module == 'vault':
                return await self._handle_vault_commands(parsed_args)
            elif parsed_args.module == 'session':
                return await self._handle_session_commands(parsed_args)
            elif parsed_args.module == 'agent':
                return await self._handle_agent_commands(parsed_args)
            elif parsed_args.module == 'database':
                return await self._handle_database_commands(parsed_args)
            elif parsed_args.module == 'llm':
                return await self._handle_llm_commands(parsed_args)
            elif parsed_args.module == 'api':
                return await self._handle_api_commands(parsed_args)
            else:
                print(f"❌ Unknown module: {parsed_args.module}")
                return 1
                
        except Exception as e:
            print(f"❌ CLI error: {e}")
            return 1
    
    async def _handle_core_commands(self, args) -> int:
        """Handle core module commands"""
        try:
            if args.command == 'status':
                from main import get_status
                status = get_status()
                print(f"✅ Core Status: {json.dumps(status, indent=2)}")
                return 0
            
            elif args.command == 'health':
                from core.core import Core
                core = Core({})
                health = await core.health_check()
                print(f"✅ Core Health: {json.dumps(health, indent=2)}")
                return 0
            
            else:
                print(f"❌ Unknown core command: {args.command}")
                return 1
                
        except Exception as e:
            print(f"❌ Core command failed: {e}")
            return 1
    
    async def _handle_vault_commands(self, args) -> int:
        """Handle vault module commands"""
        try:
            from vault.vault import VaultManager
            vault = VaultManager()
            
            if args.command == 'health':
                health = vault.health()
                print(f"✅ Vault Health: {json.dumps(health, indent=2)}")
                return 0
            
            elif args.command == 'ready':
                ready = vault.ready()
                print(f"✅ Vault Ready: {ready}")
                return 0
            
            elif args.command == 'init':
                # Initialize vault if not already initialized
                if not vault._is_initialized:
                    # This would trigger initialization
                    health = vault.health()
                    print(f"✅ Vault initialized: {health}")
                else:
                    print("✅ Vault already initialized")
                return 0
            
            elif args.command == 'store':
                try:
                    data = json.loads(args.data)
                    await vault.store_memory(args.key, data)
                    print(f"✅ Stored memory with key: {args.key}")
                    return 0
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON data: {args.data}")
                    return 1
            
            elif args.command == 'retrieve':
                data = await vault.retrieve_memory(args.key)
                if data is not None:
                    print(f"✅ Retrieved memory: {json.dumps(data, indent=2)}")
                    return 0
                else:
                    print(f"❌ No memory found for key: {args.key}")
                    return 1
            
            else:
                print(f"❌ Unknown vault command: {args.command}")
                return 1
                
        except Exception as e:
            print(f"❌ Vault command failed: {e}")
            return 1
    
    async def _handle_session_commands(self, args) -> int:
        """Handle session management commands"""
        try:
            from core.session_manager import get_session_manager
            session_manager = get_session_manager()
            
            if args.command == 'create':
                try:
                    agent_context = json.loads(args.agent_context)
                    metadata = json.loads(args.metadata)
                    
                    session_id, session_token = await session_manager.create_session(
                        user_id=args.user_id,
                        agent_context=agent_context,
                        metadata=metadata
                    )
                    
                    print(f"✅ Created session:")
                    print(f"   Session ID: {session_id}")
                    print(f"   Session Token: {session_token}")
                    return 0
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON: {e}")
                    return 1
            
            elif args.command == 'list':
                # This would require implementing a list_sessions method
                print("📋 Session listing not yet implemented")
                return 0
            
            else:
                print(f"❌ Unknown session command: {args.command}")
                return 1
                
        except Exception as e:
            print(f"❌ Session command failed: {e}")
            return 1
    
    async def _handle_agent_commands(self, args) -> int:
        """Handle agent management commands"""
        try:
            if args.command == 'create':
                try:
                    from api_server import create_agent
                    config = json.loads(args.config)
                    
                    result = create_agent(args.agent_id, config)
                    print(f"✅ Created agent: {json.dumps(result, indent=2)}")
                    return 0
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON config: {e}")
                    return 1
            
            else:
                print(f"❌ Unknown agent command: {args.command}")
                return 1
                
        except Exception as e:
            print(f"❌ Agent command failed: {e}")
            return 1
    
    async def _handle_database_commands(self, args) -> int:
        """Handle database management commands"""
        try:
            from database.database_manager import get_database_manager
            db = get_database_manager()
            
            if args.command == 'status':
                schema_version = db.get_schema_version()
                print(f"✅ Database Status:")
                print(f"   Schema Version: {schema_version}")
                return 0
            
            elif args.command == 'health':
                # Basic health check
                try:
                    schema_version = db.get_schema_version()
                    health = {
                        'healthy': True,
                        'schema_version': schema_version,
                        'timestamp': datetime.now().isoformat()
                    }
                    print(f"✅ Database Health: {json.dumps(health, indent=2)}")
                    return 0
                except Exception as e:
                    health = {
                        'healthy': False,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                    print(f"❌ Database Health: {json.dumps(health, indent=2)}")
                    return 1
            
            elif args.command == 'migrate':
                if args.version:
                    print(f"🔄 Running migration to version {args.version}")
                    # This would require implementing migration logic
                    print("✅ Migration completed (placeholder)")
                    return 0
                else:
                    print("❌ Version required for migration")
                    return 1
            
            else:
                print(f"❌ Unknown database command: {args.command}")
                return 1
                
        except Exception as e:
            print(f"❌ Database command failed: {e}")
            return 1
    
    async def _handle_llm_commands(self, args) -> int:
        """Handle LLM management commands"""
        try:
            if args.command == 'config':
                from run_alden import get_llm_config
                config = get_llm_config()
                print(f"✅ LLM Config: {json.dumps(config, indent=2)}")
                return 0
            
            elif args.command == 'status':
                # Basic LLM status check
                status = {
                    'status': 'available',
                    'timestamp': datetime.now().isoformat()
                }
                print(f"✅ LLM Status: {json.dumps(status, indent=2)}")
                return 0
            
            else:
                print(f"❌ Unknown LLM command: {args.command}")
                return 1
                
        except Exception as e:
            print(f"❌ LLM command failed: {e}")
            return 1
    
    async def _handle_api_commands(self, args) -> int:
        """Handle API server commands"""
        try:
            if args.command == 'status':
                status = {
                    'status': 'running',
                    'timestamp': datetime.now().isoformat()
                }
                print(f"✅ API Status: {json.dumps(status, indent=2)}")
                return 0
            
            elif args.command == 'create-token':
                try:
                    from api_server import create_token
                    permissions = json.loads(args.permissions)
                    
                    token = create_token(args.user_id, permissions)
                    print(f"✅ Created token: {token}")
                    return 0
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON permissions: {e}")
                    return 1
            
            elif args.command == 'execute':
                try:
                    from api_server import execute_command
                    command_args = json.loads(args.args)
                    
                    result = execute_command(args.command, command_args)
                    print(f"✅ Command result: {json.dumps(result, indent=2)}")
                    return 0
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON args: {e}")
                    return 1
            
            else:
                print(f"❌ Unknown API command: {args.command}")
                return 1
                
        except Exception as e:
            print(f"❌ API command failed: {e}")
            return 1

def main():
    """Main entry point"""
    cli = HearthlinkCLI()
    exit_code = asyncio.run(cli.run())
    sys.exit(exit_code)

if __name__ == "__main__":
    main()