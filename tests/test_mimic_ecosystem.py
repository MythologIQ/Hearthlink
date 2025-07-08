#!/usr/bin/env python3
"""
Mimic Persona Ecosystem Tests

Comprehensive test suite for the Mimic persona ecosystem, covering:
- Dynamic persona generation
- Performance analytics and tracking
- Persona forking and merging
- Knowledge indexing and retrieval
- Plugin extension management
- Core session integration
- Vault schema validation

References:
- hearthlink_system_documentation_master.md: Mimic persona specification
- PLATINUM_BLOCKERS.md: Testing requirements

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import json
import uuid
import tempfile
import shutil
import traceback
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
import unittest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import asdict

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from personas.mimic import (
    MimicPersona, MimicPersonaMemory, CoreTraits, GrowthStats,
    PerformanceRecord, TopicScore, KnowledgeSummary, PluginExtension,
    PersonaStatus, PerformanceTier, MimicError, PersonaGenerationError,
    PerformanceAnalyticsError, PersonaForkError, KnowledgeIndexError,
    PluginExtensionError
)
from core.mimic_integration import MimicCoreIntegration
from llm.local_llm_client import LocalLLMClient, LLMConfig
from vault.mimic_schema import SchemaValidationError
from main import HearthlinkLogger


class MockLocalLLMClient(LocalLLMClient):
    """Mock LocalLLMClient for testing purposes."""
    
    def __init__(self, config: LLMConfig = None, logger: Optional[HearthlinkLogger] = None):
        if config is None:
            config = LLMConfig(
                engine="mock",
                base_url="http://localhost:11434",
                model="mock-model",
                timeout=30
            )
        super().__init__(config, logger)
        self.mock_responses = []
        self.call_count = 0
    
    def generate(self, request):
        """Mock generate method that returns predefined responses."""
        self.call_count += 1
        if self.mock_responses:
            response = self.mock_responses.pop(0)
            return response
        else:
            # Default mock response
            return Mock(
                content="Mock response content",
                model="mock-model",
                response_time=0.1,
                timestamp=datetime.now().isoformat(),
                usage={"prompt_tokens": 10, "completion_tokens": 20},
                finish_reason="stop",
                context=request.context,
                request_id=request.request_id
            )
    
    def add_mock_response(self, response):
        """Add a mock response to the queue."""
        self.mock_responses.append(response)


class TestMimicPersonaGeneration(unittest.TestCase):
    """Test Mimic persona generation functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = HearthlinkLogger()
        
        # Create mock LLM client
        self.mock_llm_client = MockLocalLLMClient()
        
        # Create test persona
        self.persona = MimicPersona(self.mock_llm_client, self.logger)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_persona_generation_basic(self):
        """Test basic persona generation."""
        try:
            # Generate persona
            persona_id = self.persona.generate_persona(
                role="researcher",
                context={"requires_precision": True, "tags": ["research", "analysis"]}
            )
            
            # Verify persona ID
            self.assertIsInstance(persona_id, str)
            self.assertTrue(persona_id.startswith("mimic-"))
            
            # Verify memory state
            self.assertIsNotNone(self.persona.memory)
            self.assertIsInstance(self.persona.memory.persona_id, str)
            self.assertTrue(self.persona.memory.persona_id.startswith("mimic-"))
            
        except Exception as e:
            self.fail(f"Basic persona generation failed: {str(e)}")
    
    def test_persona_generation_with_traits(self):
        """Test persona generation with custom traits."""
        try:
            base_traits = {
                "focus": 80, "creativity": 70, "precision": 90,
                "humor": 30, "empathy": 60, "assertiveness": 75,
                "adaptability": 65, "collaboration": 55
            }
            
            persona_id = self.persona.generate_persona(
                role="analyst",
                context={"requires_precision": True},
                base_traits=base_traits
            )
            
            # Verify traits were applied
            memory = self.persona.memory
            self.assertEqual(memory.core_traits.focus, 80)
            self.assertEqual(memory.core_traits.precision, 90)
            self.assertEqual(memory.core_traits.creativity, 70)
            
        except Exception as e:
            self.fail(f"Persona generation with traits failed: {str(e)}")
    
    def test_persona_generation_with_preferences(self):
        """Test persona generation with user preferences."""
        try:
            user_preferences = {
                "communication_style": "formal",
                "detail_level": "high",
                "interaction_frequency": "moderate"
            }
            
            persona_id = self.persona.generate_persona(
                role="consultant",
                context={"requires_adaptability": True},
                user_preferences=user_preferences
            )
            
            # Verify persona was created
            self.assertIsInstance(persona_id, str)
            self.assertTrue(persona_id.startswith("mimic-"))
            
        except Exception as e:
            self.fail(f"Persona generation with preferences failed: {str(e)}")
    
    def test_persona_generation_error_handling(self):
        """Test error handling in persona generation."""
        try:
            # Test with invalid role
            with self.assertRaises(PersonaGenerationError):
                self.persona.generate_persona("", {})
            
        except Exception as e:
            self.fail(f"Error handling test failed: {str(e)}")


class TestMimicPerformanceAnalytics(unittest.TestCase):
    """Test Mimic performance analytics functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = HearthlinkLogger()
        self.mock_llm_client = MockLocalLLMClient()
        self.persona = MimicPersona(self.mock_llm_client, self.logger)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_performance_recording(self):
        """Test performance recording functionality."""
        try:
            session_id = "test-session-001"
            
            # Record performance
            self.persona.record_performance(
                session_id=session_id,
                task="Data Analysis",
                score=85,
                user_feedback="Excellent analysis",
                success=True,
                duration=1800.0,
                context={"dataset_size": "large", "complexity": "high"}
            )
            
            # Verify performance was recorded
            self.assertEqual(len(self.persona.memory.performance_history), 1)
            record = self.persona.memory.performance_history[0]
            self.assertEqual(record.session_id, session_id)
            self.assertEqual(record.score, 85)
            self.assertTrue(record.success)
            
        except Exception as e:
            self.fail(f"Performance recording failed: {str(e)}")
    
    def test_growth_stats_update(self):
        """Test growth statistics update."""
        try:
            # Record multiple performances
            for i in range(3):
                self.persona.record_performance(
                    session_id=f"session-{i}",
                    task=f"Task {i}",
                    score=80 + i * 5,
                    user_feedback=f"Good performance {i}",
                    success=True,
                    duration=900.0
                )
            
            # Verify growth stats
            stats = self.persona.memory.growth_stats
            self.assertEqual(stats.sessions_completed, 3)
            self.assertEqual(stats.unique_tasks, 3)
            self.assertGreater(stats.total_usage_time, 0)
            
        except Exception as e:
            self.fail(f"Growth stats update failed: {str(e)}")
    
    def test_performance_analytics_generation(self):
        """Test performance analytics generation."""
        try:
            # Add some performance data
            for i in range(5):
                self.persona.record_performance(
                    session_id=f"session-{i}",
                    task=f"Task {i}",
                    score=70 + i * 5,
                    user_feedback=f"Performance {i}",
                    success=i < 4,  # One failure
                    duration=1200.0
                )
            
            # Generate analytics
            analytics = self.persona.get_performance_analytics()
            
            # Verify analytics structure
            self.assertIn("overall_score", analytics)
            self.assertIn("success_rate", analytics)
            self.assertIn("growth_trend", analytics)
            self.assertIn("recommendations", analytics)
            
            # Verify values
            self.assertGreater(analytics["overall_score"], 0)
            self.assertLessEqual(analytics["success_rate"], 1.0)
            
        except Exception as e:
            self.fail(f"Performance analytics generation failed: {str(e)}")
    
    def test_performance_tier_calculation(self):
        """Test performance tier calculation."""
        try:
            # Test different performance scenarios
            test_cases = [
                (50, False, PerformanceTier.UNSTABLE),
                (70, True, PerformanceTier.RISKY),
                (85, True, PerformanceTier.STABLE),
                (95, True, PerformanceTier.EXCELLENT)
            ]
            
            for score, success, expected_tier in test_cases:
                # Clear performance history
                self.persona.memory.performance_history.clear()
                
                # Record single performance
                self.persona.record_performance(
                    session_id="test-tier",
                    task="Tier Test",
                    score=score,
                    user_feedback="Tier test",
                    success=success,
                    duration=600.0
                )
                
                # Check tier
                actual_tier = self.persona.get_performance_tier()
                self.assertEqual(actual_tier, expected_tier)
            
        except Exception as e:
            self.fail(f"Performance tier calculation failed: {str(e)}")


class TestMimicPersonaForking(unittest.TestCase):
    """Test Mimic persona forking functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = HearthlinkLogger()
        self.mock_llm_client = MockLocalLLMClient()
        self.persona = MimicPersona(self.mock_llm_client, self.logger)
        
        # Create base persona
        self.base_persona_id = self.persona.generate_persona(
            role="researcher",
            context={"requires_precision": True}
        )
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_persona_forking_basic(self):
        """Test basic persona forking."""
        try:
            # Fork persona
            new_persona_id = self.persona.fork_persona(
                source_persona_id=self.base_persona_id,
                new_role="specialist",
                modifications={
                    "core_traits": {"precision": 95, "focus": 90},
                    "description": "Specialized research persona"
                }
            )
            
            # Verify forked persona
            self.assertIsInstance(new_persona_id, str)
            self.assertTrue(new_persona_id.startswith("mimic-"))
            self.assertNotEqual(new_persona_id, self.base_persona_id)
            
        except Exception as e:
            self.fail(f"Basic persona forking failed: {str(e)}")
    
    def test_persona_forking_with_trait_modifications(self):
        """Test persona forking with trait modifications."""
        try:
            modifications = {
                "core_traits": {
                    "creativity": 80,
                    "empathy": 70,
                    "collaboration": 85
                },
                "user_tags": ["creative", "collaborative"]
            }
            
            new_persona_id = self.persona.fork_persona(
                source_persona_id=self.base_persona_id,
                new_role="creative_collaborator",
                modifications=modifications
            )
            
            # Verify modifications were applied
            # Note: In a real implementation, you'd need to access the forked persona
            self.assertIsInstance(new_persona_id, str)
            
        except Exception as e:
            self.fail(f"Persona forking with modifications failed: {str(e)}")
    
    def test_persona_merging(self):
        """Test persona merging functionality."""
        try:
            # Create second persona
            second_persona_id = self.persona.generate_persona(
                role="analyst",
                context={"requires_creativity": True}
            )
            
            # Merge personas
            merged_persona_id = self.persona.merge_personas(
                primary_persona_id=self.base_persona_id,
                secondary_persona_id=second_persona_id,
                merge_strategy="selective"
            )
            
            # Verify merged persona
            self.assertIsInstance(merged_persona_id, str)
            self.assertTrue(merged_persona_id.startswith("mimic-"))
            
        except Exception as e:
            self.fail(f"Persona merging failed: {str(e)}")
    
    def test_persona_merging_strategies(self):
        """Test different persona merging strategies."""
        try:
            # Create second persona
            second_persona_id = self.persona.generate_persona(
                role="consultant",
                context={"requires_adaptability": True}
            )
            
            strategies = ["selective", "comprehensive", "hybrid"]
            
            for strategy in strategies:
                merged_persona_id = self.persona.merge_personas(
                    primary_persona_id=self.base_persona_id,
                    secondary_persona_id=second_persona_id,
                    merge_strategy=strategy
                )
                
                self.assertIsInstance(merged_persona_id, str)
            
        except Exception as e:
            self.fail(f"Persona merging strategies failed: {str(e)}")


class TestMimicKnowledgeIndexing(unittest.TestCase):
    """Test Mimic knowledge indexing functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = HearthlinkLogger()
        self.mock_llm_client = MockLocalLLMClient()
        self.persona = MimicPersona(self.mock_llm_client, self.logger)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_knowledge_index_initialization(self):
        """Test knowledge index initialization."""
        try:
            # Verify initial knowledge index
            self.assertIsInstance(self.persona.memory.relevance_index, list)
            
            # Check default topics
            default_topics = [
                "general_knowledge", "task_specific", "user_preferences",
                "domain_expertise", "communication_style", "problem_solving"
            ]
            
            for topic in default_topics:
                topic_found = any(ts.topic == topic for ts in self.persona.memory.relevance_index)
                self.assertTrue(topic_found, f"Default topic {topic} not found")
            
        except Exception as e:
            self.fail(f"Knowledge index initialization failed: {str(e)}")
    
    def test_relevance_index_update(self):
        """Test relevance index update."""
        try:
            # Record performance to trigger relevance update
            self.persona.record_performance(
                session_id="knowledge-test",
                task="Data Analysis with Machine Learning",
                score=85,
                user_feedback="Good ML analysis",
                success=True,
                duration=2400.0,
                context={"domain": "machine_learning", "tools": ["python", "scikit-learn"]}
            )
            
            # Verify relevance index was updated
            # Note: In a real implementation, you'd check for specific topic updates
            self.assertIsInstance(self.persona.memory.relevance_index, list)
            
        except Exception as e:
            self.fail(f"Relevance index update failed: {str(e)}")
    
    def test_custom_knowledge_management(self):
        """Test custom knowledge management."""
        try:
            # Add custom knowledge
            custom_knowledge = KnowledgeSummary(
                doc_id="test-doc-001",
                summary="This is a test knowledge summary about data analysis",
                relevance_score=0.8,
                tags=["data_analysis", "test"],
                created_at=datetime.now().isoformat()
            )
            
            self.persona.memory.custom_knowledge.append(custom_knowledge)
            
            # Verify knowledge was added
            self.assertEqual(len(self.persona.memory.custom_knowledge), 1)
            added_knowledge = self.persona.memory.custom_knowledge[0]
            self.assertEqual(added_knowledge.doc_id, "test-doc-001")
            self.assertEqual(added_knowledge.relevance_score, 0.8)
            
        except Exception as e:
            self.fail(f"Custom knowledge management failed: {str(e)}")


class TestMimicPluginExtensions(unittest.TestCase):
    """Test Mimic plugin extensions functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = HearthlinkLogger()
        self.mock_llm_client = MockLocalLLMClient()
        self.persona = MimicPersona(self.mock_llm_client, self.logger)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_plugin_extension_addition(self):
        """Test plugin extension addition."""
        try:
            # Add plugin extension
            self.persona.add_plugin_extension(
                plugin_id="test-plugin-001",
                name="Test Plugin",
                version="1.0.0",
                permissions=["read", "write"],
                performance_impact=0.1
            )
            
            # Verify plugin was added
            self.assertEqual(len(self.persona.memory.plugin_extensions), 1)
            plugin = self.persona.memory.plugin_extensions[0]
            self.assertEqual(plugin.plugin_id, "test-plugin-001")
            self.assertEqual(plugin.name, "Test Plugin")
            self.assertTrue(plugin.enabled)
            
        except Exception as e:
            self.fail(f"Plugin extension addition failed: {str(e)}")
    
    def test_plugin_extension_update(self):
        """Test plugin extension update."""
        try:
            # Add plugin first
            self.persona.add_plugin_extension(
                plugin_id="update-test",
                name="Update Test Plugin",
                version="1.0.0",
                permissions=["read"]
            )
            
            # Update plugin
            for plugin in self.persona.memory.plugin_extensions:
                if plugin.plugin_id == "update-test":
                    plugin.version = "1.1.0"
                    plugin.permissions = ["read", "write", "execute"]
                    plugin.performance_impact = 0.2
                    break
            
            # Verify update
            updated_plugin = next(
                (p for p in self.persona.memory.plugin_extensions if p.plugin_id == "update-test"),
                None
            )
            self.assertIsNotNone(updated_plugin)
            self.assertEqual(updated_plugin.version, "1.1.0")
            self.assertEqual(len(updated_plugin.permissions), 3)
            
        except Exception as e:
            self.fail(f"Plugin extension update failed: {str(e)}")
    
    def test_multiple_plugin_extensions(self):
        """Test multiple plugin extensions."""
        try:
            # Add multiple plugins
            plugins = [
                ("plugin-1", "Plugin One", "1.0.0"),
                ("plugin-2", "Plugin Two", "2.0.0"),
                ("plugin-3", "Plugin Three", "1.5.0")
            ]
            
            for plugin_id, name, version in plugins:
                self.persona.add_plugin_extension(
                    plugin_id=plugin_id,
                    name=name,
                    version=version,
                    permissions=["read"]
                )
            
            # Verify all plugins were added
            self.assertEqual(len(self.persona.memory.plugin_extensions), 3)
            
            # Verify plugin IDs
            plugin_ids = [p.plugin_id for p in self.persona.memory.plugin_extensions]
            self.assertIn("plugin-1", plugin_ids)
            self.assertIn("plugin-2", plugin_ids)
            self.assertIn("plugin-3", plugin_ids)
            
        except Exception as e:
            self.fail(f"Multiple plugin extensions failed: {str(e)}")


class TestMimicSchemaValidation(unittest.TestCase):
    """Test Mimic schema validation functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = HearthlinkLogger()
        self.mock_llm_client = MockLocalLLMClient()
        self.persona = MimicPersona(self.mock_llm_client, self.logger)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_memory_validation_valid(self):
        """Test valid memory validation."""
        try:
            # Create valid memory
            valid_memory = MimicPersonaMemory(
                persona_id="test-valid",
                persona_name="Valid Test Persona",
                role="tester",
                description="A valid test persona",
                status=PersonaStatus.ACTIVE,
                core_traits=CoreTraits(
                    focus=75, creativity=60, precision=80,
                    humor=30, empathy=70, assertiveness=65,
                    adaptability=75, collaboration=80
                )
            )
            
            # Validate memory (should not raise exception)
            self.assertIsNotNone(valid_memory)
            self.assertEqual(valid_memory.persona_id, "test-valid")
            self.assertEqual(valid_memory.status, PersonaStatus.ACTIVE)
            
        except Exception as e:
            self.fail(f"Valid memory validation failed: {str(e)}")
    
    def test_memory_validation_invalid(self):
        """Test invalid memory validation."""
        try:
            # Test with invalid trait values
            with self.assertRaises(SchemaValidationError):
                invalid_memory = MimicPersonaMemory(
                    persona_id="test-invalid",
                    core_traits=CoreTraits(
                        focus=150,  # Invalid: > 100
                        creativity=60,
                        precision=80,
                        humor=30,
                        empathy=70,
                        assertiveness=65,
                        adaptability=75,
                        collaboration=80
                    )
                )
            
        except Exception as e:
            self.fail(f"Invalid memory validation test failed: {str(e)}")
    
    def test_memory_creation(self):
        """Test memory creation with validation."""
        try:
            # Create memory through persona
            persona_id = self.persona.generate_persona(
                role="validator",
                context={"requires_validation": True}
            )
            
            # Verify memory was created and validated
            self.assertIsNotNone(self.persona.memory)
            self.assertEqual(self.persona.memory.persona_id, persona_id)
            
            # Verify core traits are within valid range
            traits = self.persona.memory.core_traits
            for trait_name, trait_value in asdict(traits).items():
                self.assertGreaterEqual(trait_value, 0)
                self.assertLessEqual(trait_value, 100)
            
        except Exception as e:
            self.fail(f"Memory creation failed: {str(e)}")
    
    def test_schema_migration(self):
        """Test schema migration functionality."""
        try:
            # Create memory with old schema version
            old_memory_data = {
                "persona_id": "migration-test",
                "schema_version": "0.9.0",  # Old version
                "persona_name": "Migration Test",
                "role": "migrator",
                "status": "active",  # Old enum format
                "core_traits": {
                    "focus": 70, "creativity": 60, "precision": 80,
                    "humor": 30, "empathy": 70, "assertiveness": 65,
                    "adaptability": 75, "collaboration": 80
                }
            }
            
            # Import old memory (should trigger migration)
            self.persona.import_memory(old_memory_data)
            
            # Verify migration occurred
            self.assertEqual(self.persona.memory.schema_version, "1.0.0")
            self.assertEqual(self.persona.memory.status, PersonaStatus.ACTIVE)
            
        except Exception as e:
            self.fail(f"Schema migration failed: {str(e)}")


class TestMimicCoreIntegration(unittest.TestCase):
    """Test Mimic-Core integration functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = HearthlinkLogger()
        
        # Create mock Core
        self.mock_core = Mock()
        self.mock_core.add_persona_to_session.return_value = True
        self.mock_core.remove_persona_from_session.return_value = True
        self.mock_core.share_insight.return_value = True
        
        # Create integration
        self.integration = MimicCoreIntegration(self.mock_core, self.logger)
        
        # Create test personas
        self.mock_llm_client = MockLocalLLMClient()
        self.persona1 = MimicPersona(self.mock_llm_client, self.logger)
        self.persona2 = MimicPersona(self.mock_llm_client, self.logger)
        
        # Register personas
        self.integration.register_mimic_persona(self.persona1)
        self.integration.register_mimic_persona(self.persona2)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_persona_registration(self):
        """Test persona registration."""
        try:
            # Verify personas are registered
            self.assertEqual(len(self.integration.mimic_personas), 2)
            self.assertIn(self.persona1.memory.persona_id, self.integration.mimic_personas)
            self.assertIn(self.persona2.memory.persona_id, self.integration.mimic_personas)
            
        except Exception as e:
            self.fail(f"Persona registration failed: {str(e)}")
    
    def test_persona_recommendation(self):
        """Test persona recommendation for sessions."""
        try:
            # Get recommendations
            recommendations = self.integration.recommend_personas_for_session(
                session_topic="Data Analysis",
                session_context={"requires_precision": True},
                max_recommendations=5
            )
            
            # Verify recommendations
            self.assertIsInstance(recommendations, list)
            self.assertLessEqual(len(recommendations), 5)
            
            for recommendation in recommendations:
                self.assertIsInstance(recommendation, type(self.integration).__module__ + '.PersonaRecommendation')
                self.assertIsNotNone(recommendation.persona_id)
                self.assertIsNotNone(recommendation.persona_name)
                self.assertIsNotNone(recommendation.role)
                self.assertGreaterEqual(recommendation.confidence_score, 0.0)
                self.assertLessEqual(recommendation.confidence_score, 1.0)
            
        except Exception as e:
            self.fail(f"Persona recommendation failed: {str(e)}")
    
    def test_session_integration(self):
        """Test session integration functionality."""
        try:
            session_id = "test-session-001"
            persona_id = self.persona1.memory.persona_id
            user_id = "user-123"
            
            # Add persona to session
            success = self.integration.add_persona_to_session(session_id, persona_id, user_id)
            self.assertTrue(success)
            
            # Verify session tracking
            self.assertIn(session_id, self.integration.session_participants)
            self.assertIn(persona_id, self.integration.session_participants[session_id])
            
            # Remove persona from session
            success = self.integration.remove_persona_from_session(session_id, persona_id, user_id)
            self.assertTrue(success)
            
        except Exception as e:
            self.fail(f"Session integration failed: {str(e)}")
    
    def test_insight_sharing(self):
        """Test insight sharing functionality."""
        try:
            session_id = "test-session-002"
            persona_id = self.persona1.memory.persona_id
            user_id = "user-456"
            
            # Add persona to session first
            self.integration.add_persona_to_session(session_id, persona_id, user_id)
            
            # Share insight
            success = self.integration.share_insight_in_session(
                session_id=session_id,
                persona_id=persona_id,
                insight_type="knowledge",
                content="This is a test insight about data analysis",
                relevance_score=0.8,
                context={"topic": "data_analysis"},
                tags=["insight", "test"]
            )
            
            self.assertTrue(success)
            
            # Verify insight was tracked
            insights = self.integration.get_session_insights(session_id)
            self.assertEqual(len(insights), 1)
            insight = insights[0]
            self.assertEqual(insight.session_id, session_id)
            self.assertEqual(insight.persona_id, persona_id)
            self.assertEqual(insight.insight_type, "knowledge")
            
        except Exception as e:
            self.fail(f"Insight sharing failed: {str(e)}")
    
    def test_performance_tracking(self):
        """Test performance tracking in sessions."""
        try:
            session_id = "test-session-003"
            persona_id = self.persona1.memory.persona_id
            user_id = "user-789"
            
            # Add persona to session
            self.integration.add_persona_to_session(session_id, persona_id, user_id)
            
            # Record performance
            self.integration.record_session_performance(
                session_id=session_id,
                persona_id=persona_id,
                task="Session Task",
                score=85,
                user_feedback="Good performance in session",
                success=True,
                duration=1800.0,
                context={"session_type": "collaborative"}
            )
            
            # Get performance summary
            summary = self.integration.get_session_performance_summary(session_id)
            
            # Verify summary
            self.assertIn("session_id", summary)
            self.assertIn("participants", summary)
            self.assertIn(persona_id, summary["participants"])
            
            participant_summary = summary["participants"][persona_id]
            self.assertEqual(participant_summary["tasks_completed"], 1)
            self.assertEqual(participant_summary["average_score"], 85)
            self.assertEqual(participant_summary["success_rate"], 1.0)
            
        except Exception as e:
            self.fail(f"Performance tracking failed: {str(e)}")
    
    def test_integration_status(self):
        """Test integration status reporting."""
        try:
            # Get integration status
            status = self.integration.get_integration_status()
            
            # Verify status structure
            self.assertIn("registered_personas", status)
            self.assertIn("active_sessions", status)
            self.assertIn("total_insights_shared", status)
            self.assertIn("persona_performance_tiers", status)
            self.assertIn("session_participation", status)
            
            # Verify values
            self.assertEqual(status["registered_personas"], 2)
            self.assertEqual(status["active_sessions"], 0)
            self.assertEqual(status["total_insights_shared"], 0)
            
        except Exception as e:
            self.fail(f"Integration status failed: {str(e)}")


def run_mimic_ecosystem_tests():
    """Run all Mimic ecosystem tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestMimicPersonaGeneration,
        TestMimicPerformanceAnalytics,
        TestMimicPersonaForking,
        TestMimicKnowledgeIndexing,
        TestMimicPluginExtensions,
        TestMimicSchemaValidation,
        TestMimicCoreIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return results
    return {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "success_rate": (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun if result.testsRun > 0 else 0
    }


if __name__ == "__main__":
    print("🧪 Mimic Persona Ecosystem Test Suite")
    print("=" * 50)
    
    results = run_mimic_ecosystem_tests()
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Tests Run: {results['tests_run']}")
    print(f"Failures: {results['failures']}")
    print(f"Errors: {results['errors']}")
    print(f"Success Rate: {results['success_rate']:.1%}")
    
    if results['failures'] == 0 and results['errors'] == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        exit(1) 