# Contributing to Memento AI

Thank you for contributing to Memento AI! We maintain structured development practices to ensure code quality, consistency, and clean version control.

---

## 1. Development Setup

### Backend Setup
1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install development dependencies:
   ```bash
   pip install black flake8 mypy bandit safety pre-commit
   ```
5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```
6. Download the required GGUF and ONNX models and place them in the `backend/models/` directory.

### Frontend Setup
1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install Node packages:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```

### Mobile Setup (Flutter)
1. Install Flutter SDK: https://flutter.dev/docs/get-started/install
2. Navigate to the `mobile/` directory:
   ```bash
   cd mobile
   ```
3. Install dependencies:
   ```bash
   flutter pub get
   ```
4. Run the app:
   ```bash
   flutter run
   ```

---

## 2. Code Quality Standards

### Python Code
- **Formatting**: Use `black` for code formatting
  ```bash
  black backend/
  ```
- **Linting**: Use `flake8` for linting
  ```bash
  flake8 backend/
  ```
- **Type Checking**: Use `mypy` for type checking
  ```bash
  mypy backend/
  ```
- **Security**: Use `bandit` for security scanning
  ```bash
  bandit -r backend/
  ```
- **Dependency Scanning**: Use `safety` to check for vulnerable dependencies
  ```bash
  safety check
  ```

### Frontend Code
- **Linting**: ESLint is configured for the frontend
  ```bash
  cd frontend
  npm run lint
  ```
- **Formatting**: Prettier is configured for code formatting
  ```bash
  npm run format
  ```

### Pre-commit Hooks
Pre-commit hooks are configured to automatically run quality checks before each commit:
- Python formatting with black
- Python linting with flake8
- Python type checking with mypy
- Security scanning with bandit
- Frontend linting with ESLint
- Trailing whitespace removal

To run pre-commit hooks manually:
```bash
pre-commit run --all-files
```

---

## 3. Branch Naming Conventions

Always create a new branch for your work. Branches should be named using the following prefixes:

- `feature/` : For new features or enhancements (e.g., `feature/whisper-integration`)
- `bugfix/`  : For bug fixes (e.g., `bugfix/fix-pdf-coordinate-ocr`)
- `docs/`    : For documentation changes (e.g., `docs/update-architecture`)
- `refactor/`: For code refactoring without behavior changes (e.g., `refactor/sqlite-queries`)
- `chore/`   : For build changes, dependencies, or metadata (e.g., `chore/add-license`)

---

## 4. Commit Conventions

We follow the **Conventional Commits** specification. Commits should be structured as follows:

```
<type>(<scope>): <description>

[optional body]
```

### Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools and libraries

### Examples:
- `feat(ai): integrate llama.cpp with phi-3 gguf model`
- `fix(ocr): resolve null pointer exception when parsing empty images`
- `docs(spec): add hardware requirements table`

---

## 5. Pull Requests (PR) & Code Review

All changes must pass through a pull request before being merged into the `main` branch.

1. **Create a Branch**: Commit your changes locally to a feature or bugfix branch.
2. **Push and Open a PR**: Push your branch to GitLab and open a Pull Request targeting the `main` branch.
3. **Self-Review**: Review your own diff to catch any leftover debug statements, formatting issues, or missing comments.
4. **Request Review**: Request a review from the other team member.
5. **Approval**: A PR requires at least one approval from the other member before it can be merged.
6. **Merge**: Once approved and all CI checks pass, merge the PR. Delete the source branch after merging.

---

## 6. Continuous Integration

The GitLab CI pipeline automatically runs the following checks on every commit and merge request:

### Python Checks
- **Black**: Code formatting check
- **Flake8**: Linting check
- **Mypy**: Type checking
- **Bandit**: Security vulnerability scanning
- **Safety**: Dependency vulnerability scanning

### Frontend Checks
- **ESLint**: JavaScript/React linting
- **Build**: Frontend build verification

### Tests
- **Python Tests**: Backend unit tests
- **Frontend Tests**: Frontend unit tests

All checks must pass before a merge request can be merged.

---

## 7. Testing

### Backend Tests
Run backend tests:
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
Run frontend tests:
```bash
cd frontend
npm test
```

---

## 8. Security Guidelines

- Never commit API keys, passwords, or sensitive data
- Use environment variables for configuration
- Run security scans before committing
- Report security vulnerabilities privately
- Follow the principle of least privilege

---

## 9. Getting Help

If you need help:
1. Check the existing documentation in the `docs/` directory
2. Review the README.md for project overview
3. Open an issue on GitLab for bugs or feature requests
4. Contact the team directly for urgent matters

---

## 10. License

By contributing to Memento AI, you agree that your contributions will be licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
