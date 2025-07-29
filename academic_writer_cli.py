#!/usr/bin/env python3
"""
Academic Writer CLI
==================

A specialized command-line interface for the Academic Writer Agent.
"""

import sys
import os
import asyncio
from datetime import datetime
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.academic_writer import academic_writer

class AcademicWriterCLI:
    """Command-line interface for the Academic Writer Agent."""
    
    def __init__(self):
        self.writer = academic_writer
    
    def print_banner(self):
        """Print the application banner."""
        print("=" * 70)
        print("🎓 Academic Writer Agent CLI")
        print("=" * 70)
        print("Specialized academic writing assistant for essays, papers, and research")
        print("Type 'help' for commands or 'exit' to quit")
        print("=" * 70)
    
    def print_help(self):
        """Print help information."""
        print("\n📚 Academic Writer Commands:")
        print("-" * 40)
        print("write essay about [topic]          - Write an academic essay")
        print("write research paper on [topic]    - Write a research paper")
        print("write argumentative essay about [topic] - Write argumentative essay")
        print("write analytical paper on [topic]  - Write analytical paper")
        print("write compare contrast essay about [topic] - Compare/contrast essay")
        print("write narrative essay about [topic] - Write narrative essay")
        print("\n📏 Length Options:")
        print("- short (500 words)")
        print("- medium (1000 words) - Default")
        print("- long (2000 words)")
        print("- extensive (3000 words)")
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
        print("write essay about climate change")
        print("write research paper on artificial intelligence")
        print("write argumentative essay about remote work")
        print("write analytical paper on digital marketing")
        print("write compare contrast essay about traditional vs online education")
        print("write narrative essay about personal growth")
        print("\n🔧 Advanced Options:")
        print("You can specify multiple options:")
        print("write long graduate research paper on machine learning")
        print("write short high_school argumentative essay about social media")
        print("write extensive doctoral thesis on quantum computing")
    
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
    
    def generate_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate academic content based on parameters."""
        
        if not params["topic"]:
            return {
                "success": False,
                "error": "No topic specified. Please provide a topic to write about."
            }
        
        try:
            print(f"\n🎓 Generating {params['content_type']} about: {params['topic']}")
            print(f"📏 Length: {params['length']}")
            print(f"🎓 Level: {params['academic_level']}")
            print(f"🎨 Style: {params['style']}")
            print("⏳ Please wait...")
            
            # Generate the content
            result = self.writer.write_academic_content(
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
                "error": f"Content generation failed: {str(e)}"
            }
    
    def display_result(self, result: Dict[str, Any]):
        """Display the generated content."""
        
        if not result["success"]:
            print(f"\n❌ Error: {result['error']}")
            return
        
        content_data = result["result"]
        
        print(f"\n✅ Content Generated Successfully!")
        print("=" * 60)
        print(f"📄 Title: {content_data.get('content', '').split('\n')[0]}")
        print(f"📊 Word Count: {content_data.get('word_count', 0)} words")
        print(f"📄 Estimated Pages: {content_data.get('estimated_pages', 0)} pages")
        print(f"🎨 Style: {content_data.get('style', 'unknown')}")
        print(f"🎓 Level: {content_data.get('academic_level', 'unknown')}")
        print("=" * 60)
        
        # Display the content
        content = content_data.get('content', '')
        print("\n📝 Generated Content:")
        print("-" * 40)
        print(content)
        print("-" * 40)
        
        # Offer to save to file
        self.offer_save_to_file(content_data)
    
    def offer_save_to_file(self, content_data: Dict[str, Any]):
        """Offer to save the content to a file."""
        
        print(f"\n💾 Would you like to save this to a file? (y/n): ", end="")
        response = input().lower().strip()
        
        if response in ['y', 'yes']:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            topic_clean = content_data.get('topic', 'academic_paper').replace(' ', '_').replace('/', '_')[:30]
            filename = f"academic_{topic_clean}_{timestamp}.txt"
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content_data.get('content', ''))
                
                print(f"✅ Content saved to: {filename}")
                
            except Exception as e:
                print(f"❌ Error saving file: {e}")
    
    def run(self):
        """Run the CLI."""
        
        self.print_banner()
        
        while True:
            try:
                print(f"\n🎓 Academic Writer > ", end="")
                command = input().strip()
                
                if not command:
                    continue
                
                if command.lower() in ['exit', 'quit', 'q']:
                    print("👋 Thank you for using Academic Writer Agent!")
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
                    print("❌ Please specify a topic to write about.")
                    print("💡 Example: write essay about climate change")
                    continue
                
                # Generate content
                result = self.generate_content(params)
                
                # Display result
                self.display_result(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 Thank you for using Academic Writer Agent!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("💡 Type 'help' for available commands")

def main():
    """Main function."""
    
    cli = AcademicWriterCLI()
    cli.run()

if __name__ == "__main__":
    main() 