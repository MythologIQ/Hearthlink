# USER_MANUAL.md

## Overview
This manual provides user guidance for Hearthlink's voice interaction system and troubleshooting common issues.

## Talking to the System

### Voice Agent Switching
- **Address by Name**: Say "Hey Alden", "Alice, can you...", or "Mimic, help me..."
- **Voice HUD Selection**: Use the Voice Interaction HUD to visually select agents
- **Agent Confirmation**: The system will confirm which agent you're speaking with
- **Automatic Routing**: If no agent is specified, Core delegates to the currently active agent

### Deference Protocol
Agents can suggest better-suited agents for specific tasks:
- **Passive Suggestion**: "Alice might be better at this..."
- **Direct Request**: "Can I talk to Alice?"
- **Delegation**: "Hand this off to Alice."

### Voice HUD Behavior
The Voice Interaction HUD provides:
- **Live Input Transcript**: Real-time display of your voice input
- **Active Agent Display**: Clear indication of which agent is currently active
- **Reroute Handling Visual**: Visual feedback when voice input is rerouted between agents
- **Agent Selection Interface**: Visual controls for switching between available agents

## Troubleshooting Voice Issues

### Misrouting Handling
- **Recovery Protocol**: Alden handles all voice misroutes via recovery dialogue
- **Common Scenarios**:
  - "I think you meant to talk to Alice about that. Would you like me to switch you over?"
  - "That's outside my expertise, but I can connect you with Mimic who specializes in that area."
  - "Let me help you get to the right agent for this request."

### Offline Fallback Behavior
When offline or no internet connection is detected:
- **Local Agents**: Alden, Alice, Mimic, and Sentry remain fully functional
- **External Services**: All outbound requests to external APIs are blocked
- **User Alert**: "External services unavailable. Local systems fully operational."
- **Detection**: System uses dynamic detection (failed pings, Windows flags, timeout events)

### Expected Authentication Flow
- **Dev Mode Activation**: Activation phrase → Challenge phrase → PIN entry → Dev Mode UI
- **Current Implementation**: Stub logic with simulated challenge prompt and PIN UI stub
- **Security**: Temporarily unlocks system modification mode, logged in Vault

### Voice Settings Configuration
- **Per-Agent Permissions**: Core → Agent Settings → [Agent Name] → Voice Interaction
- **Global Defaults**: Settings → Hearthlink Voice Settings → External Agent Defaults
- **External Agents**: Disabled by default for security, require explicit activation

## Voice Access States

### Voice Interaction Enabled
- Full conversational interaction with local agents
- External agents permitted if explicitly enabled
- Universal voice HUD routes input according to active agent context

### Voice Interaction Disabled
- Voice HUD and microphone remain inactive
- No voice parsing, transcription, or command handling
- Agent memory marks user preference to disable voice interactions

## Best Practices

### Agent Selection
- Use specific agent names for specialized tasks
- Let Core delegate when unsure which agent to use
- Trust agent deference suggestions for optimal results

### Voice Clarity
- Speak clearly and at normal volume
- Use agent names to ensure proper routing
- Wait for agent confirmation before continuing

### Troubleshooting Steps
1. **Check Voice Settings**: Ensure voice interaction is enabled
2. **Verify Agent Permissions**: Confirm agent has voice access enabled
3. **Check Network Status**: External agents require internet connection
4. **Restart Voice HUD**: If routing issues persist
5. **Contact Support**: For persistent issues, contact `system@hearthlink.local`

## Support

For questions or issues with voice interaction:
- **Documentation**: `/docs/VOICE_ACCESS_POLICY.md`
- **UI Guide**: `/docs/UI_ALIGNMENT_AUDIT.md`
- **Contact**: `system@hearthlink.local` 