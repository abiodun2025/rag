#!/usr/bin/env python3
"""
GitHub Repository Code Review Agent
==================================

A simple agent that reviews any GitHub repository and returns a comprehensive report.
Version: 1.0.0
"""

import sys
import os
import json
import argparse
from datetime import datetime
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.github_code_reviewer import GitHubCodeReviewer
from agent.code_reviewer import code_reviewer

class GitHubReviewAgent:
    """Agent for reviewing GitHub repositories."""
    
    def __init__(self, github_token: str = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.reviewer = GitHubCodeReviewer(self.github_token)
        self.version = "1.0.0"
    
    def extract_repo_info(self, repo_url: str) -> Dict[str, str]:
        """Extract owner and repo name from various URL formats."""
        # Clean the URL
        repo_url = repo_url.strip()
        
        # Handle different URL formats
        if repo_url.startswith('https://github.com/'):
            repo_url = repo_url.replace('https://github.com/', '')
        elif repo_url.startswith('http://github.com/'):
            repo_url = repo_url.replace('http://github.com/', '')
        elif repo_url.startswith('github.com/'):
            repo_url = repo_url.replace('github.com/', '')
        
        # Remove trailing slash and .git
        repo_url = repo_url.rstrip('/').replace('.git', '')
        
        # Split into owner and repo
        if '/' in repo_url:
            parts = repo_url.split('/')
            if len(parts) >= 2:
                owner = parts[0]
                repo = parts[1]
                return {"owner": owner, "repo": repo}
        
        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
    
    def review_repository(self, repo_url: str, output_file: str = None, clone_locally: bool = True) -> Dict[str, Any]:
        """Review a GitHub repository and generate a comprehensive report."""
        try:
            # Extract repository information
            repo_info = self.extract_repo_info(repo_url)
            owner = repo_info["owner"]
            repo = repo_info["repo"]
            
            print(f"🔍 Starting code review for: {repo_url}")
            print(f"📦 Repository: {owner}/{repo}")
            print("📊 Analyzing repository...")
            
            # Analyze the repository
            analysis_result = self.reviewer.analyze_repository(owner, repo, clone_locally)
            
            if not analysis_result["success"]:
                return {
                    "success": False,
                    "error": analysis_result["error"],
                    "repository": f"{owner}/{repo}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Generate comprehensive report
            report = self._generate_comprehensive_report(analysis_result, repo_url)
            
            # Save report if output file specified
            if output_file:
                self._save_report(report, output_file)
            
            return report
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Review failed: {str(e)}",
                "repository": repo_url,
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_comprehensive_report(self, analysis_result: Dict[str, Any], repo_url: str) -> Dict[str, Any]:
        """Generate a comprehensive report from analysis results."""
        
        summary = analysis_result["summary"]
        results = analysis_result["results"]
        
        # Collect all issues and categorize them
        all_issues = []
        critical_issues = []
        high_issues = []
        medium_issues = []
        low_issues = []
        
        file_reports = []
        
        for file_result in results:
            if 'report' in file_result:
                report = file_result['report']
                file_info = {
                    "file": file_result['file'],
                    "score": report['score'],
                    "grade": report['grade'],
                    "language": report['language'],
                    "issues_count": report['issues']['total'],
                    "critical_issues": report['issues']['critical'],
                    "high_issues": report['issues']['high'],
                    "medium_issues": report['issues']['medium'],
                    "low_issues": report['issues']['low']
                }
                file_reports.append(file_info)
                
                # Collect all issues
                for issue in report['issues']['details']:
                    issue_info = {
                        'file': file_result['file'],
                        'line': issue.get('line', 'N/A'),
                        'severity': issue.get('severity', 'unknown'),
                        'category': issue.get('category', 'unknown'),
                        'message': issue.get('message', ''),
                        'suggestion': issue.get('suggestion', '')
                    }
                    all_issues.append(issue_info)
                    
                    # Categorize by severity
                    if issue.get('severity') == 'critical':
                        critical_issues.append(issue_info)
                    elif issue.get('severity') == 'high':
                        high_issues.append(issue_info)
                    elif issue.get('severity') == 'medium':
                        medium_issues.append(issue_info)
                    elif issue.get('severity') == 'low':
                        low_issues.append(issue_info)
        
        # Calculate overall metrics
        total_files = len(file_reports)
        successful_reviews = len([f for f in file_reports if f['score'] > 0])
        avg_score = sum([f['score'] for f in file_reports]) / total_files if total_files > 0 else 0
        
        # Determine overall grade
        if avg_score >= 90:
            overall_grade = "A"
        elif avg_score >= 80:
            overall_grade = "B"
        elif avg_score >= 70:
            overall_grade = "C"
        elif avg_score >= 60:
            overall_grade = "D"
        else:
            overall_grade = "F"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(critical_issues, high_issues, medium_issues, file_reports)
        
        # Create comprehensive report
        report = {
            "success": True,
            "repository": analysis_result["repository"],
            "repository_url": repo_url,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files": total_files,
                "successful_reviews": successful_reviews,
                "average_score": round(avg_score, 2),
                "overall_grade": overall_grade,
                "total_issues": len(all_issues),
                "critical_issues": len(critical_issues),
                "high_issues": len(high_issues),
                "medium_issues": len(medium_issues),
                "low_issues": len(low_issues)
            },
            "file_analysis": file_reports,
            "critical_issues": critical_issues[:20],  # Top 20 critical issues
            "high_priority_issues": high_issues[:30],  # Top 30 high priority issues
            "recommendations": recommendations,
            "local_path": analysis_result.get("local_path"),
            "note": "Use cleanup_local_repository() to remove cloned repository"
        }
        
        return report
    
    def _generate_recommendations(self, critical_issues: list, high_issues: list, medium_issues: list, file_reports: list) -> list:
        """Generate actionable recommendations based on analysis."""
        
        recommendations = []
        
        # Critical issues
        if critical_issues:
            recommendations.append({
                "priority": "critical",
                "message": f"🔴 CRITICAL: Address {len(critical_issues)} critical issues immediately",
                "details": "These issues pose serious security or safety risks and must be fixed before deployment."
            })
        
        # High priority issues
        if high_issues:
            recommendations.append({
                "priority": "high",
                "message": f"🟠 HIGH: Fix {len(high_issues)} high-priority issues",
                "details": "These issues should be addressed before the next release."
            })
        
        # Performance recommendations
        low_score_files = [f for f in file_reports if f['score'] < 70]
        if low_score_files:
            recommendations.append({
                "priority": "medium",
                "message": f"🟡 MEDIUM: Improve {len(low_score_files)} files with low scores",
                "details": "Focus on files with scores below 70 for significant improvements."
            })
        
        # Security recommendations
        security_issues = [i for i in critical_issues + high_issues if i['category'] == 'security']
        if security_issues:
            recommendations.append({
                "priority": "high",
                "message": f"🔒 SECURITY: Address {len(security_issues)} security vulnerabilities",
                "details": "Security issues should be prioritized for immediate attention."
            })
        
        # Code quality recommendations
        if len(file_reports) > 10:
            recommendations.append({
                "priority": "medium",
                "message": "📚 DOCUMENTATION: Consider improving code documentation",
                "details": "Large codebases benefit from comprehensive documentation."
            })
        
        # Testing recommendations
        if len(critical_issues) + len(high_issues) > 20:
            recommendations.append({
                "priority": "medium",
                "message": "🧪 TESTING: Consider adding more comprehensive tests",
                "details": "High issue count suggests need for better testing coverage."
            })
        
        return recommendations
    
    def _save_report(self, report: Dict[str, Any], output_file: str):
        """Save report to file."""
        try:
            # If output_file doesn't have a path, save to Downloads folder
            if not os.path.dirname(output_file):
                # Get Downloads folder path
                downloads_path = os.path.expanduser("~/Downloads")
                output_file = os.path.join(downloads_path, output_file)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📄 Report saved to: {output_file}")
        except Exception as e:
            print(f"⚠️  Failed to save report: {e}")
    
    def cleanup_local_repository(self, local_path: str):
        """Clean up locally cloned repository."""
        if local_path and os.path.exists(local_path):
            try:
                self.reviewer.cleanup_local_repository(local_path)
                print(f"🧹 Cleaned up: {local_path}")
                return True
            except Exception as e:
                print(f"⚠️  Failed to clean up {local_path}: {e}")
                return False
        return False
    
    def print_report_summary(self, report: Dict[str, Any]):
        """Print a summary of the report."""
        if not report["success"]:
            print(f"❌ Review failed: {report.get('error', 'Unknown error')}")
            return
        
        summary = report["summary"]
        
        print("\n" + "="*80)
        print("🔍 GITHUB REPOSITORY CODE REVIEW REPORT")
        print("="*80)
        print(f"📦 Repository: {report['repository']}")
        print(f"🔗 URL: {report['repository_url']}")
        print(f"📅 Timestamp: {report['timestamp']}")
        print(f"📊 Overall Grade: {summary['overall_grade']} ({summary['average_score']}/100)")
        print()
        
        print("📈 SUMMARY STATISTICS:")
        print(f"   📁 Total Files: {summary['total_files']}")
        print(f"   ✅ Successful Reviews: {summary['successful_reviews']}")
        print(f"   🚨 Total Issues: {summary['total_issues']}")
        print(f"   🔴 Critical: {summary['critical_issues']}")
        print(f"   🟠 High: {summary['high_issues']}")
        print(f"   🟡 Medium: {summary['medium_issues']}")
        print(f"   🟢 Low: {summary['low_issues']}")
        print()
        
        # Show top critical and high issues
        if report.get('critical_issues'):
            print("🔴 CRITICAL ISSUES (Top 5):")
            for i, issue in enumerate(report['critical_issues'][:5], 1):
                print(f"   {i}. {issue['file']}:{issue['line']} - {issue['message']}")
            print()
        
        if report.get('high_priority_issues'):
            print("🟠 HIGH PRIORITY ISSUES (Top 5):")
            for i, issue in enumerate(report['high_priority_issues'][:5], 1):
                print(f"   {i}. {issue['file']}:{issue['line']} - {issue['message']}")
            print()
        
        # Show recommendations
        if report.get('recommendations'):
            print("🎯 KEY RECOMMENDATIONS:")
            for rec in report['recommendations']:
                priority_emoji = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(rec['priority'], 'ℹ️')
                print(f"   {priority_emoji} {rec['message']}")
            print()
        
        if report.get('local_path'):
            print(f"📂 Local repository: {report['local_path']}")
            print("💡 Use cleanup_local_repository() to remove cloned repository")
        
        print("="*80)

def main():
    """Main function for command-line usage."""
    
    parser = argparse.ArgumentParser(description='Review GitHub repositories with AI-powered analysis')
    parser.add_argument('repository', help='GitHub repository URL or owner/repo format')
    parser.add_argument('--token', '-t', help='GitHub token (or set GITHUB_TOKEN env var)')
    parser.add_argument('--output', '-o', help='Output file for detailed report (JSON)')
    parser.add_argument('--api-only', action='store_true', help='Use GitHub API only (no local cloning)')
    parser.add_argument('--cleanup', action='store_true', help='Clean up local repository after analysis')
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = GitHubReviewAgent(args.token)
    
    # Review repository
    report = agent.review_repository(
        args.repository, 
        args.output, 
        clone_locally=not args.api_only
    )
    
    # Print summary
    agent.print_report_summary(report)
    
    # Cleanup if requested
    if args.cleanup and report.get('local_path'):
        agent.cleanup_local_repository(report['local_path'])

if __name__ == "__main__":
    main() 