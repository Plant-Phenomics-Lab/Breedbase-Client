# Contributing to Breedbase-Client

Thanks for helping out! This project lets AI assistants (like Claude) search and download data from plant breeding databases that use BrAPI. You don't need to be a professional developer to contribute. If you get stuck at any step, open an issue and ask. That's what it's for.

Please be kind and respectful in issues and code reviews. Everyone here is learning.

## Ways to help

- **Found a bug?** [Open an issue](https://github.com/Plant-Phenomics-Lab/Breedbase-Client/issues/new/choose) and tell us what you did, what you expected, and what happened.
- **Have an idea?** Open an issue to talk about it *before* you write a lot of code. We can help you plan it.
- **Fix the docs.** Typos, confusing instructions, and new examples in `Examples/` are all great first contributions.
- **Write code.** Look for issues labeled `good first issue`.

## One-time setup

You need [git](https://git-scm.com/downloads), a GitHub account, and [uv](https://docs.astral.sh/uv/getting-started/installation/), the tool we use to install Python and the project's packages.

1. **Fork the repo.** Click **Fork** at the top of the [project page](https://github.com/Plant-Phenomics-Lab/Breedbase-Client). This makes your own copy on GitHub that you're free to change.

2. **Download your fork** to your computer:

   ```bash
   git clone https://github.com/<YOUR-USERNAME>/Breedbase-Client.git
   cd Breedbase-Client
   ```

3. **Install everything:**

   ```bash
   uv sync
   ```

4. **Create your settings file:**

   ```bash
   cp .env.example .env
   ```

   The defaults connect to SweetPotatoBase, which is public, so you don't need a username or password to get started. Leave the login lines blank.

5. **Check that it works:**

   ```bash
   uv run pytest
   ```

   You should see `1 passed`. The test connects to SweetPotatoBase, so you need to be online.

## Making a change

1. **Get the latest code.** On your fork's GitHub page, click **Sync fork**, then download the changes:

   ```bash
   git switch main
   git pull
   ```

2. **Make a branch** for your change. A branch keeps your work separate, so you can work on more than one thing at a time. Give it a short name that describes the change:

   ```bash
   git switch -c fix-download-typo
   ```

3. **Make your changes.** Test them by running the server (`uv run src/main.py`) or the tests (`uv run pytest`).

4. **Tidy up the code** before you save it to git:

   ```bash
   uv run ruff format .
   uv run ruff check .
   ```

   `ruff format` automatically fixes spacing and quotes to match the project's style. `ruff check` points out likely mistakes, such as unused imports.

5. **Commit your changes.** A commit is a saved snapshot of your work with a short message. Add the files you changed by name:

   ```bash
   git status                       # see which files you changed
   git add src/the_file_you_changed.py
   git commit -m "Fix typo in download instructions"
   ```

   ⚠️ **Never commit your `.env` file.** It can contain your password. Also don't commit the `cache/`, `Downloads/`, or `logs/` folders. Avoid `git add .`, because it adds everything, including files you didn't mean to share.

6. **Upload your branch** to your fork:

   ```bash
   git push -u origin fix-download-typo
   ```

7. **Open a pull request.** A pull request ("PR") asks us to add your changes to the main project. Go to your fork on GitHub, click **Compare & pull request**, and fill in the short form. Explain what you changed and how you tested it.

## What happens next

- Automatic checks run on your PR: formatting, lint, and tests. The first time you contribute, a maintainer has to click a button before they start, so don't worry if they look stuck.
- A maintainer will review your code and might ask for changes. Make them on the same branch, then `git commit` and `git push` again. Your PR updates automatically.
- When it's approved, we'll merge it, and your name will appear in the project's contributors. Messy commit history is fine. We combine your commits into one when we merge.

**Tip:** for your commits to count on your GitHub profile, the email in `git config user.email` must match an email on your GitHub account.

## Tips for writing code here

- The code you'll most likely touch is in `src/mcp_server/tools/`. These are the "tools" the AI can call.
- **The docstring of a tool is what the AI reads** to decide when to use it, so write it clearly.
- If you add or rename a tool, update the `EXPECTED_TOOLS` list in `tests/test_server.py`.
- The databases we connect to are shared community resources. Don't write code or tests that send huge numbers of requests.

## License

Your contributions will be shared under the project's [MIT License](LICENSE.txt).
