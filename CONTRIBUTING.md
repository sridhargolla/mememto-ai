# Contributing to Memento AI

Thank you for contributing to Memento AI! As a two-member team, we maintain structured development practices to ensure code quality, consistency, and clean version control.

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
4. Download the required GGUF and ONNX models and place them in the `backend/models/` directory.

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

---

## 2. Branch Naming Conventions

Always create a new branch for your work. Branches should be named using the following prefixes:

- `feature/` : For new features or enhancements (e.g., `feature/whisper-integration`)
- `bugfix/`  : For bug fixes (e.g., `bugfix/fix-pdf-coordinate-ocr`)
- `docs/`    : For documentation changes (e.g., `docs/update-architecture`)
- `refactor/`: For code refactoring without behavior changes (e.g., `refactor/sqlite-queries`)
- `chore/`   : For build changes, dependencies, or metadata (e.g., `chore/add-license`)

---

## 3. Commit Conventions

We follow the **Conventional Commits** specification. Commits should be structured as follows:

```
<type>(<scope>): <description>

[optional body]
```

### Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc.)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools and libraries

### Examples:
- `feat(ai): integrate llama.cpp with phi-3 gguf model`
- `fix(ocr): resolve null pointer exception when parsing empty images`
- `docs(spec): add hardware requirements table`

---

## 4. Pull Requests (PR) & Code Review

Even with a two-member team, all changes must pass through a pull request before being merged into the `main` branch.

1. **Create a Branch**: Commit your changes locally to a feature or bugfix branch.
2. **Push and Open a PR**: Push your branch to GitLab and open a Pull Request targeting the `main` branch.
3. **Self-Review**: Review your own diff to catch any leftover debug statements, formatting issues, or missing comments.
4. **Request Review**: Request a review from the other team member.
5. **Approval**: A PR requires at least one approval from the other member before it can be merged.
6. **Merge**: Once approved and all CI checks pass, merge the PR. Delete the source branch after merging.
