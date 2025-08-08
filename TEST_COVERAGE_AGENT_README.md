# Test Coverage & Suggestions Agent

🧪 **Intelligent Test Coverage Monitoring and Suggestions**

A sophisticated agent that monitors test coverage of pull requests and provides intelligent suggestions for missing test cases. Supports multiple coverage tools and uses LLM-enhanced analysis to provide actionable recommendations.

## 🚀 Features

### Core Functionality
- **Multi-Language Support**: JaCoCo (Java/Kotlin), Istanbul (JS/TS), Python coverage, Go test
- **PR Analysis**: Automatically analyze test coverage for GitHub pull requests
- **Intelligent Suggestions**: LLM-enhanced suggestions for missing test cases
- **Priority Classification**: High, medium, and low priority suggestions
- **Comprehensive Reporting**: Detailed coverage reports with actionable recommendations

### Smart Analysis
- **Line-by-Line Analysis**: Identifies specific uncovered lines
- **Code Pattern Recognition**: Classifies code types (null checks, edge cases, error handling, etc.)
- **Context-Aware Suggestions**: Provides specific suggestions based on code context
- **Coverage Thresholds**: Configurable coverage targets and alerts

## 📋 Supported Languages & Tools

| Language | Coverage Tool | File Extensions |
|----------|---------------|-----------------|
| Java | JaCoCo | `.java` |
| Kotlin | JaCoCo | `.kt` |
| JavaScript | Istanbul | `.js` |
| TypeScript | Istanbul | `.ts` |
| Python | Coverage.py | `.py` |
| Go | Go test | `.go` |

## 🛠️ Installation

### Prerequisites
```bash
# Python 3.8+
python3 --version

# Required packages
pip install requests xml.etree.ElementTree dataclasses pathlib
```

### Setup
1. **Clone the repository** (if not already done)
2. **Set environment variables**:
   ```bash
   # GitHub integration
   export GITHUB_TOKEN="your_github_token"
   export GITHUB_OWNER="your_username"
   export GITHUB_REPO="your_repo"
   
   # LLM API (optional, for enhanced suggestions)
   export LLM_API_KEY="your_llm_api_key"
   ```

## 🎯 Usage

### Command Line Interface

#### Interactive Mode
```bash
python3 test_coverage_cli.py interactive
```

#### Analyze Pull Request
```bash
python3 test_coverage_cli.py analyze-pr 123 owner repo
```

#### Analyze Single File
```bash
python3 test_coverage_cli.py analyze-file src/main.py
```

#### Generate Test Suggestions
```bash
python3 test_coverage_cli.py generate-suggestions tests/test_file.py
```

### Programmatic Usage

```python
from agent.test_coverage_agent import TestCoverageAgent

# Initialize agent
agent = TestCoverageAgent()

# Analyze PR coverage
report = agent.analyze_pr_coverage(123, "owner", "repo")
print(report)

# Analyze specific file
coverage_data = agent._analyze_file_coverage("src/main.py", "py")
suggestions = agent._generate_test_suggestions(coverage_data, "src/main.py", "py")
```

## 📊 Output Examples

### Coverage Report
```
📊 Coverage Report
==================================================
🎯 Overall Coverage: 67.5%
📈 Total Lines: 200
✅ Covered Lines: 135
❌ Uncovered Lines: 65

📁 File Coverage:
   src/main.py: 75.0%
   src/utils.py: 60.0%

💡 Test Suggestions:
   🔴 High Priority: 3
   🟡 Medium Priority: 5
   🟢 Low Priority: 2

🎯 Top Suggestions:
   1. Add test case for null/empty input: 'if user_data is None:'
      File: src/main.py:15
      Type: null_check | Priority: high

   2. Add test case for edge condition: 'if age >= 18:'
      File: src/main.py:25
      Type: edge_case | Priority: medium

📋 Recommendations:
   • ⚠️ Coverage is below 80%. Add more comprehensive test cases.
   • 🎯 Focus on 3 high-priority test suggestions.
   • 🔍 Add 2 null/empty input test cases.
   • ⚡ Add 3 edge case test scenarios.
```

### Test Suggestions
```
💡 Test Suggestions (10 total)
==================================================

🔴 High Priority (3):
   1. Add test case for null/empty input: 'if user_data is None:'
      Line 15: if user_data is None:

   2. Add test case for error scenario: 'except ValueError:'
      Line 28: except ValueError as e:

🟡 Medium Priority (5):
   1. Add test case for edge condition: 'if age >= 18:'
      Line 25: if age >= 18:
```

## 🔧 Configuration

### Coverage Tool Configuration

#### JaCoCo (Java/Kotlin)
```xml
<!-- Maven pom.xml -->
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.7</version>
    <executions>
        <execution>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

#### Istanbul (JavaScript/TypeScript)
```json
// package.json
{
  "scripts": {
    "test:coverage": "nyc --reporter=json --reporter=text mocha"
  },
  "nyc": {
    "extends": "@istanbuljs/nyc-config-typescript"
  }
}
```

#### Python Coverage
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run -m pytest
coverage report
coverage html
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python3 -m pytest test_test_coverage_agent.py

# Run specific test
python3 test_test_coverage_agent.py TestTestCoverageAgent.test_language_detection
```

### Run Demo
```bash
# Run interactive demo
python3 test_test_coverage_agent.py
```

## 🔍 How It Works

### 1. Coverage Analysis
1. **File Detection**: Identifies changed files in PR
2. **Language Detection**: Determines programming language from file extension
3. **Tool Selection**: Chooses appropriate coverage tool
4. **Report Parsing**: Parses coverage reports (XML, JSON, etc.)
5. **Data Extraction**: Extracts coverage metrics and uncovered lines

### 2. Suggestion Generation
1. **Line Classification**: Categorizes uncovered lines by type
   - `null_check`: Null/empty input handling
   - `edge_case`: Conditional logic
   - `error_handling`: Exception handling
   - `boundary`: Boundary conditions
   - `control_flow`: Return/break/continue statements
   - `general`: Other uncovered code

2. **Context Analysis**: Analyzes code context for better suggestions
3. **Priority Assignment**: Assigns priority based on coverage impact
4. **Description Generation**: Creates actionable test suggestions

### 3. Report Generation
1. **Metrics Calculation**: Computes overall and per-file coverage
2. **Suggestion Aggregation**: Groups suggestions by priority and type
3. **Recommendation Generation**: Provides actionable recommendations
4. **Report Formatting**: Creates comprehensive, readable reports

## 🎯 Best Practices

### For Developers
1. **Run Coverage Regularly**: Integrate coverage analysis into CI/CD
2. **Focus on High Priority**: Address high-priority suggestions first
3. **Context Matters**: Consider the business logic when writing tests
4. **Edge Cases**: Pay special attention to boundary conditions

### For Teams
1. **Set Coverage Targets**: Establish minimum coverage thresholds
2. **Review Suggestions**: Regularly review and implement suggestions
3. **Track Progress**: Monitor coverage improvements over time
4. **Automate**: Integrate agent into pull request workflows

## 🔧 Integration

### GitHub Actions
```yaml
name: Test Coverage Analysis
on: [pull_request]

jobs:
  coverage-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests with coverage
        run: |
          coverage run -m pytest
          coverage report
      - name: Analyze coverage
        run: python3 test_coverage_cli.py analyze-pr ${{ github.event.pull_request.number }} ${{ github.repository_owner }} ${{ github.event.repository.name }}
```

### CI/CD Integration
```bash
#!/bin/bash
# coverage_analysis.sh

# Run tests with coverage
coverage run -m pytest

# Generate coverage report
coverage report

# Analyze with Test Coverage Agent
python3 test_coverage_cli.py analyze-file src/main.py

# Post results to PR
# (Implementation depends on your CI system)
```

## 🚀 Advanced Features

### Custom Coverage Tools
Extend the agent to support additional coverage tools:

```python
class CustomCoverageAgent(TestCoverageAgent):
    def _analyze_custom_coverage(self, file_path: str) -> Optional[CoverageData]:
        # Implement custom coverage analysis
        pass
    
    def _find_custom_report(self, file_path: str) -> Optional[str]:
        # Implement custom report finding
        pass
```

### LLM Integration
For enhanced suggestions, integrate with LLM APIs:

```python
def _generate_llm_suggestion(self, code_line: str, context: str) -> str:
    # Use LLM to generate more sophisticated suggestions
    prompt = f"Generate a test case for this line: {code_line}\nContext: {context}"
    # Call LLM API and return suggestion
    return llm_response
```

## 📈 Performance

### Benchmarks
- **Small PRs** (< 10 files): ~2-5 seconds
- **Medium PRs** (10-50 files): ~5-15 seconds
- **Large PRs** (> 50 files): ~15-30 seconds

### Optimization Tips
1. **Cache Coverage Reports**: Store parsed coverage data
2. **Parallel Processing**: Analyze multiple files concurrently
3. **Incremental Analysis**: Only analyze changed files
4. **Report Caching**: Cache coverage reports between runs

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd agentic-rag-knowledge-graph

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python3 -m pytest

# Run linting
flake8 agent/ tests/
```

### Adding New Language Support
1. **Implement Coverage Parser**: Add `_analyze_<language>_coverage` method
2. **Add Report Finder**: Implement `_find_<language>_report` method
3. **Update Language Map**: Add file extensions to `supported_languages`
4. **Add Tests**: Create test cases for new language support

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **JaCoCo**: Java code coverage library
- **Istanbul**: JavaScript code coverage tool
- **Coverage.py**: Python coverage measurement tool
- **Go test**: Go testing and coverage tool

---

**🧪 Test Coverage & Suggestions Agent** - Making test coverage analysis intelligent and actionable!
