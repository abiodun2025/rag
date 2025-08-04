#!/usr/bin/env python3
"""
Code Reviewer Module
===================

Basic code review functionality and rules.
"""

import re
from typing import Dict, List, Any

class CodeReviewer:
    """Basic code reviewer with common rules and patterns."""
    
    def __init__(self):
        self.rules = {
            'security': [
                (r'eval\s*\(', 'eval() usage detected', 'critical'),
                (r'exec\s*\(', 'exec() usage detected', 'critical'),
                (r'__import__\s*\(', '__import__() usage detected', 'critical'),
                (r'input\s*\(', 'input() usage detected', 'high'),
                (r'pickle\.loads', 'pickle.loads() usage detected', 'high'),
            ],
            'style': [
                (r'print\s*\(', 'print() statement detected', 'medium'),
                (r'[a-z][a-z0-9_]*\s*=\s*[0-9]+', 'Magic number detected', 'medium'),
                (r'[a-z][a-z0-9_]*\s*=\s*"[^"]{20,}"', 'Long hardcoded string detected', 'medium'),
            ],
            'performance': [
                (r'for\s+.*\s+in\s+range\s*\(len\s*\(', 'Inefficient loop with range(len())', 'medium'),
                (r'\.append\s*\(.*\)\s+in\s+loop', 'Appending in loop detected', 'medium'),
            ]
        }
    
    def analyze_code(self, code: str, filename: str = "") -> Dict[str, Any]:
        """Analyze code for issues."""
        issues = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_issues = self._analyze_line(line, line_num, filename)
            issues.extend(line_issues)
        
        # Calculate score
        score = self._calculate_score(issues)
        
        return {
            'success': True,
            'score': score,
            'total_issues': len(issues),
            'issues': issues,
            'summary': self._generate_summary(issues, score)
        }
    
    def _analyze_line(self, line: str, line_num: int, filename: str) -> List[Dict]:
        """Analyze a single line for issues."""
        issues = []
        
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            return issues
        
        # Check each rule category
        for category, patterns in self.rules.items():
            for pattern, message, severity in patterns:
                if re.search(pattern, line):
                    issues.append({
                        'line': line_num,
                        'severity': severity,
                        'category': category,
                        'message': message,
                        'suggestion': f'Review {category} issue: {message}'
                    })
        
        return issues
    
    def _calculate_score(self, issues: List[Dict]) -> int:
        """Calculate score based on issues."""
        score = 100
        
        for issue in issues:
            severity = issue.get('severity', 'low')
            if severity == 'critical':
                score -= 10
            elif severity == 'high':
                score -= 5
            elif severity == 'medium':
                score -= 2
            elif severity == 'low':
                score -= 1
        
        return max(0, score)
    
    def _generate_summary(self, issues: List[Dict], score: int) -> str:
        """Generate a summary of the analysis."""
        if not issues:
            return "No issues found. Code looks good!"
        
        summary = f"Found {len(issues)} issues. Score: {score}/100\n"
        
        # Group issues by severity
        by_severity = {}
        for issue in issues:
            severity = issue.get('severity', 'low')
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(issue)
        
        for severity in ['critical', 'high', 'medium', 'low']:
            if severity in by_severity:
                summary += f"{severity.title()}: {len(by_severity[severity])} issues\n"
        
        return summary
    
    def generate_report(self, code: str, filename: str = "") -> Dict[str, Any]:
        """Generate a comprehensive report."""
        return self.analyze_code(code, filename)

# Create a global instance
code_reviewer = CodeReviewer() 