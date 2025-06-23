# Branch Protection Rules for Main Branch

## Required Settings for `main` branch

### ✅ Protection Rules to Enable:

1. **Require a pull request before merging**
   - ✅ Required approving reviews: 1
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require review from CODEOWNERS
   - ❌ Restrict reviews (leave unchecked to allow any collaborator to review)
   - ✅ Require approval of the most recent reviewable push

2. **Require status checks to pass before merging**
   - ✅ Require branches to be up to date before merging
   - Add these status checks (if available):
     - `CI / Test`
     - `CI / Lint`
     - `build`

3. **Require conversation resolution before merging**
   - ✅ Enable this setting

4. **Require signed commits** (Optional but recommended)
   - ⚠️ Enable only if all contributors use commit signing

5. **Include administrators**
   - ❌ Do NOT check this - allows @sdandey to push directly when needed

6. **Restrict who can push to matching branches**
   - ✅ Enable this setting
   - Add users/teams who can push:
     - @sdandey (repository owner)
   - Leave empty to prevent all direct pushes (even from admins)

7. **Rules for force pushes and deletions**
   - ✅ Allow force pushes - Everyone
   - ❌ Specify who can force push: @sdandey only
   - ✅ Allow deletions
   - ❌ Restrict deletions to: @sdandey only

## 🔧 How to Apply These Settings:

1. Go to: https://github.com/Py-Forge-Cli/PyForge-CLI/settings/branches
2. Click "Add rule" or edit existing rule for `main`
3. Apply settings as listed above
4. Click "Create" or "Save changes"

## 🚨 Important Notes:

- By NOT checking "Include administrators", @sdandey can bypass PR requirements in emergencies
- All other contributors MUST create PRs to merge into main
- The CODEOWNERS file ensures @sdandey must review all changes
- Contributors with write access can still create branches and PRs

## 📊 Resulting Workflow:

1. **For @sdandey**:
   - Can push directly to main (emergency use only)
   - Can merge PRs without additional approval
   - Must review all PRs due to CODEOWNERS

2. **For Other Contributors**:
   - Cannot push directly to main
   - Must create PR for all changes
   - PR requires review from @sdandey
   - Can review PRs but cannot merge without @sdandey approval