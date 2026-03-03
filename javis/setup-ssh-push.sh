#!/bin/bash
# Complete setup for pushing to GitHub via SSH

echo "🔑 SSH Key Setup for Javis Repository"
echo "======================================"
echo ""

# Step 1: Show the public key
echo "✅ Your SSH public key:"
cat ~/.ssh/id_ed25519.pub
echo ""

# Step 2: Instructions to add to GitHub
echo "📋 Next steps:"
echo "   1. Copy the SSH key above"
echo "   2. Go to https://github.com/settings/keys"
echo "   3. Click 'New SSH key'"
echo "   4. Title: 'Raspberry Pi (Javis)'"
echo "   5. Paste the key and click 'Add SSH key'"
echo ""

# Step 3: Test connection
echo "🔍 Testing GitHub SSH connection..."
ssh -T git@github.com 2>&1 | grep -E "(successfully authenticated|welcome)" && echo "✅ SSH connection works!" || echo "⚠️  You need to add your SSH key to GitHub first"
