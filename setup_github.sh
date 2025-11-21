#!/bin/bash

echo "🚀 Setting up Git repository and preparing for GitHub..."

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git repository already initialized"
fi

# Add all files
echo "📝 Adding files to Git..."
git add .

# Check if there are changes to commit
if git diff --cached --quiet && git diff --quiet; then
    echo "ℹ️  No changes to commit. Repository is up to date."
else
    # Create commit
    echo "💾 Creating commit..."
    git commit -m "Prepare project for GitHub and Vercel deployment

- Add comprehensive .gitignore
- Add .env.example files
- Update requirements.txt with all dependencies
- Add Vercel configuration files
- Update README.md with full documentation
- Add DEPLOYMENT.md guide
- Update main.py with Mangum handler for serverless
- Add frontend configuration files"
    
    echo "✅ Changes committed"
fi

# Check if remote exists
if git remote | grep -q "^origin$"; then
    echo "✅ Remote 'origin' already exists"
    REMOTE_URL=$(git remote get-url origin)
    echo "📍 Current remote: $REMOTE_URL"
    
    # Ask if user wants to update
    read -p "Do you want to push to existing remote? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Pushing to GitHub..."
        git branch -M main
        git push -u origin main
        echo "✅ Code pushed to GitHub successfully!"
        echo "🌐 Repository: $REMOTE_URL"
    else
        echo "ℹ️  Skipping push. Run 'git push -u origin main' manually when ready."
    fi
else
    # Prompt for GitHub repo URL
    echo ""
    echo "📝 No remote repository found."
    echo "Please provide your GitHub repository URL:"
    echo "Example: https://github.com/username/ppt-agent.git"
    read -p "Repository URL: " REPO_URL
    
    if [ -n "$REPO_URL" ]; then
        # Add remote
        echo "🔗 Adding remote repository..."
        git remote add origin "$REPO_URL"
        
        # Push to GitHub
        echo "📤 Pushing to GitHub..."
        git branch -M main
        git push -u origin main
        
        echo "✅ Code pushed to GitHub successfully!"
        echo "🌐 Repository: $REPO_URL"
    else
        echo "ℹ️  No URL provided. To add remote later, run:"
        echo "   git remote add origin <your-repo-url>"
        echo "   git branch -M main"
        echo "   git push -u origin main"
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "✅ Git setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Verify all files are committed"
echo "   2. Push to GitHub if not done automatically"
echo "   3. Set up environment variables in Vercel"
echo "   4. Deploy backend: vercel --prod"
echo "   5. Deploy frontend: cd ppt-agent-frontend && vercel --prod"
echo ""
echo "📖 See DEPLOYMENT.md for detailed deployment instructions"
echo "═══════════════════════════════════════════════════"

