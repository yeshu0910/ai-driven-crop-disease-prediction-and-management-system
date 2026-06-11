# Contributing to AI-Driven Crop Disease Prediction and Management System

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

- Use the issue tracker to report bugs
- Include steps to reproduce the bug
- Include expected and actual behavior
- Include screenshots if applicable
- Include your environment details (OS, Python version, etc.)

### Suggesting Features

- Use the issue tracker to suggest features
- Clearly describe the feature and its use case
- Explain why this feature would be useful
- Be open to feedback and discussion

### Code Contributions

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following our coding standards
4. Run tests and linting (`pytest`, `ruff check .`, `mypy .`)
5. Commit your changes with a descriptive message
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://code.swecha.org/yeshu_09/ai-driven-crop-disease-prediction-and-management-system.git
cd ai-driven-crop-disease-prediction-and-management-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

## Coding Standards

- Follow PEP 8 style guidelines
- Use type hints in all Python code
- Write docstrings for all functions and classes
- Keep functions small and focused
- Write tests for new functionality
- Update documentation for new features

## Commit Message Format

We use conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(model): add support for tomato early blight detection

- Added 500 new training images
- Updated model architecture to ResNet-50
- Achieved 92% accuracy on test set
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Ensure code passes linting (`ruff check .`)
5. Ensure type checking passes (`mypy .`)
6. Request review from maintainers

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run linting
ruff check .

# Run type checking
mypy .

```

## Questions?

Feel free to open an issue for any questions about contributing.
