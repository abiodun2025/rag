# GitHub-Integrated Test Coverage & Suggestions Agent

🔗 **Connect to GitHub, Clone Repositories, Run Tests, Analyze Coverage**

A powerful agent that connects to GitHub repositories, clones code, runs tests with coverage, and provides intelligent suggestions for missing test cases. This agent can analyze both individual pull requests and entire repositories.

## 🚀 Key Features

### 🔗 GitHub Integration
- **Repository Cloning**: Automatically clones GitHub repositories
- **PR Analysis**: Analyzes test coverage for specific pull requests
- **Branch Support**: Works with any branch (main, feature branches, etc.)
- **GitHub API**: Uses GitHub API for repository information

### 🧪 Test Execution
- **Multi-Language Support**: Java (Maven), JavaScript/TypeScript (npm), Python (pip), Go
- **Automatic Detection**: Detects project type and runs appropriate tests
- **Coverage Collection**: Collects coverage reports from various tools
- **Dependency Management**: Installs dependencies automatically

### 📊 Intelligent Analysis
- **Real Coverage Data**: Uses actual test execution results
- **Line-by-Line Analysis**: Identifies specific uncovered lines
- **Smart Suggestions**: Provides context-aware test suggestions
- **Priority Classification**: High, medium, low priority recommendations

## 🛠️ Prerequisites

### Required Tools
```bash
# Git (for cloning repositories)
git --version

# Language-specific tools (at least one)
mvn --version      # Java/Maven
npm --version      # JavaScript/TypeScript
pip --version      # Python
go version         # Go
```

### GitHub Configuration
Set up environment variables:
```bash
export GITHUB_TOKEN="your_github_personal_access_token"
export GITHUB_OWNER="your_username_or_organization"
export GITHUB_REPO="your_repository_name"
```

### GitHub Token Setup
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` scope
3. Copy the token and set it as `GITHUB_TOKEN`

## 🎯 Usage

### Command Line Interface

#### Analyze Pull Request Coverage
```bash
python3 github_coverage_cli.py pr 123
```
This will:
1. Clone the repository with the PR branch
2. Run tests with coverage
3. Analyze coverage for changed files
4. Generate intelligent suggestions

#### Analyze Repository Coverage
```bash
python3 github_coverage_cli.py repo main
python3 github_coverage_cli.py repo feature/new-feature
```
This will:
1. Clone the specified branch
2. Detect project type
3. Run tests with coverage
4. Analyze all source files
5. Generate comprehensive report

#### Test GitHub Connection
```bash
python3 github_coverage_cli.py test
```
Verifies:
- GitHub API access
- Repository permissions
- Token validity
- PR access

#### Check Prerequisites
```bash
python3 github_coverage_cli.py check
```
Checks for:
- Git availability
- Language-specific tools
- Missing dependencies

#### Interactive Mode
```bash
python3 github_coverage_cli.py interactive
```
Provides an interactive interface for:
- Real-time analysis
- Multiple commands
- Demo functionality

### Programmatic Usage

```python
from agent.github_coverage_agent import GitHubCoverageAgent, GitHubConfig

# Configure GitHub access
config = GitHubConfig(
    token="your_github_token",
    owner="your_username",
    repo="your_repo"
)

# Initialize agent
agent = GitHubCoverageAgent(config)

# Analyze PR coverage
report = agent.analyze_pr_coverage(123)
print(report)

# Analyze repository coverage
report = agent.analyze_repository_coverage("main")
print(report)
```

## 📊 Supported Project Types

### Java/Kotlin (Maven)
- **Detection**: `pom.xml` or `build.gradle` files
- **Test Command**: `mvn clean test jacoco:report`
- **Coverage Tool**: JaCoCo
- **Report Location**: `target/site/jacoco/jacoco.xml`

### JavaScript/TypeScript (npm)
- **Detection**: `package.json` file
- **Test Command**: `npm run test:coverage`
- **Coverage Tool**: Istanbul/nyc
- **Report Location**: `coverage/coverage-final.json`

### Python (pip)
- **Detection**: `requirements.txt` file
- **Test Command**: `coverage run -m pytest`
- **Coverage Tool**: Coverage.py
- **Report Location**: `.coverage` file

### Go
- **Detection**: `go.mod` file
- **Test Command**: `go test -coverprofile=coverage.out ./...`
- **Coverage Tool**: Go test coverage
- **Report Location**: `coverage.out`

## 🔍 How It Works

### 1. Repository Analysis
1. **GitHub API**: Fetches repository and PR information
2. **Repository Cloning**: Clones the repository to temporary directory
3. **Project Detection**: Identifies project type from configuration files
4. **Dependency Installation**: Installs required dependencies

### 2. Test Execution
1. **Tool Detection**: Checks for required tools (Maven, npm, pip, Go)
2. **Test Running**: Executes tests with coverage enabled
3. **Report Generation**: Generates coverage reports
4. **Data Collection**: Parses coverage data

### 3. Coverage Analysis
1. **Report Parsing**: Parses coverage reports (XML, JSON, etc.)
2. **Line Analysis**: Identifies uncovered lines
3. **File Processing**: Analyzes source files for context
4. **Suggestion Generation**: Creates intelligent test suggestions

### 4. Report Generation
1. **Metrics Calculation**: Computes overall and per-file coverage
2. **Suggestion Aggregation**: Groups suggestions by priority
3. **Recommendation Creation**: Provides actionable recommendations
4. **Cleanup**: Removes temporary files

## 📋 Sample Output

### PR Analysis Report
```
📊 Coverage Report
============================================================
📋 PR #123: Add new feature
👤 Author: username
📁 Repository: owner/repo

🎯 Overall Coverage: 75.2%
📈 Total Lines: 150
✅ Covered Lines: 113
❌ Uncovered Lines: 37

📁 File Coverage:
   src/main.py: 80.0%
   src/utils.py: 65.0%

💡 Test Suggestions:
   🔴 High Priority: 2
   🟡 Medium Priority: 3
   🟢 Low Priority: 1

🎯 Top Suggestions:
   1. Add test case for null/empty input: 'if user_data is None:'
      File: src/main.py:25
      Type: null_check | Priority: high

   2. Add test case for edge condition: 'if age >= 18:'
      File: src/main.py:35
      Type: edge_case | Priority: medium

📋 Recommendations:
   • ⚠️ Coverage is below 80%. Add more comprehensive test cases.
   • 🎯 Focus on 2 high-priority test suggestions.
   • 🔍 Add 1 null/empty input test cases.
```

### Repository Analysis Report
```
📊 Coverage Report
============================================================
📁 Repository: owner/repo
🌿 Branch: main

🎯 Overall Coverage: 82.5%
📈 Total Lines: 500
✅ Covered Lines: 413
❌ Uncovered Lines: 87

📁 File Coverage:
   src/main.py: 85.0%
   src/utils.py: 78.0%
   src/models.py: 90.0%

💡 Test Suggestions:
   🔴 High Priority: 1
   🟡 Medium Priority: 4
   🟢 Low Priority: 2

📋 Recommendations:
   • ✅ Good coverage! Consider adding integration tests for better confidence.
   • 🎯 Focus on 1 high-priority test suggestions.
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
GITHUB_TOKEN=ghp_your_token_here
GITHUB_OWNER=your_username
GITHUB_REPO=your_repo

# Optional
LLM_API_KEY=your_llm_api_key  # For enhanced suggestions
```

### Project-Specific Configuration

#### Java/Maven
```xml
<!-- pom.xml -->
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

#### JavaScript/TypeScript
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

#### Python
```bash
# requirements.txt
pytest
coverage
```

## 🚀 Advanced Features

### Custom Test Commands
The agent automatically detects and runs appropriate test commands:

- **Java**: `mvn clean test jacoco:report`
- **JavaScript**: `npm run test:coverage`
- **Python**: `coverage run -m pytest`
- **Go**: `go test -coverprofile=coverage.out ./...`

### Coverage Report Parsing
Supports multiple coverage report formats:

- **JaCoCo XML**: Java/Kotlin projects
- **Istanbul JSON**: JavaScript/TypeScript projects
- **Coverage.py**: Python projects
- **Go coverage**: Go projects

### Intelligent Suggestions
Provides context-aware suggestions:

- **Null Checks**: Identifies missing null/empty input tests
- **Edge Cases**: Suggests boundary condition tests
- **Error Handling**: Recommends exception testing
- **Control Flow**: Identifies missing branch coverage

## 🔍 Troubleshooting

### Common Issues

#### GitHub Token Issues
```bash
❌ GitHub API error: 401
```
**Solution**: Check your GitHub token has `repo` scope

#### Missing Tools
```bash
❌ Maven not found
```
**Solution**: Install required tools for your project type

#### Test Failures
```bash
❌ Test execution failed: Command failed
```
**Solution**: Check your project's test configuration

#### Coverage Report Issues
```bash
⚠️ No coverage report found
```
**Solution**: Ensure your project generates coverage reports

### Debug Mode
Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
python3 github_coverage_cli.py pr 123
```

## 🎯 Use Cases

### For Developers
1. **Pre-commit Analysis**: Check coverage before creating PRs
2. **PR Review**: Analyze coverage for incoming PRs
3. **Quality Assurance**: Ensure adequate test coverage
4. **Test Planning**: Identify areas needing test coverage

### For Teams
1. **Code Review**: Include coverage analysis in reviews
2. **CI/CD Integration**: Automated coverage monitoring
3. **Quality Gates**: Enforce minimum coverage thresholds
4. **Progress Tracking**: Monitor coverage improvements

### For Organizations
1. **Quality Metrics**: Track overall test coverage
2. **Compliance**: Ensure testing standards
3. **Risk Assessment**: Identify untested code areas
4. **Resource Planning**: Focus testing efforts efficiently

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
      - name: Analyze coverage
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_OWNER: ${{ github.repository_owner }}
          GITHUB_REPO: ${{ github.event.repository.name }}
        run: python3 github_coverage_cli.py pr ${{ github.event.pull_request.number }}
```

### CI/CD Integration
```bash
#!/bin/bash
# coverage_analysis.sh

# Set GitHub configuration
export GITHUB_TOKEN="$GITHUB_TOKEN"
export GITHUB_OWNER="$GITHUB_OWNER"
export GITHUB_REPO="$GITHUB_REPO"

# Analyze PR coverage
python3 github_coverage_cli.py pr $PR_NUMBER

# Post results to PR
# (Implementation depends on your CI system)
```

## 📈 Performance

### Benchmarks
- **Small Repos** (< 10 files): ~30-60 seconds
- **Medium Repos** (10-50 files): ~1-3 minutes
- **Large Repos** (> 50 files): ~3-10 minutes

### Optimization Tips
1. **Shallow Cloning**: Uses `--depth 1` for faster cloning
2. **Parallel Processing**: Ready for concurrent analysis
3. **Caching**: Framework for report caching
4. **Incremental Analysis**: Only analyze changed files

## 🚀 Next Steps

### Immediate Enhancements
1. **More Languages**: Add support for C#, Rust, etc.
2. **Web Interface**: Create web-based dashboard
3. **Historical Tracking**: Track coverage over time
4. **Team Analytics**: Multi-repository analysis

### Advanced Features
1. **Test Generation**: Auto-generate test cases
2. **Mutation Testing**: Suggest mutation test scenarios
3. **Performance Testing**: Include performance test suggestions
4. **Security Testing**: Add security test recommendations

---

## 🏆 Conclusion

The **GitHub-Integrated Test Coverage & Suggestions Agent** provides:

1. **Real GitHub Integration** - Connects to actual repositories
2. **Automated Test Execution** - Runs tests and collects coverage
3. **Intelligent Analysis** - Provides context-aware suggestions
4. **Comprehensive Reporting** - Detailed coverage reports
5. **Easy Integration** - Works with existing CI/CD pipelines

**Ready for production use with real GitHub repositories!** 🚀
