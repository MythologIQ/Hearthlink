#!/usr/bin/env python3
"""
Alden CLI Interface

Command-line interface for Alden persona interactions.
Provides interactive chat, memory management, and configuration commands.

References:
- hearthlink_system_documentation_master.md: CLI requirements and user experience
- PLATINUM_BLOCKERS.md: Security and usability requirements

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import json
import uuid
import argparse
import readline
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import HearthlinkLogger, HearthlinkError
from personas.alden import AldenPersona, PersonaError, create_alden_persona
from llm.local_llm_client import LLMError


class AldenCLI:
    """
    Command-line interface for Alden persona.
    
    Provides interactive chat, memory management, and configuration
    capabilities through a user-friendly terminal interface.
    """
    
    def __init__(self, alden_persona: AldenPersona, logger: Optional[HearthlinkLogger] = None):
        """
        Initialize Alden CLI.
        
        Args:
            alden_persona: Configured Alden persona instance
            logger: Optional logger instance
        """
        self.alden = alden_persona
        self.logger = logger or HearthlinkLogger()
        self.session_id = str(uuid.uuid4())
        self.running = False
        
        # Command history
        self.command_history = []
        
        # Available commands
        self.commands = {
            'help': self._cmd_help,
            'status': self._cmd_status,
            'traits': self._cmd_traits,
            'correction': self._cmd_correction,
            'mood': self._cmd_mood,
            'export': self._cmd_export,
            'quit': self._cmd_quit,
            'exit': self._cmd_quit,
            'clear': self._cmd_clear
        }
        
        self.logger.logger.info("Alden CLI initialized successfully", 
                              extra={"extra_fields": {
                                  "event_type": "alden_cli_init",
                                  "session_id": self.session_id
                              }})
    
    def _print_banner(self) -> None:
        """Print Alden CLI banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    Alden — Your AI Companion                 ║
║                                                              ║
║  Type your message to chat with Alden, or use commands:     ║
║  • /help     - Show available commands                      ║
║  • /status   - Show Alden's current status                  ║
║  • /traits   - View or modify Alden's personality traits    ║
║  • /correction - Add learning feedback for Alden            ║
║  • /mood     - Record your current mood                     ║
║  • /export   - Export Alden's memory data                   ║
║  • /quit     - Exit the CLI                                 ║
║                                                              ║
║  Session ID: {session_id}                                    ║
╚══════════════════════════════════════════════════════════════╝
""".format(session_id=self.session_id[:8])
        
        print(banner)
    
    def _print_prompt(self) -> None:
        """Print input prompt."""
        print("\n💬 You: ", end="", flush=True)
    
    def _print_alden_response(self, response: str) -> None:
        """Print Alden's response with formatting."""
        print(f"\n🤖 Alden: {response}")
        print("-" * 80)
    
    def _print_error(self, message: str) -> None:
        """Print error message with formatting."""
        print(f"\n❌ Error: {message}")
        print("-" * 80)
    
    def _print_success(self, message: str) -> None:
        """Print success message with formatting."""
        print(f"\n✅ {message}")
        print("-" * 80)
    
    def _cmd_help(self, args: List[str]) -> None:
        """Show available commands."""
        help_text = """
Available Commands:
  /help                    - Show this help message
  /status                  - Show Alden's current status and health
  /traits                  - View current personality traits
  /traits <trait> <value>  - Update a trait (0-100)
  /correction <type> <desc> - Add learning feedback (positive/negative)
  /mood <mood> <score>     - Record mood (positive/neutral/negative, 0-100)
  /export [filename]       - Export memory data to file
  /clear                   - Clear the screen
  /quit, /exit            - Exit the CLI

Examples:
  /traits openness 85
  /correction positive "Great response to my question about productivity"
  /mood positive 85
  /export my_alden_data.json
"""
        print(help_text)
    
    def _cmd_status(self, args: List[str]) -> None:
        """Show Alden's current status."""
        try:
            status = self.alden.get_status()
            
            print("\n📊 Alden Status:")
            print(f"  Persona ID: {status['persona_id']}")
            print(f"  User ID: {status['user_id']}")
            print(f"  Schema Version: {status['schema_version']}")
            print(f"  Timestamp: {status['timestamp']}")
            
            print("\n🧠 Personality Traits:")
            for trait, value in status['traits'].items():
                print(f"  {trait.capitalize()}: {value}/100")
            
            print(f"\n💡 Behavioral Metrics:")
            print(f"  Motivation Style: {status['motivation_style']}")
            print(f"  Trust Level: {status['trust_level']:.2f}")
            print(f"  Learning Agility: {status['learning_agility']:.1f}/10")
            print(f"  Reflective Capacity: {status['reflective_capacity']}/20")
            print(f"  Engagement: {status['engagement']}/20")
            
            print(f"\n📈 Statistics:")
            for stat, value in status['stats'].items():
                print(f"  {stat.replace('_', ' ').title()}: {value}")
            
            print(f"\n🔗 LLM Status:")
            llm_status = status['llm_status']
            print(f"  Engine: {llm_status.get('engine', 'unknown')}")
            print(f"  Model: {llm_status.get('model', 'unknown')}")
            print(f"  Connected: {llm_status.get('connected', False)}")
            
        except Exception as e:
            self._print_error(f"Failed to get status: {str(e)}")
    
    def _cmd_traits(self, args: List[str]) -> None:
        """View or modify Alden's personality traits."""
        try:
            if len(args) == 0:
                # Show current traits
                status = self.alden.get_status()
                print("\n🧠 Current Personality Traits:")
                for trait, value in status['traits'].items():
                    print(f"  {trait.capitalize()}: {value}/100")
                
                print("\nTo modify a trait: /traits <trait_name> <value>")
                print("Example: /traits openness 85")
                
            elif len(args) == 2:
                # Update trait
                trait_name = args[0].lower()
                try:
                    new_value = int(args[1])
                except ValueError:
                    self._print_error("Trait value must be a number between 0 and 100")
                    return
                
                if not 0 <= new_value <= 100:
                    self._print_error("Trait value must be between 0 and 100")
                    return
                
                self.alden.update_trait(trait_name, new_value, "cli_update")
                self._print_success(f"Updated {trait_name} to {new_value}")
                
            else:
                self._print_error("Usage: /traits [trait_name value]")
                
        except Exception as e:
            self._print_error(f"Failed to handle traits command: {str(e)}")
    
    def _cmd_correction(self, args: List[str]) -> None:
        """Add learning feedback for Alden."""
        try:
            if len(args) < 2:
                self._print_error("Usage: /correction <type> <description>")
                self._print_error("Type must be 'positive' or 'negative'")
                return
            
            event_type = args[0].lower()
            if event_type not in ["positive", "negative"]:
                self._print_error("Correction type must be 'positive' or 'negative'")
                return
            
            description = " ".join(args[1:])
            if not description.strip():
                self._print_error("Description cannot be empty")
                return
            
            # Determine impact score based on type
            impact_score = 0.5 if event_type == "positive" else -0.3
            
            self.alden.add_correction_event(
                event_type=event_type,
                description=description,
                impact_score=impact_score,
                context={"source": "cli"}
            )
            
            self._print_success(f"Added {event_type} correction: {description}")
            
        except Exception as e:
            self._print_error(f"Failed to add correction: {str(e)}")
    
    def _cmd_mood(self, args: List[str]) -> None:
        """Record current mood."""
        try:
            if len(args) != 2:
                self._print_error("Usage: /mood <mood> <score>")
                self._print_error("Mood: positive, neutral, or negative")
                self._print_error("Score: 0-100")
                return
            
            mood = args[0].lower()
            if mood not in ["positive", "neutral", "negative"]:
                self._print_error("Mood must be 'positive', 'neutral', or 'negative'")
                return
            
            try:
                score = int(args[1])
            except ValueError:
                self._print_error("Score must be a number between 0 and 100")
                return
            
            if not 0 <= score <= 100:
                self._print_error("Score must be between 0 and 100")
                return
            
            self.alden.record_session_mood(
                session_id=self.session_id,
                mood=mood,
                score=score,
                context={"source": "cli"}
            )
            
            self._print_success(f"Recorded mood: {mood} (score: {score})")
            
        except Exception as e:
            self._print_error(f"Failed to record mood: {str(e)}")
    
    def _cmd_export(self, args: List[str]) -> None:
        """Export Alden's memory data."""
        try:
            filename = args[0] if args else f"alden_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Ensure .json extension
            if not filename.endswith('.json'):
                filename += '.json'
            
            memory_data = self.alden.export_memory()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
            
            self._print_success(f"Memory exported to {filename}")
            
        except Exception as e:
            self._print_error(f"Failed to export memory: {str(e)}")
    
    def _cmd_quit(self, args: List[str]) -> None:
        """Exit the CLI."""
        self._print_success("Goodbye! Thank you for chatting with Alden.")
        self.running = False
    
    def _cmd_clear(self, args: List[str]) -> None:
        """Clear the screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        self._print_banner()
    
    def _process_input(self, user_input: str) -> None:
        """Process user input and execute appropriate action."""
        try:
            user_input = user_input.strip()
            if not user_input:
                return
            
            # Add to command history
            self.command_history.append(user_input)
            
            # Check if it's a command
            if user_input.startswith('/'):
                parts = user_input[1:].split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if command in self.commands:
                    self.commands[command](args)
                else:
                    self._print_error(f"Unknown command: {command}")
                    print("Type /help for available commands")
            else:
                # Regular message - send to Alden
                self._print_prompt()
                print(user_input)  # Echo the input
                
                response = self.alden.generate_response(
                    user_message=user_input,
                    session_id=self.session_id,
                    context={"source": "cli"}
                )
                
                self._print_alden_response(response)
                
        except Exception as e:
            self.logger.log_error(e, "cli_input_processing", {
                "user_input": user_input[:100],  # Truncate for logging
                "session_id": self.session_id
            })
            self._print_error(f"Failed to process input: {str(e)}")
    
    def run(self) -> None:
        """Run the interactive CLI."""
        try:
            self.running = True
            self._print_banner()
            
            # Configure readline for better input experience
            try:
                readline.parse_and_bind("tab: complete")
                readline.set_completer(self._completer)
            except:
                pass  # readline not available on all systems
            
            while self.running:
                try:
                    self._print_prompt()
                    user_input = input().strip()
                    
                    if user_input:
                        self._process_input(user_input)
                        
                except KeyboardInterrupt:
                    print("\n\nUse /quit to exit gracefully")
                except EOFError:
                    self._cmd_quit([])
                    break
                    
        except Exception as e:
            self.logger.log_error(e, "cli_run_error", {
                "session_id": self.session_id
            })
            self._print_error(f"CLI error: {str(e)}")
    
    def _completer(self, text: str, state: int) -> Optional[str]:
        """Command completion for readline."""
        commands = [cmd for cmd in self.commands.keys() if cmd.startswith(text)]
        if state < len(commands):
            return commands[state]
        return None


def create_alden_cli(llm_config: Dict[str, Any], logger: Optional[HearthlinkLogger] = None) -> AldenCLI:
    """
    Factory function to create Alden CLI with persona.
    
    Args:
        llm_config: LLM configuration dictionary
        logger: Optional logger instance
        
    Returns:
        AldenCLI: Configured Alden CLI instance
        
    Raises:
        PersonaError: If CLI creation fails
    """
    try:
        alden_persona = create_alden_persona(llm_config, logger)
        return AldenCLI(alden_persona, logger)
    except Exception as e:
        raise PersonaError(f"Failed to create Alden CLI: {str(e)}") from e


def main():
    """Main entry point for Alden CLI."""
    parser = argparse.ArgumentParser(
        description="Alden CLI - Interactive AI Companion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python alden_cli.py --engine ollama --model llama2
  python alden_cli.py --engine lmstudio --url http://localhost:1234 --model local-model
        """
    )
    
    parser.add_argument("--engine", default="ollama", 
                       choices=["ollama", "lmstudio", "custom"],
                       help="LLM engine to use")
    parser.add_argument("--url", default="http://localhost:11434",
                       help="LLM base URL")
    parser.add_argument("--model", default="llama2",
                       help="LLM model name")
    parser.add_argument("--timeout", type=int, default=30,
                       help="Request timeout in seconds")
    parser.add_argument("--temperature", type=float, default=0.7,
                       help="LLM temperature (0.0-1.0)")
    parser.add_argument("--max-tokens", type=int, default=2048,
                       help="Maximum tokens per response")
    
    args = parser.parse_args()
    
    # Create LLM configuration
    llm_config = {
        "engine": args.engine,
        "base_url": args.url,
        "model": args.model,
        "timeout": args.timeout,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens
    }
    
    try:
        # Create and run CLI
        cli = create_alden_cli(llm_config)
        cli.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"Failed to start Alden CLI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 