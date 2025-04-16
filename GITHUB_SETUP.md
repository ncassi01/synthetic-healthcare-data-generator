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

## 6. Troubleshooting GitHub Authentication Issues

### "Invalid username or password" Error

If you encounter an error like this when pushing to GitHub:

```
remote: Invalid username or password.
fatal: Authentication failed for 'https://github.com/YOUR_USERNAME/synthetic-healthcare-data-generator.git'
```

Follow these troubleshooting steps:

### 1. Check Your GitHub Credentials

Verify that you're using the correct username and password:

```bash
# Check your configured GitHub username
git config user.name

# Check the remote URL to ensure it has your correct username
git remote -v
```

### 2. Use Personal Access Token Instead of Password

GitHub no longer supports password authentication for Git operations. You must use a Personal Access Token (PAT) instead:

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Generate new token
2. Select the necessary scopes (at minimum: `repo`, `workflow`, and `write:packages`)
3. Generate the token and copy it
4. Use this token instead of your password when prompted

### 3. Update Remote URL to Use PAT

You can embed your PAT in the remote URL:

```bash
# Remove the existing remote
git remote remove origin

# Add the remote with your PAT included
git remote add origin https://YOUR_USERNAME:YOUR_PERSONAL_ACCESS_TOKEN@github.com/YOUR_USERNAME/synthetic-healthcare-data-generator.git

# Verify the new remote URL
git remote -v
```

### 4. Use Git Credential Manager

If you're on Windows or macOS, you can use Git Credential Manager:

```bash
# Install Git Credential Manager (Windows)
git config --global credential.helper manager

# For macOS
git config --global credential.helper osxkeychain
```

### 5. Check for Two-Factor Authentication Issues

If you have 2FA enabled on GitHub:

1. You MUST use a personal access token instead of a password
2. Ensure your token has the correct permissions

### 6. Verify SSH Setup (Alternative Method)

If HTTPS authentication continues to fail, consider switching to SSH:

```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add your SSH key to the ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy your public key to clipboard (Windows)
clip < ~/.ssh/id_ed25519.pub

# For macOS
pbcopy < ~/.ssh/id_ed25519.pub

# For Linux
cat ~/.ssh/id_ed25519.pub
```

Then add the SSH key to your GitHub account (GitHub → Settings → SSH and GPG keys → New SSH key).

Finally, update your remote URL to use SSH:

```bash
# Remove the existing remote
git remote remove origin

# Add the remote with SSH URL
git remote add origin git@github.com:YOUR_USERNAME/synthetic-healthcare-data-generator.git

# Try pushing again
git push -u origin master
```

### 7. Common Error Messages and Solutions

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| `remote: Invalid username or password` | Using password instead of PAT | Use a personal access token |
| `remote: Support for password authentication was removed` | GitHub's password authentication deprecation | Use a personal access token |
| `fatal: Authentication failed` | Incorrect credentials | Verify username and use PAT |
| `remote: Permission to ... denied` | Insufficient permissions | Check repository access or PAT scopes |
| `error: failed to push some refs` | Local repository not in sync | Pull changes first with `git pull --rebase origin master` |

## Next Steps

- Set up branch protection rules if needed
- Add collaborators to your repository
- Configure GitHub Actions for CI/CD
- Set up issue templates and project boards

Your Synthetic Healthcare Data Generator project is now hosted on GitHub and ready for collaboration!