#!/bin/bash
# Script to set up branch protection for main branch
# This uses GitHub CLI (gh) to configure protection rules

echo "🔒 Setting up branch protection for main branch..."

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed. Please install it first:"
    echo "   brew install gh  (macOS)"
    echo "   https://cli.github.com/ (other platforms)"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub. Please run: gh auth login"
    exit 1
fi

REPO="Py-Forge-Cli/PyForge-CLI"
BRANCH="main"

echo "📋 Configuring protection rules for $REPO branch: $BRANCH"

# Create branch protection rule
# Note: gh doesn't have full branch protection API support yet, 
# so we'll use the API directly

cat << 'EOF' > branch-protection.json
{
  "required_status_checks": {
    "strict": true,
    "contexts": []
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "require_last_push_approval": false,
    "dismissal_restrictions": {},
    "bypass_pull_request_allowances": {
      "users": ["sdandey"],
      "teams": [],
      "apps": []
    }
  },
  "restrictions": {
    "users": ["sdandey"],
    "teams": [],
    "apps": []
  },
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": true
}
EOF

# Apply branch protection using GitHub API
echo "🚀 Applying branch protection rules..."
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/$REPO/branches/$BRANCH/protection \
  --input branch-protection.json

if [ $? -eq 0 ]; then
    echo "✅ Branch protection successfully applied!"
    echo ""
    echo "📊 Summary of protection rules:"
    echo "   - Pull requests required for all changes"
    echo "   - No approval required for @sdandey (can self-merge)"
    echo "   - Other contributors cannot merge their own PRs"
    echo "   - Only @sdandey can push/merge to main"
    echo "   - Force pushes and deletions prevented"
    echo "   - Conversation resolution required"
else
    echo "❌ Failed to apply branch protection"
    echo ""
    echo "🔧 Please configure manually at:"
    echo "   https://github.com/$REPO/settings/branches"
fi

# Clean up
rm -f branch-protection.json

echo ""
echo "📝 Next steps:"
echo "1. Verify settings at: https://github.com/$REPO/settings/branches"
echo "2. Test by trying to push directly to main (should fail for non-admins)"
echo "3. Test PR workflow to ensure it works correctly"