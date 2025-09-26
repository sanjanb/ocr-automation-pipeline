# Contributing to OCR Automation Pipeline

Thank you for your interest in contributing! This guide will help you get started with contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code.

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

## Getting Started

### Ways to Contribute

- 🐛 **Bug Reports**: Found a bug? Report it!
- 🚀 **Feature Requests**: Have an idea? Share it!
- 📝 **Documentation**: Improve or add documentation
- 🔧 **Code Contributions**: Fix bugs or implement features
- 🧪 **Testing**: Add tests or improve test coverage
- 🌐 **Translations**: Help translate error messages or UI text

### Before You Start

1. Check if an issue already exists for your bug/feature
2. For major changes, discuss the approach in an issue first
3. Fork the repository and create a branch for your work
4. Follow the development setup instructions

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- A Gemini API key (for testing)

### Setup Instructions

1. **Fork and Clone**

   ```bash
   git clone https://github.com/YOUR_USERNAME/ocr-automation-pipeline.git
   cd ocr-automation-pipeline
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Set Up Environment**

   ```bash
   cp .env.example .env
   # Edit .env with your Gemini API key
   ```

5. **Run Tests**

   ```bash
   pytest tests/ -v
   ```

6. **Start Development Server**
   ```bash
   uvicorn app:app --reload
   ```

### Development Dependencies

Additional tools for development:

```bash
pip install -r requirements-dev.txt
```

This includes:

- `pytest` - Testing framework
- `black` - Code formatter
- `flake8` - Linter
- `mypy` - Type checker
- `pre-commit` - Git hooks
- `coverage` - Test coverage

## Contributing Guidelines

### Issue Guidelines

#### Bug Reports

Include:

- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Error messages or logs
- Screenshots if applicable

**Template:**

```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**

1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen.

**Actual Behavior**
What actually happens.

**Environment**

- OS: [e.g., Windows 10]
- Python Version: [e.g., 3.9.0]
- Browser: [e.g., Chrome 91.0]

**Additional Context**
Any other relevant information.
```

#### Feature Requests

Include:

- Clear description of the feature
- Use case and motivation
- Proposed implementation (if you have ideas)
- Alternatives considered

### Code Contributions

#### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

#### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

- feat: add new document type support
- fix: resolve API timeout issues
- docs: update installation guide
- test: add unit tests for processor
- refactor: improve error handling
- style: fix code formatting
- chore: update dependencies
```

## Pull Request Process

### Before Submitting

1. **Update Documentation**: Ensure relevant docs are updated
2. **Add Tests**: Include tests for new features/bug fixes
3. **Run Tests**: Ensure all tests pass
4. **Check Code Style**: Run formatters and linters
5. **Update CHANGELOG**: Add entry for significant changes

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Linked to relevant issues

### PR Template

```markdown
## Description

Brief description of changes.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

Describe how you tested your changes.

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes

## Related Issues

Closes #123
```

### Review Process

1. Automated checks must pass (CI/CD)
2. At least one maintainer review required
3. Address all feedback before merge
4. Squash commits when merging

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [flake8](https://flake8.pycqa.org/) for linting
- Use type hints where appropriate

### Code Quality

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/

# Run all checks
pre-commit run --all-files
```

### Project Structure

```
src/
  document_processor/
    __init__.py
    core.py          # Main processing logic
    schemas.py       # Document schemas
    config.py        # Configuration management
    utils.py         # Utility functions
tests/
  conftest.py        # Test configuration
  test_core.py       # Core logic tests
  test_api.py        # API endpoint tests
  fixtures/          # Test data
```

### Naming Conventions

- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Files**: `snake_case.py`
- **Directories**: `snake_case`

### Documentation Standards

- Use docstrings for all public functions/classes
- Follow [Google Style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Include type hints
- Add inline comments for complex logic

```python
def process_document(
    image_path: str,
    document_type: Optional[str] = None,
    confidence_threshold: float = 0.5
) -> ProcessingResult:
    """Process a document image and extract structured data.

    Args:
        image_path: Path to the document image file
        document_type: Expected document type (auto-detected if None)
        confidence_threshold: Minimum confidence score (0.0-1.0)

    Returns:
        ProcessingResult containing extracted data and metadata

    Raises:
        ProcessingError: If document processing fails
        ValidationError: If confidence is below threshold
    """
```

## Testing

### Test Categories

1. **Unit Tests**: Test individual functions/classes
2. **Integration Tests**: Test API endpoints
3. **E2E Tests**: Test complete workflows
4. **Performance Tests**: Test processing speed/memory

### Writing Tests

```python
import pytest
from src.document_processor.core import DocumentProcessor

class TestDocumentProcessor:
    def test_valid_document_processing(self, sample_aadhaar_image):
        """Test processing valid Aadhaar document."""
        processor = DocumentProcessor()
        result = processor.process(sample_aadhaar_image, "aadhaar")

        assert result.success
        assert result.document_type == "aadhaar"
        assert result.confidence > 0.5
        assert "aadhaar_number" in result.extracted_data

    def test_invalid_document_type(self):
        """Test handling of invalid document type."""
        processor = DocumentProcessor()

        with pytest.raises(ValidationError):
            processor.process("image.jpg", "invalid_type")
```

### Test Data

- Store test images in `tests/fixtures/`
- Use small, anonymized sample documents
- Include various quality levels and edge cases
- Document test data sources and licenses

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run specific test
pytest tests/test_core.py::test_valid_document_processing

# Run tests in parallel
pytest -n auto
```

## Documentation

### Types of Documentation

1. **API Documentation**: In-code docstrings + API.md
2. **User Guide**: README.md, SETUP.md
3. **Developer Guide**: This file + inline comments
4. **Architecture**: Technical design documents

### Documentation Guidelines

- Keep documentation up-to-date with code changes
- Use clear, concise language
- Include code examples
- Add diagrams where helpful
- Test documentation examples

### Building Documentation

```bash
# Generate API documentation
pdoc src/ --html --output-dir docs/

# Check documentation links
# (Add link checker tool)
```

## Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):

- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features, backward compatible
- Patch: Bug fixes, backward compatible

### Release Checklist

1. Update version in `__init__.py`
2. Update `CHANGELOG.md`
3. Create release branch
4. Run full test suite
5. Update documentation
6. Create GitHub release
7. Deploy to staging/production

## Community

### Communication Channels

- **Issues**: Bug reports, feature requests
- **Discussions**: Questions, ideas, help
- **Discord**: [Join our Discord](https://discord.gg/your-server) (if applicable)

### Recognition

Contributors will be recognized:

- Added to `CONTRIBUTORS.md`
- Mentioned in release notes
- GitHub contributor graph
- Special thanks for significant contributions

## Help and Support

### Getting Help

- Check existing [Issues](https://github.com/sanjanb/ocr-automation-pipeline/issues)
- Read the [documentation](README.md)
- Ask in [Discussions](https://github.com/sanjanb/ocr-automation-pipeline/discussions)

### Common Development Issues

#### Environment Setup Problems

```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Test Failures

```bash
# Clear pytest cache
pytest --cache-clear

# Run tests with verbose output
pytest -vv --tb=long
```

#### API Key Issues

- Ensure `.env` file exists and has valid key
- Check API key permissions
- Verify network connectivity to Gemini API

Thank you for contributing! 🚀
