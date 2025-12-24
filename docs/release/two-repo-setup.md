# Name: release-sync.yml
# Path: .github/workflows/release-sync.yml
# Purpose: Automatically sync releases from sum-platform (private) to sum-core (public)
# Family: Release automation
# Dependencies: scripts/sync_to_public.py

name: Release Sync

on:
  # Trigger on merge to main (release PRs)
  push:
    branches:
      - main
    paths:
      - 'core/**'
      - 'boilerplate/**'
      - 'docs/public/**'
      - 'pyproject.toml'

  # Manual trigger for re-syncs or debugging
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to tag (e.g., v0.6.0). Leave empty for sync-only.'
        required: false
        type: string
      dry_run:
        description: 'Dry run (no push)'
        required: false
        type: boolean
        default: false

permissions:
  contents: read

jobs:
  sync:
    name: Sync to Public Repository
    runs-on: ubuntu-latest
    timeout-minutes: 10

    # Only run if commit message indicates a release
    # OR if manually triggered
    if: |
      github.event_name == 'workflow_dispatch' ||
      contains(github.event.head_commit.message, 'chore(release)')

    steps:
      - name: Checkout sum-platform
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for tags

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Configure Git
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"

      - name: Set up SSH for public repo
        uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ secrets.SUM_CORE_DEPLOY_KEY }}

      - name: Extract version from commit (auto)
        if: github.event_name == 'push'
        id: extract_version
        run: |
          # Try to extract version from commit message
          # Expected format: "chore(release): v0.6.0" or "chore(release): prepare v0.6.0"
          COMMIT_MSG="${{ github.event.head_commit.message }}"
          VERSION=$(echo "$COMMIT_MSG" | grep -oP 'v\d+\.\d+\.\d+' | head -1 || echo "")
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "Extracted version: $VERSION"

      - name: Determine version
        id: version
        run: |
          if [ -n "${{ github.event.inputs.version }}" ]; then
            VERSION="${{ github.event.inputs.version }}"
          else
            VERSION="${{ steps.extract_version.outputs.version }}"
          fi

          # Normalize version (ensure v prefix)
          if [ -n "$VERSION" ] && [[ ! "$VERSION" =~ ^v ]]; then
            VERSION="v$VERSION"
          fi

          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "Final version: $VERSION"

      - name: Run sync script
        env:
          VERSION: ${{ steps.version.outputs.version }}
          DRY_RUN: ${{ github.event.inputs.dry_run }}
        run: |
          ARGS=""

          if [ -n "$VERSION" ]; then
            ARGS="$ARGS --version $VERSION"
          fi

          if [ "$DRY_RUN" = "true" ]; then
            ARGS="$ARGS --no-push"
          fi

          python scripts/sync_to_public.py $ARGS

      - name: Verify sync (if version provided)
        if: steps.version.outputs.version != '' && github.event.inputs.dry_run != 'true'
        env:
          VERSION: ${{ steps.version.outputs.version }}
        run: |
          # Verify tag exists on public repo
          git ls-remote --tags git@github.com:markashton480/sum-core.git | grep -q "$VERSION" || {
            echo "❌ Tag $VERSION not found on sum-core"
            exit 1
          }
          echo "✅ Tag $VERSION verified on sum-core"

      - name: Create GitHub Release (if version provided)
        if: steps.version.outputs.version != '' && github.event.inputs.dry_run != 'true'
        env:
          GH_TOKEN: ${{ secrets.SUM_CORE_PAT }}
          VERSION: ${{ steps.version.outputs.version }}
        run: |
          # Generate release notes from recent commits
          NOTES=$(git log $(git describe --tags --abbrev=0 HEAD~1 2>/dev/null || echo HEAD~10)..HEAD --oneline --no-merges | head -20)

          # Create release on public repo
          gh release create "$VERSION" \
            --repo markashton480/sum-core \
            --title "Release $VERSION" \
            --notes "## Changes

          $NOTES

          ## Installation

          \`\`\`bash
          pip install \"sum_core @ git+https://github.com/markashton480/sum-core.git@$VERSION\"
          \`\`\`
          " || echo "Release may already exist"

  notify:
    name: Notify on Failure
    runs-on: ubuntu-latest
    needs: sync
    if: failure()

    steps:
      - name: Report failure
        run: |
          echo "❌ Release sync failed!"
          echo "Check the workflow logs for details."
          # Add Slack/email notification here if desired