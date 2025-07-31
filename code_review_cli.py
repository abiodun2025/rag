#!/usr/bin/env python3
"""
Code Review CLI
==============

A command-line interface for the Code Reviewer Agent that provides
comprehensive code analysis, issue identification, and improvement suggestions.
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, List

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.code_reviewer import code_reviewer

class CodeReviewCLI:
    """Command-line interface for the Code Reviewer Agent."""
    
    def __init__(self):
        self.reviewer = code_reviewer
    
    def print_banner(self):
        """Print the application banner."""
        print("=" * 70)
        print("🔍 Code Reviewer CLI")
        print("=" * 70)
        print("Comprehensive code analysis, issue detection, and improvement suggestions")
        print("Type 'help' for commands or 'exit' to quit")
        print("=" * 70)
    
    def print_help(self):
        """Print help information."""
        print("\n🔍 Code Review Commands:")
        print("-" * 40)
        print("review [filename]                    - Review a specific file")
        print("review code [code]                   - Review code from input")
        print("analyze [filename]                   - Analyze code structure")
        print("issues [filename]                    - List all issues found")
        print("suggestions [filename]               - Get improvement suggestions")
        print("report [filename] [output.json]      - Generate detailed report")
        print("batch [directory]                    - Review all files in directory")
        print("\n📊 Analysis Categories:")
        print("- Security vulnerabilities")
        print("- Performance optimizations")
        print("- Code readability")
        print("- Style and formatting")
        print("- Documentation")
        print("- Architecture patterns")
        print("- Testing practices")
        print("- Error handling")
        print("- Code complexity")
        print("- Best practices")
        print("\n🎯 Severity Levels:")
        print("- 🔴 Critical: Must fix immediately")
        print("- 🟠 High: Should address soon")
        print("- 🟡 Medium: Consider fixing")
        print("- 🟢 Low: Suggestions for improvement")
        print("- ℹ️  Info: Informational notes")
        print("\n💡 Examples:")
        print("review myfile.py")
        print("review code 'def hello(): print(\"Hello\")'")
        print("analyze project/main.py")
        print("issues src/utils.py")
        print("suggestions app/views.py")
        print("report backend/api.py report.json")
        print("batch ./src")
        print("\n🔧 Supported Languages:")
        print("- Python (.py)")
        print("- JavaScript (.js, .jsx, .ts, .tsx)")
        print("- Java (.java)")
        print("- C++ (.cpp, .cc, .cxx, .h, .hpp)")
        print("- C# (.cs)")
        print("- Generic (other languages)")
    
    def read_file(self, filename: str) -> str:
        """Read file content."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
            return ""
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return ""
    
    def review_file(self, filename: str) -> Dict[str, Any]:
        """Review a specific file."""
        
        if not os.path.exists(filename):
            return {
                "success": False,
                "error": f"File not found: {filename}"
            }
        
        code = self.read_file(filename)
        if not code:
            return {
                "success": False,
                "error": "Could not read file content"
            }
        
        try:
            print(f"🔍 Reviewing: {filename}")
            report = self.reviewer.generate_report(code, filename)
            return {
                "success": True,
                "report": report
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Review failed: {str(e)}"
            }
    
    def review_code(self, code: str) -> Dict[str, Any]:
        """Review code from input."""
        
        try:
            print("🔍 Reviewing provided code...")
            report = self.reviewer.generate_report(code)
            return {
                "success": True,
                "report": report
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Review failed: {str(e)}"
            }
    
    def analyze_structure(self, filename: str) -> Dict[str, Any]:
        """Analyze code structure only."""
        
        code = self.read_file(filename)
        if not code:
            return {
                "success": False,
                "error": "Could not read file content"
            }
        
        try:
            language = self.reviewer.detect_language(code, filename)
            structure = self.reviewer.analyze_code_structure(code, language)
            
            return {
                "success": True,
                "language": language,
                "structure": structure
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }
    
    def get_issues(self, filename: str) -> Dict[str, Any]:
        """Get only the issues from a file."""
        
        code = self.read_file(filename)
        if not code:
            return {
                "success": False,
                "error": "Could not read file content"
            }
        
        try:
            language = self.reviewer.detect_language(code, filename)
            issues = self.reviewer.identify_issues(code, language)
            
            return {
                "success": True,
                "language": language,
                "issues": issues
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Issue detection failed: {str(e)}"
            }
    
    def get_suggestions(self, filename: str) -> Dict[str, Any]:
        """Get improvement suggestions for a file."""
        
        code = self.read_file(filename)
        if not code:
            return {
                "success": False,
                "error": "Could not read file content"
            }
        
        try:
            language = self.reviewer.detect_language(code, filename)
            issues = self.reviewer.identify_issues(code, language)
            suggestions = self.reviewer.suggest_improvements(code, language, issues)
            
            return {
                "success": True,
                "language": language,
                "suggestions": suggestions
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Suggestion generation failed: {str(e)}"
            }
    
    def generate_report_file(self, filename: str, output_file: str) -> Dict[str, Any]:
        """Generate a detailed report and save to file."""
        
        result = self.review_file(filename)
        if not result["success"]:
            return result
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result["report"], f, indent=2, default=str)
            
            return {
                "success": True,
                "message": f"Report saved to: {output_file}",
                "report": result["report"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to save report: {str(e)}"
            }
    
    def batch_review(self, directory: str) -> Dict[str, Any]:
        """Review all files in a directory."""
        
        if not os.path.exists(directory):
            return {
                "success": False,
                "error": f"Directory not found: {directory}"
            }
        
        if not os.path.isdir(directory):
            return {
                "success": False,
                "error": f"Not a directory: {directory}"
            }
        
        results = []
        supported_extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.cs']
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in supported_extensions):
                    filepath = os.path.join(root, file)
                    print(f"🔍 Reviewing: {filepath}")
                    
                    result = self.review_file(filepath)
                    if result["success"]:
                        results.append({
                            "file": filepath,
                            "report": result["report"]
                        })
                    else:
                        results.append({
                            "file": filepath,
                            "error": result["error"]
                        })
        
        return {
            "success": True,
            "total_files": len(results),
            "results": results
        }
    
    def display_report(self, report: Dict[str, Any]):
        """Display a code review report."""
        
        print(f"\n📊 Code Review Report")
        print("=" * 60)
        print(f"📄 File: {report.get('filename', 'Unknown')}")
        print(f"🔤 Language: {report.get('language', 'Unknown')}")
        print(f"📅 Timestamp: {report.get('timestamp', 'Unknown')}")
        print(f"📈 Score: {report.get('score', 0)}/100 ({report.get('grade', 'Unknown')})")
        
        # Summary
        summary = report.get('summary', {})
        print(f"\n📋 Code Summary:")
        print(f"   📏 Lines of Code: {summary.get('lines_of_code', 0)}")
        print(f"   🔧 Functions: {summary.get('functions', 0)}")
        print(f"   🏗️  Classes: {summary.get('classes', 0)}")
        print(f"   📦 Imports: {summary.get('imports', 0)}")
        print(f"   🧮 Complexity Score: {summary.get('complexity_score', 0)}")
        print(f"   📐 Max Nesting Depth: {summary.get('nesting_depth', 0)}")
        
        # Issues summary
        issues = report.get('issues', {})
        print(f"\n🚨 Issues Summary:")
        print(f"   🔴 Critical: {issues.get('critical', 0)}")
        print(f"   🟠 High: {issues.get('high', 0)}")
        print(f"   🟡 Medium: {issues.get('medium', 0)}")
        print(f"   🟢 Low: {issues.get('low', 0)}")
        print(f"   📊 Total: {issues.get('total', 0)}")
        
        # Issues by category
        by_category = issues.get('by_category', {})
        if by_category:
            print(f"\n📂 Issues by Category:")
            for category, count in by_category.items():
                print(f"   {category.title()}: {count}")
        
        # Critical and high issues
        issue_details = issues.get('details', [])
        critical_high_issues = [i for i in issue_details if i.get('severity') in ['critical', 'high']]
        
        if critical_high_issues:
            print(f"\n🚨 Critical & High Priority Issues:")
            for issue in critical_high_issues:
                severity_emoji = "🔴" if issue.get('severity') == 'critical' else "🟠"
                print(f"   {severity_emoji} Line {issue.get('line', 'N/A')}: {issue.get('message', '')}")
                if issue.get('suggestion'):
                    print(f"      💡 Suggestion: {issue.get('suggestion')}")
        
        # Suggestions
        suggestions = report.get('suggestions', [])
        if suggestions:
            print(f"\n💡 Improvement Suggestions:")
            for suggestion in suggestions[:5]:  # Show first 5
                severity_emoji = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢',
                    'info': 'ℹ️'
                }.get(suggestion.get('severity', 'info'), 'ℹ️')
                
                print(f"   {severity_emoji} {suggestion.get('category', '').title()}: {suggestion.get('message', '')}")
                if suggestion.get('suggestion'):
                    print(f"      💡 {suggestion.get('suggestion')}")
        
        # Recommendations
        recommendations = report.get('recommendations', [])
        if recommendations:
            print(f"\n🎯 Key Recommendations:")
            for rec in recommendations:
                print(f"   {rec}")
        
        print("=" * 60)
    
    def display_structure(self, structure: Dict[str, Any], language: str):
        """Display code structure analysis."""
        
        print(f"\n🏗️  Code Structure Analysis ({language})")
        print("=" * 50)
        print(f"📏 Lines of Code: {structure.get('lines_of_code', 0)}")
        print(f"🔧 Functions: {len(structure.get('functions', []))}")
        print(f"🏗️  Classes: {len(structure.get('classes', []))}")
        print(f"📦 Imports: {len(structure.get('imports', []))}")
        print(f"🧮 Complexity Score: {structure.get('complexity_score', 0)}")
        print(f"📐 Max Nesting Depth: {structure.get('nesting_depth', 0)}")
        
        # Show functions
        functions = structure.get('functions', [])
        if functions:
            print(f"\n🔧 Functions:")
            for func in functions:
                if isinstance(func, dict):
                    name = func.get('name', 'Unknown')
                    line = func.get('line', 'N/A')
                    args = func.get('args', 'N/A')
                    print(f"   - {name} (line {line}, {args} args)")
        
        # Show classes
        classes = structure.get('classes', [])
        if classes:
            print(f"\n🏗️  Classes:")
            for cls in classes:
                if isinstance(cls, dict):
                    name = cls.get('name', 'Unknown')
                    line = cls.get('line', 'N/A')
                    methods = cls.get('methods', 'N/A')
                    print(f"   - {name} (line {line}, {methods} methods)")
        
        print("=" * 50)
    
    def display_issues(self, issues: List[Dict[str, Any]], language: str):
        """Display issues found in code."""
        
        print(f"\n🚨 Issues Found ({language})")
        print("=" * 50)
        
        if not issues:
            print("✅ No issues found!")
            return
        
        # Group by severity
        by_severity = {}
        for issue in issues:
            severity = issue.get('severity', 'unknown')
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(issue)
        
        severity_order = ['critical', 'high', 'medium', 'low', 'info']
        severity_emojis = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢',
            'info': 'ℹ️'
        }
        
        for severity in severity_order:
            if severity in by_severity:
                emoji = severity_emojis.get(severity, 'ℹ️')
                print(f"\n{emoji} {severity.upper()} Priority Issues:")
                for issue in by_severity[severity]:
                    line = issue.get('line', 'N/A')
                    category = issue.get('category', 'unknown').title()
                    message = issue.get('message', '')
                    print(f"   Line {line} ({category}): {message}")
                    if issue.get('suggestion'):
                        print(f"      💡 {issue.get('suggestion')}")
        
        print("=" * 50)
    
    def display_suggestions(self, suggestions: List[Dict[str, Any]], language: str):
        """Display improvement suggestions."""
        
        print(f"\n💡 Improvement Suggestions ({language})")
        print("=" * 50)
        
        if not suggestions:
            print("✅ No suggestions available!")
            return
        
        # Group by category
        by_category = {}
        for suggestion in suggestions:
            category = suggestion.get('category', 'unknown')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(suggestion)
        
        for category, category_suggestions in by_category.items():
            print(f"\n📂 {category.title()}:")
            for suggestion in category_suggestions:
                severity_emoji = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢',
                    'info': 'ℹ️'
                }.get(suggestion.get('severity', 'info'), 'ℹ️')
                
                message = suggestion.get('message', '')
                print(f"   {severity_emoji} {message}")
                if suggestion.get('suggestion'):
                    print(f"      💡 {suggestion.get('suggestion')}")
        
        print("=" * 50)
    
    def run(self):
        """Run the CLI."""
        
        self.print_banner()
        
        while True:
            try:
                print(f"\n🔍 Code Reviewer > ", end="")
                command = input().strip()
                
                if not command:
                    continue
                
                if command.lower() in ['exit', 'quit', 'q']:
                    print("👋 Thank you for using Code Reviewer!")
                    break
                
                if command.lower() in ['help', 'h', '?']:
                    self.print_help()
                    continue
                
                if command.lower() in ['clear', 'cls']:
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.print_banner()
                    continue
                
                # Parse command
                parts = command.split()
                if not parts:
                    continue
                
                action = parts[0].lower()
                
                if action == 'review':
                    if len(parts) < 2:
                        print("❌ Please specify a file to review.")
                        print("💡 Example: review myfile.py")
                        continue
                    
                    if parts[1] == 'code' and len(parts) >= 3:
                        # Review code from input
                        code = ' '.join(parts[2:])
                        result = self.review_code(code)
                        if result["success"]:
                            self.display_report(result["report"])
                        else:
                            print(f"❌ {result['error']}")
                    else:
                        # Review file
                        filename = parts[1]
                        result = self.review_file(filename)
                        if result["success"]:
                            self.display_report(result["report"])
                        else:
                            print(f"❌ {result['error']}")
                
                elif action == 'analyze':
                    if len(parts) < 2:
                        print("❌ Please specify a file to analyze.")
                        continue
                    
                    filename = parts[1]
                    result = self.analyze_structure(filename)
                    if result["success"]:
                        self.display_structure(result["structure"], result["language"])
                    else:
                        print(f"❌ {result['error']}")
                
                elif action == 'issues':
                    if len(parts) < 2:
                        print("❌ Please specify a file to check for issues.")
                        continue
                    
                    filename = parts[1]
                    result = self.get_issues(filename)
                    if result["success"]:
                        self.display_issues(result["issues"], result["language"])
                    else:
                        print(f"❌ {result['error']}")
                
                elif action == 'suggestions':
                    if len(parts) < 2:
                        print("❌ Please specify a file to get suggestions for.")
                        continue
                    
                    filename = parts[1]
                    result = self.get_suggestions(filename)
                    if result["success"]:
                        self.display_suggestions(result["suggestions"], result["language"])
                    else:
                        print(f"❌ {result['error']}")
                
                elif action == 'report':
                    if len(parts) < 2:
                        print("❌ Please specify a file to generate report for.")
                        continue
                    
                    filename = parts[1]
                    output_file = parts[2] if len(parts) > 2 else f"code_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    
                    result = self.generate_report_file(filename, output_file)
                    if result["success"]:
                        print(f"✅ {result['message']}")
                        self.display_report(result["report"])
                    else:
                        print(f"❌ {result['error']}")
                
                elif action == 'batch':
                    if len(parts) < 2:
                        print("❌ Please specify a directory to review.")
                        continue
                    
                    directory = parts[1]
                    result = self.batch_review(directory)
                    if result["success"]:
                        print(f"✅ Batch review completed for {result['total_files']} files")
                        for file_result in result["results"]:
                            if "error" in file_result:
                                print(f"   ❌ {file_result['file']}: {file_result['error']}")
                            else:
                                report = file_result["report"]
                                score = report.get('score', 0)
                                grade = report.get('grade', 'Unknown')
                                print(f"   ✅ {file_result['file']}: {score}/100 ({grade})")
                    else:
                        print(f"❌ {result['error']}")
                
                else:
                    print(f"❌ Unknown command: {action}")
                    print("💡 Type 'help' for available commands")
                
            except KeyboardInterrupt:
                print("\n\n👋 Thank you for using Code Reviewer!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("💡 Type 'help' for available commands")

def main():
    """Main function."""
    
    cli = CodeReviewCLI()
    cli.run()

if __name__ == "__main__":
    main() 