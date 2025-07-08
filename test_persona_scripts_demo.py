#!/usr/bin/env python3
"""
Persona Introduction Scripts Demo

Demonstrates the comprehensive onboarding narratives for each core Hearthlink persona,
showing how they introduce themselves with warmth, inclusivity, and emotional impact.
"""

import sys
import time
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

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

def create_persona_introductions():
    """Create all persona introduction scripts."""
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
        )
    }

def display_persona_introduction(introduction: PersonaIntroduction):
    """Display a persona introduction."""
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

def demonstrate_emotional_themes():
    """Demonstrate emotional themes across personas."""
    print("\n🧪 Demonstrating Emotional Themes")
    print("=" * 60)
    
    introductions = create_persona_introductions()
    
    themes = {
        "alden": "Gentle, Patient, Caring",
        "sentry": "Confident, Protective, Reliable", 
        "alice": "Enthusiastic, Curious, Energetic"
    }
    
    for persona, theme in themes.items():
        intro = introductions.get(persona)
        if intro:
            print(f"\n{persona.title()}: {theme}")
            print(f"   Emotional notes: {intro.emotional_notes}")
            print(f"   Accessibility: {intro.accessibility_notes}")

def demonstrate_privacy_reassurances():
    """Demonstrate privacy reassurances."""
    print("\n🧪 Demonstrating Privacy Reassurances")
    print("=" * 60)
    
    introductions = create_persona_introductions()
    
    for persona in ["alden", "sentry", "alice"]:
        intro = introductions.get(persona)
        if intro:
            print(f"\n{persona.title()}:")
            print(f"   {intro.privacy_reassurance}")
            print()

def demonstrate_next_steps():
    """Demonstrate next steps and sample commands."""
    print("\n🧪 Demonstrating Next Steps and Sample Commands")
    print("=" * 60)
    
    introductions = create_persona_introductions()
    
    for persona in ["alden", "sentry", "alice"]:
        intro = introductions.get(persona)
        if intro:
            print(f"\n{persona.title()} - Next Steps:")
            for i, step in enumerate(intro.next_steps, 1):
                print(f"   {i}. {step}")
            
            print(f"\n{persona.title()} - Sample Commands:")
            for i, command in enumerate(intro.sample_commands, 1):
                print(f"   {i}. {command}")
            print()

def main():
    """Run the persona onboarding demo."""
    print("🌟 Hearthlink Persona Onboarding Demo")
    print("=" * 80)
    print("Demonstrating comprehensive onboarding narratives for warmth and inclusivity")
    print("=" * 80)
    
    introductions = create_persona_introductions()
    
    # Display each persona introduction
    for persona_name, introduction in introductions.items():
        display_persona_introduction(introduction)
        print("-" * 80)
        time.sleep(1)  # Brief pause between personas
    
    # Demonstrate key features
    demonstrate_emotional_themes()
    demonstrate_privacy_reassurances()
    demonstrate_next_steps()
    
    # Team introduction
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
    
    print("\n🎉 Demo completed successfully!")
    print("\n📋 Key Features Demonstrated:")
    print("   ✅ Individual persona introductions with unique emotional tones")
    print("   ✅ Comprehensive privacy reassurances")
    print("   ✅ Clear next steps and sample commands")
    print("   ✅ Accessibility and inclusivity guidelines")
    print("   ✅ Warm, welcoming language throughout")
    print("   ✅ Team coordination and harmony")
    print("\n🌟 Persona onboarding narratives are ready for platinum deployment!")

if __name__ == "__main__":
    main() 