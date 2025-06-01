# Contributing to Djelia Python SDK

Welcome to the Djelia Python SDK! We're thrilled you're interested in contributing to our mission of advancing AI for African languages like Bambara. Whether you're fixing bugs, adding features, or improving documentation, your contributions are valuable. This guide will help you get started with setting up the project, submitting issues, and creating pull requests. Let's make something awesome together! 🫂

## Table of Contents

1. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Setting Up the Development Environment](#setting-up-the-development-environment)
2. [How to Contribute](#how-to-contribute)
   - [Reporting Bugs](#reporting-bugs)
   - [Suggesting Features](#suggesting-features)
   - [Submitting Pull Requests](#submitting-pull-requests)
3. [Code Style and Quality](#code-style-and-quality)
4. [Testing](#testing)
5. [Community Guidelines](#community-guidelines)
6. [Versioning and Releases](#versioning-and-releases)


## Getting Started

### Prerequisites

To contribute, you'll need:
- **Python 3.7+**: Ensure you have a compatible Python version installed.
- **Git**: For cloning the repository and managing version control.
- **pip** or **uv**: For installing dependencies.
- A **Djelia API key**: Sign up at [djelia.cloud](https://djelia.cloud) to get one.
- A valid audio file (e.g., `audio.wav`) for testing transcription and TTS features.

### Setting Up the Development Environment

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/djelia/djelia-python-sdk.git
   cd djelia-python-sdk
   ```

2. **Install Dependencies**:
   Install the required dependencies for development:
   ```bash
   pip install -e . 
   pip install -r dev-requirements.txt
   ```
   Alternatively, use `uv` for faster dependency resolution:
   ```bash
   uv pip install -e . 
   uv pip install -r dev-requirements.txt
   ```

3. **Set Up Pre-Commit Hooks**:
   Install pre-commit to enforce code style:
   ```bash
   pre-commit install
   ```

4. **Configure Environment**:
   Create a `.env` file in the project root with your API key and test audio file path:
   ```bash
   echo "DJELIA_API_KEY=your_api_key_here" >> .env
   echo "TEST_AUDIO_FILE=/path/to/your/audio.wav" >> .env
   ```

5. **Run the Cookbook**:
   Verify your setup by running the test suite:
   ```bash
   python -m cookbook.main
   ```
   This executes the Djelia SDK Cookbook, testing translation, transcription, and TTS features.

## How to Contribute

### Reporting Bugs

Found a bug? Help us squash it! 
- Check the [issue tracker](https://github.com/djelia/djelia-python-sdk/issues) to ensure the bug hasn't been reported.
- Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) to submit a new issue.
- Include:
  - A clear description of the bug.
  - Steps to reproduce it.
  - Expected and actual behavior.
  - Logs or screenshots, if applicable.
- Tag `@sudoping01` in your issue for faster review.

### Suggesting Features

Have an idea to make the SDK even better? 
- Submit a feature request using the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).
- Describe the problem your feature solves and your proposed solution.
- Mention any alternatives you've considered.
- Tag `@sudoping01` to ensure visibility.

### Submitting Pull Requests

Ready to contribute code or documentation? Here's how:
1. **Fork the Repository**:
   Fork the [Djelia Python SDK repo](https://github.com/djelia/djelia-python-sdk) and clone your fork:
   ```bash
   git clone https://github.com/your-username/djelia-python-sdk.git
   ```

2. **Create a Branch**:
   Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**:
   - Follow the [code style guidelines](#code-style-and-quality).
   - Update or add tests in the `cookbook` module if your changes affect functionality.
   - Update `README.md` or other documentation if needed.

4. **Run Code Style Checks**:
   Ensure your code passes linting and formatting:
   ```bash
   ./fix-code.sh
   ```
   This runs `ruff`, `isort`, and optionally `black` (if enabled in `dev-requirements.txt`).

5. **Test Your Changes**:
   Run the cookbook to verify your changes:
   ```bash
   python -m cookbook.main
   ```
   Ensure all tests pass and no new errors are introduced.

6. **Commit Your Changes**:
   Use clear, concise commit messages:
   ```bash
   git commit -m "Add feature: your feature description"
   ```

7. **Push and Create a Pull Request**:
   Push your branch and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```
   - Use the pull request template and link to related issues.
   - Describe your changes, their purpose, and any testing done.
   - Tag `@sudoping01` for review.

8. **Address Feedback**:
   Respond to reviewer comments and make necessary updates. The GitHub Actions workflow (`code-check.yml`) will run `ruff` and `isort` to ensure code quality.

## Code Style and Quality

To maintain consistency, we use:
- **Ruff**: For linting and formatting. Run `ruff check .` to verify.
- **isort**: For sorting imports. Use `isort . --check-only` to check.
- **Pre-Commit Hooks**: Automatically run `ruff` and `isort` before commits.
- **Black** (optional): If enabled in `dev-requirements.txt`, run `black .` for formatting.

Before submitting a pull request:
- Run `./fix-code.sh` to apply fixes automatically.
- Ensure no linting errors remain with `ruff check .` and `isort . --check-only`.

## Testing

All contributions should include tests to ensure reliability:
- Use the `cookbook` module (`cookbook/cookbook.py`) as a reference for writing tests.
- Add new tests for new features or bug fixes in the `cookbook` directory.
- Verify tests pass with:
  ```bash
  python -m cookbook.main
  ```
- If adding new dependencies, update `setup.py` (under `extras_require["test"]`) and `dev-requirements.txt`.

## Community Guidelines
We value a welcoming and inclusive community. Please:
- Follow our [Code of Conduct](CODE_OF_CONDUCT.md).
- Be respectful and constructive in issues, pull requests, and discussions.
- Follow the [MIT License](LICENSE) terms.
- Reach out to `@sudoping01` for questions or guidance.


## Versioning and Releases
- We use [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH).
- Update the `version` field in `setup.py` when making changes:
  - Increment `MAJOR` for breaking changes.
  - Increment `MINOR` for new features.
  - Increment `PATCH` for bug fixes.
- To create a release:
  1. Update `setup.py` with the new version.
  2. Tag the release: `git tag vX.Y.Z && git push origin vX.Y.Z`.
  3. maintainers will handle PyPI publication (contact `@sudoping01`).

**Pro Tip**: Check out the [Djelia SDK Cookbook](README.md#explore-the-djelia-sdk-cookbook) for a comprehensive example of using the SDK. It's a great way to understand the codebase before contributing!

**Thank you for contributing to Djelia Python SDK! Your efforts help bring AI powered African language processing to the world. Let's keep the vibe awesome! ❤️ 🇲🇱**