#!/usr/bin/env python3
"""
Embedding Generation Tests for Semantic Retrieval System
Tests embedding quality, consistency, and performance
"""

import pytest
import numpy as np
import time
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import asyncio
import psycopg2
from sklearn.metrics.pairwise import cosine_similarity

class TestEmbeddingGeneration:
    
    @pytest.fixture(scope="class")
    def model(self):
        """Load the embedding model"""
        return SentenceTransformer('all-MiniLM-L6-v2')
    
    @pytest.fixture(scope="class") 
    def postgres_conn(self):
        """Create PostgreSQL connection"""
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='hearthlink_test_semantic',
            user='postgres',
            password='hearthlink_test_pass'
        )
        yield conn
        conn.close()
        
    @pytest.fixture(scope="class")
    def test_texts(self):
        """Sample texts for testing"""
        return [
            "User wants to schedule a meeting for tomorrow at 3 PM",
            "The database connection is experiencing timeout issues",
            "System performance has degraded significantly over the past hour",
            "New feature request: Add dark mode to the user interface",
            "Security alert: Unusual login activity detected from unknown IP",
            "Memory usage is approaching critical levels on server",
            "API response times have increased by 200% since last deployment",
            "User authentication failed due to expired credentials",
            "Scheduled backup completed successfully with no errors",
            "Configuration update required for new SSL certificates"
        ]
        
    def test_embedding_dimension(self, model):
        """Test that embeddings have correct dimensions"""
        text = "Test embedding dimension"
        embedding = model.encode([text])[0]
        
        assert embedding.shape == (384,), f"Expected 384 dimensions, got {embedding.shape}"
        assert embedding.dtype == np.float32, f"Expected float32, got {embedding.dtype}"
        
    def test_embedding_consistency(self, model):
        """Test that same text produces consistent embeddings"""
        text = "Consistent embedding test"
        
        embedding1 = model.encode([text])[0]
        embedding2 = model.encode([text])[0]
        
        similarity = cosine_similarity([embedding1], [embedding2])[0][0]
        assert similarity > 0.99, f"Embeddings should be nearly identical, similarity: {similarity}"
        
    def test_embedding_similarity(self, model):
        """Test that similar texts have higher similarity"""
        similar_texts = [
            "Schedule a meeting for tomorrow",
            "Set up a meeting for next day"
        ]
        
        different_texts = [
            "Schedule a meeting for tomorrow", 
            "Database connection error occurred"
        ]
        
        similar_embeddings = model.encode(similar_texts)
        different_embeddings = model.encode(different_texts)
        
        similar_similarity = cosine_similarity([similar_embeddings[0]], [similar_embeddings[1]])[0][0]
        different_similarity = cosine_similarity([different_embeddings[0]], [different_embeddings[1]])[0][0]
        
        assert similar_similarity > different_similarity, \
            f"Similar texts should have higher similarity: {similar_similarity} vs {different_similarity}"
            
    def test_batch_embedding_generation(self, model, test_texts):
        """Test batch embedding generation"""
        start_time = time.perf_counter()
        embeddings = model.encode(test_texts)
        end_time = time.perf_counter()
        
        batch_time = end_time - start_time
        
        assert len(embeddings) == len(test_texts), "Should generate embedding for each text"
        assert all(emb.shape == (384,) for emb in embeddings), "All embeddings should have correct shape"
        assert batch_time < 5.0, f"Batch generation should be fast, took {batch_time:.3f}s"
        
    def test_individual_embedding_generation(self, model, test_texts):
        """Test individual embedding generation and compare with batch"""
        # Generate individually
        start_time = time.perf_counter()
        individual_embeddings = []
        for text in test_texts:
            embedding = model.encode([text])[0]
            individual_embeddings.append(embedding)
        individual_time = time.perf_counter() - start_time
        
        # Generate in batch
        start_time = time.perf_counter()
        batch_embeddings = model.encode(test_texts)
        batch_time = time.perf_counter() - start_time
        
        # Compare consistency
        for i, (ind_emb, batch_emb) in enumerate(zip(individual_embeddings, batch_embeddings)):
            similarity = cosine_similarity([ind_emb], [batch_emb])[0][0]
            assert similarity > 0.99, f"Individual and batch embeddings should match for text {i}"
            
        # Batch should be faster
        assert batch_time < individual_time, f"Batch should be faster: {batch_time:.3f}s vs {individual_time:.3f}s"
        
    @pytest.mark.benchmark(group="embedding-generation")
    def test_embedding_generation_performance(self, benchmark, model):
        """Benchmark embedding generation performance"""
        test_text = "Performance test for embedding generation"
        
        def generate_embedding():
            return model.encode([test_text])[0]
            
        result = benchmark(generate_embedding)
        assert result.shape == (384,), "Should return correct embedding shape"
        
    @pytest.mark.benchmark(group="batch-embedding")
    def test_batch_embedding_performance(self, benchmark, model, test_texts):
        """Benchmark batch embedding generation performance"""
        
        def generate_batch_embeddings():
            return model.encode(test_texts)
            
        result = benchmark(generate_batch_embeddings)
        assert len(result) == len(test_texts), "Should generate all embeddings"
        
    def test_embedding_normalization(self, model):
        """Test that embeddings are properly normalized"""
        texts = [
            "Short text",
            "This is a much longer text that contains more words and should test normalization across different text lengths",
            "Medium length text with some details"
        ]
        
        embeddings = model.encode(texts)
        
        for i, embedding in enumerate(embeddings):
            norm = np.linalg.norm(embedding)
            # Embeddings should be approximately unit normalized
            assert 0.8 <= norm <= 1.2, f"Embedding {i} norm should be close to 1, got {norm}"
            
    def test_embedding_storage_format(self, model, postgres_conn):
        """Test storing and retrieving embeddings from PostgreSQL"""
        cursor = postgres_conn.cursor()
        
        # Create test table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_embeddings (
                id SERIAL PRIMARY KEY,
                content TEXT,
                embedding VECTOR(384)
            )
        """)
        
        # Clear test data
        cursor.execute("DELETE FROM test_embeddings")
        
        # Generate and store embedding
        test_text = "Test embedding storage in PostgreSQL"
        embedding = model.encode([test_text])[0]
        
        cursor.execute("""
            INSERT INTO test_embeddings (content, embedding)
            VALUES (%s, %s)
        """, (test_text, embedding.tolist()))
        
        postgres_conn.commit()
        
        # Retrieve and verify
        cursor.execute("SELECT content, embedding FROM test_embeddings WHERE id = (SELECT MAX(id) FROM test_embeddings)")
        stored_content, stored_embedding = cursor.fetchone()
        
        assert stored_content == test_text, "Content should match"
        
        # Convert back to numpy array and check similarity
        retrieved_embedding = np.array(stored_embedding, dtype=np.float32)
        similarity = cosine_similarity([embedding], [retrieved_embedding])[0][0]
        
        assert similarity > 0.99, f"Stored and retrieved embeddings should match, similarity: {similarity}"
        
        # Cleanup
        cursor.execute("DROP TABLE test_embeddings")
        postgres_conn.commit()
        
    def test_semantic_search_quality(self, model, postgres_conn):
        """Test semantic search quality with known similar/dissimilar pairs"""
        cursor = postgres_conn.cursor()
        
        # Create test table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS semantic_test (
                id SERIAL PRIMARY KEY,
                content TEXT,
                embedding VECTOR(384),
                category VARCHAR(50)
            )
        """)
        
        cursor.execute("DELETE FROM semantic_test")
        
        # Test data with categories
        test_data = [
            ("Schedule a meeting with the team", "scheduling"),
            ("Book a conference room for tomorrow", "scheduling"), 
            ("Set up a team meeting next week", "scheduling"),
            ("Database connection timeout error", "database"),
            ("SQL query performance issues", "database"),
            ("Database server is down", "database"),
            ("User interface needs dark mode", "ui"),
            ("Update the website design", "ui"),
            ("Improve user experience", "ui")
        ]
        
        # Insert test data
        for content, category in test_data:
            embedding = model.encode([content])[0]
            cursor.execute("""
                INSERT INTO semantic_test (content, embedding, category)
                VALUES (%s, %s, %s)
            """, (content, embedding.tolist(), category))
            
        postgres_conn.commit()
        
        # Test semantic search
        query = "organize a team meeting"
        query_embedding = model.encode([query])[0]
        
        cursor.execute("""
            SELECT content, category, embedding <-> %s as distance
            FROM semantic_test
            ORDER BY embedding <-> %s
            LIMIT 3
        """, (query_embedding.tolist(), query_embedding.tolist()))
        
        results = cursor.fetchall()
        
        # Top 3 results should be scheduling-related
        scheduling_results = [r for r in results if r[1] == 'scheduling']
        assert len(scheduling_results) >= 2, "Should find scheduling-related content in top results"
        
        # First result should be most relevant
        assert results[0][1] == 'scheduling', "Most relevant result should be scheduling-related"
        
        # Cleanup
        cursor.execute("DROP TABLE semantic_test")
        postgres_conn.commit()
        
    def test_multi_language_embeddings(self, model):
        """Test embedding generation for different languages (if supported)"""
        # Test with English and simple variations
        texts = [
            "Hello world",
            "Good morning everyone", 
            "How are you today?",
            "Thank you very much",
            "Please help me with this"
        ]
        
        embeddings = model.encode(texts)
        
        # All should generate valid embeddings
        for i, embedding in enumerate(embeddings):
            assert embedding.shape == (384,), f"Text {i} should generate valid embedding"
            assert not np.isnan(embedding).any(), f"Text {i} embedding should not contain NaN"
            assert not np.isinf(embedding).any(), f"Text {i} embedding should not contain Inf"
            
    def test_empty_and_special_text_handling(self, model):
        """Test handling of empty strings and special characters"""
        special_texts = [
            "",  # Empty string
            " ",  # Just whitespace
            "!!!",  # Just punctuation
            "123456",  # Just numbers
            "🚀 emoji test 📊",  # With emojis
            "Text with\nnewlines\tand\ttabs",  # With special chars
        ]
        
        embeddings = model.encode(special_texts)
        
        for i, embedding in enumerate(embeddings):
            assert embedding.shape == (384,), f"Special text {i} should generate valid embedding"
            assert not np.isnan(embedding).any(), f"Special text {i} should not contain NaN"
            
    @pytest.mark.asyncio
    async def test_async_embedding_generation(self, model, test_texts):
        """Test asynchronous embedding generation simulation"""
        
        async def generate_async_embedding(text):
            # Simulate async operation
            await asyncio.sleep(0.001)
            return model.encode([text])[0]
            
        # Generate embeddings concurrently
        tasks = [generate_async_embedding(text) for text in test_texts[:5]]
        embeddings = await asyncio.gather(*tasks)
        
        assert len(embeddings) == 5, "Should generate all embeddings"
        for embedding in embeddings:
            assert embedding.shape == (384,), "Should have correct shape"