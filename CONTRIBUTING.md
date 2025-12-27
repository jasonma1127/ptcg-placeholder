# Contributing Guide

Thank you for your interest in this project! This guide will help you understand how to set up your development environment, run tests, and release new versions.

## Table of Contents

- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [Release Process](#release-process)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [CI/CD Explanation](#cicd-explanation)
- [FAQ](#faq)

## Development Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

### Installation Steps

1. Clone the repository
```bash
git clone <repository-url>
cd ptcg-placeholder
```

2. Install uv (if not already installed)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. Install project dependencies
```bash
uv sync
```

This will automatically create a virtual environment and install all necessary dependencies (including dev dependencies).

## Running Tests

### Run all tests

```bash
uv run pytest tests/ -v
```

### Run specific test files

```bash
# Test card designer only
uv run pytest tests/test_card_designer.py -v

# Test PDF generator only
uv run pytest tests/test_pdf_generator.py -v

# Test utility functions only
uv run pytest tests/test_utils.py -v
```

### Test coverage

```bash
uv run pytest tests/ --cov=src --cov-report=html
```

Coverage report will be generated in the `htmlcov/` directory.

### Testing workflow when developing new features

1. Write tests first (TDD approach, optional)
2. Implement the feature
3. Run tests to ensure all tests pass
```bash
uv run pytest tests/ -v
```
4. Verify no existing functionality is broken

## Release Process

### Automated Release (Recommended)

The project uses GitHub Actions for automated build and release workflow.

#### Steps

1. **Update version number**

Edit `pyproject.toml`:
```toml
[project]
version = "1.2.0"  # Update version number
```

2. **Commit changes**

```bash
git add pyproject.toml
git commit -m "Bump version to 1.2.0"
git push
```

3. **Create and push Git tag**

```bash
# Create tag (must prefix with 'v')
git tag v1.2.0

# Push tag to GitHub
git push origin v1.2.0
```

4. **Automated workflow**

After pushing the tag, GitHub Actions will automatically:
- ✅ Run all tests
- 🏗️ Build executables for three platforms (Windows, macOS, Linux)
- 📦 Create a GitHub Release
- ⬆️ Upload executables to the Release

You can monitor the build progress on the GitHub Actions page.

### Manual Trigger (Optional)

To manually trigger a build without creating a release:

1. Go to your GitHub project page
2. Click the "Actions" tab
3. Select "Build and Release Executables"
4. Click "Run workflow"

### Version Numbering Rules

We follow [Semantic Versioning](https://semver.org/):

- `MAJOR.MINOR.PATCH` (e.g., `1.2.0`)
  - **MAJOR**: Incompatible API changes
  - **MINOR**: Backwards-compatible functionality additions
  - **PATCH**: Backwards-compatible bug fixes

Examples:
- `1.0.0` → `1.0.1`: Bug fix
- `1.0.1` → `1.1.0`: New feature
- `1.1.0` → `2.0.0`: Breaking change

## Project Structure

```
ptcg-placeholder/
├── src/                    # Source code
│   ├── card/              # Card design related
│   │   └── card_designer.py
│   ├── pdf/               # PDF generation related
│   │   ├── pdf_generator.py
│   │   └── page_layout.py
│   ├── api/               # PokeAPI integration
│   ├── utils/             # Utility functions
│   └── models.py          # Data models
├── tests/                 # Test files
│   ├── test_card_designer.py
│   ├── test_pdf_generator.py
│   └── test_utils.py
├── .github/
│   └── workflows/         # CI/CD workflows
│       ├── test.yml       # Testing workflow
│       └── build-release.yml  # Build and release workflow
├── config/                # Configuration files
├── main.py               # Entry point
└── pyproject.toml        # Project configuration and dependencies
```

## Development Workflow

### Adding a new feature

1. Create a new branch
```bash
git checkout -b feature/your-feature-name
```

2. Develop the feature and write tests

3. Run tests to ensure they pass
```bash
uv run pytest tests/ -v
```

4. Commit changes
```bash
git add .
git commit -m "Add: your feature description"
```

5. Push and create a Pull Request
```bash
git push origin feature/your-feature-name
```

### Fixing a bug

1. Create a new branch
```bash
git checkout -b fix/bug-description
```

2. Write a test to reproduce the bug (if possible)

3. Fix the bug

4. Verify tests pass
```bash
uv run pytest tests/ -v
```

5. Commit and create a Pull Request

## CI/CD Explanation

### Test Workflow (`.github/workflows/test.yml`)

- **Trigger**: Every push to `master`/`main` branch, or Pull Request creation
- **Runs**: All tests in Ubuntu environment
- **Purpose**: Ensure code quality and prevent regressions

### Build and Release Workflow (`.github/workflows/build-release.yml`)

- **Trigger**: Pushing a tag with `v*` format (e.g., `v1.2.0`)
- **Workflow**:
  1. **Test Job**: Run all tests
  2. **Build Job**: Build executables on three platforms (only runs if tests pass)
  3. **Release Job**: Create GitHub Release and upload executables
- **Build Platforms**:
  - Windows (`.exe`)
  - macOS ARM (Apple Silicon)
  - Linux

## FAQ

### Q: What should I do if tests fail?

Check the error message, which usually indicates which test failed and why. You can run the failing test individually for debugging:

```bash
uv run pytest tests/test_card_designer.py::test_create_card_basic -v
```

### Q: How do I build the executable locally?

```bash
# Install PyInstaller
pip install pyinstaller

# Build
pyinstaller --onefile --name pokemon-card-generator main.py

# The executable will be in the dist/ directory
```

### Q: Do I need to manually update the GitHub Release notes?

No, release notes are automatically generated based on the template in `.github/workflows/build-release.yml`. If you need to modify them, edit the `body` section in that file.

### Q: How do I add a new dependency?

```bash
# Add a runtime dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name
```

This will automatically update `pyproject.toml` and `uv.lock`.

## Need Help?

- Open an [Issue](../../issues) to report bugs or suggest features
- Check existing [Pull Requests](../../pulls)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
