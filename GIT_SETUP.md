# Git Setup & GitHub Deployment Guide

This guide will help you commit and push the Local Buyer Intelligence Platform to GitHub.

## Step 1: Initialize Git Repository (if not already initialized)

```bash
cd local-buyer-intelligence
git init
```

## Step 2: Create a .gitignore file

The `.gitignore` file is already created and includes:
- Python virtual environments
- Node modules
- Environment variables (.env files)
- Database files
- IDE files
- Build artifacts

**Important**: Make sure your `.env` files are NOT committed (they're already in .gitignore).

## Step 3: Add all files to staging

```bash
git add .
```

## Step 4: Create initial commit

```bash
git commit -m "Initial commit: Local Buyer Intelligence Platform foundation

- FastAPI backend with database models and API endpoints
- Next.js frontend with Mapbox integration
- Intelligence engine for demand scoring
- Data collector templates (Census, Property, Events)
- Docker Compose setup for local development
- Comprehensive documentation"
```

## Step 5: Create GitHub Repository

### Option A: Using GitHub CLI (if installed)

```bash
gh repo create local-buyer-intelligence --public --source=. --remote=origin --push
```

### Option B: Using GitHub Website

1. Go to https://github.com/new
2. Repository name: `local-buyer-intelligence` (or your preferred name)
3. Choose Public or Private
4. **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click "Create repository"

## Step 6: Connect local repository to GitHub

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/local-buyer-intelligence.git

# Or if using SSH:
# git remote add origin git@github.com:YOUR_USERNAME/local-buyer-intelligence.git
```

## Step 7: Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

## Alternative: All-in-One Commands

If you prefer to do it all at once (after creating the repo on GitHub):

```bash
cd local-buyer-intelligence
git init
git add .
git commit -m "Initial commit: Local Buyer Intelligence Platform"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/local-buyer-intelligence.git
git push -u origin main
```

## Verify Your Push

1. Visit your GitHub repository: `https://github.com/YOUR_USERNAME/local-buyer-intelligence`
2. Verify all files are present
3. Check that `.env` files are NOT in the repository (they should be ignored)

## Important Notes

### ⚠️ Security Checklist

Before pushing, ensure:

- [x] `.env` files are in `.gitignore` (✅ already done)
- [x] No API keys or secrets are hardcoded in the code
- [x] Database credentials are only in `.env` files (not committed)
- [x] Mapbox tokens should be in environment variables only

### 📝 Recommended GitHub Repository Settings

1. **Description**: "Data-driven local demand intelligence platform without PII scraping"
2. **Topics/Keywords**: Add tags like: `local-business`, `intelligence-platform`, `fastapi`, `nextjs`, `geographic-data`
3. **Visibility**: Choose Public (open source) or Private based on your preference

### 📄 License (Optional)

If you want to add a license:

```bash
# Create LICENSE file (choose appropriate license)
# Example: MIT License
# Visit https://choosealicense.com/ for options
```

### 🔄 Future Commits

For future changes:

```bash
git add .
git commit -m "Description of your changes"
git push
```

## Troubleshooting

### Authentication Issues

If you get authentication errors:

1. **Use GitHub CLI**: `gh auth login`
2. **Use Personal Access Token**: 
   - Settings → Developer settings → Personal access tokens → Generate new token
   - Use token as password when pushing
3. **Use SSH**: Set up SSH keys for GitHub

### Large Files

If you have large files (databases, etc.), they're already in `.gitignore`. If you need to track large files:

1. Use Git LFS: `git lfs install`
2. Track large file types: `git lfs track "*.db"`

### Merge Conflicts

If you get merge conflicts:
```bash
git pull origin main
# Resolve conflicts
git add .
git commit -m "Resolve merge conflicts"
git push
```

## Next Steps After Pushing

1. **Set up GitHub Actions** (optional): For CI/CD
2. **Add repository badges**: For README.md (build status, etc.)
3. **Create issues**: For tracking features and bugs
4. **Set up branch protection**: For main branch (Settings → Branches)
5. **Add collaborators**: Settings → Collaborators

## Quick Reference

```bash
# Check status
git status

# View what will be committed
git diff --cached

# Unstage files (if needed)
git reset HEAD <file>

# View commit history
git log

# Create new branch
git checkout -b feature/new-feature

# Push branch
git push -u origin feature/new-feature
```






