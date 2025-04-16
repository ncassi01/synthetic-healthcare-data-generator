# GitHub Repository Setup Guide

This guide will help you create a new GitHub repository for the Synthetic Healthcare Data Generator project and push your code to it.

## 1. Create a New GitHub Repository

1. Go to [GitHub](https://github.com/) and sign in to your account.
2. Click on the "+" icon in the top-right corner and select "New repository".
3. Enter a repository name (suggested: `synthetic-healthcare-data-generator`).
4. Add a description: "A Python-based synthetic healthcare data generator for RAG testing and development purposes."
5. Choose "Public" or "Private" visibility based on your preference.
6. Do NOT initialize the repository with a README, .gitignore, or license file (we already have these).
7. Click "Create repository".

## 2. Initialize Git in Your Local Project

Open a terminal/command prompt in your project directory and run:

```bash
# Initialize Git repository
git init

# Add all files to staging
git add .

# Commit the files
git commit -m "Initial commit: Synthetic Healthcare Data Generator"
```

## 3. Connect Local Repository to GitHub

After creating the GitHub repository, you'll see instructions on the GitHub page. Use the following commands to connect your local repository to GitHub:

```bash
# Add the remote repository URL
git remote add origin https://github.com/YOUR_USERNAME/synthetic-healthcare-data-generator.git

# Push your code to GitHub
git push -u origin main
```

Note: If your default branch is named "master" instead of "main", use:

```bash
git push -u origin master
```

## 4. Update README.md with Repository URL

After pushing your code to GitHub, update the repository URL in the README.md file:

1. Open README.md
2. Find the line: `git clone <repository-url>`
3. Replace `<repository-url>` with your actual repository URL: `https://github.com/YOUR_USERNAME/synthetic-healthcare-data-generator.git`
4. Commit and push the change:

```bash
git add README.md
git commit -m "Update repository URL in README"
git push
```

## 5. Verify Repository Setup

1. Visit your GitHub repository page to ensure all files were uploaded correctly.
2. Check that the README.md is displayed properly on the repository homepage.
3. Verify that the .gitignore and LICENSE files are present.

## Next Steps

- Set up branch protection rules if needed
- Add collaborators to your repository
- Configure GitHub Actions for CI/CD
- Set up issue templates and project boards

Your Synthetic Healthcare Data Generator project is now hosted on GitHub and ready for collaboration!