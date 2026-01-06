# Contributing to Irminsul

Thank you for your interest in contributing to **Irminsul**! This document provides guidelines and information for contributors to help make the contribution process smooth and effective.

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Setup](#-development-setup)
- [Contributing Guidelines](#-contributing-guidelines)
- [Code Style and Standards](#-code-style-and-standards)
- [Testing](#-testing)
- [Documentation](#-documentation)
- [Pull Request Process](#-pull-request-process)
- [Issue Reporting](#-issue-reporting)
- [Development Workflow](#-development-workflow)
- [Contact](#-contact)

## 🌟 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- **Be respectful** and inclusive in your language and actions
- **Be collaborative** and help others learn
- **Focus on constructive feedback** and solutions
- **Respect different viewpoints** and experiences
- **Show empathy** towards other community members

## 🚀 Getting Started

### Ways to Contribute

You can contribute to Irminsul in many ways:

- 🐛 **Bug Reports**: Report bugs through issues
- 💡 **Feature Requests**: Suggest new features or improvements
- 🔧 **Code Contributions**: Fix bugs or implement new features
- 📖 **Documentation**: Improve documentation, README, or guides
- 🧪 **Testing**: Help test new features or create test cases
- 🎨 **UI/UX**: Improve the user interface and experience

### Prerequisites

Before contributing, make sure you have:

- **Python 3.8+** installed
- **Git** for version control
- **Tesseract OCR** installed on your system
- **Basic understanding** of Python and tkinter (for GUI contributions)
- **Familiarity with OCR concepts** (helpful but not required)

## 🛠 Development Setup

### 1. Fork and Clone the Repository

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/Irminsul.git
cd Irminsul

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/Irminsul.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # If available
```

### 3. Install System Dependencies

#### Tesseract OCR Installation:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-ind
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
1. Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install and add to PATH
3. Install language packs (eng, ind)

### 4. Verify Installation

```bash
# Test Tesseract installation
tesseract --version

# Test the application
python gui_modern.py
```

## 📝 Contributing Guidelines

### Before You Start

1. **Check existing issues** to avoid duplicate work
2. **Create an issue** for new features or bug fixes
3. **Discuss your approach** in the issue before coding
4. **Wait for approval** before starting major changes

### Branch Naming Convention

Use descriptive branch names:

```bash
# Feature branches
feature/ocr-improvements
feature/template-creator-ui
feature/docker-optimization

# Bug fix branches
fix/screenshot-overlay-bug
fix/template-parsing-error

# Documentation branches
docs/readme-improvements
docs/api-documentation

# Test branches
test/gui-integration-tests
test/performance-benchmarks
```

### Commit Message Format

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(gui): add zoom controls to template creator
fix(ocr): resolve memory leak in batch processing
docs(readme): update installation instructions for Windows
test(gui): add unit tests for screenshot functionality
```

## 🎨 Code Style and Standards

### Python Style Guide

- **PEP 8**: Follow Python PEP 8 style guidelines
- **Line length**: Maximum 88 characters (Black formatter standard)
- **Indentation**: 4 spaces (no tabs)
- **String quotes**: Use double quotes for strings
- **Variable naming**: snake_case for variables and functions
- **Class naming**: PascalCase for classes

### Code Organization

```python
# Example code structure
"""Module docstring explaining the purpose."""

import standard_library
import third_party

# Local imports
from .local_module import LocalClass
from .constants import CONSTANT_VALUE


class MyClass:
    """Class docstring with description."""
    
    def __init__(self, param: str) -> None:
        """Initialize class with parameter."""
        self.param = param
        
    def method_name(self) -> ReturnType:
        """Method description."""
        pass
```

### GUI Development Guidelines

- **Use modern tkinter** features and styling
- **Responsive design**: Ensure GUI works on different screen sizes
- **Error handling**: Include proper error handling in GUI events
- **User feedback**: Provide loading indicators and status messages
- **Memory management**: Clean up resources properly

### Documentation Standards

- **Docstrings**: Use Google-style docstrings
- **Type hints**: Include type hints for function parameters and returns
- **Comments**: Add comments for complex logic
- **README updates**: Update README for significant changes

## 🧪 Testing

### Testing Requirements

- **Unit tests**: Write tests for new functions/methods
- **Integration tests**: Test GUI components and OCR pipeline
- **Manual testing**: Test GUI changes manually
- **Performance tests**: Include performance tests for OCR operations

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_ocr.py

# Run with coverage
python -m pytest --cov=.

# Run GUI tests (may require display)
python test_gui_image_display.py
```

### Writing Tests

```python
import unittest
from unittest.mock import patch, MagicMock

class TestOCRFunction(unittest.TestCase):
    """Test cases for OCR functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_image_path = "test_image.png"
        
    def test_extract_text_success(self):
        """Test successful text extraction."""
        # Test implementation
        
    @patch('tesseract.extract_text')
    def test_extract_text_error_handling(self, mock_extract):
        """Test error handling in text extraction."""
        mock_extract.side_effect = Exception("OCR Error")
        # Test implementation
```

### GUI Testing

For GUI components, create separate test files:

```bash
python test_image_display.py          # Test image display functionality
python test_gui_image_display.py      # Test GUI image handling
python test_ocr.py                   # Test OCR core functionality
```

## 📚 Documentation

### Documentation Types

1. **Code Documentation**: Docstrings and comments
2. **API Documentation**: Function and class documentation
3. **User Documentation**: README and usage guides
4. **Developer Documentation**: Architecture and design docs

### Documentation Guidelines

- **Keep documentation updated** with code changes
- **Use clear examples** in docstrings
- **Include type hints** in function signatures
- **Add usage examples** for complex functions
- **Update README** for new features or changes

### Building Documentation

If using Sphinx for documentation:

```bash
cd docs
make html
```

## 🔄 Pull Request Process

### Before Submitting

1. **Update your branch** with latest upstream changes:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   git push origin main
   ```

2. **Run tests** to ensure everything works:
   ```bash
   python -m pytest
   python gui_modern.py  # Manual GUI test
   ```

3. **Check code style**:
   ```bash
   black --check .
   flake8 .
   ```

4. **Update documentation** if needed

### PR Submission

1. **Create a descriptive PR title**
2. **Fill out the PR template** completely
3. **Link related issues** using keywords (fixes #123)
4. **Include screenshots** for GUI changes
5. **Add tests** for new functionality
6. **Update documentation** as needed

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Manual testing completed
- [ ] GUI changes tested

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
```

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainers
3. **Testing** by reviewers
4. **Documentation review** for completeness
5. **Approval** and merge

## 🐛 Issue Reporting

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Check documentation** for solutions
3. **Verify the issue** with latest version
4. **Test with different environments** if possible

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Screenshots
If applicable, add screenshots

## Environment
- OS: [e.g. Ubuntu 20.04, Windows 10, macOS Big Sur]
- Python Version: [e.g. 3.9.7]
- Tesseract Version: [e.g. 4.1.1]
- Irminsul Version: [e.g. 1.2.0]

## Additional Context
Any other context about the problem
```

### Feature Request Template

```markdown
## Feature Description
Clear description of the proposed feature

## Problem/Use Case
What problem does this solve?

## Proposed Solution
How you envision this feature working

## Alternatives Considered
Other solutions you've considered

## Additional Context
Any other context or screenshots
```

## 🔄 Development Workflow

### Typical Contribution Workflow

1. **Find or create an issue**
2. **Discuss the approach** in the issue
3. **Fork and create a branch**
4. **Make changes** following guidelines
5. **Write/update tests**
6. **Update documentation**
7. **Test thoroughly**
8. **Submit PR**
9. **Address review feedback**
10. **Merge and celebrate** 🎉

### Release Process

1. **Feature freeze** before release
2. **Testing phase** with all contributors
3. **Documentation review**
4. **Version tagging**
5. **Release notes** preparation
6. **GitHub release** creation

## 🏗 Architecture Guidelines

### Project Structure

```
Irminsul/
├── gui_modern.py          # Main GUI application
├── extract.py             # Core OCR functionality
├── screenshot.py          # Screenshot tools
├── template.py            # Template management
├── modern_styles.py       # GUI styling
├── enhanced_ocr.py        # Enhanced OCR features
├── requirements.txt       # Dependencies
├── dockerfile            # Docker configuration
├── tests/                # Test files
├── docs/                 # Documentation
└── CONTRIBUTING.md       # This file
```

### Design Principles

- **Modularity**: Keep components separate and focused
- **Testability**: Design for easy testing
- **Performance**: Optimize for OCR processing speed
- **User Experience**: Prioritize ease of use
- **Cross-platform**: Ensure compatibility across OS

## 🎯 Areas for Contribution

### High Priority

1. **GUI Improvements**
   - Better styling and modern appearance
   - Improved user experience
   - Accessibility features

2. **OCR Performance**
   - Speed optimizations
   - Memory usage improvements
   - Batch processing enhancements

3. **Template System**
   - Advanced template features
   - Template validation
   - Import/export improvements

4. **Documentation**
   - API documentation
   - Tutorial videos
   - Usage examples

### Nice to Have

1. **Additional OCR engines** support
2. **Plugin system** for extensions
3. **Cloud integration** options
4. **Mobile app** version
5. **Web interface** alternative

## 🛡 Security Considerations

When contributing, please keep security in mind:

- **Input validation**: Validate all user inputs
- **File handling**: Safely handle file paths and operations
- **Error handling**: Don't expose sensitive information in errors
- **Dependencies**: Keep dependencies updated and secure
- **Docker security**: Follow container security best practices

## 📞 Contact

### Maintainers

- **Project Lead**: [Your Name/Contact]
- **GUI Developer**: [Contact for GUI issues]
- **OCR Specialist**: [Contact for OCR-related issues]

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For general questions and ideas
- **Email**: [Maintainer email] for private matters

### Getting Help

1. **Check documentation** first
2. **Search existing issues** on GitHub
3. **Ask in discussions** for general questions
4. **Contact maintainers** for private issues

## 🙏 Recognition

Contributors to Irminsul will be recognized in:

- **README.md**: List of contributors
- **Release notes**: Notable contributions
- **GitHub contributors**: Automatic recognition
- **Special mentions**: For significant contributions

### Hall of Fame

Contributors who have made exceptional contributions:
- 🎯 **OCR Optimization**: [Name] - Improved processing speed by 40%
- 🎨 **UI/UX Design**: [Name] - Complete modern interface redesign
- 📚 **Documentation**: [Name] - Comprehensive user guides
- 🧪 **Testing**: [Name] - 95% test coverage achievement

## 📋 Development Roadmap

### Short Term (1-3 months)
- [ ] Improve GUI responsiveness
- [ ] Add more OCR language support
- [ ] Enhance template validation
- [ ] Performance optimizations

### Medium Term (3-6 months)
- [ ] Plugin system implementation
- [ ] Advanced batch processing
- [ ] Cloud storage integration
- [ ] Mobile app development

### Long Term (6+ months)
- [ ] AI-powered text recognition
- [ ] Multi-platform desktop app
- [ ] Enterprise features
- [ ] Community plugins marketplace

---

## Thank You! 🎉

Thank you for contributing to **Irminsul**! Every contribution, no matter how small, helps make this project better for everyone. Your time and effort are greatly appreciated.

**Happy coding!** 🚀

---

*This contribution guide is a living document. If you have suggestions for improvements, please create an issue or submit a PR to enhance it.*
