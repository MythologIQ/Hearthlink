#!/usr/bin/env python3
"""
Alden Runner - Main Entry Point

Launches Alden persona in either CLI or API mode.
Supports configuration from file and command-line arguments.

Usage:
  python run_alden.py cli [options]
  python run_alden.py api [options]

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from main import HearthlinkLogger, HearthlinkError
from personas.alden import create_alden_persona
from api.alden_api import create_alden_api
from cli.alden_cli import create_alden_cli


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dict containing configuration
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "alden_config.json"
    
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_llm_config(config: Dict[str, Any], engine: str, model: str, 
                  url: Optional[str] = None) -> Dict[str, Any]:
    """
    Get LLM configuration for specified engine.
    
    Args:
        config: Full configuration dictionary
        engine: LLM engine name
        model: Model name
        url: Optional custom URL
        
    Returns:
        LLM configuration dictionary
    """
    if engine not in config["llm_engines"]:
        raise ValueError(f"Unknown LLM engine: {engine}")
    
    llm_config = config["llm_engines"][engine].copy()
    
    # Override with command-line arguments
    if model:
        llm_config["model"] = model
    if url:
        llm_config["base_url"] = url
    
    return llm_config


def run_cli(config: Dict[str, Any], llm_config: Dict[str, Any], logger: HearthlinkLogger) -> None:
    """Run Alden in CLI mode."""
    try:
        print("🚀 Starting Alden CLI...")
        cli = create_alden_cli(llm_config, logger)
        cli.run()
    except Exception as e:
        logger.log_error(e, "cli_run_error")
        print(f"❌ Failed to start CLI: {e}")
        sys.exit(1)


def run_api(config: Dict[str, Any], llm_config: Dict[str, Any], logger: HearthlinkLogger) -> None:
    """Run Alden in API mode."""
    try:
        print("🚀 Starting Alden API...")
        api = create_alden_api(llm_config, logger)
        
        api_config = config["api"]
        host = api_config["host"]
        port = api_config["port"]
        debug = api_config["debug"]
        
        print(f"📡 API will be available at: http://{host}:{port}")
        print(f"📚 API documentation: http://{host}:{port}/docs")
        print(f"🔍 ReDoc documentation: http://{host}:{port}/redoc")
        print("Press Ctrl+C to stop the server")
        
        api.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.log_error(e, "api_run_error")
        print(f"❌ Failed to start API: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Alden - Your AI Companion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run CLI with Ollama
  python run_alden.py cli --engine ollama --model llama2
  
  # Run API with LM Studio
  python run_alden.py api --engine lmstudio --url http://localhost:1234 --model local-model
  
  # Run with custom config
  python run_alden.py cli --config my_config.json --engine custom
        """
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='mode', help='Run mode')
    
    # CLI subcommand
    cli_parser = subparsers.add_parser('cli', help='Run in CLI mode')
    cli_parser.add_argument("--engine", default="ollama", 
                           choices=["ollama", "lmstudio", "custom"],
                           help="LLM engine to use")
    cli_parser.add_argument("--url", help="LLM base URL")
    cli_parser.add_argument("--model", help="LLM model name")
    cli_parser.add_argument("--config", help="Configuration file path")
    
    # API subcommand
    api_parser = subparsers.add_parser('api', help='Run in API mode')
    api_parser.add_argument("--engine", default="ollama",
                           choices=["ollama", "lmstudio", "custom"],
                           help="LLM engine to use")
    api_parser.add_argument("--url", help="LLM base URL")
    api_parser.add_argument("--model", help="LLM model name")
    api_parser.add_argument("--config", help="Configuration file path")
    api_parser.add_argument("--host", help="API host to bind to")
    api_parser.add_argument("--port", type=int, help="API port to bind to")
    
    args = parser.parse_args()
    
    if not args.mode:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Initialize logger
        logger = HearthlinkLogger()
        
        # Get LLM configuration
        llm_config = get_llm_config(config, args.engine, args.model, args.url)
        
        # Log startup
        logger.logger.info("Alden runner started", extra={"extra_fields": {
            "event_type": "alden_runner_start",
            "mode": args.mode,
            "engine": args.engine,
            "model": llm_config["model"]
        }})
        
        # Run in specified mode
        if args.mode == "cli":
            run_cli(config, llm_config, logger)
        elif args.mode == "api":
            # Override API config with command-line arguments
            if args.host:
                config["api"]["host"] = args.host
            if args.port:
                config["api"]["port"] = args.port
            
            run_api(config, llm_config, logger)
        
    except FileNotFoundError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 