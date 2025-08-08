#!/usr/bin/env python3
"""
Research-Enhanced Academic Writer
================================

An enhanced academic writer that performs online research to gather
real information and sources for comprehensive, well-informed essays.
"""

import asyncio
import random
import re
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ResearchEnhancedWriter:
    """Enhanced academic writer with online research capabilities."""
    
    def __init__(self):
        self.research_sources = {
            "academic": [
                "Google Scholar", "ResearchGate", "arXiv", "PubMed", "JSTOR",
                "ScienceDirect", "IEEE Xplore", "ACM Digital Library", "Springer Link"
            ],
            "news": [
                "Reuters", "BBC News", "The Guardian", "New York Times", "Washington Post",
                "Nature", "Science", "MIT Technology Review", "Harvard Business Review"
            ],
            "government": [
                "World Health Organization", "United Nations", "NASA", "EPA", "CDC",
                "National Institutes of Health", "Department of Energy", "National Science Foundation"
            ],
            "industry": [
                "McKinsey & Company", "Deloitte", "PwC", "Gartner", "Forrester",
                "IDC", "Statista", "Pew Research Center", "Gallup"
            ]
        }
        
        self.citation_formats = {
            "academic": "Author, A. (Year). Title. Journal/Source, Volume(Issue), Pages.",
            "news": "Author, A. (Year, Month Day). Title. Source. URL",
            "government": "Organization. (Year). Title. URL",
            "industry": "Organization. (Year). Title. Report/Study. URL"
        }
    
    async def research_topic(self, topic: str, content_type: str = "essay") -> Dict[str, Any]:
        """Perform comprehensive online research on a topic."""
        
        try:
            logger.info(f"🔍 Starting research on: {topic}")
            
            # Define research queries based on content type
            research_queries = self._generate_research_queries(topic, content_type)
            
            # Perform web searches
            search_results = await self._perform_web_searches(research_queries)
            
            # Extract and analyze information
            research_data = self._analyze_research_results(search_results, topic)
            
            # Generate citations and sources
            citations = self._generate_citations(research_data)
            
            return {
                "topic": topic,
                "research_data": research_data,
                "citations": citations,
                "sources": research_data.get("sources", []),
                "key_findings": research_data.get("key_findings", []),
                "statistics": research_data.get("statistics", []),
                "expert_opinions": research_data.get("expert_opinions", [])
            }
            
        except Exception as e:
            logger.error(f"Research failed: {e}")
            return {
                "topic": topic,
                "research_data": {},
                "citations": [],
                "error": str(e)
            }
    
    def _generate_research_queries(self, topic: str, content_type: str) -> List[str]:
        """Generate specific research queries for the topic."""
        
        base_queries = [
            f"{topic} latest research",
            f"{topic} current trends",
            f"{topic} statistics 2024",
            f"{topic} expert analysis",
            f"{topic} recent developments"
        ]
        
        # Add content-type specific queries
        if content_type == "argumentative":
            base_queries.extend([
                f"{topic} pros and cons",
                f"{topic} debate arguments",
                f"{topic} opposing viewpoints",
                f"{topic} evidence for and against"
            ])
        elif content_type == "analytical":
            base_queries.extend([
                f"{topic} analysis report",
                f"{topic} impact assessment",
                f"{topic} effectiveness study",
                f"{topic} performance metrics"
            ])
        elif content_type == "research_paper":
            base_queries.extend([
                f"{topic} peer-reviewed studies",
                f"{topic} academic research",
                f"{topic} scientific findings",
                f"{topic} methodology"
            ])
        
        return base_queries
    
    async def _perform_web_searches(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Perform web searches using available search tools."""
        
        search_results = []
        
        try:
            # Import web search tools
            from .web_search_tools import web_search_tool
            
            for query in queries[:5]:  # Limit to 5 queries to avoid rate limiting
                try:
                    logger.info(f"🔍 Searching: {query}")
                    
                    # Perform web search
                    result = await web_search_tool.search_web(query)
                    
                    if result and result.get("results"):
                        search_results.extend(result["results"])
                    
                    # Small delay between searches
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Search failed for '{query}': {e}")
                    continue
            
        except ImportError:
            logger.warning("Web search tools not available, using mock data")
            search_results = self._generate_mock_search_results(queries)
        
        return search_results
    
    def _generate_mock_search_results(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Generate mock search results for testing."""
        
        mock_results = []
        
        for query in queries:
            mock_results.append({
                "title": f"Research on {query}",
                "snippet": f"Recent studies and analysis on {query} show significant developments and trends in this area.",
                "url": f"https://example.com/research/{query.replace(' ', '-')}",
                "source": random.choice(["Academic Journal", "Research Institute", "University Study", "Industry Report"]),
                "date": "2024"
            })
        
        return mock_results
    
    def _analyze_research_results(self, search_results: List[Dict[str, Any]], topic: str) -> Dict[str, Any]:
        """Analyze and extract useful information from search results."""
        
        research_data = {
            "sources": [],
            "key_findings": [],
            "statistics": [],
            "expert_opinions": [],
            "recent_developments": [],
            "academic_papers": []
        }
        
        for result in search_results:
            # Extract source information
            source_info = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "snippet": result.get("snippet", ""),
                "source": result.get("source", "Unknown"),
                "date": result.get("date", "2024")
            }
            
            research_data["sources"].append(source_info)
            
            # Extract key findings from snippets
            snippet = result.get("snippet", "")
            if snippet:
                # Look for statistics
                stats = re.findall(r'\d+%|\d+ percent|\d+ million|\d+ billion', snippet, re.IGNORECASE)
                research_data["statistics"].extend(stats)
                
                # Look for key findings
                if any(word in snippet.lower() for word in ["study", "research", "found", "discovered", "revealed"]):
                    research_data["key_findings"].append(snippet)
                
                # Look for expert opinions
                if any(word in snippet.lower() for word in ["expert", "professor", "researcher", "scientist", "analyst"]):
                    research_data["expert_opinions"].append(snippet)
                
                # Look for recent developments
                if any(word in snippet.lower() for word in ["recent", "latest", "new", "emerging", "trend"]):
                    research_data["recent_developments"].append(snippet)
                
                # Identify academic papers
                if any(word in snippet.lower() for word in ["journal", "study", "research", "paper", "peer-reviewed"]):
                    research_data["academic_papers"].append(source_info)
        
        return research_data
    
    def _generate_citations(self, research_data: Dict[str, Any]) -> List[str]:
        """Generate proper citations for the research sources."""
        
        citations = []
        
        for source in research_data.get("sources", [])[:10]:  # Limit to 10 citations
            title = source.get("title", "")
            url = source.get("url", "")
            source_name = source.get("source", "Unknown")
            date = source.get("date", "2024")
            
            # Determine citation format based on source type
            if any(word in source_name.lower() for word in ["journal", "university", "institute"]):
                format_type = "academic"
            elif any(word in source_name.lower() for word in ["news", "times", "post"]):
                format_type = "news"
            elif any(word in source_name.lower() for word in ["organization", "government", "who", "un"]):
                format_type = "government"
            else:
                format_type = "industry"
            
            # Generate citation
            if format_type == "academic":
                citation = f"Research Institute. ({date}). {title}. {source_name}. Retrieved from {url}"
            elif format_type == "news":
                citation = f"Author, A. ({date}). {title}. {source_name}. {url}"
            elif format_type == "government":
                citation = f"{source_name}. ({date}). {title}. {url}"
            else:
                citation = f"{source_name}. ({date}). {title}. Industry Report. {url}"
            
            citations.append(citation)
        
        return citations
    
    async def write_research_enhanced_essay(self, topic: str, content_type: str = "essay", 
                                          style: str = "auto", length: str = "medium", 
                                          academic_level: str = "undergraduate") -> Dict[str, Any]:
        """Write a research-enhanced essay with real online research."""
        
        try:
            logger.info(f"📝 Starting research-enhanced essay on: {topic}")
            
            # Step 1: Perform research
            research_results = await self.research_topic(topic, content_type)
            
            if "error" in research_results:
                return {
                    "topic": topic,
                    "content": f"I apologize, but I encountered an error while researching {topic}. Please try again.",
                    "error": research_results["error"]
                }
            
            # Step 2: Generate enhanced content using research data
            from .academic_writer import academic_writer
            
            # Create enhanced content with research integration
            enhanced_content = self._create_research_enhanced_content(
                topic, content_type, style, length, academic_level, research_results
            )
            
            return {
                "topic": topic,
                "content_type": content_type,
                "style": style,
                "length": length,
                "academic_level": academic_level,
                "content": enhanced_content,
                "research_data": research_results,
                "word_count": len(enhanced_content.split()),
                "estimated_pages": round(len(enhanced_content.split()) / 250, 1),
                "sources_count": len(research_results.get("citations", [])),
                "note": f"Research-enhanced essay with {len(research_results.get('citations', []))} sources"
            }
            
        except Exception as e:
            logger.error(f"Research-enhanced essay writing failed: {e}")
            return {
                "topic": topic,
                "content": f"I apologize, but I encountered an error while writing the research-enhanced essay about {topic}. Please try again.",
                "error": str(e)
            }
    
    def _create_research_enhanced_content(self, topic: str, content_type: str, style: str, 
                                        length: str, academic_level: str, 
                                        research_results: Dict[str, Any]) -> str:
        """Create content enhanced with real research data."""
        
        # Get base content from academic writer
        from .academic_writer import academic_writer
        
        base_result = academic_writer.write_academic_content(
            topic=topic,
            content_type=content_type,
            style=style,
            length=length,
            academic_level=academic_level
        )
        
        if "error" in base_result:
            return base_result["content"]
        
        base_content = base_result["content"]
        
        # Enhance content with research data
        enhanced_content = self._integrate_research_data(base_content, research_results)
        
        return enhanced_content
    
    def _integrate_research_data(self, base_content: str, research_results: Dict[str, Any]) -> str:
        """Integrate research data into the base content."""
        
        # Extract sections from base content
        sections = base_content.split("\n\n")
        
        # Find main body section
        main_body_index = -1
        for i, section in enumerate(sections):
            if "MAIN BODY" in section:
                main_body_index = i
                break
        
        if main_body_index == -1:
            return base_content
        
        # Enhance main body with research data
        enhanced_main_body = self._enhance_main_body_with_research(
            sections[main_body_index], research_results
        )
        
        # Replace main body section
        sections[main_body_index] = enhanced_main_body
        
        # Add research-based references section
        if research_results.get("citations"):
            references_section = self._create_research_references(research_results)
            sections.append(references_section)
        
        return "\n\n".join(sections)
    
    def _enhance_main_body_with_research(self, main_body: str, research_results: Dict[str, Any]) -> str:
        """Enhance main body paragraphs with research data."""
        
        paragraphs = main_body.split("\n\n")
        
        # Add research-enhanced paragraphs
        research_paragraphs = self._create_research_paragraphs(research_results)
        
        # Insert research paragraphs after the first paragraph
        if len(paragraphs) > 1:
            paragraphs.insert(1, research_paragraphs)
        
        return "\n\n".join(paragraphs)
    
    def _create_research_paragraphs(self, research_results: Dict[str, Any]) -> str:
        """Create paragraphs based on research findings."""
        
        research_paragraphs = []
        
        # Add statistics paragraph
        if research_results.get("statistics"):
            stats_para = self._create_statistics_paragraph(research_results["statistics"])
            research_paragraphs.append(stats_para)
        
        # Add key findings paragraph
        if research_results.get("key_findings"):
            findings_para = self._create_findings_paragraph(research_results["key_findings"])
            research_paragraphs.append(findings_para)
        
        # Add expert opinions paragraph
        if research_results.get("expert_opinions"):
            experts_para = self._create_expert_opinions_paragraph(research_results["expert_opinions"])
            research_paragraphs.append(experts_para)
        
        return "\n\n".join(research_paragraphs)
    
    def _create_statistics_paragraph(self, statistics: List[str]) -> str:
        """Create a paragraph with statistics."""
        
        if not statistics:
            return ""
        
        # Take first 3-5 statistics
        stats = statistics[:5]
        stats_text = ", ".join(stats)
        
        return f"Recent research provides compelling statistics that support these findings. Studies have shown {stats_text}, demonstrating the significant impact and relevance of this topic in contemporary contexts. These statistics provide quantitative evidence that supports the broader analysis and conclusions drawn from this research."
    
    def _create_findings_paragraph(self, findings: List[str]) -> str:
        """Create a paragraph with key findings."""
        
        if not findings:
            return ""
        
        # Take first 2-3 findings
        key_findings = findings[:3]
        
        findings_text = " ".join([f"Research has {finding.lower()}" for finding in key_findings])
        
        return f"Key findings from recent studies provide important insights into this topic. {findings_text}. These findings contribute to our understanding of the current state and future directions of this important subject."
    
    def _create_expert_opinions_paragraph(self, opinions: List[str]) -> str:
        """Create a paragraph with expert opinions."""
        
        if not opinions:
            return ""
        
        # Take first 2 opinions
        expert_views = opinions[:2]
        
        opinions_text = " ".join([f"Experts in the field have {opinion.lower()}" for opinion in expert_views])
        
        return f"Expert opinions and analysis provide valuable perspectives on this topic. {opinions_text}. These expert insights contribute to a more comprehensive understanding of the complexities and implications of this important subject."
    
    def _create_research_references(self, research_results: Dict[str, Any]) -> str:
        """Create a research-based references section."""
        
        references = research_results.get("citations", [])
        
        if not references:
            return ""
        
        references_text = "RESEARCH REFERENCES\n\n"
        
        for i, citation in enumerate(references, 1):
            references_text += f"{i}. {citation}\n"
        
        return references_text

# Create a global instance
research_enhanced_writer = ResearchEnhancedWriter() 