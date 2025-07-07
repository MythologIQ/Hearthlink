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

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from personas.mimic import (
    MimicPersona, MimicError, PersonaGenerationError, PerformanceAnalyticsError,
    PersonaForkError, KnowledgeIndexError, PluginExtensionError,
    CoreTraits, PerformanceTier, PersonaStatus, MimicPersonaMemory
)
from vault.mimic_schema import (
    MimicSchemaManager, validate_mimic_memory, migrate_mimic_memory,
    create_mimic_memory_slice
)
from core.mimic_integration import MimicCoreIntegration, MimicIntegrationError
from main import HearthlinkLogger


class TestMimicPersonaGeneration(unittest.TestCase):
    """Test Mimic persona generation functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = HearthlinkLogger()
        
        # Mock LLM client
        self.mock_llm_client = Mock()
        
        # Create test persona
        self.persona = MimicPersona(self.mock_llm_client, self.logger)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_persona_generation_basic(self):
        """Test basic persona generation."""
        try:
            # Generate persona with basic parameters
            persona_id = self.persona.generate_persona(
                role="researcher",
                context={"description": "Academic research assistant"}
            )
            
            # Verify persona was created
            self.assertIsNotNone(persona_id)
            self.assertTrue(persona_id.startswith("mimic-"))
            self.assertEqual(len(persona_id), 13)  # mimic- + 8 hex chars
            
        except Exception as e:
            self.fail(f"Persona generation failed: {str(e)}")
    
    def test_persona_generation_with_traits(self):
        """Test persona generation with custom traits."""
        try:
            base_traits = {
                "focus": 85,
                "creativity": 70,
                "precision": 90,
                "humor": 20,
                "empathy": 60,
                "assertiveness": 75,
                "adaptability": 80,
                "collaboration": 65
            }
            
            persona_id = self.persona.generate_persona(
                role="analyst",
                context={"requires_precision": True, "requires_creativity": True},
                base_traits=base_traits
            )
            
            self.assertIsNotNone(persona_id)
            
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
                context={"domain": "business_strategy"},
                user_preferences=user_preferences
            )
            
            self.assertIsNotNone(persona_id)
            
        except Exception as e:
            self.fail(f"Persona generation with preferences failed: {str(e)}")
    
    def test_persona_generation_error_handling(self):
        """Test error handling in persona generation."""
        try:
            # Test with invalid role
            with self.assertRaises(PersonaGenerationError):
                self.persona.generate_persona(role="", context={})
            
        except Exception as e:
            self.fail(f"Error handling test failed: {str(e)}")


class TestMimicPerformanceAnalytics(unittest.TestCase):
    """Test Mimic performance analytics functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = HearthlinkLogger()
        self.mock_llm_client = Mock()
        self.persona = MimicPersona(self.mock_llm_client, self.logger)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_performance_recording(self):
        """Test performance recording functionality."""
        try:
            # Record performance
            self.persona.record_performance(
                session_id="test-session-001",
                task="Data Analysis",
                score=85,
                user_feedback="Excellent analysis, very thorough",
                success=True,
                duration=1800.0,  # 30 minutes
                context={"dataset_size": "large", "complexity": "high"}
            )
            
            # Verify performance was recorded
            self.assertEqual(len(self.persona.memory.performance_history), 1)
            record = self.persona.memory.performance_history[0]
            self.assertEqual(record.session_id, "test-session-001")
            self.assertEqual(record.score, 85)
            self.assertTrue(record.success)
            
        except Exception as e:
            self.fail(f"Performance recording failed: {str(e)}")
    
    def test_growth_stats_update(self):
        """Test growth statistics update."""
        try:
            # Record multiple performances
            for i in range(5):
                self.persona.record_performance(
                    session_id=f"test-session-{i:03d}",
                    task=f"Task {i}",
                    score=70 + i * 5,
                    user_feedback=f"Good work on task {i}",
                    success=True,
                    duration=900.0
                )
            
            # Verify growth stats
            stats = self.persona.memory.growth_stats
            self.assertEqual(stats.sessions_completed, 5)
            self.assertEqual(stats.unique_tasks, 5)
            self.assertEqual(stats.repeat_tasks, 0)
            self.assertGreater(stats.total_usage_time, 0.0)
            
        except Exception as e:
            self.fail(f"Growth stats update failed: {str(e)}")
    
    def test_performance_analytics_generation(self):
        """Test performance analytics generation."""
        try:
            # Record some performance data
            for i in range(10):
                self.persona.record_performance(
                    session_id=f"test-session-{i:03d}",
                    task=f"Task {i}",
                    score=75 + (i % 20),
                    user_feedback=f"Feedback {i}",
                    success=i % 3 != 0,  # Some failures
                    duration=1200.0
                )
            
            # Generate analytics
            analytics = self.persona.get_performance_analytics()
            
            # Verify analytics structure
            self.assertIn("persona_id", analytics)
            self.assertIn("total_sessions", analytics)
            self.assertIn("average_score", analytics)
            self.assertIn("success_rate", analytics)
            self.assertIn("performance_trend", analytics)
            self.assertIn("recommendations", analytics)
            
            # Verify analytics values
            self.assertEqual(analytics["total_sessions"], 10)
            self.assertGreater(analytics["average_score"], 0)
            self.assertLessEqual(analytics["average_score"], 100)
            self.assertGreater(analytics["success_rate"], 0)
            self.assertLessEqual(analytics["success_rate"], 1)
            
        except Exception as e:
            self.fail(f"Performance analytics generation failed: {str(e)}")
    
    def test_performance_tier_calculation(self):
        """Test performance tier calculation."""
        try:
            # Test unstable tier (no performance data)
            tier = self.persona.get_performance_tier()
            self.assertEqual(tier, PerformanceTier.UNSTABLE)
            
            # Add some poor performance
            for i in range(3):
                self.persona.record_performance(
                    session_id=f"poor-session-{i}",
                    task=f"Poor Task {i}",
                    score=30 + i * 5,
                    user_feedback="Needs improvement",
                    success=False,
                    duration=600.0
                )
            
            tier = self.persona.get_performance_tier()
            self.assertEqual(tier, PerformanceTier.UNSTABLE)
            
            # Add good performance
            for i in range(10):
                self.persona.record_performance(
                    session_id=f"good-session-{i}",
                    task=f"Good Task {i}",
                    score=85 + i * 2,
                    user_feedback="Excellent work",
                    success=True,
                    duration=900.0
                )
            
            tier = self.persona.get_performance_tier()
            self.assertIn(tier, [PerformanceTier.STABLE, PerformanceTier.EXCELLENT])
            
        except Exception as e:
            self.fail(f"Performance tier calculation failed: {str(e)}")


class TestMimicPersonaForking(unittest.TestCase):
    """Test Mimic persona forking functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = HearthlinkLogger()
        self.mock_llm_client = Mock()
        self.persona = MimicPersona(self.mock_llm_client, self.logger)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_persona_forking_basic(self):
        """Test basic persona forking."""
        try:
            # Create source persona with some data
            source_persona_id = self.persona.generate_persona(
                role="researcher",
                context={"domain": "AI ethics"}
            )
            
            # Add some performance data
            self.persona.record_performance(
                session_id="source-session",
                task="Research Analysis",
                score=85,
                user_feedback="Good research",
                success=True,
                duration=1800.0
            )
            
            # Fork the persona
            modifications = {
                "name": "Specialized Researcher",
                "description": "Focused on AI safety research",
                "tags": ["ai_safety", "specialized"]
            }
            
            forked_persona_id = self.persona.fork_persona(
                source_persona_id=source_persona_id,
                new_role="AI Safety Researcher",
                modifications=modifications
            )
            
            # Verify forked persona
            self.assertIsNotNone(forked_persona_id)
            self.assertNotEqual(forked_persona_id, source_persona_id)
            self.assertTrue(forked_persona_id.startswith("mimic-"))
            
        except Exception as e:
            self.fail(f"Persona forking failed: {str(e)}")
    
    def test_persona_forking_with_trait_modifications(self):
        """Test persona forking with trait modifications."""
        try:
            # Create source persona
            source_persona_id = self.persona.generate_persona(
                role="analyst",
                context={"domain": "data_analysis"}
            )
            
            # Fork with trait modifications
            modifications = {
                "traits": {
                    "focus": 95,
                    "creativity": 60,
                    "precision": 90,
                    "humor": 10,
                    "empathy": 40,
                    "assertiveness": 80,
                    "adaptability": 70,
                    "collaboration": 50
                },
                "name": "Precision Analyst",
                "description": "Highly focused precision analyst"
            }
            
            forked_persona_id = self.persona.fork_persona(
                source_persona_id=source_persona_id,
                new_role="Precision Data Analyst",
                modifications=modifications
            )
            
            self.assertIsNotNone(forked_persona_id)
            
        except Exception as e:
            self.fail(f"Persona forking with traits failed: {str(e)}")
    
    def test_persona_merging(self):
        """Test persona merging functionality."""
        try:
            # Create two personas
            persona1_id = self.persona.generate_persona(
                role="researcher",
                context={"domain": "machine_learning"}
            )
            
            persona2_id = self.persona.generate_persona(
                role="analyst",
                context={"domain": "data_visualization"}
            )
            
            # Merge personas
            merged_persona_id = self.persona.merge_personas(
                primary_persona_id=persona1_id,
                secondary_persona_id=persona2_id,
                merge_strategy="selective"
            )
            
            # Verify merged persona
            self.assertIsNotNone(merged_persona_id)
            self.assertNotEqual(merged_persona_id, persona1_id)
            self.assertNotEqual(merged_persona_id, persona2_id)
            
        except Exception as e:
            self.fail(f"Persona merging failed: {str(e)}")
    
    def test_persona_merging_strategies(self):
        """Test different persona merging strategies."""
        try:
            # Create source personas
            persona1_id = self.persona.generate_persona(
                role="creative_writer",
                context={"style": "narrative"}
            )
            
            persona2_id = self.persona.generate_persona(
                role="technical_writer",
                context={"style": "documentation"}
            )
            
            # Test selective merging
            selective_merged = self.persona.merge_personas(
                primary_persona_id=persona1_id,
                secondary_persona_id=persona2_id,
                merge_strategy="selective"
            )
            
            # Test comprehensive merging
            comprehensive_merged = self.persona.merge_personas(
                primary_persona_id=persona1_id,
                secondary_persona_id=persona2_id,
                merge_strategy="comprehensive"
            )
            
            # Test hybrid merging
            hybrid_merged = self.persona.merge_personas(
                primary_persona_id=persona1_id,
                secondary_persona_id=persona2_id,
                merge_strategy="hybrid"
            )
            
            # Verify all merges created different personas
            merged_ids = {selective_merged, comprehensive_merged, hybrid_merged}
            self.assertEqual(len(merged_ids), 3)
            
        except Exception as e:
            self.fail(f"Persona merging strategies failed: {str(e)}")


class TestMimicKnowledgeIndexing(unittest.TestCase):
    """Test Mimic knowledge indexing functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = HearthlinkLogger()
        self.mock_llm_client = Mock()
        self.persona = MimicPersona(self.mock_llm_client, self.logger)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_knowledge_index_initialization(self):
        """Test knowledge index initialization."""
        try:
            # Verify default knowledge index
            self.assertGreater(len(self.persona.memory.relevance_index), 0)
            
            # Check for default topics
            topic_names = [topic.topic for topic in self.persona.memory.relevance_index]
            expected_topics = ["general_knowledge", "task_specific", "user_preferences"]
            
            for topic in expected_topics:
                self.assertIn(topic, topic_names)
            
        except Exception as e:
            self.fail(f"Knowledge index initialization failed: {str(e)}")
    
    def test_relevance_index_update(self):
        """Test relevance index update during performance recording."""
        try:
            # Record performance with specific context
            self.persona.record_performance(
                session_id="research-session",
                task="AI Ethics Research",
                score=85,
                user_feedback="Excellent research on AI ethics",
                success=True,
                duration=3600.0,
                context={"topics": ["ai_ethics", "research_analysis"]}
            )
            
            # Verify relevance index was updated
            topic_scores = {topic.topic: topic.score for topic in self.persona.memory.relevance_index}
            
            # Check if AI ethics topic was added or updated
            ai_ethics_topics = [topic for topic in self.persona.memory.relevance_index 
                              if "ai_ethics" in topic.topic.lower()]
            self.assertGreater(len(ai_ethics_topics), 0)
            
        except Exception as e:
            self.fail(f"Relevance index update failed: {str(e)}")
    
    def test_custom_knowledge_management(self):
        """Test custom knowledge management."""
        try:
            # Add custom knowledge
            knowledge_content = "Advanced machine learning techniques for natural language processing"
            knowledge_tags = ["machine_learning", "nlp", "advanced"]
            
            # Simulate adding knowledge (this would normally be done through API)
            from personas.mimic import KnowledgeSummary
            
            knowledge = KnowledgeSummary(
                doc_id=f"doc-{uuid.uuid4().hex[:8]}",
                summary=knowledge_content,
                relevance_score=0.8,
                tags=knowledge_tags,
                created_at=datetime.now().isoformat()
            )
            
            self.persona.memory.custom_knowledge.append(knowledge)
            
            # Verify knowledge was added
            self.assertEqual(len(self.persona.memory.custom_knowledge), 1)
            added_knowledge = self.persona.memory.custom_knowledge[0]
            self.assertEqual(added_knowledge.summary, knowledge_content)
            self.assertEqual(added_knowledge.tags, knowledge_tags)
            
        except Exception as e:
            self.fail(f"Custom knowledge management failed: {str(e)}")


class TestMimicPluginExtensions(unittest.TestCase):
    """Test Mimic plugin extension functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = HearthlinkLogger()
        self.mock_llm_client = Mock()
        self.persona = MimicPersona(self.mock_llm_client, self.logger)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_plugin_extension_addition(self):
        """Test adding plugin extensions."""
        try:
            # Add plugin extension
            self.persona.add_plugin_extension(
                plugin_id="summarizer-v1",
                name="Text Summarizer",
                version="1.0.0",
                permissions=["read_documents", "write_summaries"],
                performance_impact=0.1
            )
            
            # Verify plugin was added
            self.assertEqual(len(self.persona.memory.plugin_extensions), 1)
            plugin = self.persona.memory.plugin_extensions[0]
            self.assertEqual(plugin.plugin_id, "summarizer-v1")
            self.assertEqual(plugin.name, "Text Summarizer")
            self.assertEqual(plugin.version, "1.0.0")
            self.assertTrue(plugin.enabled)
            
        except Exception as e:
            self.fail(f"Plugin extension addition failed: {str(e)}")
    
    def test_plugin_extension_update(self):
        """Test updating existing plugin extensions."""
        try:
            # Add initial plugin
            self.persona.add_plugin_extension(
                plugin_id="analyzer-v1",
                name="Data Analyzer",
                version="1.0.0",
                permissions=["read_data"],
                performance_impact=0.0
            )
            
            # Update plugin
            self.persona.add_plugin_extension(
                plugin_id="analyzer-v1",
                name="Advanced Data Analyzer",
                version="2.0.0",
                permissions=["read_data", "write_reports"],
                performance_impact=0.2
            )
            
            # Verify plugin was updated
            self.assertEqual(len(self.persona.memory.plugin_extensions), 1)
            plugin = self.persona.memory.plugin_extensions[0]
            self.assertEqual(plugin.name, "Advanced Data Analyzer")
            self.assertEqual(plugin.version, "2.0.0")
            self.assertEqual(len(plugin.permissions), 2)
            
        except Exception as e:
            self.fail(f"Plugin extension update failed: {str(e)}")
    
    def test_multiple_plugin_extensions(self):
        """Test managing multiple plugin extensions."""
        try:
            # Add multiple plugins
            plugins = [
                ("summarizer-v1", "Text Summarizer", "1.0.0", ["read_documents"], 0.1),
                ("translator-v1", "Language Translator", "1.0.0", ["read_text"], 0.05),
                ("analyzer-v1", "Data Analyzer", "1.0.0", ["read_data"], 0.0)
            ]
            
            for plugin_id, name, version, permissions, impact in plugins:
                self.persona.add_plugin_extension(
                    plugin_id=plugin_id,
                    name=name,
                    version=version,
                    permissions=permissions,
                    performance_impact=impact
                )
            
            # Verify all plugins were added
            self.assertEqual(len(self.persona.memory.plugin_extensions), 3)
            
            # Check plugin names
            plugin_names = [plugin.name for plugin in self.persona.memory.plugin_extensions]
            expected_names = ["Text Summarizer", "Language Translator", "Data Analyzer"]
            self.assertEqual(set(plugin_names), set(expected_names))
            
        except Exception as e:
            self.fail(f"Multiple plugin extensions failed: {str(e)}")


class TestMimicSchemaValidation(unittest.TestCase):
    """Test Mimic schema validation functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.schema_manager = MimicSchemaManager()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_memory_validation_valid(self):
        """Test validation of valid memory data."""
        try:
            # Create valid memory data
            memory_data = {
                "persona_id": "mimic-test123",
                "user_id": "user-123",
                "schema_version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "persona_name": "Test Persona",
                "role": "Tester",
                "description": "Test persona for validation",
                "status": "draft",
                "core_traits": {
                    "focus": 50, "creativity": 50, "precision": 50, "humor": 25,
                    "empathy": 50, "assertiveness": 50, "adaptability": 50, "collaboration": 50
                },
                "growth_stats": {
                    "sessions_completed": 0, "unique_tasks": 0, "repeat_tasks": 0,
                    "usage_streak": 0, "total_usage_time": 0.0, "last_used": None,
                    "created_at": datetime.now().isoformat(), "growth_rate": 0.0, "skill_decay_rate": 0.05
                },
                "performance_history": [],
                "relevance_index": [],
                "custom_knowledge": [],
                "plugin_extensions": [],
                "archived_sessions": [],
                "user_tags": [],
                "editable_fields": ["persona_name", "role", "description", "tags"],
                "audit_log": [],
                "parent_persona_id": None,
                "forked_from": None,
                "merged_into": None,
                "fork_history": []
            }
            
            # Validate memory
            is_valid = validate_mimic_memory(memory_data)
            self.assertTrue(is_valid)
            
        except Exception as e:
            self.fail(f"Valid memory validation failed: {str(e)}")
    
    def test_memory_validation_invalid(self):
        """Test validation of invalid memory data."""
        try:
            # Create invalid memory data (missing required fields)
            memory_data = {
                "persona_id": "mimic-test123",
                # Missing user_id, schema_version, etc.
            }
            
            # Validate memory should fail
            with self.assertRaises(SchemaValidationError):
                validate_mimic_memory(memory_data)
            
        except Exception as e:
            self.fail(f"Invalid memory validation test failed: {str(e)}")
    
    def test_memory_creation(self):
        """Test memory slice creation."""
        try:
            # Create memory slice
            memory = create_mimic_memory_slice(
                persona_id="mimic-new123",
                user_id="user-456",
                persona_name="New Persona",
                role="Creator"
            )
            
            # Verify memory
            self.assertEqual(memory.persona_id, "mimic-new123")
            self.assertEqual(memory.user_id, "user-456")
            self.assertEqual(memory.persona_name, "New Persona")
            self.assertEqual(memory.role, "Creator")
            self.assertEqual(memory.schema_version, "1.0.0")
            
            # Validate memory
            memory.validate()
            
        except Exception as e:
            self.fail(f"Memory creation failed: {str(e)}")
    
    def test_schema_migration(self):
        """Test schema migration functionality."""
        try:
            # Create old format memory data
            old_memory_data = {
                "persona_id": "mimic-old123",
                "user_id": "user-789",
                "persona_name": "Old Persona",
                "role": "Legacy"
                # Missing new fields
            }
            
            # Migrate to current version
            migrated_data = migrate_mimic_memory(old_memory_data, "1.0.0")
            
            # Verify migration
            self.assertEqual(migrated_data["schema_version"], "1.0.0")
            self.assertIn("status", migrated_data)
            self.assertIn("core_traits", migrated_data)
            self.assertIn("growth_stats", migrated_data)
            
            # Validate migrated data
            validate_mimic_memory(migrated_data)
            
        except Exception as e:
            self.fail(f"Schema migration failed: {str(e)}")


class TestMimicCoreIntegration(unittest.TestCase):
    """Test Mimic-Core integration functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = HearthlinkLogger()
        
        # Mock Core instance
        self.mock_core = Mock()
        self.mock_core.add_participant.return_value = True
        self.mock_core.remove_participant.return_value = True
        self.mock_core.share_insight.return_value = True
        
        # Create integration
        self.integration = MimicCoreIntegration(self.mock_core, self.logger)
        
        # Create test personas
        self.mock_llm_client = Mock()
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