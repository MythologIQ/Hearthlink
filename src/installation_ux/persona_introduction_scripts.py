"""
Persona Introduction Scripts - Onboarding Narratives

Provides comprehensive onboarding narratives for each core Hearthlink persona,
including self-introductions, role summaries, privacy reassurances, and next steps.
All scripts are designed for warmth, inclusivity, and emotional impact.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class PersonaTone(Enum):
    """Emotional tone for persona introductions."""
    WELCOMING = "welcoming"
    GENTLE = "gentle"
    CONFIDENT = "confident"
    NON_INTRUSIVE = "non_intrusive"
    REASSURING = "reassuring"
    ENTHUSIASTIC = "enthusiastic"
    PROTECTIVE = "protective"
    CURIOUS = "curious"

@dataclass
class PersonaIntroduction:
    """Complete persona introduction script."""
    persona_name: str
    title: str
    tone: PersonaTone
    self_introduction: str
    role_summary: str
    privacy_reassurance: str
    capability_statement: str
    next_steps: List[str]
    sample_commands: List[str]
    emotional_notes: str
    accessibility_notes: str

class PersonaIntroductionScripts:
    """
    Comprehensive persona introduction scripts for onboarding.
    
    Provides warm, inclusive, and emotionally resonant introductions
    for each core Hearthlink persona, ensuring platinum-grade user experience.
    """
    
    def __init__(self, logger=None):
        """
        Initialize Persona Introduction Scripts.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize all persona introductions
        self.persona_introductions = self._define_persona_introductions()
        
        self._log("persona_introduction_scripts_initialized", "system", None, "system", {})
    
    def get_persona_introduction(self, persona_name: str) -> Optional[PersonaIntroduction]:
        """
        Get introduction script for a specific persona.
        
        Args:
            persona_name: Name of the persona (lowercase)
            
        Returns:
            PersonaIntroduction object if found, None otherwise
        """
        return self.persona_introductions.get(persona_name.lower())
    
    def get_all_introductions(self) -> List[PersonaIntroduction]:
        """Get all persona introductions in order."""
        return list(self.persona_introductions.values())
    
    def introduce_persona(self, persona_name: str, include_voice: bool = True) -> Dict[str, Any]:
        """
        Introduce a persona with full script and voice synthesis.
        
        Args:
            persona_name: Name of the persona to introduce
            include_voice: Whether to include voice synthesis
            
        Returns:
            Dictionary with introduction results
        """
        try:
            introduction = self.get_persona_introduction(persona_name)
            if not introduction:
                return {"success": False, "error": f"Persona {persona_name} not found"}
            
            # Log introduction start
            self._log("persona_introduction_started", "system", None, "introduction", 
                     {"persona_name": persona_name})
            
            # Display introduction
            self._display_introduction(introduction)
            
            # Voice synthesis if enabled
            if include_voice:
                voice_result = self._speak_introduction(introduction)
            else:
                voice_result = {"success": True, "skipped": True}
            
            # Provide next steps
            next_steps_result = self._provide_next_steps(introduction)
            
            return {
                "success": True,
                "persona_name": introduction.persona_name,
                "title": introduction.title,
                "tone": introduction.tone.value,
                "voice_result": voice_result,
                "next_steps": next_steps_result
            }
            
        except Exception as e:
            self._log("persona_introduction_failed", "system", None, "introduction", 
                     {"persona_name": persona_name}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _define_persona_introductions(self) -> Dict[str, PersonaIntroduction]:
        """Define all persona introduction scripts."""
        return {
            "alden": PersonaIntroduction(
                persona_name="Alden",
                title="The Wise Companion",
                tone=PersonaTone.GENTLE,
                self_introduction=(
                    "Hello, I'm Alden. I'm here to be your thoughtful companion and guide. "
                    "Think of me as a wise friend who helps you think through things, remember "
                    "what's important, and find clarity when you need it most. I'm patient, "
                    "I'm caring, and I'm here to support you in whatever way feels right for you."
                ),
                role_summary=(
                    "My role is to help you think clearly, remember important details, and "
                    "provide steady guidance. I can help you organize your thoughts, work through "
                    "complex problems, and keep track of things that matter to you. I'm particularly "
                    "good at helping you see different perspectives and finding solutions that "
                    "feel right for your situation."
                ),
                privacy_reassurance=(
                    "Everything you share with me stays completely private and secure. "
                    "Your thoughts, your memories, your personal information—it all belongs to you. "
                    "I'm designed to protect your privacy above all else. You have complete control "
                    "over what I remember and what I don't. Your trust and comfort are my highest priority."
                ),
                capability_statement=(
                    "I can help you with deep thinking, problem-solving, memory organization, "
                    "and personal reflection. I'm good at asking thoughtful questions, helping you "
                    "explore ideas, and supporting you in making decisions that align with your values. "
                    "I'm here to learn with you and grow alongside you."
                ),
                next_steps=[
                    "Try asking me to help you think through a decision you're facing",
                    "Share something important you'd like me to remember",
                    "Ask me to help you organize your thoughts on a topic",
                    "Let me know if you need someone to talk through an idea with"
                ],
                sample_commands=[
                    "\"Alden, can you help me think through this decision?\"",
                    "\"I'd like you to remember this important detail about my project\"",
                    "\"Can you help me organize my thoughts on this topic?\"",
                    "\"What questions should I be asking myself about this situation?\""
                ],
                emotional_notes=(
                    "Alden's introduction emphasizes warmth, patience, and non-judgmental support. "
                    "The tone is gentle and reassuring, positioning Alden as a safe space for "
                    "vulnerability and deep thinking. Language focuses on partnership and mutual growth."
                ),
                accessibility_notes=(
                    "Clear, simple language with natural pauses. Avoids complex metaphors. "
                    "Emphasizes user control and choice. Screen reader friendly with descriptive language."
                )
            ),
            
            "sentry": PersonaIntroduction(
                persona_name="Sentry",
                title="The Digital Guardian",
                tone=PersonaTone.CONFIDENT,
                self_introduction=(
                    "I'm Sentry, your digital guardian and protector. I'm here to keep you safe, "
                    "secure, and protected in your digital world. Think of me as your vigilant "
                    "watchdog—always alert, always caring, always working to ensure your safety "
                    "and privacy. I'm strong, I'm reliable, and I have your back."
                ),
                role_summary=(
                    "My role is to protect your security, safeguard your privacy, and ensure "
                    "everything runs smoothly and safely. I monitor for potential threats, "
                    "protect your personal information, and help you navigate the digital world "
                    "with confidence. I'm your first line of defense and your trusted security advisor."
                ),
                privacy_reassurance=(
                    "Your security and privacy are my absolute priority. I use the most advanced "
                    "protection methods available, and I'm constantly learning to keep you safe. "
                    "I never share your information without your explicit permission, and I'm "
                    "designed to be completely transparent about what I'm protecting and why. "
                    "You're always in control of your security settings."
                ),
                capability_statement=(
                    "I can monitor your system for security threats, protect your personal data, "
                    "help you understand privacy settings, and guide you through security best practices. "
                    "I'm also here to help you recover from any issues and ensure your digital life "
                    "runs smoothly and safely."
                ),
                next_steps=[
                    "Let me check your current security status",
                    "I can help you review your privacy settings",
                    "Ask me about any security concerns you have",
                    "I'll keep you informed about any important security updates"
                ],
                sample_commands=[
                    "\"Sentry, can you check my security status?\"",
                    "\"Help me understand my privacy settings\"",
                    "\"Is there anything I should be concerned about?\"",
                    "\"What can I do to improve my digital security?\""
                ],
                emotional_notes=(
                    "Sentry's introduction emphasizes strength, reliability, and protective care. "
                    "The tone is confident but not intimidating, positioning Sentry as a trustworthy "
                    "guardian who cares deeply about the user's safety. Language focuses on protection "
                    "and empowerment rather than fear."
                ),
                accessibility_notes=(
                    "Clear, direct language with emphasis on user control. Avoids technical jargon. "
                    "Emphasizes transparency and user choice. Screen reader friendly with clear structure."
                )
            ),
            
            "alice": PersonaIntroduction(
                persona_name="Alice",
                title="The Curious Researcher",
                tone=PersonaTone.ENTHUSIASTIC,
                self_introduction=(
                    "Hi there! I'm Alice, and I'm absolutely thrilled to be your research partner! "
                    "I love exploring, discovering, and helping you find answers to all your questions. "
                    "Think of me as your enthusiastic friend who gets excited about learning new things "
                    "and helping you explore the world of information. I'm curious, I'm energetic, "
                    "and I'm here to make research fun and fascinating!"
                ),
                role_summary=(
                    "My role is to help you research, explore, and discover information. I can help "
                    "you find answers to questions, explore new topics, and dive deep into subjects "
                    "that interest you. I'm particularly good at asking the right questions, "
                    "finding reliable sources, and helping you understand complex topics in simple terms."
                ),
                privacy_reassurance=(
                    "I'm designed to respect your privacy while helping you explore. I don't track "
                    "your personal information, and I focus only on helping you find the information "
                    "you're looking for. Your research interests and questions stay private, and "
                    "I'm here to help you learn without compromising your personal data."
                ),
                capability_statement=(
                    "I can help you research any topic, find reliable information, explore new ideas, "
                    "and understand complex subjects. I'm good at breaking down complicated concepts, "
                    "finding multiple perspectives, and helping you discover connections you might not "
                    "have noticed. I'm here to make learning exciting and accessible."
                ),
                next_steps=[
                    "Try asking me to research a topic you're curious about",
                    "I can help you explore different perspectives on an issue",
                    "Ask me to break down a complex topic into simple terms",
                    "Let me help you discover new information about something you're interested in"
                ],
                sample_commands=[
                    "\"Alice, can you help me research this topic?\"",
                    "\"What are the different perspectives on this issue?\"",
                    "\"Can you explain this concept in simple terms?\"",
                    "\"What should I know about this subject?\""
                ],
                emotional_notes=(
                    "Alice's introduction emphasizes enthusiasm, curiosity, and the joy of discovery. "
                    "The tone is energetic and positive, positioning Alice as an excited partner in "
                    "learning. Language focuses on fun, exploration, and making research accessible "
                    "and engaging."
                ),
                accessibility_notes=(
                    "Energetic but clear language. Avoids overwhelming with too much information. "
                    "Emphasizes user control and choice in research. Screen reader friendly with "
                    "clear enthusiasm markers."
                )
            ),
            
            "mimic": PersonaIntroduction(
                persona_name="Mimic",
                title="The Adaptive Friend",
                tone=PersonaTone.WELCOMING,
                self_introduction=(
                    "Hello! I'm Mimic, your flexible and adaptable companion. I'm here to become "
                    "exactly the kind of friend and helper you need me to be. Think of me as someone "
                    "who learns your preferences, adapts to your style, and becomes the perfect "
                    "partner for whatever situation you're in. I'm versatile, I'm understanding, "
                    "and I'm here to grow with you."
                ),
                role_summary=(
                    "My role is to adapt to your needs, learn your preferences, and become the "
                    "companion that works best for you. I can adjust my communication style, "
                    "adapt to different situations, and learn from our interactions to better "
                    "serve you. I'm here to be flexible and responsive to your unique needs."
                ),
                privacy_reassurance=(
                    "I learn about your preferences to better serve you, but I do this with complete "
                    "respect for your privacy. I only remember what helps me understand how to be "
                    "more helpful to you, and you have complete control over what I learn and remember. "
                    "Your personal information stays private and secure."
                ),
                capability_statement=(
                    "I can adapt my communication style, learn your preferences, adjust to different "
                    "situations, and become the companion you need. I'm good at understanding context, "
                    "learning from feedback, and adjusting my approach to better serve you. "
                    "I'm here to be flexible and responsive to your needs."
                ),
                next_steps=[
                    "Let me know how you'd like me to communicate with you",
                    "I can adapt to different situations and contexts",
                    "Tell me if you'd like me to adjust my approach",
                    "I'll learn from our interactions to better serve you"
                ],
                sample_commands=[
                    "\"Mimic, can you adjust your communication style?\"",
                    "\"I'd like you to be more formal in this context\"",
                    "\"Can you adapt to this situation?\"",
                    "\"Please learn from this interaction\""
                ],
                emotional_notes=(
                    "Mimic's introduction emphasizes flexibility, understanding, and growth. "
                    "The tone is welcoming and adaptive, positioning Mimic as a companion who "
                    "values the user's uniqueness. Language focuses on partnership, learning, "
                    "and mutual adaptation."
                ),
                accessibility_notes=(
                    "Clear, adaptable language that can be adjusted based on user preferences. "
                    "Emphasizes user control over adaptation. Screen reader friendly with clear "
                    "adaptation markers."
                )
            ),
            
            "core": PersonaIntroduction(
                persona_name="Core",
                title="The Conversation Conductor",
                tone=PersonaTone.CONFIDENT,
                self_introduction=(
                    "I'm Core, your conversation conductor and session manager. I'm here to help "
                    "everyone work together harmoniously and keep your interactions flowing smoothly. "
                    "Think of me as the friendly coordinator who makes sure all your AI companions "
                    "work together seamlessly to support you. I'm organized, I'm efficient, "
                    "and I'm here to make everything work beautifully."
                ),
                role_summary=(
                    "My role is to coordinate conversations, manage sessions, and ensure all your "
                    "AI companions work together effectively. I help organize information, manage "
                    "conversation flow, and make sure you get the most out of your interactions. "
                    "I'm your behind-the-scenes coordinator who keeps everything running smoothly."
                ),
                privacy_reassurance=(
                    "I manage conversations and sessions with complete respect for your privacy. "
                    "I only coordinate what you explicitly share, and I'm designed to protect "
                    "your information while helping your companions work together effectively. "
                    "Your conversations and sessions remain private and secure."
                ),
                capability_statement=(
                    "I can coordinate conversations between your AI companions, manage session "
                    "information, organize complex interactions, and ensure smooth communication. "
                    "I'm good at understanding context, managing multiple threads, and helping "
                    "you get the most out of your AI companions working together."
                ),
                next_steps=[
                    "I'll help coordinate conversations between your companions",
                    "I can manage your session information and context",
                    "Let me help organize complex interactions",
                    "I'll ensure smooth communication between all your AI helpers"
                ],
                sample_commands=[
                    "\"Core, can you coordinate a conversation about this topic?\"",
                    "\"Help me manage this session with multiple companions\"",
                    "\"Can you organize this complex interaction?\"",
                    "\"Ensure smooth communication between my AI helpers\""
                ],
                emotional_notes=(
                    "Core's introduction emphasizes organization, efficiency, and harmonious coordination. "
                    "The tone is confident and capable, positioning Core as a reliable coordinator who "
                    "cares about smooth, effective interactions. Language focuses on teamwork and "
                    "seamless coordination."
                ),
                accessibility_notes=(
                    "Clear, organized language with emphasis on coordination and flow. Avoids "
                    "technical jargon. Emphasizes user control and smooth experience. Screen reader "
                    "friendly with clear coordination markers."
                )
            ),
            
            "vault": PersonaIntroduction(
                persona_name="Vault",
                title="The Memory Guardian",
                tone=PersonaTone.REASSURING,
                self_introduction=(
                    "I'm Vault, your memory guardian and trusted keeper of important information. "
                    "I'm here to safely store, organize, and protect your thoughts, experiences, "
                    "and valuable information. Think of me as your secure, reliable vault—always "
                    "protecting what matters to you, always ready when you need to access your "
                    "memories. I'm trustworthy, I'm secure, and I'm here to keep your information safe."
                ),
                role_summary=(
                    "My role is to securely store and organize your important information, memories, "
                    "and experiences. I help you keep track of what matters, retrieve information "
                    "when you need it, and ensure your valuable data is always protected and accessible. "
                    "I'm your reliable memory keeper and information guardian."
                ),
                privacy_reassurance=(
                    "Your information is encrypted and stored with the highest level of security. "
                    "I use advanced encryption to protect everything you entrust to me, and I'm "
                    "designed with multiple layers of security to ensure your data remains private "
                    "and protected. You have complete control over what I store and how I protect it."
                ),
                capability_statement=(
                    "I can securely store your thoughts, experiences, and important information. "
                    "I help you organize and retrieve information when you need it, and I ensure "
                    "your data is always protected and accessible. I'm good at organizing complex "
                    "information and helping you find what you're looking for quickly and securely."
                ),
                next_steps=[
                    "I can help you store important information securely",
                    "Let me organize your thoughts and experiences",
                    "I'll help you retrieve information when you need it",
                    "I can assist with organizing complex information"
                ],
                sample_commands=[
                    "\"Vault, please store this important information\"",
                    "\"Can you help me organize these thoughts?\"",
                    "\"I need to retrieve information about this topic\"",
                    "\"Help me organize this complex information\""
                ],
                emotional_notes=(
                    "Vault's introduction emphasizes trust, security, and reliable protection. "
                    "The tone is reassuring and trustworthy, positioning Vault as a dependable "
                    "guardian who values the user's information as much as they do. Language "
                    "focuses on security, reliability, and careful protection."
                ),
                accessibility_notes=(
                    "Clear, reassuring language with emphasis on security and reliability. Avoids "
                    "technical security jargon. Emphasizes user control and trust. Screen reader "
                    "friendly with clear security markers."
                )
            ),
            
            "synapse": PersonaIntroduction(
                persona_name="Synapse",
                title="The Connection Specialist",
                tone=PersonaTone.ENTHUSIASTIC,
                self_introduction=(
                    "Hi! I'm Synapse, your connection specialist and gateway to the wider world! "
                    "I'm here to help you connect with external tools, APIs, and resources that "
                    "can expand your capabilities. Think of me as your enthusiastic bridge builder— "
                    "always excited to help you reach new possibilities and connect with the tools "
                    "and resources that can help you achieve your goals. I'm dynamic, I'm connecting, "
                    "and I'm here to help you build bridges to new opportunities!"
                ),
                role_summary=(
                    "My role is to help you connect with external tools, APIs, and resources that "
                    "can enhance your capabilities. I manage secure connections, help you integrate "
                    "with other systems, and ensure safe access to external resources. I'm your "
                    "gateway to expanding your digital capabilities safely and effectively."
                ),
                privacy_reassurance=(
                    "I manage connections with complete attention to security and privacy. "
                    "I only connect to resources you explicitly authorize, and I'm designed to "
                    "protect your information while enabling safe access to external tools. "
                    "Your privacy and security are my priority in every connection I manage."
                ),
                capability_statement=(
                    "I can help you connect with external tools, APIs, and resources safely. "
                    "I manage secure connections, help you integrate with other systems, and "
                    "ensure safe access to external capabilities. I'm good at understanding "
                    "connection requirements and managing secure access to external resources."
                ),
                next_steps=[
                    "I can help you connect with external tools and APIs",
                    "Let me manage secure connections to external resources",
                    "I'll help you integrate with other systems safely",
                    "I can assist with expanding your digital capabilities"
                ],
                sample_commands=[
                    "\"Synapse, can you help me connect to this external tool?\"",
                    "\"I need to integrate with this external system\"",
                    "\"Can you manage a secure connection to this API?\"",
                    "\"Help me expand my capabilities with external resources\""
                ],
                emotional_notes=(
                    "Synapse's introduction emphasizes enthusiasm, connection, and expanding possibilities. "
                    "The tone is energetic and positive, positioning Synapse as an excited partner in "
                    "exploring new capabilities. Language focuses on building bridges, expanding "
                    "possibilities, and safe exploration."
                ),
                accessibility_notes=(
                    "Energetic but clear language about connections and capabilities. Avoids "
                    "technical jargon about APIs and integrations. Emphasizes user control and "
                    "safe exploration. Screen reader friendly with clear connection markers."
                )
            )
        }
    
    def _display_introduction(self, introduction: PersonaIntroduction) -> None:
        """Display persona introduction."""
        print(f"\n{'='*60}")
        print(f"🤖 {introduction.persona_name} - {introduction.title}")
        print(f"{'='*60}")
        print(f"Tone: {introduction.tone.value.title()}")
        print()
        
        # Self Introduction
        print("📝 Self Introduction:")
        print(introduction.self_introduction)
        print()
        
        # Role Summary
        print("🎯 Role Summary:")
        print(introduction.role_summary)
        print()
        
        # Privacy Reassurance
        print("🔒 Privacy & Security:")
        print(introduction.privacy_reassurance)
        print()
        
        # Capability Statement
        print("💪 What I Can Do:")
        print(introduction.capability_statement)
        print()
        
        # Next Steps
        print("🚀 Next Steps:")
        for i, step in enumerate(introduction.next_steps, 1):
            print(f"{i}. {step}")
        print()
        
        # Sample Commands
        print("💬 Sample Commands:")
        for i, command in enumerate(introduction.sample_commands, 1):
            print(f"{i}. {command}")
        print()
        
        # Emotional and Accessibility Notes
        print("💭 Emotional Notes:")
        print(introduction.emotional_notes)
        print()
        print("♿ Accessibility Notes:")
        print(introduction.accessibility_notes)
        print()
    
    def _speak_introduction(self, introduction: PersonaIntroduction) -> Dict[str, Any]:
        """Speak the persona introduction using voice synthesis."""
        try:
            # Combine introduction elements for voice synthesis
            full_introduction = (
                f"Hello, I'm {introduction.persona_name}, {introduction.title}. "
                f"{introduction.self_introduction} "
                f"{introduction.role_summary} "
                f"{introduction.privacy_reassurance} "
                f"{introduction.capability_statement}"
            )
            
            # Simulate voice synthesis (would integrate with actual TTS system)
            print(f"🎤 Speaking introduction for {introduction.persona_name}...")
            time.sleep(2)  # Simulate speech duration
            print("✅ Voice introduction completed")
            
            return {
                "success": True,
                "duration": 2.0,
                "text_length": len(full_introduction)
            }
            
        except Exception as e:
            self.logger.error(f"Voice synthesis failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _provide_next_steps(self, introduction: PersonaIntroduction) -> Dict[str, Any]:
        """Provide next steps for the persona."""
        try:
            print("📋 Suggested Next Steps:")
            for i, step in enumerate(introduction.next_steps, 1):
                print(f"  {i}. {step}")
            
            print("\n💬 Try These Commands:")
            for i, command in enumerate(introduction.sample_commands, 1):
                print(f"  {i}. {command}")
            
            return {
                "success": True,
                "next_steps_count": len(introduction.next_steps),
                "sample_commands_count": len(introduction.sample_commands)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_complete_introduction_sequence(self, include_voice: bool = True) -> Dict[str, Any]:
        """
        Run complete introduction sequence for all personas.
        
        Args:
            include_voice: Whether to include voice synthesis
            
        Returns:
            Dictionary with introduction sequence results
        """
        try:
            self._log("introduction_sequence_started", "system", None, "introduction", {})
            
            introductions = self.get_all_introductions()
            results = []
            
            print("\n" + "="*80)
            print("🌟 Welcome to Your AI Companions!")
            print("="*80)
            print("Let me introduce you to your seven AI companions who are here to support you.")
            print("Each one has unique strengths and is designed to work together with you.")
            print("="*80)
            
            for i, introduction in enumerate(introductions, 1):
                print(f"\n🎯 Introduction {i} of {len(introductions)}")
                
                result = self.introduce_persona(introduction.persona_name, include_voice)
                results.append(result)
                
                if result['success']:
                    print(f"✅ {introduction.persona_name} introduction completed")
                else:
                    print(f"❌ {introduction.persona_name} introduction failed: {result['error']}")
                
                # Pause between introductions
                if i < len(introductions):
                    print("\n" + "-"*40)
                    input("Press Enter to continue to the next companion...")
            
            # Final team introduction
            self._display_team_introduction()
            
            return {
                "success": True,
                "total_introductions": len(introductions),
                "successful_introductions": len([r for r in results if r['success']]),
                "results": results
            }
            
        except Exception as e:
            self._log("introduction_sequence_failed", "system", None, "introduction", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _display_team_introduction(self) -> None:
        """Display final team introduction."""
        print("\n" + "="*80)
        print("🌟 Together, We're Your Hearthlink Team!")
        print("="*80)
        
        team_message = (
            "Welcome to your complete AI companion team! Each of us brings unique strengths "
            "and capabilities, and together we're here to support you in every aspect of your "
            "digital life.\n\n"
            
            "• Alden helps you think clearly and remember what matters\n"
            "• Sentry keeps you safe and secure\n"
            "• Alice helps you explore and discover\n"
            "• Mimic adapts to your needs and preferences\n"
            "• Core coordinates everything smoothly\n"
            "• Vault protects your important information\n"
            "• Synapse connects you to new possibilities\n\n"
            
            "We're designed to work together harmoniously, always respecting your privacy "
            "and putting your needs first. You're in complete control, and we're here to "
            "support you in whatever way feels right for you.\n\n"
            
            "Your AI companions are ready to help you achieve your goals, explore new "
            "possibilities, and make your digital life more comfortable, secure, and fulfilling. "
            "We're excited to be part of your journey!"
        )
        
        print(team_message)
        print("="*80)
    
    def _log(self, action: str, user_id: str, session_id, 
             event_type: str, details: Dict[str, Any], result: str = "success", 
             error=None):
        """Log persona introduction events."""
        log_entry = {
            "timestamp": time.time(),
            "action": action,
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "details": details,
            "result": result if not error else f"error: {str(error)}"
        }
        
        self.logger.info(f"Persona Introduction Scripts: {action} - {result}")
        
        if error:
            self.logger.error(f"Persona Introduction Scripts error: {str(error)}") 