# Contributing to Breedbase-Client

Thanks for your interest in contributing! This project is an MCP server that gives LLMs access to BrAPI v2 plant breeding databases. We welcome contributions from breeders, researchers, students, and software engineers.

Please read this guide before opening an issue or pull request.

## Code of Conduct

Be respectful and constructive in all issues, discussions, and code reviews. We want this to be a welcoming project for people from both the plant science and software communities.

## Ways to Contribute

- **Report a bug.** Open an issue with steps to reproduce, the BrAPI server you were using (`BASE_URL`), your MCP client (Claude Desktop, VS Code, etc.), and any relevant log output.
- **Report a server compatibility problem.** BrAPI implementations vary. If a tool misbehaves against a specific server, tell us which server and which endpoint.
- **Suggest a feature.** Open an issue *before* starting significant work, so we can agree on the approach and you don't spend time on something we can't merge.
- **Improve documentation.** Fix errors, clarify setup steps, or add workflow examples to `Examples/`.
- **Contribute code.** Bug fixes, new tools, and improvements via pull request.

Issues labeled `good first issue` are a good place to start.

## Development Setup

You need [uv](https://docs.astral.sh/uv/) and Python 3.11+.

```bash
# Fork the repo on GitHub, then clone your fork
git clone https://github.com/<YOUR-USERNAME>/Breedbase-Client.git
cd Breedbase-Client

# Add the main repo as "upstream"
git remote add upstream https://github.com/Plant-Phenomics-Lab/Breedbase-Client.git

# Install dependencies, including dev tools (pytest, ruff)
uv sync

# Configure your environment
cp .env.example .env
```

For local development, point `BASE_URL` at a public BrAPI server (the default is SweetPotatoBase) and leave `AUTH_TYPE` and the credentials blank unless your change involves authentication. See [Examples/CONFIGURATION.md](Examples/CONFIGURATION.md) for all options.

Run the server:

```bash
uv run src/main.py
```

### Project layout

- `src/` — the main MCP server (`src/main.py`). Tools live in `src/mcp_server/tools/`, and each module exposes a `register_*_tools(...)` function.
- `src/psa/` — a separate, simplified server for the Parental Selection Agent.
- `tests/` — pytest suite.
- `Examples/` — user-facing documentation and workflow examples.

## Code Style

We use [ruff](https://docs.astral.sh/ruff/) for formatting and linting. Settings are in `pyproject.toml`: **2-space indentation**, single quotes, 120-character lines. Please don't reformat code outside the lines you're changing.

Before pushing, run:

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
```

CI runs the same three checks on every pull request.

- Use type hints on new functions.
- Add docstrings to new tools. **The tool's docstring is what the LLM reads** to decide when and how to call it, so make it clear and specific.
- Keep tool output compact. Large results should go through the session cache and download links, not straight into the LLM's context.

## Testing

```bash
uv run pytest
```

The tests build the real server, which queries the BrAPI server at `BASE_URL`, so they need network access. If you add or rename a tool, update `EXPECTED_TOOLS` in `tests/test_server.py`. Add tests for new behavior where you can.

Please be considerate of the public BrAPI servers. These are community resources, so don't write tests or scripts that make large numbers of requests or download whole databases.

## Pull Request Workflow

1. **Create a branch** from an up-to-date `main`. Use a descriptive name:

   ```bash
   git fetch upstream
   git switch -c fix/pagination-off-by-one upstream/main
   ```

   Prefixes: `feature/`, `fix/`, `docs/`, `refactor/`.

2. **Make your changes** in small, focused commits with clear messages, for example `Fix pagination when totalCount is missing`.

3. **Stage files deliberately.** Avoid `git add .`. Never commit:
   - `.env` or any credentials, tokens, or passwords
   - `cache/`, `Downloads/`, `logs/`, or other data the server produces
   - Data downloaded from breeding databases. It may not be yours to redistribute.

4. **Keep your branch up to date** with `main` before opening the PR:

   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

5. **Push to your fork** and open a pull request against `Plant-Phenomics-Lab/Breedbase-Client`, base branch `main`:

   ```bash
   git push -u origin fix/pagination-off-by-one
   ```

6. **Fill in the PR template.** Describe what changed and why, link the issue (`Closes #12`), and tell us how you tested it, including which BrAPI server you tested against.

> **Getting credit:** make sure your `git config user.email` matches a verified email on your GitHub account, so your commits are attributed to your profile.

## Review Process

- A maintainer will review your PR. We may ask for changes. Push them to the same branch and the PR updates automatically.
- For first-time contributors, a maintainer has to approve the CI run before it starts. This is a GitHub security default, not a reflection on your PR.
- PRs are merged with **Squash and Merge**, so your PR becomes a single commit on `main` that is attributed to you. Don't worry about tidying your commit history.

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE.txt).

## Questions?

Open an issue with the `question` label.
