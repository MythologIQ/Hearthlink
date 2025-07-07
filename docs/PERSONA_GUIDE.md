# Hearthlink Persona Guide - Behavioral Analysis Multimodal

## Overview

The Hearthlink persona system now includes advanced behavioral analysis capabilities that enable multimodal understanding of user behavior patterns, session dynamics, and contextual signals. This guide documents the behavioral analysis features, integration patterns, and usage examples.

## Table of Contents

1. [Behavioral Analysis Overview](#behavioral-analysis-overview)
2. [Core Components](#core-components)
3. [Integration Patterns](#integration-patterns)
4. [Analysis Types](#analysis-types)
5. [Signal Processing](#signal-processing)
6. [Adaptive Feedback](#adaptive-feedback)
7. [Reporting and Insights](#reporting-and-insights)
8. [API Reference](#api-reference)
9. [Usage Examples](#usage-examples)
10. [Configuration](#configuration)
11. [Best Practices](#best-practices)

## Behavioral Analysis Overview

The behavioral analysis system provides comprehensive understanding of user behavior through multiple modalities:

- **Text Analysis**: Sentiment analysis, emotion detection, engagement indicators
- **Session Patterns**: Interaction flow, collaboration patterns, adaptation signals
- **External Signals**: Image/audio metadata, environmental data, user interactions
- **Multimodal Fusion**: Combined analysis across multiple signal types
- **Adaptive Feedback**: Real-time persona adjustment recommendations

### Key Features

- **Real-time Analysis**: Continuous behavioral pattern recognition
- **Multimodal Support**: Text, session history, and external signal processing
- **Adaptive Responses**: Dynamic persona behavior adjustment
- **Comprehensive Reporting**: Detailed behavioral insights and recommendations
- **Privacy-First**: Local processing with user-controlled data sharing

## Core Components

### 1. BehavioralAnalysis Class

The main behavioral analysis engine that processes signals and generates insights.

```python
from core.behavioral_analysis import BehavioralAnalysis

# Initialize with configuration and vault
behavioral_analysis = BehavioralAnalysis(config, vault, logger)
```

### 2. Signal Types

Supported signal types for multimodal analysis:

```python
from core.behavioral_analysis import SignalType

# Text signals
text_signal = ExternalSignal(
    signal_type=SignalType.TEXT,
    data={"text": "user message content"}
)

# Session history signals
session_signal = ExternalSignal(
    signal_type=SignalType.SESSION_HISTORY,
    data={"sessions": [...]}
)

# External signals (future phase)
image_signal = ExternalSignal(
    signal_type=SignalType.IMAGE_METADATA,
    data={"metadata": {...}}
)
```

### 3. Analysis Results

Structured analysis results with confidence metrics:

```python
# Text analysis results
text_analysis = TextAnalysis(
    sentiment_score=0.75,  # -1.0 to 1.0
    emotion_labels=["joy", "excitement"],
    complexity_score=0.6,  # 0.0 to 1.0
    engagement_indicators=["detailed_response", "question_asking"],
    behavioral_markers=["seeking_help", "expressing_opinion"],
    confidence=0.85
)

# Session analysis results
session_analysis = SessionAnalysis(
    session_id="session-123",
    duration_minutes=45.0,
    interaction_count=23,
    participant_engagement={"user1": 0.8, "user2": 0.6},
    topic_coherence=0.85,
    collaboration_patterns=["collaborative_discussion"],
    adaptation_signals=["adaptive_response"],
    effectiveness_score=0.78
)
```

## Integration Patterns

### Core Module Integration

The behavioral analysis is integrated into the Core module for session-level analysis:

```python
# Analyze session behavior
session_analysis = core.analyze_session_behavior(session_id, user_id)

# Generate behavioral insights
insights = core.generate_behavioral_insights(user_id, session_id)

# Create comprehensive report
report = core.create_behavioral_report(user_id, session_id)
```

### Persona Integration

Personas can use behavioral analysis for adaptive responses:

```python
# Set behavioral analysis for persona
alden.set_behavioral_analysis(behavioral_analysis)

# Generate response with behavioral analysis
response = alden.generate_response(user_message, session_id)
```

## Analysis Types

### 1. Text Sentiment Analysis

Analyzes text for sentiment, emotions, and behavioral patterns:

```python
# Analyze text behavior
text_analysis = behavioral_analysis.analyze_text("I'm really excited about this project!")

print(f"Sentiment: {text_analysis.sentiment_score}")
print(f"Emotions: {text_analysis.emotion_labels}")
print(f"Engagement: {text_analysis.engagement_indicators}")
```

### 2. Session Pattern Analysis

Analyzes session dynamics and interaction patterns:

```python
# Analyze session patterns
session_data = {
    "session_id": "session-123",
    "events": [...],
    "participants": [...],
    "duration_minutes": 45.0
}

session_analysis = behavioral_analysis.analyze_session(session_data)
```

### 3. Multimodal Signal Processing

Processes multiple signal types for comprehensive analysis:

```python
# Process external signals
signal = ExternalSignal(
    signal_type=SignalType.USER_INTERACTION,
    data={"type": "click", "target": "button", "timestamp": "2024-01-01T10:00:00Z"}
)

result = behavioral_analysis.process_external_signal(signal)
```

## Signal Processing

### Text Signal Processing

Text signals are processed for:
- Sentiment analysis (positive/negative/neutral)
- Emotion detection (joy, sadness, anger, fear, etc.)
- Complexity assessment
- Engagement indicators
- Behavioral markers

### Session History Processing

Session history signals provide:
- Interaction frequency analysis
- Participant engagement metrics
- Topic coherence assessment
- Collaboration pattern recognition
- Adaptation signal identification

### External Signal Processing

External signals (image/audio metadata) are processed as stubs for future implementation:

```python
# Image metadata processing (future phase)
image_signal = ExternalSignal(
    signal_type=SignalType.IMAGE_METADATA,
    data={
        "format": "JPEG",
        "size": "2.5MB",
        "dimensions": "1920x1080",
        "timestamp": "2024-01-01T10:00:00Z"
    }
)

# Audio metadata processing (future phase)
audio_signal = ExternalSignal(
    signal_type=SignalType.AUDIO_METADATA,
    data={
        "format": "WAV",
        "duration": "30s",
        "sample_rate": "44.1kHz",
        "channels": 2
    }
)
```

## Adaptive Feedback

### Feedback Generation

The system generates adaptive feedback for persona adjustment:

```python
# Generate adaptive feedback
feedback = behavioral_analysis.generate_adaptive_feedback(insights, "alden")

for item in feedback:
    print(f"Type: {item.feedback_type}")
    print(f"Priority: {item.priority}")
    print(f"Description: {item.description}")
    print(f"Suggestions: {item.implementation_suggestions}")
```

### Feedback Types

1. **Persona Adaptation**: Adjust persona response style and behavior
2. **Session Optimization**: Improve session flow and engagement
3. **Engagement Improvement**: Enhance user engagement strategies
4. **Collaboration Enhancement**: Foster better collaboration patterns

### Feedback Application

Personas automatically apply high-priority feedback:

```python
# Apply adaptive feedback
def _apply_adaptive_feedback(self, feedback_list):
    for feedback in feedback_list:
        if feedback.priority in ["high", "critical"]:
            self._apply_single_feedback(feedback)
            feedback.status = "implemented"
```

## Reporting and Insights

### Behavioral Reports

Comprehensive behavioral analysis reports:

```python
# Create behavioral report
report = behavioral_analysis.create_behavioral_report(
    user_id="user-123",
    session_id="session-456",
    analysis_period=("2024-01-01T00:00:00Z", "2024-01-31T23:59:59Z")
)

print(f"Report ID: {report.report_id}")
print(f"Patterns: {[p.value for p in report.patterns_identified]}")
print(f"Insights: {len(report.insights)}")
print(f"Feedback: {len(report.feedback_recommendations)}")
```

### Behavioral Insights

Generated insights provide actionable recommendations:

```python
# Generate insights
insights = behavioral_analysis.generate_behavioral_insights(analyses, user_id)

for insight in insights:
    print(f"Type: {insight.insight_type}")
    print(f"Description: {insight.description}")
    print(f"Confidence: {insight.confidence}")
    print(f"Evidence: {insight.evidence}")
    print(f"Recommendations: {insight.recommendations}")
```

## API Reference

### BehavioralAnalysis Methods

#### analyze_text(text: str, context: Optional[Dict] = None) -> TextAnalysis
Analyzes text for behavioral patterns and sentiment.

#### analyze_session(session_data: Dict) -> SessionAnalysis
Analyzes session patterns and dynamics.

#### process_external_signal(signal: ExternalSignal) -> Dict
Processes external signals (text, session history, external data).

#### generate_behavioral_insights(analyses: List, user_id: str, session_id: Optional[str] = None) -> List[BehavioralInsight]
Generates behavioral insights from multiple analyses.

#### generate_adaptive_feedback(insights: List[BehavioralInsight], target_persona: str) -> List[AdaptiveFeedback]
Generates adaptive feedback for persona adjustment.

#### create_behavioral_report(user_id: str, session_id: Optional[str] = None, analysis_period: Optional[Tuple] = None) -> BehavioralReport
Creates comprehensive behavioral analysis report.

### Core Integration Methods

#### analyze_session_behavior(session_id: str, user_id: str) -> Optional[SessionAnalysis]
Analyzes behavioral patterns in a session.

#### analyze_text_behavior(text: str, user_id: str, session_id: Optional[str] = None) -> TextAnalysis
Analyzes behavioral patterns in text.

#### process_behavioral_signal(signal_data: Dict, user_id: str, session_id: Optional[str] = None) -> Dict
Processes behavioral signals.

#### generate_behavioral_insights(user_id: str, session_id: Optional[str] = None, analysis_period: Optional[Tuple] = None) -> List[BehavioralInsight]
Generates behavioral insights for user/session.

#### generate_adaptive_feedback(user_id: str, target_persona: str = "alden", session_id: Optional[str] = None) -> List[AdaptiveFeedback]
Generates adaptive feedback for persona adjustment.

#### create_behavioral_report(user_id: str, session_id: Optional[str] = None, analysis_period: Optional[Tuple] = None) -> BehavioralReport
Creates comprehensive behavioral analysis report.

### Persona Integration Methods

#### set_behavioral_analysis(behavioral_analysis: BehavioralAnalysis) -> None
Sets behavioral analysis instance for persona.

#### generate_response(user_message: str, session_id: Optional[str] = None, context: Optional[Dict] = None) -> str
Generates response with behavioral analysis integration.

## Usage Examples

### Basic Text Analysis

```python
from core.behavioral_analysis import BehavioralAnalysis

# Initialize behavioral analysis
behavioral_analysis = BehavioralAnalysis(config, vault, logger)

# Analyze text
text = "I'm really excited about this new project! Can you help me get started?"
analysis = behavioral_analysis.analyze_text(text)

print(f"Sentiment: {analysis.sentiment_score}")
print(f"Emotions: {analysis.emotion_labels}")
print(f"Engagement: {analysis.engagement_indicators}")
```

### Session Analysis

```python
# Analyze session behavior
session_analysis = core.analyze_session_behavior(session_id, user_id)

print(f"Duration: {session_analysis.duration_minutes} minutes")
print(f"Interactions: {session_analysis.interaction_count}")
print(f"Effectiveness: {session_analysis.effectiveness_score}")
```

### Adaptive Feedback Generation

```python
# Generate insights and feedback
insights = core.generate_behavioral_insights(user_id, session_id)
feedback = core.generate_adaptive_feedback(user_id, "alden", session_id)

for item in feedback:
    print(f"Feedback: {item.description}")
    print(f"Priority: {item.priority}")
    print(f"Impact: {item.expected_impact}")
```

### Comprehensive Reporting

```python
# Create comprehensive report
report = core.create_behavioral_report(
    user_id="user-123",
    session_id="session-456",
    analysis_period=("2024-01-01T00:00:00Z", "2024-01-31T23:59:59Z")
)

print(f"Summary: {report.summary}")
print(f"Patterns: {[p.value for p in report.patterns_identified]}")
print(f"Confidence: {report.confidence_metrics}")
```

### Persona Integration

```python
# Set behavioral analysis for Alden
alden.set_behavioral_analysis(behavioral_analysis)

# Generate adaptive response
response = alden.generate_response(
    "I'm feeling overwhelmed with this project",
    session_id="session-123"
)

# Response will include behavioral analysis context and adaptive adjustments
```

## Configuration

### Behavioral Analysis Configuration

```python
behavioral_config = {
    "analysis": {
        "text_analysis": {
            "sentiment_threshold": 0.1,
            "emotion_detection": True,
            "complexity_analysis": True,
            "engagement_indicators": True
        },
        "session_analysis": {
            "pattern_recognition": True,
            "collaboration_analysis": True,
            "adaptation_tracking": True
        },
        "signal_processing": {
            "text_signals": True,
            "session_history": True,
            "external_signals": False  # Future phase
        }
    },
    "feedback": {
        "auto_apply_high_priority": True,
        "feedback_generation": True,
        "persona_adaptation": True
    },
    "reporting": {
        "generate_insights": True,
        "create_reports": True,
        "export_data": True
    }
}
```

### Core Integration Configuration

```python
core_config = {
    "behavioral_analysis": {
        "enabled": True,
        "real_time_analysis": True,
        "session_integration": True,
        "persona_integration": True
    }
}
```

## Best Practices

### 1. Privacy and Data Handling

- All behavioral analysis is performed locally
- User data is not shared without explicit consent
- Analysis results are stored in user-controlled vault
- External signals are processed as metadata only

### 2. Performance Optimization

- Use asynchronous processing for real-time analysis
- Cache analysis results for repeated patterns
- Limit analysis depth for high-frequency interactions
- Implement graceful degradation for analysis failures

### 3. Integration Guidelines

- Always handle behavioral analysis errors gracefully
- Provide fallback behavior when analysis is unavailable
- Log analysis results for debugging and improvement
- Validate analysis inputs and outputs

### 4. Adaptive Feedback

- Apply high-priority feedback immediately
- Validate feedback before application
- Track feedback effectiveness over time
- Allow user override of automatic adjustments

### 5. Reporting

- Generate reports on-demand rather than continuously
- Include confidence metrics with all insights
- Provide actionable recommendations
- Export data in standard formats

## Future Enhancements

### Phase 2: Advanced Signal Processing

- **Image Analysis**: Process image content for behavioral context
- **Audio Analysis**: Analyze voice patterns and emotional tone
- **Environmental Signals**: Process device and environment data
- **Biometric Integration**: Heart rate, stress levels, attention metrics

### Phase 3: Advanced Pattern Recognition

- **Long-term Pattern Analysis**: Identify behavioral trends over time
- **Predictive Modeling**: Anticipate user needs and preferences
- **Cross-session Analysis**: Understand behavior across multiple sessions
- **Collaborative Pattern Recognition**: Group behavior analysis

### Phase 4: Advanced Adaptive Systems

- **Multi-persona Coordination**: Coordinate multiple personas based on analysis
- **Dynamic Personality Adjustment**: Real-time persona trait modification
- **Contextual Memory Integration**: Integrate behavioral insights with memory
- **Proactive Intervention**: Anticipate and address user needs

## Troubleshooting

### Common Issues

1. **Analysis Failures**: Check input validation and error handling
2. **Performance Issues**: Monitor analysis frequency and caching
3. **Integration Problems**: Verify behavioral analysis initialization
4. **Feedback Loops**: Ensure feedback application doesn't create cycles

### Debugging

```python
# Enable debug logging
logger.setLevel(logging.DEBUG)

# Check behavioral analysis status
status = behavioral_analysis.get_status()

# Validate signal processing
result = behavioral_analysis.process_external_signal(test_signal)

# Export analysis data for debugging
data = behavioral_analysis.export_analysis_data(report_id)
```

## Conclusion

The behavioral analysis multimodal system provides comprehensive understanding of user behavior through multiple signal types. By integrating text analysis, session patterns, and external signals, the system enables adaptive persona responses and actionable insights.

The modular design allows for gradual enhancement and future expansion while maintaining privacy and user control. The integration with Core and Persona modules provides seamless behavioral understanding across the entire Hearthlink system.

For questions or support, refer to the main Hearthlink documentation or contact the development team. 