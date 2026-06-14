# GitHub Upload Guide

Run all commands from this folder:

```bash
cd github_repo
```

## Option A: Upload With Git Commands

1. Create an empty repository on GitHub.
2. Do not add a README or license on GitHub, because this folder already has project files.
3. Copy the repository URL, then run:

```bash
git init
git add .
git commit -m "Prepare final Task 2 project"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

Replace `<YOUR_GITHUB_REPO_URL>` with the HTTPS or SSH URL from GitHub.

## Option B: Upload With GitHub CLI

If `gh` is installed and logged in:

```bash
git init
git add .
git commit -m "Prepare final Task 2 project"
gh repo create <REPO_NAME> --private --source . --remote origin --push
```

Use `--public` instead of `--private` only if you want the repository to be public.

## After Uploading

- Paste the GitHub URL into `docs/final_slides.marp.md`.
- Confirm student IDs on the title slide.
- Export the final Marp slides to PDF again if you changed the slide source.
- Check GitHub's file list to make sure reference PDFs, local environments, and old temporary runs were not uploaded.
