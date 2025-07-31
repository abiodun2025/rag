#!/usr/bin/env python3
"""
Research-Enhanced Essay CLI
==========================

A specialized command-line interface for the Research-Enhanced Academic Writer
that performs online research and creates well-sourced essays.
"""

import sys
import os
import asyncio
from datetime import datetime
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.research_enhanced_writer import research_enhanced_writer

class ResearchEssayCLI:
    """Command-line interface for the Research-Enhanced Essay Writer."""
    
    def __init__(self):
        self.writer = research_enhanced_writer
    
    def print_banner(self):
        """Print the application banner."""
        print("=" * 70)
        print("🔍 Research-Enhanced Essay Writer CLI")
        print("=" * 70)
        print("AI-powered essay writer with real online research and sources")
        print("Type 'help' for commands or 'exit' to quit")
        print("=" * 70)
    
    def print_help(self):
        """Print help information."""
        print("\n📚 Research-Enhanced Essay Commands:")
        print("-" * 40)
        print("research essay about [topic]          - Write research-enhanced essay")
        print("research paper on [topic]             - Write research paper with sources")
        print("research argumentative essay about [topic] - Argumentative essay with research")
        print("research analytical essay on [topic]  - Analytical essay with research")
        print("research compare contrast essay about [topic] - Compare/contrast with research")
        print("research narrative essay about [topic] - Narrative essay with research")
        print("\n📏 Length Options:")
        print("- short (800+ words)")
        print("- medium (2000+ words) - Default")
        print("- long (4000+ words)")
        print("- extensive (6000+ words)")
        print("\n🎓 Academic Levels:")
        print("- high_school")
        print("- undergraduate - Default")
        print("- graduate")
        print("- doctoral")
        print("\n📝 Content Types:")
        print("- essay")
        print("- research_paper")
        print("- thesis")
        print("- dissertation")
        print("- article")
        print("- report")
        print("\n🎨 Styles:")
        print("- argumentative")
        print("- expository")
        print("- analytical")
        print("- research")
        print("- narrative")
        print("- compare_contrast")
        print("- auto (automatic detection)")
        print("\n💡 Examples:")
        print("research essay about climate change")
        print("research paper on artificial intelligence")
        print("research argumentative essay about remote work")
        print("research analytical essay on digital marketing")
        print("research compare contrast essay about traditional vs online education")
        print("research narrative essay about personal growth")
        print("\n🔧 Advanced Options:")
        print("You can specify multiple options:")
        print("research long graduate research paper on machine learning")
        print("research short high_school argumentative essay about social media")
        print("research extensive doctoral thesis on quantum computing")
        print("\n🔍 Research Features:")
        print("- Real online research and sources")
        print("- Current statistics and data")
        print("- Expert opinions and analysis")
        print("- Academic citations and references")
        print("- Recent developments and trends")
    
    def parse_command(self, command: str) -> Dict[str, Any]:
        """Parse user command and extract parameters."""
        
        command_lower = command.lower()
        
        # Default values
        params = {
            "topic": "",
            "content_type": "essay",
            "style": "auto",
            "length": "medium",
            "academic_level": "undergraduate"
        }
        
        # Extract content type
        if "research paper" in command_lower:
            params["content_type"] = "research_paper"
        elif "thesis" in command_lower:
            params["content_type"] = "thesis"
        elif "dissertation" in command_lower:
            params["content_type"] = "dissertation"
        elif "article" in command_lower:
            params["content_type"] = "article"
        elif "report" in command_lower:
            params["content_type"] = "report"
        
        # Extract style
        if "argumentative" in command_lower:
            params["style"] = "argumentative"
        elif "analytical" in command_lower:
            params["style"] = "analytical"
        elif "narrative" in command_lower:
            params["style"] = "narrative"
        elif "compare" in command_lower and "contrast" in command_lower:
            params["style"] = "compare_contrast"
        elif "expository" in command_lower:
            params["style"] = "expository"
        elif "research" in command_lower and "paper" in command_lower:
            params["style"] = "research"
        
        # Extract length
        if "short" in command_lower:
            params["length"] = "short"
        elif "long" in command_lower:
            params["length"] = "long"
        elif "extensive" in command_lower:
            params["length"] = "extensive"
        
        # Extract academic level
        if "high school" in command_lower or "high_school" in command_lower:
            params["academic_level"] = "high_school"
        elif "graduate" in command_lower:
            params["academic_level"] = "graduate"
        elif "doctoral" in command_lower or "doctorate" in command_lower:
            params["academic_level"] = "doctoral"
        
        # Extract topic (everything after "about" or "on")
        topic_keywords = ["about", "on", "regarding", "concerning"]
        for keyword in topic_keywords:
            if keyword in command_lower:
                # Find the position of the keyword
                pos = command_lower.find(keyword)
                # Extract everything after the keyword
                topic_part = command[pos + len(keyword):].strip()
                if topic_part:
                    params["topic"] = topic_part
                    break
        
        return params
    
    async def generate_research_essay(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate research-enhanced essay based on parameters."""
        
        if not params["topic"]:
            return {
                "success": False,
                "error": "No topic specified. Please provide a topic to research and write about."
            }
        
        try:
            print(f"\n🔍 Researching: {params['topic']}")
            print(f"📝 Type: {params['content_type']}")
            print(f"📏 Length: {params['length']}")
            print(f"🎓 Level: {params['academic_level']}")
            print(f"🎨 Style: {params['style']}")
            print("⏳ Researching and writing... This may take a few minutes.")
            
            # Generate the research-enhanced essay
            result = await self.writer.write_research_enhanced_essay(
                topic=params["topic"],
                content_type=params["content_type"],
                style=params["style"],
                length=params["length"],
                academic_level=params["academic_level"]
            )
            
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"]
                }
            
            return {
                "success": True,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Research essay generation failed: {str(e)}"
            }
    
    def display_result(self, result: Dict[str, Any]):
        """Display the generated research-enhanced essay."""
        
        if not result["success"]:
            print(f"\n❌ Error: {result['error']}")
            return
        
        content_data = result["result"]
        
        print(f"\n✅ Research-Enhanced Essay Generated Successfully!")
        print("=" * 60)
        print(f"📄 Title: {content_data.get('content', '').split('\n')[0]}")
        print(f"📊 Word Count: {content_data.get('word_count', 0)} words")
        print(f"📄 Estimated Pages: {content_data.get('estimated_pages', 0)} pages")
        print(f"🎨 Style: {content_data.get('style', 'unknown')}")
        print(f"🎓 Level: {content_data.get('academic_level', 'unknown')}")
        print(f"🔍 Sources: {content_data.get('sources_count', 0)} research sources")
        print("=" * 60)
        
        # Display research information
        research_data = content_data.get('research_data', {})
        if research_data:
            print(f"\n🔍 Research Summary:")
            print(f"   📊 Statistics found: {len(research_data.get('statistics', []))}")
            print(f"   📝 Key findings: {len(research_data.get('key_findings', []))}")
            print(f"   👨‍🎓 Expert opinions: {len(research_data.get('expert_opinions', []))}")
            print(f"   📚 Academic sources: {len(research_data.get('academic_papers', []))}")
        
        # Display the content
        content = content_data.get('content', '')
        print(f"\n📝 Generated Research-Enhanced Essay:")
        print("-" * 40)
        print(content)
        print("-" * 40)
        
        # Offer to save to file
        self.offer_save_to_file(content_data)
    
    def offer_save_to_file(self, content_data: Dict[str, Any]):
        """Offer to save the research-enhanced essay to a file."""
        
        print(f"\n💾 Would you like to save this research-enhanced essay to a file? (y/n): ", end="")
        response = input().lower().strip()
        
        if response in ['y', 'yes']:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            topic_clean = content_data.get('topic', 'research_essay').replace(' ', '_').replace('/', '_')[:30]
            filename = f"research_essay_{topic_clean}_{timestamp}.txt"
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content_data.get('content', ''))
                
                print(f"✅ Research-enhanced essay saved to: {filename}")
                
                # Also save research data separately
                research_filename = f"research_data_{topic_clean}_{timestamp}.txt"
                research_data = content_data.get('research_data', {})
                if research_data:
                    with open(research_filename, 'w', encoding='utf-8') as f:
                        f.write("RESEARCH DATA SUMMARY\n")
                        f.write("=" * 50 + "\n\n")
                        f.write(f"Topic: {content_data.get('topic', '')}\n")
                        f.write(f"Sources: {content_data.get('sources_count', 0)}\n\n")
                        
                        if research_data.get('citations'):
                            f.write("CITATIONS:\n")
                            f.write("-" * 20 + "\n")
                            for i, citation in enumerate(research_data['citations'], 1):
                                f.write(f"{i}. {citation}\n")
                            f.write("\n")
                        
                        if research_data.get('statistics'):
                            f.write("STATISTICS:\n")
                            f.write("-" * 20 + "\n")
                            for stat in research_data['statistics']:
                                f.write(f"- {stat}\n")
                            f.write("\n")
                        
                        if research_data.get('key_findings'):
                            f.write("KEY FINDINGS:\n")
                            f.write("-" * 20 + "\n")
                            for finding in research_data['key_findings']:
                                f.write(f"- {finding}\n")
                            f.write("\n")
                    
                    print(f"📊 Research data saved to: {research_filename}")
                
            except Exception as e:
                print(f"❌ Error saving file: {e}")
    
    async def run(self):
        """Run the CLI."""
        
        self.print_banner()
        
        while True:
            try:
                print(f"\n🔍 Research Essay Writer > ", end="")
                command = input().strip()
                
                if not command:
                    continue
                
                if command.lower() in ['exit', 'quit', 'q']:
                    print("👋 Thank you for using Research-Enhanced Essay Writer!")
                    break
                
                if command.lower() in ['help', 'h', '?']:
                    self.print_help()
                    continue
                
                if command.lower() in ['clear', 'cls']:
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.print_banner()
                    continue
                
                # Parse the command
                params = self.parse_command(command)
                
                if not params["topic"]:
                    print("❌ Please specify a topic to research and write about.")
                    print("💡 Example: research essay about climate change")
                    continue
                
                # Generate research-enhanced essay
                result = await self.generate_research_essay(params)
                
                # Display result
                self.display_result(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 Thank you for using Research-Enhanced Essay Writer!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("💡 Type 'help' for available commands")

async def main():
    """Main function."""
    
    cli = ResearchEssayCLI()
    await cli.run()

if __name__ == "__main__":
    asyncio.run(main()) 