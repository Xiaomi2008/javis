# 🔑 SSH Setup for Javis GitHub Push

## ✅ Completed Steps

1. **Generated SSH key**: `~/.ssh/id_ed25519`
   - Type: ED25519 (modern, secure)
   - Fingerprint: `SHA256:Nlpb9cfap6B9AxCoAWzZxg1KhwjkhNhIT1YePQBsPPY`

2. **Configured remote**: Changed to SSH URL
   ```bash
   git@github.com:Pizze/javis.git
   ```

## 📋 What You Need to Do

### Step 1: Copy Your Public Key
```bash
cat ~/.ssh/id_ed25519.pub
```

**Your key:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGQSqABUQlJRjyjKqJ4jCVdJCDERNb+JELRYodwtrEN2 pizze@raspberrypi
```

### Step 2: Add to GitHub
1. Go to https://github.com/settings/keys
2. Click **"New SSH key"**
3. Title: `Raspberry Pi (Javis)`
4. Paste the key above
5. Click **"Add SSH key"**

### Step 3: Verify Connection
```bash
ssh -T git@github.com
```

You should see:
```
Hi Pizze! You've successfully authenticated, but GitHub does not provide shell access.
```

### Step 4: Push Your Code
```bash
cd /home/pizze/.openclaw/workspace/javis
git push -u origin master
```

## 🎉 After Pushing

Your repository will be available at:
**https://github.com/Pizze/javis**

## 🔧 Troubleshooting

### If SSH connection fails:
```bash
# Test connection
ssh -T git@github.com

# Check key permissions (should be 600 for private, 644 for public)
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# Add to SSH agent (if using passphrase)
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### If you get "Permission denied":
- Make sure you added the key to GitHub
- Check that the public key matches what's in your `~/.ssh/id_ed25519.pub` file
- Try: `ssh -v git@github.com` for verbose output

---

**Ready?** Add your SSH key to GitHub, then run `git push -u origin master`! 🚀
