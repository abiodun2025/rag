#!/usr/bin/env python3
"""
Content Generator
================

A ChatGPT-like content generator that can write multiple paragraphs on any topic.
"""

import random
import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Generate ChatGPT-like content on any topic."""
    
    def __init__(self):
        self.content_styles = {
            "informative": {
                "tone": "professional and educational",
                "structure": "introduction, main points, conclusion",
                "language": "clear and accessible"
            },
            "creative": {
                "tone": "engaging and imaginative",
                "structure": "narrative flow with vivid descriptions",
                "language": "expressive and colorful"
            },
            "analytical": {
                "tone": "objective and data-driven",
                "structure": "problem, analysis, solution",
                "language": "precise and logical"
            },
            "conversational": {
                "tone": "friendly and approachable",
                "structure": "natural flow with personal insights",
                "language": "casual and relatable"
            },
            "professional": {
                "tone": "formal and authoritative",
                "structure": "executive summary, detailed analysis, recommendations",
                "language": "business-appropriate"
            }
        }
        
        self.paragraph_transitions = [
            "Furthermore,", "Moreover,", "Additionally,", "In addition,", "Beyond that,",
            "On the other hand,", "However,", "Nevertheless,", "That said,", "At the same time,",
            "Moving forward,", "Looking ahead,", "As we consider,", "When examining,", "In exploring,",
            "It's important to note that,", "Another key aspect is,", "A crucial point to consider is,",
            "Delving deeper into,", "Expanding on this idea,", "Building upon this foundation,"
        ]
        
        self.conclusion_phrases = [
            "In conclusion,", "To summarize,", "Ultimately,", "In essence,", "At its core,",
            "The bottom line is,", "What this means is,", "The key takeaway is,", "To put it simply,",
            "In the final analysis,", "When all is said and done,", "The fundamental truth is,"
        ]
    
    def generate_content(self, topic: str, style: str = "informative", length: str = "medium", context: Dict[str, Any] = None) -> Dict[str, str]:
        """Generate comprehensive content on any topic."""
        
        try:
            # Analyze the topic and determine appropriate style
            detected_style = self._detect_content_style(topic)
            if style == "auto":
                style = detected_style
            
            # Determine paragraph count based on length
            paragraph_count = self._get_paragraph_count(length)
            
            # Generate the content
            content = self._create_multi_paragraph_content(topic, style, paragraph_count, context)
            
            return {
                "topic": topic,
                "style": style,
                "length": length,
                "content": content,
                "paragraph_count": paragraph_count,
                "word_count": len(content.split())
            }
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return {
                "topic": topic,
                "style": style,
                "length": length,
                "content": f"I apologize, but I encountered an error while generating content about {topic}. Please try again with a different topic or approach.",
                "error": str(e)
            }
    
    def _detect_content_style(self, topic: str) -> str:
        """Automatically detect the appropriate content style based on the topic."""
        
        topic_lower = topic.lower()
        
        # Business/Professional topics
        if any(word in topic_lower for word in ["business", "strategy", "management", "leadership", "marketing", "finance", "analysis", "report", "planning"]):
            return "professional"
        
        # Creative/Artistic topics
        if any(word in topic_lower for word in ["story", "creative", "art", "design", "fiction", "poetry", "imagination", "fantasy", "adventure"]):
            return "creative"
        
        # Technical/Analytical topics
        if any(word in topic_lower for word in ["technology", "data", "research", "study", "analysis", "comparison", "evaluation", "assessment", "review"]):
            return "analytical"
        
        # Personal/Conversational topics
        if any(word in topic_lower for word in ["personal", "experience", "life", "journey", "reflection", "thoughts", "opinion", "view", "perspective"]):
            return "conversational"
        
        # Default to informative for educational topics
        return "informative"
    
    def _get_paragraph_count(self, length: str) -> int:
        """Determine number of paragraphs based on requested length."""
        
        length_mapping = {
            "short": 2,
            "medium": 4,
            "long": 6,
            "extensive": 8
        }
        
        return length_mapping.get(length, 4)
    
    def _create_multi_paragraph_content(self, topic: str, style: str, paragraph_count: int, context: Dict[str, Any] = None) -> str:
        """Create multi-paragraph content on the given topic."""
        
        style_config = self.content_styles.get(style, self.content_styles["informative"])
        
        # Generate introduction paragraph
        introduction = self._generate_introduction(topic, style_config)
        
        # Generate main content paragraphs
        main_paragraphs = []
        for i in range(paragraph_count - 2):  # -2 for intro and conclusion
            paragraph = self._generate_main_paragraph(topic, style_config, i, main_paragraphs)
            main_paragraphs.append(paragraph)
        
        # Generate conclusion paragraph
        conclusion = self._generate_conclusion(topic, style_config, main_paragraphs)
        
        # Combine all paragraphs
        all_paragraphs = [introduction] + main_paragraphs + [conclusion]
        
        # Join with proper spacing
        content = "\n\n".join(all_paragraphs)
        
        return content
    
    def _generate_introduction(self, topic: str, style_config: Dict[str, str]) -> str:
        """Generate an engaging introduction paragraph."""
        
        intro_templates = {
            "informative": [
                f"{topic} is a fascinating subject that touches on many aspects of our modern world. Understanding this topic requires us to explore its various dimensions and implications.",
                f"When we think about {topic}, we're delving into a complex and multifaceted area that has significant relevance in today's society.",
                f"The concept of {topic} encompasses a wide range of considerations that are worth exploring in detail."
            ],
            "creative": [
                f"Imagine a world where {topic} takes center stage - a realm of possibilities waiting to be discovered and explored.",
                f"Picture yourself diving into the depths of {topic}, where every discovery reveals new wonders and insights.",
                f"Step into the fascinating universe of {topic}, where imagination meets reality in unexpected ways."
            ],
            "analytical": [
                f"To properly analyze {topic}, we must examine its core components, underlying principles, and broader implications.",
                f"A comprehensive examination of {topic} reveals multiple layers of complexity that demand careful consideration.",
                f"The study of {topic} presents us with a systematic framework for understanding its various aspects."
            ],
            "conversational": [
                f"You know, {topic} is something I've been thinking about a lot lately. It's one of those topics that keeps coming up in conversations.",
                f"Have you ever really stopped to think about {topic}? It's one of those subjects that's more interesting than it might seem at first glance.",
                f"I find {topic} to be absolutely fascinating. There's so much more to it than meets the eye."
            ],
            "professional": [
                f"In today's competitive landscape, {topic} represents a critical factor that organizations must carefully consider and strategically address.",
                f"The strategic importance of {topic} cannot be overstated in our current business environment.",
                f"Effective management of {topic} is essential for achieving sustainable competitive advantage and long-term success."
            ]
        }
        
        templates = intro_templates.get(style_config["tone"].split()[0], intro_templates["informative"])
        return random.choice(templates)
    
    def _generate_main_paragraph(self, topic: str, style_config: Dict[str, str], paragraph_index: int, previous_paragraphs: List[str]) -> str:
        """Generate a main content paragraph."""
        
        # Choose transition phrase
        transition = random.choice(self.paragraph_transitions)
        
        # Generate paragraph content based on style and position
        if style_config["tone"].startswith("professional"):
            content = self._generate_professional_paragraph(topic, paragraph_index)
        elif style_config["tone"].startswith("creative"):
            content = self._generate_creative_paragraph(topic, paragraph_index)
        elif style_config["tone"].startswith("analytical"):
            content = self._generate_analytical_paragraph(topic, paragraph_index)
        elif style_config["tone"].startswith("conversational"):
            content = self._generate_conversational_paragraph(topic, paragraph_index)
        else:
            content = self._generate_informative_paragraph(topic, paragraph_index)
        
        return f"{transition} {content}"
    
    def _generate_informative_paragraph(self, topic: str, paragraph_index: int) -> str:
        """Generate an informative paragraph."""
        
        informative_content = [
            f"One of the key aspects of {topic} involves understanding its fundamental principles and how they apply in various contexts. This foundational knowledge provides the basis for deeper exploration and practical application.",
            f"Another important consideration when examining {topic} is the way it interacts with other related concepts and systems. These interactions often reveal unexpected connections and opportunities for innovation.",
            f"The practical applications of {topic} extend far beyond theoretical understanding. Real-world implementation requires careful planning, adaptation, and continuous refinement based on feedback and results.",
            f"Looking at {topic} from a historical perspective reveals how it has evolved over time and adapted to changing circumstances. This evolutionary process offers valuable insights for future development."
        ]
        
        return informative_content[paragraph_index % len(informative_content)]
    
    def _generate_creative_paragraph(self, topic: str, paragraph_index: int) -> str:
        """Generate a creative paragraph."""
        
        creative_content = [
            f"Imagine the possibilities that emerge when we view {topic} through the lens of creativity and innovation. Every challenge becomes an opportunity, every limitation a catalyst for breakthrough thinking.",
            f"The beauty of {topic} lies in its ability to inspire and transform. Like a master artist working with a blank canvas, we can shape and mold it into something truly extraordinary.",
            f"Picture the journey through {topic} as an adventure filled with unexpected discoveries and delightful surprises. Each step forward reveals new horizons and unexplored territories waiting to be claimed.",
            f"The magic of {topic} unfolds when we allow ourselves to think beyond conventional boundaries and embrace the unknown. It's in these moments of exploration that true innovation takes flight."
        ]
        
        return creative_content[paragraph_index % len(creative_content)]
    
    def _generate_analytical_paragraph(self, topic: str, paragraph_index: int) -> str:
        """Generate an analytical paragraph."""
        
        analytical_content = [
            f"Data analysis reveals that {topic} demonstrates consistent patterns across different contexts and applications. These patterns provide valuable insights for strategic decision-making and resource allocation.",
            f"Comparative studies of {topic} across various industries and sectors show significant variations in implementation approaches and outcomes. Understanding these differences is crucial for optimizing performance.",
            f"Statistical modeling of {topic} indicates strong correlations with key performance indicators and success metrics. These relationships form the basis for predictive analytics and risk assessment.",
            f"Market research on {topic} suggests evolving trends and shifting priorities that organizations must address to maintain competitive advantage and market relevance."
        ]
        
        return analytical_content[paragraph_index % len(analytical_content)]
    
    def _generate_conversational_paragraph(self, topic: str, paragraph_index: int) -> str:
        """Generate a conversational paragraph."""
        
        conversational_content = [
            f"You know what's really interesting about {topic}? It's one of those things that seems simple at first, but the more you dig into it, the more fascinating it becomes.",
            f"I've found that people often have very different perspectives on {topic}, and that's what makes it so engaging to discuss. Everyone brings their own unique experiences and insights to the table.",
            f"What I love about {topic} is how it connects to so many other aspects of life and work. It's like a thread that runs through everything, tying different ideas and concepts together.",
            f"Have you ever noticed how {topic} keeps popping up in unexpected places? It's amazing how relevant it is to so many different situations and challenges we face."
        ]
        
        return conversational_content[paragraph_index % len(conversational_content)]
    
    def _generate_professional_paragraph(self, topic: str, paragraph_index: int) -> str:
        """Generate a professional paragraph."""
        
        professional_content = [
            f"Organizational leaders must recognize that {topic} represents a strategic imperative that requires dedicated resources, clear objectives, and measurable outcomes. Success depends on systematic implementation and continuous monitoring.",
            f"Effective management of {topic} demands a comprehensive approach that integrates multiple stakeholders, processes, and technologies. This integrated approach ensures alignment with organizational goals and maximizes return on investment.",
            f"Risk assessment and mitigation strategies for {topic} should be developed in collaboration with key stakeholders and regularly reviewed to address emerging challenges and opportunities.",
            f"Performance metrics and key performance indicators related to {topic} must be clearly defined, regularly measured, and used to drive continuous improvement and strategic decision-making."
        ]
        
        return professional_content[paragraph_index % len(professional_content)]
    
    def _generate_conclusion(self, topic: str, style_config: Dict[str, str], main_paragraphs: List[str]) -> str:
        """Generate a conclusion paragraph."""
        
        conclusion_phrase = random.choice(self.conclusion_phrases)
        
        conclusion_templates = {
            "informative": f"{conclusion_phrase} {topic} represents a multifaceted subject that continues to evolve and adapt to changing circumstances. The insights gained from exploring this topic provide valuable perspectives for future consideration and application.",
            "creative": f"{conclusion_phrase} {topic} offers endless possibilities for exploration and discovery. The journey through this fascinating subject reminds us that creativity and imagination are powerful tools for understanding and transforming our world.",
            "analytical": f"{conclusion_phrase} the systematic analysis of {topic} reveals important patterns and relationships that inform strategic decision-making and guide future research and development efforts.",
            "conversational": f"{conclusion_phrase} {topic} is one of those subjects that keeps giving - the more you explore it, the more you discover. It's a reminder that learning and growth are ongoing processes that enrich our lives and expand our horizons.",
            "professional": f"{conclusion_phrase} effective management and strategic implementation of {topic} are essential for achieving sustainable competitive advantage and long-term organizational success in today's dynamic business environment."
        }
        
        style_key = style_config["tone"].split()[0]
        return conclusion_templates.get(style_key, conclusion_templates["informative"])

# Create a global instance
content_generator = ContentGenerator() 