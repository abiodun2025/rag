#!/usr/bin/env python3
"""
Code Review Agent for Pull Requests
Automatically reviews pull requests and generates detailed review reports with accessible links.
"""

import os
import json
import requests
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import webbrowser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReviewFinding:
    """A single review finding."""
    type: str  # security, performance, style, bug, suggestion
    severity: str  # low, medium, high, critical
    line: Optional[int]
    file: Optional[str]
    message: str
    suggestion: Optional[str]
    code_snippet: Optional[str]

@dataclass
class CodeReview:
    """Complete code review result."""
    review_id: str
    pr_number: int
    repository: str
    review_date: str
    overall_score: float
    findings: List[ReviewFinding]
    summary: str
    recommendations: List[str]
    review_url: str
    status: str  # approved, needs_changes, comment_only

class CodeReviewAgent:
    """Automated code review agent for pull requests."""
    
    def __init__(self, reports_dir: str = "review_reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        self.review_history = {}
        
    def review_pull_request(self, pr_number: int, pr_details: Dict = None, pr_files: List[Dict] = None, repository: str = None) -> Dict[str, Any]:
        """Review a pull request and generate a detailed report."""
        try:
            logger.info(f"🔍 Starting code review for PR #{pr_number}")
            
            # Use provided PR details or create default ones
            if not pr_details:
                pr_details = {
                    "number": pr_number,
                    "title": f"Pull Request #{pr_number}",
                    "repository": repository or "unknown/unknown",
                    "state": "open"
                }
            
            # Use provided PR files or create a test file for demonstration
            if not pr_files:
                pr_files = self._create_test_files()
            
            # Perform code analysis
            review = self._perform_code_analysis(pr_number, pr_details, pr_files)
            
            # Generate review report
            report = self._generate_review_report(review)
            
            # Save report and create accessible link
            report_url = self._save_review_report(report)
            
            # Store in history
            self.review_history[review.review_id] = {
                "review_id": review.review_id,
                "pr_number": pr_number,
                "repository": review.repository,
                "review_date": review.review_date,
                "overall_score": review.overall_score,
                "status": review.status,
                "report_url": report_url,
                "findings_count": len(review.findings)
            }
            
            logger.info(f"✅ Code review completed for PR #{pr_number}")
            logger.info(f"   Report URL: {report_url}")
            
            return {
                "success": True,
                "review_id": review.review_id,
                "pr_number": pr_number,
                "overall_score": review.overall_score,
                "findings_count": len(review.findings),
                "status": review.status,
                "report_url": report_url,
                "summary": review.summary,
                "recommendations": review.recommendations
            }
            
        except Exception as e:
            logger.error(f"❌ Code review failed for PR #{pr_number}: {e}")
            return {"success": False, "error": f"Code review failed: {str(e)}"}
    
    def _create_test_files(self) -> List[Dict]:
        """Create test files for demonstration when no real files are provided."""
        return [
            {
                "filename": "test_code_for_review.py",
                "content": '''#!/usr/bin/env python3
"""
Test file for automated code review
This file contains various code patterns to test the review agent.
"""

import os
import requests

def insecure_function(user_input):
    """This function has security issues."""
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    # This is vulnerable to SQL injection
    return execute_query(query)

def performance_issue():
    """This function has performance issues."""
    users = get_all_users()
    for user in users:
        # N+1 query problem
        profile = get_user_profile(user.id)
        print(profile.name)

def style_issues():
    """This function has style issues."""
    x = 42  # Magic number
    if x > 40:
        print("Value is high")
    
    # Long function with many lines
    for i in range(100):
        print(f"Line {i}")
        if i % 10 == 0:
            print("Multiple of 10")
        elif i % 5 == 0:
            print("Multiple of 5")
        else:
            print("Regular number")

def good_function():
    """This function follows good practices."""
    MAX_RETRIES = 3
    TIMEOUT = 30
    
    try:
        response = requests.get("https://api.example.com/data", timeout=TIMEOUT)
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

if __name__ == "__main__":
    # Test the functions
    insecure_function("admin")
    performance_issue()
    style_issues()
    good_function()
''',
                "status": "added"
            }
        ]
    
    def _perform_code_analysis(self, pr_number: int, pr_details: Dict, pr_files: List[Dict]) -> CodeReview:
        """Perform comprehensive code analysis."""
        review_id = f"review_{uuid.uuid4().hex[:8]}"
        findings = []
        
        logger.info(f"🔍 Analyzing {len(pr_files)} files in PR #{pr_number}")
        
        # Analyze each file
        for file_info in pr_files:
            file_findings = self._analyze_file(file_info)
            findings.extend(file_findings)
        
        # Generate review summary
        summary = self._generate_summary(findings, pr_details)
        recommendations = self._generate_recommendations(findings)
        overall_score = self._calculate_score(findings)
        status = self._determine_status(findings)
        
        return CodeReview(
            review_id=review_id,
            pr_number=pr_number,
            repository=pr_details.get("repository", "unknown"),
            review_date=datetime.now().isoformat(),
            overall_score=overall_score,
            findings=findings,
            summary=summary,
            recommendations=recommendations,
            review_url=f"https://github.com/{pr_details.get('repository', '')}/pull/{pr_number}",
            status=status
        )
    
    def _analyze_file(self, file_info: Dict) -> List[ReviewFinding]:
        """Analyze a single file for issues."""
        findings = []
        file_path = file_info.get("filename", "")
        content = file_info.get("content", "")
        language = self._detect_language(file_path)
        
        # Security analysis
        security_findings = self._analyze_security(content, file_path, language)
        findings.extend(security_findings)
        
        # Performance analysis
        performance_findings = self._analyze_performance(content, file_path, language)
        findings.extend(performance_findings)
        
        # Code style analysis
        style_findings = self._analyze_style(content, file_path, language)
        findings.extend(style_findings)
        
        # Bug detection
        bug_findings = self._analyze_bugs(content, file_path, language)
        findings.extend(bug_findings)
        
        return findings
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.cs': 'csharp',
            '.html': 'html',
            '.css': 'css',
            '.sql': 'sql'
        }
        return language_map.get(ext, 'unknown')
    
    def _analyze_security(self, content: str, file_path: str, language: str) -> List[ReviewFinding]:
        """Analyze code for security issues."""
        findings = []
        
        # SQL Injection detection
        if 'sql' in language or 'query' in content.lower():
            if any(pattern in content.lower() for pattern in ['execute(', 'query(', 'raw_query']):
                if '?' not in content and '%s' not in content:
                    findings.append(ReviewFinding(
                        type="security",
                        severity="high",
                        line=None,
                        file=file_path,
                        message="Potential SQL injection vulnerability detected",
                        suggestion="Use parameterized queries or prepared statements",
                        code_snippet=self._extract_relevant_lines(content, 'query')
                    ))
        
        # Hardcoded credentials
        if any(pattern in content.lower() for pattern in ['password', 'secret', 'token', 'key']):
            if any(pattern in content for pattern in ['"password"', "'password'", '= "secret']):
                findings.append(ReviewFinding(
                    type="security",
                    severity="critical",
                    line=None,
                    file=file_path,
                    message="Hardcoded credentials detected",
                    suggestion="Use environment variables or secure configuration management",
                    code_snippet=self._extract_relevant_lines(content, 'password')
                ))
        
        # XSS vulnerabilities
        if language in ['html', 'javascript', 'php']:
            if 'innerHTML' in content or 'document.write' in content:
                findings.append(ReviewFinding(
                    type="security",
                    severity="medium",
                    line=None,
                    file=file_path,
                    message="Potential XSS vulnerability with innerHTML usage",
                    suggestion="Use textContent or proper sanitization",
                    code_snippet=self._extract_relevant_lines(content, 'innerHTML')
                ))
        
        return findings
    
    def _analyze_performance(self, content: str, file_path: str, language: str) -> List[ReviewFinding]:
        """Analyze code for performance issues."""
        findings = []
        
        # N+1 query detection
        if language == 'python' and 'for' in content and 'query' in content:
            findings.append(ReviewFinding(
                type="performance",
                severity="medium",
                line=None,
                file=file_path,
                message="Potential N+1 query pattern detected",
                suggestion="Consider using select_related() or prefetch_related() for database queries",
                code_snippet=self._extract_relevant_lines(content, 'for')
            ))
        
        # Memory leaks
        if 'while True' in content and 'break' not in content:
            findings.append(ReviewFinding(
                type="performance",
                severity="high",
                line=None,
                file=file_path,
                message="Potential infinite loop detected",
                suggestion="Ensure proper exit conditions are in place",
                code_snippet=self._extract_relevant_lines(content, 'while True')
            ))
        
        return findings
    
    def _analyze_style(self, content: str, file_path: str, language: str) -> List[ReviewFinding]:
        """Analyze code style and conventions."""
        findings = []
        
        # Long functions
        lines = content.split('\n')
        if len(lines) > 50:
            findings.append(ReviewFinding(
                type="style",
                severity="low",
                line=None,
                file=file_path,
                message=f"Function is {len(lines)} lines long",
                suggestion="Consider breaking into smaller functions",
                code_snippet=None
            ))
        
        # Magic numbers
        if any(char.isdigit() for char in content):
            findings.append(ReviewFinding(
                type="style",
                severity="low",
                line=None,
                file=file_path,
                message="Magic numbers detected",
                suggestion="Define constants for better maintainability",
                code_snippet=None
            ))
        
        return findings
    
    def _analyze_bugs(self, content: str, file_path: str, language: str) -> List[ReviewFinding]:
        """Analyze code for potential bugs."""
        findings = []
        
        # Unused variables
        if 'import' in content and 'unused' in content.lower():
            findings.append(ReviewFinding(
                type="bug",
                severity="low",
                line=None,
                file=file_path,
                message="Unused imports detected",
                suggestion="Remove unused imports to clean up code",
                code_snippet=None
            ))
        
        # Division by zero
        if '/' in content and '0' in content:
            findings.append(ReviewFinding(
                type="bug",
                severity="high",
                line=None,
                file=file_path,
                message="Potential division by zero",
                suggestion="Add proper validation before division",
                code_snippet=self._extract_relevant_lines(content, '/')
            ))
        
        return findings
    
    def _extract_relevant_lines(self, content: str, keyword: str) -> str:
        """Extract lines containing a keyword for context."""
        lines = content.split('\n')
        relevant_lines = []
        for i, line in enumerate(lines, 1):
            if keyword in line:
                relevant_lines.append(f"Line {i}: {line.strip()}")
        return '\n'.join(relevant_lines[:3])  # Return first 3 relevant lines
    
    def _generate_summary(self, findings: List[ReviewFinding], pr_details: Dict) -> str:
        """Generate a summary of the review."""
        total_findings = len(findings)
        critical = len([f for f in findings if f.severity == "critical"])
        high = len([f for f in findings if f.severity == "high"])
        medium = len([f for f in findings if f.severity == "medium"])
        low = len([f for f in findings if f.severity == "low"])
        
        summary = f"Code review completed for PR #{pr_details.get('number', 'unknown')}\n\n"
        summary += f"📊 **Review Summary:**\n"
        summary += f"- Total findings: {total_findings}\n"
        summary += f"- Critical issues: {critical}\n"
        summary += f"- High priority: {high}\n"
        summary += f"- Medium priority: {medium}\n"
        summary += f"- Low priority: {low}\n\n"
        
        if critical > 0 or high > 0:
            summary += "⚠️ **Action Required:** Critical or high-priority issues found.\n\n"
        elif total_findings == 0:
            summary += "✅ **Excellent:** No issues found in this review.\n\n"
        else:
            summary += "📝 **Suggestions:** Minor improvements recommended.\n\n"
        
        return summary
    
    def _generate_recommendations(self, findings: List[ReviewFinding]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Group findings by type
        security_findings = [f for f in findings if f.type == "security"]
        performance_findings = [f for f in findings if f.type == "performance"]
        style_findings = [f for f in findings if f.type == "style"]
        bug_findings = [f for f in findings if f.type == "bug"]
        
        if security_findings:
            recommendations.append("🔒 Address security vulnerabilities before merging")
        
        if performance_findings:
            recommendations.append("⚡ Consider performance optimizations")
        
        if style_findings:
            recommendations.append("🎨 Improve code style and maintainability")
        
        if bug_findings:
            recommendations.append("🐛 Fix potential bugs and edge cases")
        
        if not recommendations:
            recommendations.append("✅ Code looks good! Ready for merge.")
        
        return recommendations
    
    def _calculate_score(self, findings: List[ReviewFinding]) -> float:
        """Calculate overall review score (0-100)."""
        if not findings:
            return 100.0
        
        # Weight findings by severity
        weights = {"critical": 10, "high": 5, "medium": 2, "low": 1}
        total_weight = sum(weights.get(f.severity, 1) for f in findings)
        
        # Calculate score (higher weight = lower score)
        max_possible_weight = len(findings) * 10  # Assume all critical
        score = max(0, 100 - (total_weight / max_possible_weight) * 100)
        
        return round(score, 1)
    
    def _determine_status(self, findings: List[ReviewFinding]) -> str:
        """Determine review status based on findings."""
        critical = len([f for f in findings if f.severity == "critical"])
        high = len([f for f in findings if f.severity == "high"])
        
        if critical > 0:
            return "needs_changes"
        elif high > 0:
            return "comment_only"
        else:
            return "approved"
    
    def _generate_review_report(self, review: CodeReview) -> Dict[str, Any]:
        """Generate a comprehensive review report."""
        report = {
            "review_id": review.review_id,
            "pr_number": review.pr_number,
            "repository": review.repository,
            "review_date": review.review_date,
            "overall_score": review.overall_score,
            "status": review.status,
            "summary": review.summary,
            "recommendations": review.recommendations,
            "findings": [
                {
                    "type": f.type,
                    "severity": f.severity,
                    "line": f.line,
                    "file": f.file,
                    "message": f.message,
                    "suggestion": f.suggestion,
                    "code_snippet": f.code_snippet
                }
                for f in review.findings
            ],
            "github_url": review.review_url
        }
        
        return report
    
    def _save_review_report(self, report: Dict[str, Any]) -> str:
        """Save review report and return accessible URL."""
        review_id = report["review_id"]
        
        # Save JSON report
        json_file = self.reports_dir / f"{review_id}.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate HTML report
        html_content = self._generate_html_report(report)
        html_file = self.reports_dir / f"{review_id}.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        # Create accessible URL
        report_url = f"file://{html_file.absolute()}"
        
        logger.info(f"📄 Review report saved: {report_url}")
        return report_url
    
    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML report for easy viewing."""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Review Report - PR #{report['pr_number']}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f6f8fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header .subtitle {{ margin: 10px 0 0; opacity: 0.9; }}
        .score {{ font-size: 3em; font-weight: bold; margin: 20px 0; }}
        .content {{ padding: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #24292e; border-bottom: 2px solid #e1e4e8; padding-bottom: 10px; }}
        .finding {{ background: #f6f8fa; border-left: 4px solid #d73a49; margin: 15px 0; padding: 15px; border-radius: 4px; }}
        .finding.critical {{ border-left-color: #d73a49; }}
        .finding.high {{ border-left-color: #f6a434; }}
        .finding.medium {{ border-left-color: #f6a434; }}
        .finding.low {{ border-left-color: #28a745; }}
        .finding.security {{ border-left-color: #d73a49; }}
        .finding.performance {{ border-left-color: #f6a434; }}
        .finding.style {{ border-left-color: #6f42c1; }}
        .finding.bug {{ border-left-color: #d73a49; }}
        .severity {{ font-weight: bold; text-transform: uppercase; font-size: 0.8em; }}
        .severity.critical {{ color: #d73a49; }}
        .severity.high {{ color: #f6a434; }}
        .severity.medium {{ color: #f6a434; }}
        .severity.low {{ color: #28a745; }}
        .recommendations {{ background: #e1f5fe; border: 1px solid #b3e5fc; border-radius: 4px; padding: 15px; }}
        .recommendations ul {{ margin: 10px 0; }}
        .code-snippet {{ background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 4px; padding: 10px; font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace; font-size: 0.9em; overflow-x: auto; }}
        .status {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; text-transform: uppercase; font-size: 0.8em; }}
        .status.approved {{ background: #d4edda; color: #155724; }}
        .status.needs_changes {{ background: #f8d7da; color: #721c24; }}
        .status.comment_only {{ background: #fff3cd; color: #856404; }}
        .github-link {{ display: inline-block; margin-top: 20px; padding: 10px 20px; background: #24292e; color: white; text-decoration: none; border-radius: 4px; }}
        .github-link:hover {{ background: #444d56; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Code Review Report</h1>
            <div class="subtitle">Pull Request #{report['pr_number']} • {report['repository']}</div>
            <div class="score">{report['overall_score']}/100</div>
            <span class="status {report['status']}">{report['status'].replace('_', ' ').title()}</span>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📊 Summary</h2>
                <pre style="white-space: pre-wrap; font-family: inherit;">{report['summary']}</pre>
            </div>
            
            <div class="section">
                <h2>💡 Recommendations</h2>
                <div class="recommendations">
                    <ul>
                        {''.join(f'<li>{rec}</li>' for rec in report['recommendations'])}
                    </ul>
                </div>
            </div>
            
            <div class="section">
                <h2>🔍 Findings ({len(report['findings'])})</h2>
                {''.join(f'''
                <div class="finding {finding['type']} {finding['severity']}">
                    <div class="severity {finding['severity']}">{finding['severity'].upper()} • {finding['type'].title()}</div>
                    <h4>{finding['message']}</h4>
                    <p><strong>File:</strong> {finding['file'] or 'N/A'}</p>
                    {f'<p><strong>Suggestion:</strong> {finding["suggestion"]}</p>' if finding['suggestion'] else ''}
                    {f'<div class="code-snippet">{finding["code_snippet"]}</div>' if finding['code_snippet'] else ''}
                </div>
                ''' for finding in report['findings'])}
            </div>
            
            <div class="section">
                <h2>🔗 Links</h2>
                <a href="{report['github_url']}" class="github-link" target="_blank">View on GitHub</a>
            </div>
        </div>
    </div>
</body>
</html>
        """
        return html
    
    def _post_review_to_github(self, pr_number: int, review: CodeReview) -> Dict[str, Any]:
        """Post review comments to GitHub."""
        try:
            # Generate review comments from findings
            comments = []
            for finding in review.findings:
                if finding.severity in ["critical", "high"]:
                    comment = f"**{finding.severity.upper()} - {finding.type.title()}:** {finding.message}"
                    if finding.suggestion:
                        comment += f"\n\n**Suggestion:** {finding.suggestion}"
                    if finding.code_snippet:
                        comment += f"\n\n```\n{finding.code_snippet}\n```"
                    comments.append(comment)
            
            # Post review to GitHub
            response = requests.post(
                f"{self.base_url}/call",
                json={
                    "tool": "review_pull_request",
                    "arguments": {
                        "pr_id": str(pr_number),
                        "review_type": review.status,
                        "comments": comments,
                        "reviewer": "Code Review Agent"
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                logger.warning(f"Failed to post review to GitHub: {response.status_code}")
                return {"success": False, "error": "Failed to post to GitHub"}
                
        except Exception as e:
            logger.error(f"Failed to post review to GitHub: {e}")
            return {"success": False, "error": str(e)}
    
    def get_review_history(self) -> List[Dict[str, Any]]:
        """Get history of all reviews."""
        history = []
        for json_file in self.reports_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    report = json.load(f)
                    history.append({
                        "review_id": report["review_id"],
                        "pr_number": report["pr_number"],
                        "repository": report["repository"],
                        "review_date": report["review_date"],
                        "overall_score": report["overall_score"],
                        "status": report["status"],
                        "findings_count": len(report["findings"]),
                        "report_url": f"file://{json_file.with_suffix('.html').absolute()}"
                    })
            except Exception as e:
                logger.error(f"Failed to load report {json_file}: {e}")
        
        return sorted(history, key=lambda x: x["review_date"], reverse=True)
    
    def open_review_report(self, review_id: str):
        """Open a review report in the browser."""
        html_file = self.reports_dir / f"{review_id}.html"
        if html_file.exists():
            webbrowser.open(f"file://{html_file.absolute()}")
            return True
        else:
            logger.error(f"Review report not found: {review_id}")
            return False

def main():
    """Main function for testing the code review agent."""
    agent = CodeReviewAgent()
    
    print("🔍 Code Review Agent")
    print("=" * 50)
    
    # Test with a PR number
    pr_number = input("Enter PR number to review (or press Enter to see history): ").strip()
    
    if pr_number:
        try:
            pr_number = int(pr_number)
            result = agent.review_pull_request(pr_number)
            
            if result["success"]:
                print(f"✅ Review completed!")
                print(f"   Review ID: {result['review_id']}")
                print(f"   Score: {result['overall_score']}/100")
                print(f"   Status: {result['status']}")
                print(f"   Findings: {result['findings_count']}")
                print(f"   Report URL: {result['report_url']}")
                
                # Open report in browser
                open_report = input("Open report in browser? (y/N): ").strip().lower()
                if open_report in ['y', 'yes']:
                    agent.open_review_report(result['review_id'])
            else:
                print(f"❌ Review failed: {result['error']}")
        except ValueError:
            print("❌ Invalid PR number")
    else:
        # Show review history
        history = agent.get_review_history()
        if history:
            print("📋 Review History:")
            for review in history[:10]:  # Show last 10
                print(f"   PR #{review['pr_number']} - Score: {review['overall_score']}/100 - {review['status']}")
                print(f"     Report: {review['report_url']}")
                print()
        else:
            print("No review history found")

if __name__ == "__main__":
    main()