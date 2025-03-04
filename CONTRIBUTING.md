# Contributing to TaskFlow

Thank you for considering contributing to TaskFlow! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find that the bug has already been reported. When you are creating a bug report, please include as many details as possible by filling out the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

### Suggesting Enhancements

Before creating enhancement suggestions, please check the existing issues as you might find that the enhancement has already been suggested. When you are creating an enhancement suggestion, please include as many details as possible by filling out the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).

### Your First Code Contribution

Unsure where to begin contributing to TaskFlow? You can start by looking through the `beginner` and `help-wanted` issues:

* [Beginner issues](https://github.com/kiaranhurley/TaskFlow/labels/beginner) - issues which should only require a few lines of code.
* [Help wanted issues](https://github.com/kiaranhurley/TaskFlow/labels/help%20wanted) - issues which should be a bit more involved than `beginner` issues.

### Pull Requests

Follow these steps for contributing code:

1. Fork the repository.
2. Create a new branch: `git checkout -b my-branch-name`.
3. Make your changes.
4. Run the tests: `pytest`.
5. Commit your changes: `git commit -m 'Add some feature'`.
6. Push to the branch: `git push origin my-branch-name`.
7. Submit a pull request.

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Python Styleguide

All Python code follows [PEP 8](https://www.python.org/dev/peps/pep-0008/). We use `flake8` for linting.

Some key points:
* Use 4 spaces per indentation level
* Use snake_case for variable and function names
* Use CamelCase for class names
* Use docstrings to document functions, classes, and modules

### HTML/CSS/JavaScript Styleguide

* Use 2 spaces per indentation level
* Use classes for styling, IDs for JavaScript hooks
* Prefer vanilla JavaScript over jQuery when possible

## Additional Notes

### Issue and Pull Request Labels

This project uses labels to help organize and prioritize work. Here's what they mean:

* `bug`: Something isn't working
* `documentation`: Improvements or additions to documentation
* `duplicate`: This issue or pull request already exists
* `enhancement`: New feature or request
* `good first issue`: Good for newcomers
* `help wanted`: Extra attention is needed
* `invalid`: This doesn't seem right
* `question`: Further information is requested
* `wontfix`: This will not be worked on

## Development Environment Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/kiaranhurley/TaskFlow.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Install development dependencies: `pip install -r requirements-dev.txt` (if available)

## Testing

When submitting a pull request, make sure to add or update tests as appropriate.

Run tests with:
```bash
pytest
```

Run tests with coverage report:
```bash
pytest --cov=app
```

## Documentation

When adding or modifying features, update the appropriate documentation, including:
* Docstrings
* README.md
* Comments for complex code sections

## Thank You!

Your contributions to open source, large or small, make projects like this possible. Thank you for taking the time to contribute.