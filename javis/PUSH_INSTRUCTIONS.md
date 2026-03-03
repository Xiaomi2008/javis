# Push Javis to GitHub - Instructions

## Current Status

✅ Local repository ready with initial commit
- Branch: `master`
- Remote: `origin` → https://github.com/Pizze/javis.git

## Option 1: Using Environment Variable (Recommended)

```bash
export GITHUB_TOKEN=ghp_your_token_here
cd /home/pizze/.openclaw/workspace/javis
git push -u origin master
```

### How to get a GitHub Token:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full control of private repositories)
4. Generate and copy the token
5. Run the export command above with your token

## Option 2: Using Git Credential Helper

```bash
# Configure git to use credential helper
git config --global credential.helper store

# Try pushing (you'll be prompted for username/password or token)
cd /home/pizze/.openclaw/workspace/javis
git push -u origin master

# When prompted:
# Username: Pizze
# Password/Token: [paste your GitHub personal access token]
```

## Option 3: Using SSH (Most Secure for Long-term)

### Step 1: Generate SSH Key (if you don't have one)
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
```

### Step 2: Add Public Key to GitHub
1. Go to https://github.com/settings/keys
2. Click "New SSH key"
3. Give it a title (e.g., "Raspberry Pi")
4. Paste your public key content
5. Click "Add SSH key"

### Step 3: Change Remote URL to SSH
```bash
cd /home/pizze/.openclaw/workspace/javis
git remote set-url origin git@github.com:Pizze/javis.git
git push -u origin master
```

## After Pushing

Once pushed, you can:
- View your repository at https://github.com/Pizze/javis
- Create issues and pull requests
- Set up CI/CD with GitHub Actions
- Enable GitHub Pages for documentation

---

**Need help?** Let me know which option you'd like to use!
