#!/usr/bin/env python3
"""
Memory Pruning Manager

Implements intelligent conversation cleanup and memory management:
- Automated cleanup of old conversations
- Configurable retention policies  
- Smart pruning based on importance scores
- Memory usage optimization
- Conversation archival

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import HearthlinkLogger, HearthlinkError


class MemoryPruningError(HearthlinkError):
    """Exception raised for memory pruning errors."""
    pass


@dataclass
class ConversationMetrics:
    """Metrics for conversation importance scoring."""
    session_id: str
    message_count: int
    total_characters: int
    duration_hours: float
    last_activity: str
    user_engagement_score: float  # 0.0 to 1.0
    correction_events: int
    positive_feedback: int
    negative_feedback: int
    importance_score: float  # Calculated composite score


@dataclass
class PruningReport:
    """Report of memory pruning operation."""
    operation_id: str
    timestamp: str
    conversations_analyzed: int
    conversations_pruned: int
    conversations_archived: int
    bytes_freed: int
    retention_policy: str
    pruning_duration: float
    errors: List[str]


class MemoryPruningManager:
    """
    Intelligent memory pruning manager for conversation cleanup.
    
    Features:
    - Smart importance scoring to preserve valuable conversations
    - Configurable retention policies
    - Gradual pruning to avoid performance impact
    - Conversation archival for important but old content
    - Memory usage optimization
    """
    
    def __init__(self, project_root: Optional[Path] = None, logger: Optional[HearthlinkLogger] = None):
        """
        Initialize memory pruning manager.
        
        Args:
            project_root: Root directory of project (auto-detected if None)
            logger: Optional logger instance
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger or HearthlinkLogger()
        
        # Database paths
        self.database_path = self.project_root / "hearthlink_data" / "hearthlink.db"
        self.vault_path = self.project_root / "hearthlink_data" / "vault_storage"
        
        # Archive directory for important conversations
        self.archive_path = self.project_root / "hearthlink_data" / "conversation_archive"
        self.archive_path.mkdir(exist_ok=True)
        
        # Pruning configuration
        self.retention_policies = {
            "aggressive": {
                "max_age_days": 7,
                "max_conversations": 50,
                "importance_threshold": 0.3,
                "archive_threshold": 0.7
            },
            "moderate": {
                "max_age_days": 30,
                "max_conversations": 200,
                "importance_threshold": 0.2,
                "archive_threshold": 0.6
            },
            "conservative": {
                "max_age_days": 90,
                "max_conversations": 500,
                "importance_threshold": 0.1,
                "archive_threshold": 0.5
            }
        }
        
        self.current_policy = "moderate"
        
        self.logger.logger.info("Memory pruning manager initialized", 
                              extra={"extra_fields": {
                                  "event_type": "memory_pruning_init",
                                  "database_path": str(self.database_path),
                                  "vault_path": str(self.vault_path),
                                  "archive_path": str(self.archive_path),
                                  "policy": self.current_policy
                              }})
    
    def analyze_conversations(self) -> List[ConversationMetrics]:
        """
        Analyze all conversations to calculate importance scores.
        
        Returns:
            List[ConversationMetrics]: Metrics for each conversation
        """
        conversations = []
        
        try:
            # Analyze database conversations
            db_conversations = self._analyze_database_conversations()
            conversations.extend(db_conversations)
            
            # Analyze vault conversations
            vault_conversations = self._analyze_vault_conversations()
            conversations.extend(vault_conversations)
            
            # Calculate importance scores
            for conv in conversations:
                conv.importance_score = self._calculate_importance_score(conv)
            
            # Sort by importance score (highest first)
            conversations.sort(key=lambda x: x.importance_score, reverse=True)
            
            self.logger.logger.info("Conversation analysis completed", 
                                  extra={"extra_fields": {
                                      "event_type": "conversation_analysis",
                                      "total_conversations": len(conversations),
                                      "avg_importance": sum(c.importance_score for c in conversations) / len(conversations) if conversations else 0
                                  }})
            
            return conversations
            
        except Exception as e:
            self.logger.log_error(e, "conversation_analysis_error")
            return []
    
    def _analyze_database_conversations(self) -> List[ConversationMetrics]:
        """Analyze conversations stored in SQLite database."""
        conversations = []
        
        if not self.database_path.exists():
            return conversations
        
        try:
            with sqlite3.connect(str(self.database_path)) as conn:
                cursor = conn.cursor()
                
                # Get conversation data (assuming a conversation_history table exists)
                try:
                    cursor.execute("""
                        SELECT session_id, COUNT(*) as message_count, 
                               SUM(LENGTH(message)) as total_chars,
                               MIN(timestamp) as first_message,
                               MAX(timestamp) as last_message
                        FROM conversation_history 
                        GROUP BY session_id
                    """)
                    for row in cursor.fetchall():
                        session_id, msg_count, total_chars, first_msg, last_msg = row
                        
                        # Calculate duration
                        try:
                            first_time = datetime.fromisoformat(first_msg)
                            last_time = datetime.fromisoformat(last_msg)
                            duration = (last_time - first_time).total_seconds() / 3600
                        except:
                            duration = 0.0
                        
                        # Get feedback data
                        cursor.execute("""
                            SELECT COUNT(*) FROM correction_events 
                            WHERE session_id = ? AND event_type = 'positive'
                        """, (session_id,))
                        positive_feedback = cursor.fetchone()[0] or 0
                        
                        cursor.execute("""
                            SELECT COUNT(*) FROM correction_events 
                            WHERE session_id = ? AND event_type = 'negative'
                        """, (session_id,))
                        negative_feedback = cursor.fetchone()[0] or 0
                        
                        cursor.execute("""
                            SELECT COUNT(*) FROM correction_events 
                            WHERE session_id = ?
                        """, (session_id,))
                        correction_events = cursor.fetchone()[0] or 0
                        
                        conversations.append(ConversationMetrics(
                            session_id=session_id,
                            message_count=msg_count or 0,
                            total_characters=total_chars or 0,
                            duration_hours=duration,
                            last_activity=last_msg or "",
                            user_engagement_score=min(1.0, (msg_count or 0) / 20),  # Normalize to 0-1
                            correction_events=correction_events,
                            positive_feedback=positive_feedback,
                            negative_feedback=negative_feedback,
                            importance_score=0.0  # Will be calculated later
                        ))
                        
                except sqlite3.OperationalError as e:
                    # Table might not exist or have different schema
                    self.logger.logger.warning(f"Database conversation analysis failed: {e}")
                    
        except Exception as e:
            self.logger.logger.warning(f"Database analysis error: {e}")
        
        return conversations
    
    def _analyze_vault_conversations(self) -> List[ConversationMetrics]:
        """Analyze conversations stored in Vault."""
        conversations = []
        
        # For now, return empty list as Vault analysis would require
        # decrypting and parsing vault storage format
        # This can be implemented when vault storage format is better defined
        
        return conversations
    
    def _calculate_importance_score(self, conv: ConversationMetrics) -> float:
        """
        Calculate importance score for a conversation.
        
        Factors:
        - Message count (more messages = more important)
        - User engagement (corrections, feedback)
        - Conversation length and duration
        - Recency (more recent = more important)
        - Positive vs negative feedback ratio
        
        Returns:
            float: Importance score from 0.0 to 1.0
        """
        score = 0.0
        
        # Message count factor (0.0 to 0.3)
        message_factor = min(0.3, conv.message_count / 50)
        score += message_factor
        
        # Character count factor (0.0 to 0.2)
        char_factor = min(0.2, conv.total_characters / 5000)
        score += char_factor
        
        # Duration factor (0.0 to 0.1)
        duration_factor = min(0.1, conv.duration_hours / 10)
        score += duration_factor
        
        # Engagement factor (0.0 to 0.2)
        engagement_factor = conv.user_engagement_score * 0.2
        score += engagement_factor
        
        # Feedback factor (0.0 to 0.2)
        if conv.positive_feedback + conv.negative_feedback > 0:
            feedback_ratio = conv.positive_feedback / (conv.positive_feedback + conv.negative_feedback)
            feedback_factor = feedback_ratio * 0.2
            score += feedback_factor
        
        # Recency factor (0.0 to 0.1)
        try:
            if conv.last_activity:
                last_time = datetime.fromisoformat(conv.last_activity)
                days_ago = (datetime.now() - last_time).days
                recency_factor = max(0.0, min(0.1, (30 - days_ago) / 30 * 0.1))
                score += recency_factor
        except:
            pass
        
        return min(1.0, score)
    
    def prune_conversations(self, policy: Optional[str] = None, dry_run: bool = False) -> PruningReport:
        """
        Prune conversations based on retention policy.
        
        Args:
            policy: Retention policy to use ("aggressive", "moderate", "conservative")
            dry_run: If True, only simulate pruning without actual deletion
            
        Returns:
            PruningReport: Report of pruning operation
        """
        operation_id = f"prune_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        policy_name = policy or self.current_policy
        policy_config = self.retention_policies.get(policy_name, self.retention_policies["moderate"])
        
        try:
            self.logger.logger.info("Starting conversation pruning", 
                                  extra={"extra_fields": {
                                      "event_type": "pruning_start",
                                      "operation_id": operation_id,
                                      "policy": policy_name,
                                      "dry_run": dry_run
                                  }})
            
            # Analyze conversations
            conversations = self.analyze_conversations()
            
            # Determine which conversations to prune/archive
            to_prune, to_archive = self._select_conversations_for_pruning(
                conversations, policy_config
            )
            
            bytes_freed = 0
            errors = []
            
            if not dry_run:
                # Archive important but old conversations
                for conv in to_archive:
                    try:
                        self._archive_conversation(conv)
                    except Exception as e:
                        errors.append(f"Archive failed for {conv.session_id}: {str(e)}")
                
                # Prune low-importance conversations
                for conv in to_prune:
                    try:
                        freed_bytes = self._delete_conversation(conv)
                        bytes_freed += freed_bytes
                    except Exception as e:
                        errors.append(f"Prune failed for {conv.session_id}: {str(e)}")
            
            # Calculate operation duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Create report
            report = PruningReport(
                operation_id=operation_id,
                timestamp=start_time.isoformat(),
                conversations_analyzed=len(conversations),
                conversations_pruned=len(to_prune),
                conversations_archived=len(to_archive),
                bytes_freed=bytes_freed,
                retention_policy=policy_name,
                pruning_duration=duration,
                errors=errors
            )
            
            # Log completion
            self.logger.logger.info("Conversation pruning completed", 
                                  extra={"extra_fields": {
                                      "event_type": "pruning_completed",
                                      "operation_id": operation_id,
                                      "conversations_pruned": len(to_prune),
                                      "conversations_archived": len(to_archive),
                                      "bytes_freed": bytes_freed,
                                      "duration": duration,
                                      "errors": len(errors)
                                  }})
            
            return report
            
        except Exception as e:
            error_msg = f"Conversation pruning failed: {str(e)}"
            self.logger.log_error(e, "pruning_error", {"operation_id": operation_id})
            
            return PruningReport(
                operation_id=operation_id,
                timestamp=start_time.isoformat(),
                conversations_analyzed=0,
                conversations_pruned=0,
                conversations_archived=0,
                bytes_freed=0,
                retention_policy=policy_name,
                pruning_duration=(datetime.now() - start_time).total_seconds(),
                errors=[error_msg]
            )
    
    def _select_conversations_for_pruning(self, conversations: List[ConversationMetrics], 
                                        policy: Dict[str, Any]) -> Tuple[List[ConversationMetrics], List[ConversationMetrics]]:
        """Select conversations for pruning and archival based on policy."""
        to_prune = []
        to_archive = []
        
        cutoff_date = datetime.now() - timedelta(days=policy["max_age_days"])
        max_conversations = policy["max_conversations"]
        importance_threshold = policy["importance_threshold"]
        archive_threshold = policy["archive_threshold"]
        
        for conv in conversations:
            try:
                # Check age
                if conv.last_activity:
                    last_activity = datetime.fromisoformat(conv.last_activity)
                    is_old = last_activity < cutoff_date
                else:
                    is_old = True
                
                # Apply pruning logic
                if conv.importance_score < importance_threshold and is_old:
                    # Low importance and old -> prune
                    to_prune.append(conv)
                elif conv.importance_score >= archive_threshold and is_old:
                    # High importance but old -> archive
                    to_archive.append(conv)
                elif len(conversations) > max_conversations:
                    # Over limit -> prune lowest importance
                    if conv.importance_score < importance_threshold:
                        to_prune.append(conv)
                        
            except Exception as e:
                self.logger.logger.warning(f"Error evaluating conversation {conv.session_id}: {e}")
        
        # Limit pruning to avoid performance impact
        max_prune_per_operation = 50
        to_prune = to_prune[:max_prune_per_operation]
        
        return to_prune, to_archive
    
    def _archive_conversation(self, conv: ConversationMetrics) -> None:
        """Archive a conversation to compressed storage."""
        archive_file = self.archive_path / f"{conv.session_id}.json"
        
        # Create archive entry
        archive_data = {
            "session_id": conv.session_id,
            "archived_at": datetime.now().isoformat(),
            "importance_score": conv.importance_score,
            "metrics": asdict(conv)
        }
        
        # Get conversation data from database
        conversation_data = self._get_conversation_data(conv.session_id)
        archive_data["conversation_data"] = conversation_data
        
        # Save to archive
        with open(archive_file, 'w') as f:
            json.dump(archive_data, f, indent=2)
        
        # Remove from active storage
        self._delete_conversation(conv)
    
    def _delete_conversation(self, conv: ConversationMetrics) -> int:
        """Delete a conversation and return bytes freed."""
        bytes_freed = 0
        
        try:
            # Delete from database
            if self.database_path.exists():
                with sqlite3.connect(str(self.database_path)) as conn:
                    cursor = conn.cursor()
                    
                    # Delete conversation history
                    cursor.execute("DELETE FROM conversation_history WHERE session_id = ?", 
                                 (conv.session_id,))
                    
                    # Delete correction events
                    cursor.execute("DELETE FROM correction_events WHERE session_id = ?", 
                                 (conv.session_id,))
                    bytes_freed += conv.total_characters
            
            # Delete from vault (if vault format allows)
            # This would need to be implemented based on vault storage format
            
        except Exception as e:
            self.logger.logger.warning(f"Error deleting conversation {conv.session_id}: {e}")
        
        return bytes_freed
    
    def _get_conversation_data(self, session_id: str) -> Dict[str, Any]:
        """Get full conversation data for archival."""
        data = {"messages": [], "events": []}
        
        try:
            if self.database_path.exists():
                with sqlite3.connect(str(self.database_path)) as conn:
                    cursor = conn.cursor()
                    
                    # Get messages
                    cursor.execute("""
                        SELECT timestamp, message, response 
                        FROM conversation_history 
                        WHERE session_id = ? 
                        ORDER BY timestamp
                    """, (session_id,))
                    
                    for row in cursor.fetchall():
                        data["messages"].append({
                            "timestamp": row[0],
                            "message": row[1],
                            "response": row[2]
                        })
                    
                    # Get correction events
                    cursor.execute("""
                        SELECT timestamp, event_type, description 
                        FROM correction_events 
                        WHERE session_id = ?
                    """, (session_id,))
                    
                    for row in cursor.fetchall():
                        data["events"].append({
                            "timestamp": row[0],
                            "event_type": row[1],
                            "description": row[2]
                        })
                        
        except Exception as e:
            self.logger.logger.warning(f"Error getting conversation data for {session_id}: {e}")
        
        return data
    
    def get_memory_usage_stats(self) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        stats = {
            "total_conversations": 0,
            "total_messages": 0,
            "total_characters": 0,
            "database_size": 0,
            "vault_size": 0,
            "archive_size": 0,
            "oldest_conversation": None,
            "newest_conversation": None
        }
        
        try:
            # Database stats
            if self.database_path.exists():
                stats["database_size"] = self.database_path.stat().st_size
                
                with sqlite3.connect(str(self.database_path)) as conn:
                    cursor = conn.cursor()
                    
                    try:
                        cursor.execute("SELECT COUNT(DISTINCT session_id) FROM conversation_history")
                        stats["total_conversations"] = cursor.fetchone()[0] or 0
                        
                        cursor.execute("SELECT COUNT(*) FROM conversation_history")
                        stats["total_messages"] = cursor.fetchone()[0] or 0
                        
                        cursor.execute("SELECT SUM(LENGTH(message)) FROM conversation_history")
                        stats["total_characters"] = cursor.fetchone()[0] or 0
                        
                        cursor.execute("SELECT MIN(timestamp) FROM conversation_history")
                        stats["oldest_conversation"] = cursor.fetchone()[0]
                        
                        cursor.execute("SELECT MAX(timestamp) FROM conversation_history")
                        stats["newest_conversation"] = cursor.fetchone()[0]
                        
                    except sqlite3.OperationalError:
                        pass
            
            # Vault stats
            if self.vault_path.exists():
                if self.vault_path.is_file():
                    stats["vault_size"] = self.vault_path.stat().st_size
                else:
                    total_size = 0
                    for file_path in self.vault_path.rglob("*"):
                        if file_path.is_file():
                            total_size += file_path.stat().st_size
                    stats["vault_size"] = total_size
            
            # Archive stats
            if self.archive_path.exists():
                total_size = 0
                for file_path in self.archive_path.glob("*.json"):
                    total_size += file_path.stat().st_size
                stats["archive_size"] = total_size
                
        except Exception as e:
            self.logger.logger.warning(f"Error getting memory stats: {e}")
        
        return stats


def main():
    """Command-line interface for memory pruning manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hearthlink Memory Pruning Manager")
    parser.add_argument("command", choices=["analyze", "prune", "stats"], 
                       help="Memory management command")
    parser.add_argument("--policy", choices=["aggressive", "moderate", "conservative"], 
                       default="moderate", help="Pruning policy")
    parser.add_argument("--dry-run", action="store_true", help="Simulate pruning without deletion")
    
    args = parser.parse_args()
    
    try:
        manager = MemoryPruningManager()
        
        if args.command == "analyze":
            conversations = manager.analyze_conversations()
            print(f"📊 Conversation Analysis ({len(conversations)} total):")
            
            if conversations:
                avg_importance = sum(c.importance_score for c in conversations) / len(conversations)
                print(f"   Average importance: {avg_importance:.3f}")
                
                print(f"\n🔝 Top 5 Most Important:")
                for i, conv in enumerate(conversations[:5]):
                    print(f"   {i+1}. {conv.session_id[:8]}... - Score: {conv.importance_score:.3f}")
                    print(f"      Messages: {conv.message_count}, Chars: {conv.total_characters:,}")
                
                print(f"\n🔻 Bottom 5 Least Important:")
                for i, conv in enumerate(conversations[-5:]):
                    print(f"   {i+1}. {conv.session_id[:8]}... - Score: {conv.importance_score:.3f}")
                    print(f"      Messages: {conv.message_count}, Chars: {conv.total_characters:,}")
            else:
                print("   No conversations found")
        
        elif args.command == "prune":
            report = manager.prune_conversations(args.policy, args.dry_run)
            
            mode = "DRY RUN" if args.dry_run else "ACTUAL"
            print(f"🧹 Memory Pruning Report ({mode}):")
            print(f"   Policy: {report.retention_policy}")
            print(f"   Conversations analyzed: {report.conversations_analyzed}")
            print(f"   Conversations pruned: {report.conversations_pruned}")
            print(f"   Conversations archived: {report.conversations_archived}")
            print(f"   Bytes freed: {report.bytes_freed:,}")
            print(f"   Duration: {report.pruning_duration:.2f}s")
            
            if report.errors:
                print(f"\n⚠️ Errors ({len(report.errors)}):")
                for error in report.errors:
                    print(f"   - {error}")
        
        elif args.command == "stats":
            stats = manager.get_memory_usage_stats()
            print(f"💾 Memory Usage Statistics:")
            print(f"   Total conversations: {stats['total_conversations']:,}")
            print(f"   Total messages: {stats['total_messages']:,}")
            print(f"   Total characters: {stats['total_characters']:,}")
            print(f"   Database size: {stats['database_size']:,} bytes")
            print(f"   Vault size: {stats['vault_size']:,} bytes")
            print(f"   Archive size: {stats['archive_size']:,} bytes")
            
            if stats['oldest_conversation']:
                print(f"   Oldest conversation: {stats['oldest_conversation']}")
            if stats['newest_conversation']:
                print(f"   Newest conversation: {stats['newest_conversation']}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()