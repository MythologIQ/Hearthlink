#!/usr/bin/env python3
"""
Example Summarizer Plugin

A simple plugin that demonstrates plugin functionality for the Synapse gateway.
This plugin provides text summarization capabilities.
"""

import json
import sys
import re
from typing import Dict, Any, List

class SummarizerPlugin:
    """Example summarizer plugin."""
    
    def __init__(self):
        self.name = "Summarizer Plugin"
        self.version = "1.0.0"
        self.description = "A simple text summarization plugin"
    
    def summarize_text(self, text: str, max_length: int = 100) -> str:
        """
        Summarize text by extracting key sentences.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summarized text
        """
        # Simple sentence extraction
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Sort by length (longer sentences often contain more information)
        sentences.sort(key=len, reverse=True)
        
        # Take sentences until we reach max_length
        summary = ""
        for sentence in sentences:
            if len(summary + sentence) <= max_length:
                summary += sentence + ". "
            else:
                break
        
        return summary.strip()
    
    def get_word_count(self, text: str) -> Dict[str, int]:
        """
        Get word count statistics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Word count statistics
        """
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = len(words)
        
        # Count unique words
        unique_words = len(set(words))
        
        # Most common words (simplified)
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top 5 words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_words": word_count,
            "unique_words": unique_words,
            "top_words": dict(top_words)
        }
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a plugin request.
        
        Args:
            request: Request data
            
        Returns:
            Response data
        """
        try:
            action = request.get("action", "summarize")
            text = request.get("text", "")
            
            if not text:
                return {
                    "success": False,
                    "error": "No text provided"
                }
            
            if action == "summarize":
                max_length = request.get("max_length", 100)
                summary = self.summarize_text(text, max_length)
                
                return {
                    "success": True,
                    "summary": summary,
                    "original_length": len(text),
                    "summary_length": len(summary)
                }
            
            elif action == "analyze":
                stats = self.get_word_count(text)
                
                return {
                    "success": True,
                    "statistics": stats
                }
            
            elif action == "both":
                max_length = request.get("max_length", 100)
                summary = self.summarize_text(text, max_length)
                stats = self.get_word_count(text)
                
                return {
                    "success": True,
                    "summary": summary,
                    "statistics": stats,
                    "original_length": len(text),
                    "summary_length": len(summary)
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

def main():
    """Main entry point for the plugin."""
    # Read input from stdin
    input_data = sys.stdin.read()
    
    try:
        # Parse JSON input
        request = json.loads(input_data)
        
        # Create plugin instance
        plugin = SummarizerPlugin()
        
        # Process request
        response = plugin.process_request(request)
        
        # Output JSON response
        print(json.dumps(response, indent=2))
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            "success": False,
            "error": f"Invalid JSON input: {e}"
        }, indent=2))
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Plugin error: {e}"
        }, indent=2))

if __name__ == "__main__":
    main() 