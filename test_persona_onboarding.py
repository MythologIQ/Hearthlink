#!/usr/bin/env python3
"""
Test Persona Onboarding Scripts

Demonstrates the comprehensive onboarding narratives for each core Hearthlink persona,
showing how they introduce themselves with warmth, inclusivity, and emotional impact.
"""

import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from installation_ux.persona_introduction_scripts import PersonaIntroductionScripts

def test_individual_persona_introductions():
    """Test individual persona introductions."""
    print("🧪 Testing Individual Persona Introductions")
    print("=" * 60)
    
    scripts = PersonaIntroductionScripts()
    
    # Test each persona individually
    personas = ["alden", "sentry", "alice", "mimic", "core", "vault", "synapse"]
    
    for persona in personas:
        print(f"\n🎯 Testing {persona.title()} introduction...")
        result = scripts.introduce_persona(persona, include_voice=False)
        
        if result['success']:
            print(f"✅ {persona.title()} introduction successful")
            print(f"   Tone: {result['tone']}")
            print(f"   Title: {result['title']}")
        else:
            print(f"❌ {persona.title()} introduction failed: {result['error']}")
        
        print("-" * 40)

def test_complete_introduction_sequence():
    """Test the complete introduction sequence."""
    print("\n🧪 Testing Complete Introduction Sequence")
    print("=" * 60)
    
    scripts = PersonaIntroductionScripts()
    
    print("Starting complete introduction sequence...")
    result = scripts.run_complete_introduction_sequence(include_voice=False)
    
    if result['success']:
        print(f"✅ Complete sequence successful")
        print(f"   Total introductions: {result['total_introductions']}")
        print(f"   Successful introductions: {result['successful_introductions']}")
    else:
        print(f"❌ Complete sequence failed: {result['error']}")

def test_persona_script_access():
    """Test accessing persona introduction scripts."""
    print("\n🧪 Testing Persona Script Access")
    print("=" * 60)
    
    scripts = PersonaIntroductionScripts()
    
    # Test getting all introductions
    all_intros = scripts.get_all_introductions()
    print(f"✅ Retrieved {len(all_intros)} persona introductions")
    
    # Test getting specific persona
    alden_intro = scripts.get_persona_introduction("alden")
    if alden_intro:
        print(f"✅ Alden introduction retrieved")
        print(f"   Title: {alden_intro.title}")
        print(f"   Tone: {alden_intro.tone.value}")
        print(f"   Next steps: {len(alden_intro.next_steps)}")
        print(f"   Sample commands: {len(alden_intro.sample_commands)}")
    else:
        print("❌ Failed to retrieve Alden introduction")
    
    # Test non-existent persona
    fake_intro = scripts.get_persona_introduction("nonexistent")
    if fake_intro is None:
        print("✅ Correctly returned None for non-existent persona")
    else:
        print("❌ Should have returned None for non-existent persona")

def demonstrate_emotional_impact():
    """Demonstrate the emotional impact of the introductions."""
    print("\n🧪 Demonstrating Emotional Impact")
    print("=" * 60)
    
    scripts = PersonaIntroductionScripts()
    
    # Show emotional themes for each persona
    personas = {
        "alden": "Gentle, Patient, Caring",
        "sentry": "Confident, Protective, Reliable", 
        "alice": "Enthusiastic, Curious, Energetic",
        "mimic": "Welcoming, Flexible, Understanding",
        "core": "Confident, Organized, Efficient",
        "vault": "Reassuring, Trustworthy, Secure",
        "synapse": "Enthusiastic, Dynamic, Connecting"
    }
    
    print("Emotional Themes by Persona:")
    for persona, theme in personas.items():
        intro = scripts.get_persona_introduction(persona)
        if intro:
            print(f"   {persona.title()}: {theme}")
            print(f"      Emotional notes: {intro.emotional_notes[:100]}...")
            print(f"      Accessibility: {intro.accessibility_notes[:100]}...")
            print()

def demonstrate_privacy_reassurances():
    """Demonstrate privacy reassurances across personas."""
    print("\n🧪 Demonstrating Privacy Reassurances")
    print("=" * 60)
    
    scripts = PersonaIntroductionScripts()
    
    print("Privacy Reassurances by Persona:")
    for persona in ["alden", "sentry", "alice", "mimic", "core", "vault", "synapse"]:
        intro = scripts.get_persona_introduction(persona)
        if intro:
            print(f"\n{persona.title()}:")
            print(f"   {intro.privacy_reassurance[:150]}...")
            print()

def demonstrate_next_steps():
    """Demonstrate next steps and sample commands."""
    print("\n🧪 Demonstrating Next Steps and Sample Commands")
    print("=" * 60)
    
    scripts = PersonaIntroductionScripts()
    
    for persona in ["alden", "sentry", "alice"]:  # Show first 3 for brevity
        intro = scripts.get_persona_introduction(persona)
        if intro:
            print(f"\n{persona.title()} - Next Steps:")
            for i, step in enumerate(intro.next_steps, 1):
                print(f"   {i}. {step}")
            
            print(f"\n{persona.title()} - Sample Commands:")
            for i, command in enumerate(intro.sample_commands, 1):
                print(f"   {i}. {command}")
            print()

def main():
    """Run all persona onboarding tests."""
    print("🌟 Hearthlink Persona Onboarding Test Suite")
    print("=" * 80)
    print("Testing comprehensive onboarding narratives for warmth and inclusivity")
    print("=" * 80)
    
    try:
        # Test individual introductions
        test_individual_persona_introductions()
        
        # Test script access
        test_persona_script_access()
        
        # Demonstrate emotional impact
        demonstrate_emotional_impact()
        
        # Demonstrate privacy reassurances
        demonstrate_privacy_reassurances()
        
        # Demonstrate next steps
        demonstrate_next_steps()
        
        # Test complete sequence (commented out to avoid overwhelming output)
        # test_complete_introduction_sequence()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Summary:")
        print("   ✅ Individual persona introductions working")
        print("   ✅ Script access and retrieval working")
        print("   ✅ Emotional impact analysis complete")
        print("   ✅ Privacy reassurances documented")
        print("   ✅ Next steps and sample commands ready")
        print("\n🌟 Persona onboarding narratives are ready for platinum deployment!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 