#!/usr/bin/env python3
"""
Code Reviewer Agent
==================

A specialized agent for comprehensive code review, analysis, and improvement suggestions.
"""

import ast
import re
import os
import sys
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
import subprocess
import tempfile

logger = logging.getLogger(__name__)

class CodeReviewer:
    """Comprehensive code review agent with multiple analysis capabilities."""
    
    def __init__(self):
        self.issue_categories = {
            "security": "Security vulnerabilities and best practices",
            "performance": "Performance optimizations and bottlenecks",
            "readability": "Code readability and maintainability",
            "style": "Code style and formatting",
            "documentation": "Documentation and comments",
            "architecture": "Architecture and design patterns",
            "testing": "Testing coverage and practices",
            "error_handling": "Error handling and edge cases",
            "complexity": "Code complexity and refactoring opportunities",
            "best_practices": "General best practices and conventions"
        }
        
        self.severity_levels = {
            "critical": "Critical issues that must be fixed immediately",
            "high": "High priority issues that should be addressed soon",
            "medium": "Medium priority issues that should be considered",
            "low": "Low priority suggestions for improvement",
            "info": "Informational notes and recommendations"
        }
        
        self.language_patterns = {
            "python": {
                "extensions": [".py"],
                "keywords": ["def", "class", "import", "from", "if", "for", "while", "try", "except"],
                "style_guide": "PEP 8"
            },
            "javascript": {
                "extensions": [".js", ".jsx", ".ts", ".tsx"],
                "keywords": ["function", "const", "let", "var", "if", "for", "while", "try", "catch"],
                "style_guide": "ESLint/Prettier"
            },
            "java": {
                "extensions": [".java"],
                "keywords": ["public", "class", "private", "static", "void", "if", "for", "while", "try", "catch"],
                "style_guide": "Google Java Style Guide"
            },
            "cpp": {
                "extensions": [".cpp", ".cc", ".cxx", ".h", ".hpp"],
                "keywords": ["class", "public", "private", "if", "for", "while", "try", "catch"],
                "style_guide": "Google C++ Style Guide"
            },
            "csharp": {
                "extensions": [".cs"],
                "keywords": ["public", "class", "private", "static", "void", "if", "for", "while", "try", "catch"],
                "style_guide": "Microsoft C# Coding Conventions"
            }
        }
    
    def detect_language(self, code: str, filename: str = "") -> str:
        """Detect the programming language of the code."""
        
        # Try to detect from filename first
        if filename:
            for lang, patterns in self.language_patterns.items():
                for ext in patterns["extensions"]:
                    if filename.endswith(ext):
                        return lang
        
        # Detect from code content
        code_lower = code.lower()
        
        # Python detection
        if any(keyword in code_lower for keyword in ["def ", "import ", "from ", "class ", "if __name__"]):
            return "python"
        
        # JavaScript detection
        if any(keyword in code_lower for keyword in ["function ", "const ", "let ", "var ", "console.log"]):
            return "javascript"
        
        # Java detection
        if any(keyword in code_lower for keyword in ["public class", "public static void", "import java"]):
            return "java"
        
        # C++ detection
        if any(keyword in code_lower for keyword in ["#include", "std::", "namespace", "class "]):
            return "cpp"
        
        # C# detection
        if any(keyword in code_lower for keyword in ["using System", "namespace ", "public class"]):
            return "csharp"
        
        return "unknown"
    
    def analyze_code_structure(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze the overall structure of the code."""
        
        analysis = {
            "lines_of_code": len(code.split('\n')),
            "functions": [],
            "classes": [],
            "imports": [],
            "complexity_score": 0,
            "nesting_depth": 0
        }
        
        if language == "python":
            return self._analyze_python_structure(code)
        elif language == "javascript":
            return self._analyze_javascript_structure(code)
        else:
            # Generic analysis for other languages
            return self._analyze_generic_structure(code, language)
    
    def _analyze_python_structure(self, code: str) -> Dict[str, Any]:
        """Analyze Python code structure using AST."""
        
        try:
            tree = ast.parse(code)
            analysis = {
                "lines_of_code": len(code.split('\n')),
                "functions": [],
                "classes": [],
                "imports": [],
                "complexity_score": 0,
                "nesting_depth": 0,
                "has_main": False,
                "has_docstrings": False
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": len(node.args.args),
                        "has_docstring": ast.get_docstring(node) is not None
                    })
                    analysis["complexity_score"] += 1
                    
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                        "has_docstring": ast.get_docstring(node) is not None
                    })
                    analysis["complexity_score"] += 2
                    
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis["imports"].append(alias.name)
                    else:
                        analysis["imports"].append(f"from {node.module}")
                
                elif isinstance(node, ast.If):
                    if "if __name__" in ast.unparse(node):
                        analysis["has_main"] = True
                
                # Calculate nesting depth
                if hasattr(node, 'lineno'):
                    depth = self._calculate_nesting_depth(node, tree)
                    analysis["nesting_depth"] = max(analysis["nesting_depth"], depth)
            
            return analysis
            
        except SyntaxError as e:
            return {
                "lines_of_code": len(code.split('\n')),
                "functions": [],
                "classes": [],
                "imports": [],
                "complexity_score": 0,
                "nesting_depth": 0,
                "syntax_error": str(e)
            }
    
    def _analyze_javascript_structure(self, code: str) -> Dict[str, Any]:
        """Analyze JavaScript code structure."""
        
        analysis = {
            "lines_of_code": len(code.split('\n')),
            "functions": [],
            "classes": [],
            "imports": [],
            "complexity_score": 0,
            "nesting_depth": 0
        }
        
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Detect functions
            if re.match(r'^(function\s+\w+|const\s+\w+\s*=\s*\(|let\s+\w+\s*=\s*\(|var\s+\w+\s*=\s*\()', line):
                func_name = re.search(r'(?:function\s+)?(\w+)', line)
                if func_name:
                    analysis["functions"].append({
                        "name": func_name.group(1),
                        "line": i,
                        "type": "function"
                    })
                    analysis["complexity_score"] += 1
            
            # Detect classes
            elif re.match(r'^class\s+\w+', line):
                class_name = re.search(r'class\s+(\w+)', line)
                if class_name:
                    analysis["classes"].append({
                        "name": class_name.group(1),
                        "line": i,
                        "type": "class"
                    })
                    analysis["complexity_score"] += 2
            
            # Detect imports
            elif re.match(r'^(import|export)', line):
                analysis["imports"].append(line)
        
        return analysis
    
    def _analyze_generic_structure(self, code: str, language: str) -> Dict[str, Any]:
        """Generic code structure analysis for other languages."""
        
        analysis = {
            "lines_of_code": len(code.split('\n')),
            "functions": [],
            "classes": [],
            "imports": [],
            "complexity_score": 0,
            "nesting_depth": 0
        }
        
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Generic function detection
            if re.search(r'\b(?:function|def|public|private|protected)\s+\w+', line):
                func_name = re.search(r'(?:function|def|public|private|protected)\s+(\w+)', line)
                if func_name:
                    analysis["functions"].append({
                        "name": func_name.group(1),
                        "line": i,
                        "type": "function"
                    })
                    analysis["complexity_score"] += 1
            
            # Generic class detection
            elif re.search(r'\bclass\s+\w+', line):
                class_name = re.search(r'class\s+(\w+)', line)
                if class_name:
                    analysis["classes"].append({
                        "name": class_name.group(1),
                        "line": i,
                        "type": "class"
                    })
                    analysis["complexity_score"] += 2
        
        return analysis
    
    def _calculate_nesting_depth(self, node: ast.AST, tree: ast.AST) -> int:
        """Calculate the nesting depth of an AST node."""
        
        depth = 0
        current = node
        
        while hasattr(current, 'parent'):
            current = current.parent
            depth += 1
        
        return depth
    
    def identify_issues(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Identify potential issues in the code."""
        
        issues = []
        
        # Language-specific issue detection
        if language == "python":
            issues.extend(self._identify_python_issues(code))
        elif language == "javascript":
            issues.extend(self._identify_javascript_issues(code))
        else:
            issues.extend(self._identify_generic_issues(code, language))
        
        # Common issues across languages
        issues.extend(self._identify_common_issues(code, language))
        
        return issues
    
    def _identify_python_issues(self, code: str) -> List[Dict[str, Any]]:
        """Identify Python-specific issues."""
        
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Security issues
            if "eval(" in line:
                issues.append({
                    "line": i,
                    "category": "security",
                    "severity": "critical",
                    "message": "Use of eval() is dangerous and should be avoided",
                    "suggestion": "Use safer alternatives like ast.literal_eval() or json.loads()"
                })
            
            if "exec(" in line:
                issues.append({
                    "line": i,
                    "category": "security",
                    "severity": "critical",
                    "message": "Use of exec() is dangerous and should be avoided",
                    "suggestion": "Refactor to avoid dynamic code execution"
                })
            
            # Style issues
            if len(line) > 79 and not line_stripped.startswith('#'):
                issues.append({
                    "line": i,
                    "category": "style",
                    "severity": "low",
                    "message": "Line exceeds PEP 8 maximum length of 79 characters",
                    "suggestion": "Break the line or use line continuation"
                })
            
            # Performance issues
            if "import *" in line:
                issues.append({
                    "line": i,
                    "category": "performance",
                    "severity": "medium",
                    "message": "Wildcard imports can impact performance and namespace",
                    "suggestion": "Import specific modules or use explicit imports"
                })
            
            # Error handling
            if "except:" in line:
                issues.append({
                    "line": i,
                    "category": "error_handling",
                    "severity": "high",
                    "message": "Bare except clause catches all exceptions",
                    "suggestion": "Specify the exception type(s) to catch"
                })
        
        return issues
    
    def _identify_javascript_issues(self, code: str) -> List[Dict[str, Any]]:
        """Identify JavaScript-specific issues."""
        
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Security issues
            if "eval(" in line:
                issues.append({
                    "line": i,
                    "category": "security",
                    "severity": "critical",
                    "message": "Use of eval() is dangerous and should be avoided",
                    "suggestion": "Use safer alternatives like JSON.parse() or Function constructor"
                })
            
            # Style issues
            if "var " in line:
                issues.append({
                    "line": i,
                    "category": "style",
                    "severity": "medium",
                    "message": "Consider using const or let instead of var",
                    "suggestion": "Use const for values that won't be reassigned, let for variables that will change"
                })
            
            # Performance issues
            if "console.log" in line:
                issues.append({
                    "line": i,
                    "category": "performance",
                    "severity": "low",
                    "message": "Console.log statements should be removed in production",
                    "suggestion": "Use proper logging framework or remove debug statements"
                })
        
        return issues
    
    def _identify_generic_issues(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Identify generic issues for other languages."""
        
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Long lines
            if len(line) > 120:
                issues.append({
                    "line": i,
                    "category": "style",
                    "severity": "low",
                    "message": f"Line exceeds recommended length for {language}",
                    "suggestion": "Break the line to improve readability"
                })
            
            # Hardcoded values
            if re.search(r'\b\d{4,}\b', line):
                issues.append({
                    "line": i,
                    "category": "best_practices",
                    "severity": "medium",
                    "message": "Consider extracting magic numbers to named constants",
                    "suggestion": "Define constants with meaningful names"
                })
        
        return issues
    
    def _identify_common_issues(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Identify common issues across all languages."""
        
        issues = []
        lines = code.split('\n')
        
        # Check for TODO comments
        for i, line in enumerate(lines, 1):
            if "TODO" in line.upper() or "FIXME" in line.upper():
                issues.append({
                    "line": i,
                    "category": "documentation",
                    "severity": "medium",
                    "message": "TODO/FIXME comment found",
                    "suggestion": "Address the TODO/FIXME or create an issue to track it"
                })
        
        # Check for commented code
        commented_code_blocks = 0
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('//') or line.strip().startswith('#'):
                if any(keyword in line for keyword in ['if', 'for', 'while', 'function', 'class', 'def']):
                    commented_code_blocks += 1
        
        if commented_code_blocks > 3:
            issues.append({
                "line": 0,
                "category": "documentation",
                "severity": "low",
                "message": f"Found {commented_code_blocks} blocks of commented code",
                "suggestion": "Remove commented code or document why it's kept"
            })
        
        return issues
    
    def suggest_improvements(self, code: str, language: str, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate improvement suggestions based on analysis."""
        
        suggestions = []
        
        # Performance improvements
        suggestions.extend(self._suggest_performance_improvements(code, language))
        
        # Readability improvements
        suggestions.extend(self._suggest_readability_improvements(code, language))
        
        # Security improvements
        suggestions.extend(self._suggest_security_improvements(code, language))
        
        # Architecture improvements
        suggestions.extend(self._suggest_architecture_improvements(code, language))
        
        return suggestions
    
    def _suggest_performance_improvements(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Suggest performance improvements."""
        
        suggestions = []
        
        if language == "python":
            # Check for list comprehensions vs loops
            if code.count("for ") > code.count("[") * 2:
                suggestions.append({
                    "category": "performance",
                    "severity": "medium",
                    "message": "Consider using list comprehensions for better performance",
                    "suggestion": "Replace simple for loops with list comprehensions where appropriate"
                })
            
            # Check for string concatenation
            if code.count("+") > code.count("join(") * 3:
                suggestions.append({
                    "category": "performance",
                    "severity": "low",
                    "message": "Consider using str.join() for multiple string concatenations",
                    "suggestion": "Use ''.join(list_of_strings) instead of multiple + operations"
                })
        
        return suggestions
    
    def _suggest_readability_improvements(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Suggest readability improvements."""
        
        suggestions = []
        
        # Check function length
        lines = code.split('\n')
        function_lines = 0
        in_function = False
        
        for line in lines:
            if re.search(r'\b(?:def|function)\s+\w+', line):
                in_function = True
                function_lines = 0
            elif in_function:
                function_lines += 1
                if function_lines > 50:
                    suggestions.append({
                        "category": "readability",
                        "severity": "medium",
                        "message": "Long function detected",
                        "suggestion": "Consider breaking the function into smaller, more focused functions"
                    })
                    break
        
        return suggestions
    
    def _suggest_security_improvements(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Suggest security improvements."""
        
        suggestions = []
        
        # Check for hardcoded secrets
        if re.search(r'(?:password|secret|key|token)\s*=\s*["\'][^"\']+["\']', code, re.IGNORECASE):
            suggestions.append({
                "category": "security",
                "severity": "high",
                "message": "Hardcoded secrets detected",
                "suggestion": "Use environment variables or secure configuration management"
            })
        
        return suggestions
    
    def _suggest_architecture_improvements(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Suggest architecture improvements."""
        
        suggestions = []
        
        # Check for single responsibility principle
        classes = re.findall(r'class\s+(\w+)', code)
        for class_name in classes:
            # This is a simplified check - in practice, you'd need more sophisticated analysis
            suggestions.append({
                "category": "architecture",
                "severity": "info",
                "message": f"Review class '{class_name}' for single responsibility",
                "suggestion": "Ensure each class has a single, well-defined responsibility"
            })
        
        return suggestions
    
    def generate_report(self, code: str, filename: str = "") -> Dict[str, Any]:
        """Generate a comprehensive code review report."""
        try:
            # Detect language
            language = self.detect_language(code, filename)
            
            # Analyze code structure
            structure = self.analyze_code_structure(code, language)
            
            # Identify issues
            issues = self.identify_issues(code, language)
            
            # Generate suggestions
            suggestions = self.suggest_improvements(code, language, issues)
            
            # Calculate metrics
            total_issues = len(issues)
            critical_issues = len([i for i in issues if i.get('severity') == 'critical'])
            high_issues = len([i for i in issues if i.get('severity') == 'high'])
            medium_issues = len([i for i in issues if i.get('severity') == 'medium'])
            low_issues = len([i for i in issues if i.get('severity') == 'low'])
            
            # Calculate score (100 - deductions for issues)
            score = 100
            score -= critical_issues * 10
            score -= high_issues * 5
            score -= medium_issues * 2
            score -= low_issues * 1
            score = max(0, score)
            
            # Generate grade
            grade = self._calculate_grade(score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(issues, suggestions)
            
            return {
                "filename": filename,
                "language": language,
                "score": score,
                "grade": grade,
                "structure": structure,
                "issues": {
                    "total": total_issues,
                    "critical": critical_issues,
                    "high": high_issues,
                    "medium": medium_issues,
                    "low": low_issues,
                    "details": issues
                },
                "suggestions": suggestions,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {
                "filename": filename,
                "language": "unknown",
                "score": 0,
                "grade": "F",
                "error": str(e),
                "issues": {
                    "total": 0,
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "details": []
                },
                "suggestions": [],
                "recommendations": ["Error occurred during analysis"],
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_code(self, code: str, filename: str = "") -> Dict[str, Any]:
        """Alias for generate_report to maintain compatibility."""
        return self.generate_report(code, filename)
    
    def _group_issues_by_category(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group issues by category."""
        
        categories = {}
        for issue in issues:
            category = issue["category"]
            categories[category] = categories.get(category, 0) + 1
        
        return categories
    
    def _group_issues_by_severity(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group issues by severity."""
        
        severities = {}
        for issue in issues:
            severity = issue["severity"]
            severities[severity] = severities.get(severity, 0) + 1
        
        return severities
    
    def _calculate_grade(self, score: int) -> str:
        """Calculate letter grade based on score."""
        
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(self, issues: List[Dict[str, Any]], suggestions: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations."""
        
        recommendations = []
        
        # Critical issues first
        critical_issues = [i for i in issues if i["severity"] == "critical"]
        if critical_issues:
            recommendations.append("🔴 CRITICAL: Address all critical security and safety issues immediately")
        
        # High priority issues
        high_issues = [i for i in issues if i["severity"] == "high"]
        if high_issues:
            recommendations.append("🟠 HIGH: Fix high-priority issues before deployment")
        
        # Performance recommendations
        performance_suggestions = [s for s in suggestions if s["category"] == "performance"]
        if performance_suggestions:
            recommendations.append("⚡ PERFORMANCE: Consider implementing performance optimizations")
        
        # Documentation recommendations
        doc_issues = [i for i in issues if i["category"] == "documentation"]
        if doc_issues:
            recommendations.append("📚 DOCUMENTATION: Improve code documentation and comments")
        
        # Testing recommendations
        if len(issues) > 10:
            recommendations.append("🧪 TESTING: Consider adding more comprehensive tests")
        
        return recommendations

# Create a global instance
code_reviewer = CodeReviewer() 