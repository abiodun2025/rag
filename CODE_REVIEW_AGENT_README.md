# GitHub Code Review Agent

A powerful, standalone tool for automatically reviewing GitHub repositories and generating comprehensive code analysis reports.

## 🚀 Features

- **🔍 Comprehensive Code Analysis**: Security, performance, quality, and style reviews
- **📄 Automatic Report Generation**: Detailed JSON reports saved to Downloads folder
- **🌐 GitHub Integration**: Direct repository cloning and analysis
- **⚡ Multiple Review Types**: Full, security, performance, and style-focused reviews
- **🎯 Smart Recommendations**: Actionable insights and improvement suggestions
- **📊 Grading System**: A-F grading with detailed scoring metrics

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/abiodun2025/rag.git
cd rag

# Install dependencies
pip install -r requirements.txt

# Set up GitHub token (optional, for private repos)
export GITHUB_TOKEN=your_github_token_here
```

## 🎯 Quick Start

### Command Line Mode
```bash
# Review a public repository
python code_review_agent_cli.py --repo https://github.com/owner/repo

# Security-focused review
python code_review_agent_cli.py --repo https://github.com/owner/repo --type security

# Performance analysis
python code_review_agent_cli.py --repo https://github.com/owner/repo --type performance

# Custom output format
python code_review_agent_cli.py --repo https://github.com/owner/repo --format detailed
```

### Interactive Mode
```bash
python code_review_agent_cli.py
```

Then type:
```
review https://github.com/owner/repo
review https://github.com/owner/repo --type security
help
version
exit
```

## 📋 Available Options

| Option | Description | Values |
|--------|-------------|--------|
| `--repo` | Repository URL to review | Any GitHub URL |
| `--type` | Review type | `full`, `security`, `performance`, `style` |
| `--format` | Output format | `summary`, `detailed`, `json` |
| `--output` | Custom filename | Any filename (saves to Downloads) |
| `--no-clone` | Skip local cloning | Flag (faster for public repos) |

## 📊 Review Types

### 🔍 Full Review
Comprehensive analysis covering all aspects:
- Security vulnerabilities
- Performance optimization
- Code quality and style
- Documentation coverage
- Testing practices
- Architecture assessment

### 🔒 Security Review
Focused on security aspects:
- Vulnerability scanning
- Input validation
- Authentication/authorization
- Data protection
- Secure coding practices

### ⚡ Performance Review
Performance-focused analysis:
- Code efficiency
- Memory usage
- Algorithm optimization
- Resource management
- Scalability considerations

### 🎨 Style Review
Code style and quality:
- Coding standards
- Readability
- Maintainability
- Best practices
- Documentation quality

## 📄 Output Formats

### Summary Format (Default)
Concise overview with key metrics:
- Overall grade (A-F)
- Score (0-100)
- Issue counts by severity
- Top recommendations

### Detailed Format
Comprehensive analysis including:
- File-by-file breakdown
- Detailed issue descriptions
- Specific recommendations
- Code examples and fixes

### JSON Format
Complete raw data for programmatic use:
- Full analysis results
- Structured data
- Machine-readable format

## 📁 Report Location

All reports are automatically saved to your **Downloads folder**:
```
~/Downloads/code_review_{repo-name}_{timestamp}.json
```

Example: `~/Downloads/code_review_facebook_react_20250729_141642.json`

## 🔧 Configuration

### GitHub Token (Optional)
For private repositories or higher rate limits:
```bash
export GITHUB_TOKEN=your_github_token_here
```

### Environment Variables
- `GITHUB_TOKEN`: GitHub API token
- `REVIEW_OUTPUT_DIR`: Custom output directory (defaults to Downloads)

## 📈 Example Output

```
🔍 Starting code review for: https://github.com/facebook/react
📊 Review type: security
📄 Output format: summary
💾 Output file: code_review_facebook_react_20250729_141642.json
📁 Clone locally: True

✅ Code review completed successfully!

================================================================================
🔍 GITHUB REPOSITORY CODE REVIEW REPORT
================================================================================
📦 Repository: facebook/react
🔗 URL: https://github.com/facebook/react
📅 Timestamp: 2025-07-29T14:17:38.352298
📊 Overall Grade: A (95.2/100)

📈 SUMMARY STATISTICS:
   📁 Total Files: 4215
   ✅ Successful Reviews: 4173
   🚨 Total Issues: 6856
   🔴 Critical: 25
   🟠 High: 0
   🟡 Medium: 5137
   🟢 Low: 1694

🔴 CRITICAL ISSUES (Top 5):
   1. packages/react-devtools-core/src/backend.js:318 - Use of eval() is dangerous
   2. packages/react-devtools-extensions/src/main/sourceSelection.js:4 - Use of eval() is dangerous
   3. packages/react-devtools-extensions/src/main/sourceSelection.js:34 - Use of eval() is dangerous

🎯 KEY RECOMMENDATIONS:
   🔴 CRITICAL: Address 25 critical issues immediately
   🟡 MEDIUM: Improve 147 files with low scores
   🟠 SECURITY: Address 25 security vulnerabilities
   🟡 DOCUMENTATION: Consider improving code documentation
   🟡 TESTING: Consider adding more comprehensive tests
================================================================================
```

## 🛠️ Development

### Project Structure
```
rag/
├── code_review_agent_cli.py      # Main CLI interface
├── github_review_agent.py        # Agent orchestrator
├── agent/
│   ├── github_code_reviewer.py   # GitHub API integration
│   └── code_reviewer.py          # Core analysis engine
└── CODE_REVIEW_AGENT_README.md   # This file
```

### Adding New Review Types
1. Extend the `review_types` in `agent/code_reviewer.py`
2. Add patterns to `agent/github_code_reviewer.py`
3. Update CLI help text in `code_review_agent_cli.py`

### Custom Analysis Rules
Modify `agent/code_reviewer.py` to add:
- New security checks
- Performance metrics
- Quality standards
- Custom scoring algorithms

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- GitHub API for repository access
- Python community for excellent libraries
- Contributors and testers

---

**Version**: 1.0.0  
**Last Updated**: July 29, 2025  
**Maintainer**: RAG Development Team 