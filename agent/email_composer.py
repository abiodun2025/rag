"""
Intelligent Email Composer
=========================

This module provides AI-powered email composition that understands user intent
and writes emails in natural, professional language.
"""

import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class IntelligentEmailComposer:
    """AI-powered email composer that writes emails in natural language."""
    
    def __init__(self):
        self.default_tone = "professional"
        self.default_style = "clear and concise"
        
        # Enhanced intent patterns
        self.intent_patterns = {
            "meeting_request": [
                r"schedule.*meeting", r"set up.*meeting", r"arrange.*meeting",
                r"book.*meeting", r"plan.*meeting", r"organize.*meeting",
                r"meeting.*request", r"meeting.*scheduling", r"about.*scheduling.*meeting",
                r"scheduling.*meeting", r"meeting.*for", r"meeting.*at"
            ],
            "thank_you": [
                r"thank.*you", r"thanks", r"appreciate", r"grateful",
                r"thank.*for.*help", r"thank.*for.*support", r"thank.*for.*assistance",
                r"appreciation.*email", r"thank.*email"
            ],
            "inquiry": [
                r"question", r"ask", r"inquiry", r"wonder", r"curious",
                r"information", r"details", r"clarification", r"enquiry"
            ],
            "update": [
                r"update", r"status", r"progress", r"report", r"latest",
                r"current.*status", r"how.*going", r"what.*happening"
            ],
            "greeting": [
                r"hello", r"hi", r"greeting", r"introduce", r"meet",
                r"connect", r"reach out", r"touch base"
            ],
            "urgent": [
                r"urgent", r"asap", r"emergency", r"immediate", r"critical",
                r"time.*sensitive", r"rush", r"priority"
            ],
            "followup": [
                r"follow.*up", r"followup", r"checking.*in", r"touch.*base",
                r"circling.*back", r"reaching.*out", r"checking.*status",
                r"followup.*email", r"follow.*up.*email"
            ],
            "introduction": [
                r"introduce", r"introduction", r"new", r"first.*time",
                r"meeting.*for.*first", r"getting.*to.*know"
            ],
            "collaboration": [
                r"collaborate", r"partnership", r"work.*together", r"join.*forces",
                r"team.*up", r"cooperation", r"alliance", r"collaboration.*proposal",
                r"partnership.*opportunity", r"propose.*collaboration", r"partnership.*offer"
            ],
            "feedback": [
                r"feedback", r"review", r"opinion", r"thoughts", r"suggestions",
                r"input", r"advice", r"recommendations", r"feedback.*request",
                r"ask.*for.*feedback", r"request.*opinion"
            ],
            "proposal": [
                r"proposal", r"offer", r"suggestion", r"idea", r"concept",
                r"proposition", r"recommendation"
            ],
            "confirmation": [
                r"confirm", r"confirmation", r"verify", r"check", r"validate",
                r"ensure", r"double.*check"
            ]
        }
        
        # Enhanced tone patterns
        self.tone_patterns = {
            "friendly": [r"friendly", r"casual", r"informal", r"relaxed", r"warm"],
            "formal": [r"formal", r"professional", r"business", r"official", r"corporate"],
            "urgent": [r"urgent", r"asap", r"emergency", r"critical", r"immediate"],
            "grateful": [r"thank", r"thanks", r"appreciate", r"grateful", r"blessed"],
            "apologetic": [r"sorry", r"apologize", r"regret", r"unfortunately", r"apology"],
            "enthusiastic": [r"excited", r"thrilled", r"delighted", r"pleased", r"happy"],
            "concerned": [r"concerned", r"worried", r"anxious", r"troubled", r"bothered"]
        }
    
    def compose_email(self, user_message: str, to_email: str, context: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Compose an intelligent email based on user intent.
        
        Args:
            user_message: The user's original message
            to_email: Recipient email address
            context: Additional context (optional)
            
        Returns:
            Dictionary with subject and body
        """
        try:
            # Analyze the user's intent and extract key information
            intent_analysis = self._analyze_email_intent(user_message)
            
            # Extract recipient name from email if possible
            recipient_name = self._extract_recipient_name(to_email, context)
            
            # Extract specific content from user message
            specific_content = self._extract_specific_content(user_message, to_email)
            
            # Debug: Log what content was extracted
            logger.info(f"Original message: {user_message}")
            logger.info(f"Extracted content: '{specific_content}'")
            
            # Generate appropriate subject and body
            subject = self._generate_subject(intent_analysis, to_email, recipient_name)
            body = self._generate_body(intent_analysis, to_email, recipient_name, context, specific_content)
            
            return {
                "subject": subject,
                "body": body,
                "intent": intent_analysis.get("intent", "general"),
                "tone": intent_analysis.get("tone", "professional"),
                "recipient_name": recipient_name,
                "urgency": intent_analysis.get("urgency", "normal"),
                "formality": intent_analysis.get("formality", "casual"),
                "specific_content": specific_content
            }
            
        except Exception as e:
            logger.error(f"Email composition failed: {e}")
            # Fallback to simple extraction
            return self._fallback_composition(user_message, to_email)
    
    def _analyze_email_intent(self, user_message: str) -> Dict[str, Any]:
        """Analyze the user's email intent and extract key information."""
        
        message_lower = user_message.lower()
        
        # Determine intent using pattern matching
        intent = "general"
        confidence = 0.0
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    intent = intent_type
                    confidence = 0.8
                    break
            if confidence > 0:
                break
        
        # Determine tone
        tone = "professional"
        for tone_type, patterns in self.tone_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    tone = tone_type
                    break
        
        # Extract key information
        key_info = {
            "intent": intent,
            "tone": tone,
            "confidence": confidence,
            "urgency": "urgent" if any(word in message_lower for word in ["urgent", "asap", "emergency", "critical", "immediate"]) else "normal",
            "formality": "formal" if any(word in message_lower for word in ["business", "professional", "formal", "corporate", "official"]) else "casual",
            "action_required": any(word in message_lower for word in ["call", "meet", "discuss", "review", "schedule", "arrange"]),
            "has_questions": any(word in message_lower for word in ["question", "ask", "inquiry", "wonder", "curious"]),
            "is_followup": any(word in message_lower for word in ["follow up", "followup", "checking in", "touch base"]),
            "is_introduction": any(word in message_lower for word in ["introduce", "meet", "new", "first time"]),
            "is_collaboration": any(word in message_lower for word in ["collaborate", "partnership", "work together", "team up"]),
            "is_feedback": any(word in message_lower for word in ["feedback", "review", "opinion", "thoughts"]),
            "is_proposal": any(word in message_lower for word in ["proposal", "offer", "suggestion", "idea"]),
            "is_confirmation": any(word in message_lower for word in ["confirm", "verify", "check", "validate"])
        }
        
        return key_info
    
    def _extract_recipient_name(self, to_email: str, context: Dict[str, Any] = None) -> str:
        """Extract recipient name from email or context."""
        
        # Try to get name from context first
        if context and context.get("recipient_name"):
            return context["recipient_name"]
        
        # Extract from email address
        if '@' in to_email:
            local_part = to_email.split('@')[0]
            
            # Handle common patterns
            if '.' in local_part:
                # john.doe@domain.com -> John Doe
                name_parts = local_part.split('.')
                return ' '.join(part.capitalize() for part in name_parts)
            elif '_' in local_part:
                # john_doe@domain.com -> John Doe
                name_parts = local_part.split('_')
                return ' '.join(part.capitalize() for part in name_parts)
            else:
                # johndoe@domain.com -> Johndoe
                return local_part.capitalize()
        
        return "[Recipient]"
    
    def _extract_specific_content(self, user_message: str, to_email: str) -> str:
        """Extract specific content that the user wants to communicate."""
        
        # Remove email address and common email-related words
        message_clean = user_message.lower()
        
        # Remove the entire email address
        if '@' in message_clean:
            # Find and remove the email address completely
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            message_clean = re.sub(email_pattern, '', message_clean)
        
        # Remove recipient names that might be extracted from email addresses
        if '@' in to_email:
            local_part = to_email.split('@')[0]
            # Remove common name patterns from the email
            if '.' in local_part:
                name_parts = local_part.split('.')
                for part in name_parts:
                    message_clean = re.sub(rf'\b{part}\b', '', message_clean, flags=re.IGNORECASE)
            elif '_' in local_part:
                name_parts = local_part.split('_')
                for part in name_parts:
                    message_clean = re.sub(rf'\b{part}\b', '', message_clean, flags=re.IGNORECASE)
            else:
                message_clean = re.sub(rf'\b{local_part}\b', '', message_clean, flags=re.IGNORECASE)
        
        # Remove only the most basic email action words, preserve important details
        basic_action_words = [
            "send", "email", "mail", "to", "at", "message", "that", "says", "saying", "with", "an"
        ]
        
        for word in basic_action_words:
            message_clean = re.sub(rf'\b{word}\b', '', message_clean)
        
        # Clean up extra whitespace and punctuation
        message_clean = re.sub(r'\s+', ' ', message_clean).strip()
        message_clean = re.sub(r'^[.,\s]+|[.,\s]+$', '', message_clean)  # Remove leading/trailing punctuation
        
        # If we have meaningful content, return it
        if len(message_clean) > 2:  # Reduced minimum length to capture more details
            return message_clean
        
        return ""
    
    def _create_coherent_sentence(self, content: str, intent: str, tone: str) -> str:
        """Create a coherent sentence from the user's content."""
        
        if not content or len(content) < 3:
            return ""
        
        # Clean up the content
        content = content.strip()
        
        # Check if content is already a complete sentence
        if content.endswith(('.', '!', '?')) and len(content.split()) > 3:
            return content.capitalize()
        
        # Check if content is a time or date
        time_patterns = [
            r'\d{1,2}:\d{2}\s*(am|pm)?',  # 1pm, 2:30pm, 14:30
            r'\d{1,2}\s*(am|pm)',  # 1 pm, 2 pm
            r'(today|tomorrow|next week|next month)',
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)'
        ]
        
        is_time_or_date = any(re.search(pattern, content.lower()) for pattern in time_patterns)
        
        # Create complete, coherent sentences based on intent and content
        if intent == "greeting":
            if tone == "friendly":
                return f"I wanted to reach out and say hello to you."
            else:
                return f"I hope this message finds you well. I wanted to connect with you."
        
        elif intent == "meeting_request":
            if is_time_or_date:
                return f"I would like to schedule a meeting for {content}. Please let me know if this time works for you."
            elif "meeting" in content.lower():
                # Extract the specific details after "meeting"
                meeting_parts = content.lower().split("meeting")
                if len(meeting_parts) > 1:
                    details = meeting_parts[1].strip()
                    if details:
                        return f"I would like to schedule a meeting {details}. Please let me know your availability."
                return f"I would like to schedule a meeting. Please let me know your availability."
            elif any(char.isdigit() for char in content):
                # Handle cases with time/date information
                # Debug: log the content
                logger.info(f"DEBUG: Content contains digits: '{content}'")
                
                # Extract time patterns from the content
                if "1pm" in content.lower():
                    logger.info("DEBUG: Found 1pm in content")
                    return f"I would like to schedule a meeting for 1pm. Please let me know if this time works for you."
                elif "2pm" in content.lower():
                    logger.info("DEBUG: Found 2pm in content")
                    return f"I would like to schedule a meeting for 2pm. Please let me know if this time works for you."
                elif "3pm" in content.lower():
                    logger.info("DEBUG: Found 3pm in content")
                    return f"I would like to schedule a meeting for 3pm. Please let me know if this time works for you."
                elif "4pm" in content.lower():
                    logger.info("DEBUG: Found 4pm in content")
                    return f"I would like to schedule a meeting for 4pm. Please let me know if this time works for you."
                elif "5pm" in content.lower():
                    logger.info("DEBUG: Found 5pm in content")
                    return f"I would like to schedule a meeting for 5pm. Please let me know if this time works for you."
                elif "6pm" in content.lower():
                    logger.info("DEBUG: Found 6pm in content")
                    return f"I would like to schedule a meeting for 6pm. Please let me know if this time works for you."
                elif "7pm" in content.lower():
                    logger.info("DEBUG: Found 7pm in content")
                    return f"I would like to schedule a meeting for 7pm. Please let me know if this time works for you."
                elif "8pm" in content.lower():
                    logger.info("DEBUG: Found 8pm in content")
                    return f"I would like to schedule a meeting for 8pm. Please let me know if this time works for you."
                elif "9pm" in content.lower():
                    logger.info("DEBUG: Found 9pm in content")
                    return f"I would like to schedule a meeting for 9pm. Please let me know if this time works for you."
                elif "10pm" in content.lower():
                    logger.info("DEBUG: Found 10pm in content")
                    return f"I would like to schedule a meeting for 10pm. Please let me know if this time works for you."
                elif "11pm" in content.lower():
                    logger.info("DEBUG: Found 11pm in content")
                    return f"I would like to schedule a meeting for 11pm. Please let me know if this time works for you."
                elif "12pm" in content.lower():
                    logger.info("DEBUG: Found 12pm in content")
                    return f"I would like to schedule a meeting for 12pm. Please let me know if this time works for you."
                else:
                    logger.info("DEBUG: No specific time found in content")
                    return f"I would like to schedule a meeting. Please let me know your availability."
            else:
                return f"I would like to schedule a meeting to discuss {content}. Please let me know your availability."
        
        elif intent == "thank_you":
            return f"I wanted to thank you for {content}. Your help has been greatly appreciated."
        
        elif intent == "inquiry":
            return f"I have a question about {content}. I would appreciate your insights on this matter."
        
        elif intent == "update":
            return f"I wanted to update you on {content}. Please let me know if you need any additional information."
        
        elif intent == "urgent":
            return f"I need to bring to your attention an urgent matter regarding {content}. This requires immediate attention."
        
        elif intent == "followup":
            return f"I'm following up on our previous discussion about {content}. I wanted to check on the current status."
        
        elif intent == "collaboration":
            return f"I would like to discuss potential collaboration on {content}. I believe this could be beneficial for both of us."
        
        elif intent == "feedback":
            return f"I would appreciate your feedback on {content}. Your input would be very valuable."
        
        elif intent == "proposal":
            return f"I have a proposal regarding {content}. I would like to discuss this with you in detail."
        
        elif intent == "confirmation":
            return f"I wanted to confirm the details about {content}. Please let me know if everything is correct."
        
        else:
            # General case - create a natural, complete sentence
            if content.startswith(('i ', 'we ', 'you ', 'they ', 'he ', 'she ', 'it ')):
                return f"{content.capitalize()}. I wanted to make sure you're aware of this."
            elif is_time_or_date:
                return f"I wanted to let you know about {content}. Please mark this in your calendar."
            elif len(content.split()) <= 3:
                # Short phrases - make them complete sentences
                return f"I wanted to discuss {content} with you. This is an important matter that needs attention."
            else:
                # Longer content - make it a complete sentence
                return f"{content.capitalize()}. I wanted to make sure you have all the necessary information."
    
    def _generate_subject(self, intent_analysis: Dict[str, Any], to_email: str, recipient_name: str) -> str:
        """Generate an appropriate subject line."""
        
        intent = intent_analysis.get("intent", "general")
        urgency = intent_analysis.get("urgency", "normal")
        
        # Enhanced subject templates
        subject_templates = {
            "meeting_request": "Meeting Request",
            "thank_you": "Thank You",
            "inquiry": "Inquiry",
            "update": "Update",
            "greeting": "Hello",
            "urgent": "URGENT: ",
            "followup": "Follow-up",
            "introduction": "Introduction",
            "collaboration": "Collaboration Opportunity",
            "feedback": "Feedback Request",
            "proposal": "Proposal",
            "confirmation": "Confirmation",
            "general": "Message"
        }
        
        base_subject = subject_templates.get(intent, "Message")
        
        # Add urgency prefix if needed
        if urgency == "urgent":
            base_subject = f"URGENT: {base_subject}"
        
        return base_subject
    
    def _generate_body(self, intent_analysis: Dict[str, Any], to_email: str, recipient_name: str, context: Dict[str, Any] = None, specific_content: str = "") -> str:
        """Generate an intelligent email body."""
        
        intent = intent_analysis.get("intent", "general")
        tone = intent_analysis.get("tone", "professional")
        formality = intent_analysis.get("formality", "casual")
        action_required = intent_analysis.get("action_required", False)
        urgency = intent_analysis.get("urgency", "normal")
        
        # Generate appropriate greeting
        greeting = self._generate_greeting(tone, formality, recipient_name)
        
        # Generate main content based on intent and specific content
        main_content = self._generate_main_content(intent, tone, formality, urgency, context, specific_content)
        
        # Generate closing
        closing = self._generate_closing(tone, formality, action_required, urgency)
        
        # Add signature
        signature = self._generate_signature(tone, formality)
        
        # Combine into full email
        email_body = f"{greeting}\n\n{main_content}\n\n{closing}\n\n{signature}"
        
        return email_body
    
    def _generate_greeting(self, tone: str, formality: str, recipient_name: str) -> str:
        """Generate personalized greeting with more detail and warmth."""
        
        if formality == "formal":
            if tone == "friendly":
                greeting = f"Dear {recipient_name},\n\nI hope this message finds you well and that you're having a productive day."
            elif tone == "professional":
                greeting = f"Dear {recipient_name},\n\nI hope this email finds you well and that your week is off to a great start."
            elif tone == "enthusiastic":
                greeting = f"Dear {recipient_name},\n\nI hope this message finds you in excellent spirits and that you're having a wonderful day!"
            elif tone == "apologetic":
                greeting = f"Dear {recipient_name},\n\nI hope this message finds you well, and I appreciate you taking the time to read this."
            else:
                greeting = f"Dear {recipient_name},\n\nI hope this message finds you well."
        else:
            if tone == "friendly":
                greeting = f"Hi {recipient_name}!\n\nI hope you're doing great and having a fantastic day."
            elif tone == "professional":
                greeting = f"Hello {recipient_name},\n\nI hope you're having a productive day."
            elif tone == "enthusiastic":
                greeting = f"Hi {recipient_name}!\n\nI hope you're having an amazing day!"
            elif tone == "apologetic":
                greeting = f"Hi {recipient_name},\n\nI hope you're doing well, and thanks for your time."
            else:
                greeting = f"Hi {recipient_name},\n\nI hope you're doing well."
        
        return greeting
    
    def _generate_main_content(self, intent: str, tone: str, formality: str, urgency: str, context: Dict[str, Any] = None, specific_content: str = "") -> str:
        """Generate main email content with much more detail and completeness."""
        
        # If we have specific content from the user, create a coherent sentence
        if specific_content and len(specific_content) > 3 and not specific_content.isdigit():
            coherent_sentence = self._create_coherent_sentence(specific_content, intent, tone)
            if coherent_sentence:
                # Build a comprehensive email around the specific content
                return self._build_comprehensive_content(intent, tone, formality, coherent_sentence, specific_content)
        
        # Enhanced content templates with much more detail and variety
        content_templates = {
            "meeting_request": [
                "I hope this message finds you well. I'm reaching out to schedule a meeting that I believe would be mutually beneficial for both of us. I've been reviewing our recent discussions and feel that a face-to-face conversation would be the best way to move forward with our collaboration.",
                "I hope you're having a productive day. I wanted to connect with you regarding an important matter that I believe requires our direct attention. A meeting would allow us to discuss this in detail and ensure we're aligned on the next steps.",
                "I hope this email finds you in good spirits. I'm writing to propose a meeting that I think could be very valuable for our ongoing partnership. There are several key points I'd like to discuss that would be best addressed in person."
            ],
            "thank_you": [
                "I wanted to take a moment to express my sincere gratitude for your recent assistance and support. Your help has been absolutely invaluable to our project's success, and I truly appreciate the time and effort you've dedicated to helping us achieve our goals.",
                "Thank you so much for your generous support and guidance throughout this process. Your contributions have made a significant difference in our work, and I'm incredibly grateful for your expertise and willingness to assist us.",
                "I'm writing to express my heartfelt thanks for your help and support. Your expertise and willingness to assist have been truly appreciated, and I wanted to make sure you know how much your contributions have meant to our team."
            ],
            "inquiry": [
                "I hope you're doing well. I have several questions regarding our recent discussions that I believe you could help clarify. Your insights on this matter would be extremely valuable, and I would appreciate the opportunity to discuss these points in detail.",
                "I hope this message finds you well. I'm reaching out to gather some information and would value your expertise on this topic. There are specific aspects I'd like to understand better, and I believe your perspective would be very helpful.",
                "I hope you're having a great day. I have some questions that I believe you could help clarify, and I would appreciate your input. Your experience in this area would be very valuable for our current project."
            ],
            "update": [
                "I hope this message finds you well. I wanted to provide you with a comprehensive update on the current status of our project and share some important developments that have occurred since our last communication. There are several key milestones we've achieved and some exciting progress to report.",
                "I hope you're doing well. I'm writing to give you a detailed progress update on our ongoing work and share some recent developments that I think you'll find interesting. We've made significant strides in several areas and I wanted to keep you informed.",
                "I hope this email finds you in good spirits. I wanted to update you on the current status of our project and discuss next steps. We've accomplished quite a bit since our last update, and I believe you'll be pleased with the progress we've made."
            ],
            "greeting": [
                "I hope this message finds you well. I wanted to reach out and connect with you to say hello and check in on how things are going. It's been a while since we last spoke, and I thought it would be nice to touch base and see how you're doing.",
                "I hope you're doing well. I'm reaching out to say hello and check in on how things are going with your projects and work. I always enjoy our conversations and wanted to see if there's anything new or exciting happening in your world.",
                "I hope this email finds you in good health. I wanted to check in and see how you're doing with your projects and see if there's anything I can help you with. It's always great to connect with colleagues and friends."
            ],
            "urgent": [
                "I need to bring an urgent matter to your attention that requires immediate action. This is a time-sensitive situation that could have significant implications if not addressed promptly. I would appreciate your prompt response and guidance on how to proceed.",
                "I'm reaching out regarding an urgent situation that needs your immediate attention. This matter is critical and requires a swift response to prevent any potential issues. I believe your expertise and quick action could make a real difference here.",
                "I hope this message reaches you quickly. There's an urgent matter that requires your immediate attention and action. This is something that can't wait and I need your input to resolve it effectively."
            ],
            "followup": [
                "I hope this message finds you well. I'm following up on our previous conversation and wanted to check in on the status of our discussion. I wanted to see how things are progressing and if there are any updates or developments I should be aware of.",
                "I hope you're doing well. I'm circling back to our recent conversation and wanted to see how things are progressing. I wanted to make sure we're still on track and if there's anything I can do to help move things forward.",
                "I hope this email finds you in good spirits. I'm reaching out to follow up on our previous discussion and check on the current status. I wanted to ensure we're aligned and see if there are any next steps we should be considering."
            ],
            "introduction": [
                "I hope this message finds you well. I wanted to introduce myself and express my interest in connecting with you professionally. I've heard great things about your work and believe there could be some interesting opportunities for collaboration between us.",
                "I hope you're doing well. I'm reaching out to introduce myself and explore potential opportunities for collaboration. I'm impressed by your work and think we might have some common interests that could lead to productive partnerships.",
                "I hope this email finds you in good health. I wanted to introduce myself and discuss potential ways we might work together. I believe our skills and interests could complement each other well, and I'd love to explore this possibility."
            ],
            "collaboration": [
                "I hope this message finds you well. I'm reaching out to discuss potential collaboration opportunities that I believe could be mutually beneficial. I've been thinking about ways we could work together and have some ideas I'd like to share with you.",
                "I hope you're doing well. I wanted to explore working together on some exciting projects I have in mind. I believe our combined expertise could create something really special, and I'd love to discuss the possibilities.",
                "I hope this email finds you in good spirits. I'm interested in discussing collaboration opportunities that could benefit both of us. I have some ideas that I think could be very interesting and would value your input."
            ],
            "feedback": [
                "I hope this message finds you well. I would greatly appreciate your feedback on a recent project and value your insights. Your perspective would be very helpful in improving our work and ensuring we're on the right track.",
                "I hope you're doing well. I'm reaching out to request your feedback on some work we've been developing. Your expertise in this area would be invaluable, and I'd love to hear your thoughts on how we can improve.",
                "I hope this email finds you in good health. I would value your opinion and feedback on a project we're working on. Your experience and insights would be very helpful in guiding our next steps."
            ],
            "proposal": [
                "I hope this message finds you well. I have a proposal that I believe could be of interest to you and would appreciate the opportunity to discuss it. I think this could be a great opportunity for both of us, and I'd love to share the details.",
                "I hope you're doing well. I wanted to share a proposal with you that I think could be beneficial for both of us. I've put a lot of thought into this and believe it could lead to some exciting possibilities.",
                "I hope this email finds you in good spirits. I have an idea I'd like to propose and would appreciate your thoughts on it. I believe this could be something really special and would value your input."
            ],
            "confirmation": [
                "I hope this message finds you well. I'm writing to confirm the details of our upcoming arrangement and ensure everything is in order. I want to make sure we're both on the same page and that all the necessary preparations are in place.",
                "I hope you're doing well. I wanted to confirm the specifics of our planned meeting and make sure we're aligned on the details. I want to ensure everything goes smoothly and that we have all the information we need.",
                "I hope this email finds you in good health. I'm reaching out to confirm our arrangements and verify all the details. I want to make sure everything is clear and that we're both prepared for what's ahead."
            ],
            "general": [
                "I hope this message finds you well. I wanted to reach out to you about something important that I believe would be of interest to you. I think this could be beneficial for both of us, and I'd love to discuss the possibilities.",
                "I hope you're doing well. I'm reaching out to connect with you regarding a matter that might interest you and could be beneficial for both of us. I have some ideas I'd like to share and would value your input.",
                "I hope this email finds you in good spirits. I wanted to get in touch to discuss a few things that I think would be worth your attention. I believe this could lead to some interesting opportunities and would love to explore them with you."
            ]
        }
        
        templates = content_templates.get(intent, content_templates["general"])
        
        # Add urgency context if needed
        if urgency == "urgent":
            templates = [
                "I need to bring an urgent matter to your attention that requires immediate action. " + template
                for template in templates
            ]
        
        # Select a random template for variety
        return random.choice(templates)
    
    def _build_comprehensive_content(self, intent: str, tone: str, formality: str, coherent_sentence: str, specific_content: str) -> str:
        """Build comprehensive email content around the specific user request."""
        
        # Start with the coherent sentence
        main_content = coherent_sentence
        
        # Add additional context and details based on intent
        if intent == "meeting_request":
            additional_context = [
                " I believe this meeting would be very productive and could help us move forward with our goals. I'm flexible with timing and would be happy to work around your schedule.",
                " This would give us the opportunity to discuss this in detail and ensure we're both on the same page. I'm available at your convenience and can accommodate your schedule.",
                " I think this would be the best way to address this matter effectively and ensure we have a clear plan moving forward. Please let me know what times work best for you."
            ]
            main_content += random.choice(additional_context)
            
        elif intent == "thank_you":
            additional_context = [
                " Your support has meant a great deal to our team, and we're truly grateful for your generosity and expertise. I hope we can continue to work together in the future.",
                " Your contributions have made a real difference, and I wanted to make sure you know how much we appreciate everything you've done. Thank you again for your time and effort.",
                " We're very fortunate to have your support, and I wanted to express our sincere appreciation for all your help. Your expertise and guidance have been invaluable."
            ]
            main_content += random.choice(additional_context)
            
        elif intent == "inquiry":
            additional_context = [
                " I believe your insights would be very valuable for our current project, and I would appreciate any guidance you can provide. Thank you in advance for your time and expertise.",
                " Your experience in this area would be very helpful, and I would be grateful for any advice or suggestions you might have. I look forward to hearing from you.",
                " I think your perspective would be very valuable, and I would appreciate any input you can share. Thank you for considering my request."
            ]
            main_content += random.choice(additional_context)
            
        elif intent == "update":
            additional_context = [
                " I wanted to make sure you're kept informed of our progress and that you have all the information you need. Please let me know if you have any questions or if there's anything else you'd like to know.",
                " I believe this update will help keep us aligned and ensure we're moving in the right direction. I'm happy to provide more details if needed.",
                " I wanted to share this information with you and make sure we're both on the same page. Please don't hesitate to reach out if you need any clarification."
            ]
            main_content += random.choice(additional_context)
            
        else:
            # For other intents, add a general follow-up
            additional_context = [
                " I wanted to make sure you have all the information you need and that we're aligned on this matter. Please let me know if you have any questions or if there's anything else I can help with.",
                " I believe this addresses the key points we discussed, and I wanted to ensure everything is clear. I'm happy to provide additional details if needed.",
                " I wanted to follow up on this and make sure we're both on the same page. Please don't hesitate to reach out if you need any clarification or have any questions."
            ]
            main_content += random.choice(additional_context)
        
        return main_content
    
    def _generate_closing(self, tone: str, formality: str, action_required: bool, urgency: str) -> str:
        """Generate appropriate closing with more detail and completeness."""
        
        if urgency == "urgent":
            if formality == "formal":
                closing = "I look forward to your prompt response and appreciate your immediate attention to this matter."
            else:
                closing = "Looking forward to hearing from you soon - this is quite urgent!"
        elif action_required:
            if formality == "formal":
                closing = "I look forward to hearing from you soon and appreciate your time and consideration."
            else:
                closing = "Looking forward to hearing from you soon!"
        elif tone == "friendly":
            if formality == "formal":
                closing = "I appreciate your time and look forward to our continued collaboration."
            else:
                closing = "Thanks so much for your time - looking forward to catching up soon!"
        elif tone == "professional":
            if formality == "formal":
                closing = "I appreciate your time and consideration, and look forward to our continued professional relationship."
            else:
                closing = "Thank you for your time and I look forward to working with you."
        elif tone == "apologetic":
            if formality == "formal":
                closing = "I appreciate your understanding and patience, and look forward to resolving this matter."
            else:
                closing = "Thanks for your understanding - I really appreciate it."
        elif tone == "enthusiastic":
            if formality == "formal":
                closing = "I'm excited about the possibilities ahead and look forward to our continued collaboration."
            else:
                closing = "I'm really excited about this and can't wait to work together!"
        else:
            if formality == "formal":
                closing = "I appreciate your time and look forward to hearing from you."
            else:
                closing = "Looking forward to hearing from you!"
        
        return closing
    
    def _generate_signature(self, tone: str, formality: str) -> str:
        """Generate appropriate signature with more detail and professionalism."""
        
        if formality == "formal":
            signature = """Best regards,
Smart Agent System
Multi-Platform Services
Email: smartagent@multiplatformservices.com
Phone: +1 (555) 123-4567
Website: www.multiplatformservices.com"""
        elif tone == "friendly":
            signature = """Best wishes,
Smart Agent System
Multi-Platform Services
Let's make great things happen together!"""
        elif tone == "professional":
            signature = """Sincerely,
Smart Agent System
Multi-Platform Services
Professional Solutions for Modern Business"""
        elif tone == "enthusiastic":
            signature = """Excited to work with you,
Smart Agent System
Multi-Platform Services
Innovation • Collaboration • Success"""
        else:
            signature = """Best regards,
Smart Agent System
Multi-Platform Services"""
        
        return signature
    
    def _fallback_composition(self, user_message: str, to_email: str) -> Dict[str, str]:
        """Fallback email composition when AI analysis fails."""
        
        # Simple extraction from user message
        lines = user_message.split('\n')
        
        # Use first line as subject if it's short, otherwise use default
        potential_subject = lines[0].strip()
        if len(potential_subject) < 50 and not '@' in potential_subject:
            subject = potential_subject
            body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else "Please see the subject line for details."
        else:
            subject = "Message from Smart Agent"
            body = user_message
        
        return {
            "subject": subject,
            "body": body,
            "intent": "general",
            "tone": "professional"
        }

# Global instance
email_composer = IntelligentEmailComposer() 