#!/bin/bash
# Test script to verify branch protection is working correctly

echo "🧪 Testing branch protection for main branch..."
echo ""

# Save current branch
CURRENT_BRANCH=$(git branch --show-current)

# Test 1: Check if we can fetch protection status
echo "1️⃣ Checking branch protection status..."
gh api \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/Py-Forge-Cli/PyForge-CLI/branches/main/protection \
  --jq '{
    require_pr: .required_pull_request_reviews.required_approving_review_count,
    dismiss_stale: .required_pull_request_reviews.dismiss_stale_reviews,
    require_codeowners: .required_pull_request_reviews.require_code_owner_reviews,
    enforce_admins: .enforce_admins,
    restrictions: .restrictions.users
  }' 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Branch protection is enabled"
else
    echo "❌ Branch protection is not enabled or not accessible"
fi

echo ""
echo "2️⃣ Testing direct push to main (should fail for non-admins)..."
echo ""

# Create a test branch
git checkout -b test-protection-check 2>/dev/null

# Create an empty commit
git commit --allow-empty -m "Test: Checking branch protection" 2>/dev/null

# Try to push to main (this should fail)
echo "Attempting to push test commit to main..."
git push origin test-protection-check:main 2>&1 | grep -E "(protected|prohibited|denied|failed)"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "✅ Direct push to main was correctly blocked"
else
    echo "⚠️  Direct push might be allowed - verify your permissions"
fi

# Clean up
git checkout $CURRENT_BRANCH 2>/dev/null
git branch -D test-protection-check 2>/dev/null

echo ""
echo "3️⃣ Checking CODEOWNERS file..."
if [ -f .github/CODEOWNERS ]; then
    echo "✅ CODEOWNERS file exists"
    echo "   Required reviewers:"
    grep "^\*" .github/CODEOWNERS | head -5
else
    echo "❌ CODEOWNERS file not found"
fi

echo ""
echo "📊 Protection Summary:"
echo "   - Only @sdandey can push directly to main"
echo "   - All others must create PRs"
echo "   - PRs require approval from @sdandey (via CODEOWNERS)"
echo ""
echo "🔗 View full settings at:"
echo "   https://github.com/Py-Forge-Cli/PyForge-CLI/settings/branches"