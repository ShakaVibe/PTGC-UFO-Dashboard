#!/usr/bin/env python3
"""Audit IV e20 + e22 (2026-10-23): writes the CI workflow files. Run it ON THE MAC from the repo root (the Claude file bridge
refuses to write .github/workflows/*):   python3 tools/audit4-ci.py      (twice: the second run must print "0 edit(s)")
  - .github/workflows/site-check.yml        NEW — on a push that touches a page: compile every page, check the committed tw.css is
                                             current, mount every page in headless Chromium. A red run = GitHub's failure e-mail.
  - .github/workflows/pipeline-watchdog.yml NEW — every 3 h: fails when the hourly data pipeline has stopped (scripts/pipeline-watchdog.mjs).
  - .github/workflows/deploy.yml            a `check` job (compile every page, ~15 s) that the deploy now NEEDS: a page that does not
                                             compile never reaches ptgc-ufo.com — the site stays on the last good version.
"""
import os
n = 0
def write(path, body):
    global n
    if os.path.exists(path) and open(path, encoding='utf-8').read() == body: return
    open(path, 'w', encoding='utf-8').write(body); n += 1
def edit(path, old, new):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == 1, f'{path}: anchor x{s.count(old)}: {old[:80]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

write('.github/workflows/site-check.yml', '''name: Site check

# Audit IV e20 (2026-10-23). On a push that touches a page: compile every page, check the committed tw.css matches the pages'
# classes (a class with no rule in tw.css does nothing live — the 2026-10-22 Affiliates receipts icon), and mount every page in
# headless Chromium with the data APIs stubbed (tools/harness). A red run = GitHub's failure e-mail to the owner. It does NOT block
# the deploy — deploy.yml's own compile check does that. Locally: cd tools/harness && node compile.js && CHROME=… node ci-mount.js

on:
  push:
    branches: [main]
    paths: ['*.html', '*.css', '*.jsx', 'tools/harness/**', 'tools/pf-v2/**', 'tools/top100/**', 'tools/affiliate/**', '.github/workflows/site-check.yml']
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: site-check
  cancel-in-progress: true

jobs:
  check:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    # the image ships the Chromium build that playwright-core 1.47.0 (tools/harness/package.json) drives
    container: mcr.microsoft.com/playwright:v1.47.0-jammy
    steps:
      - name: Checkout
        uses: actions/checkout@v7

      - name: Install the harness
        working-directory: tools/harness
        run: npm install --no-audit --no-fund

      - name: Compile every page
        working-directory: tools/harness
        run: node compile.js

      - name: tw.css is current
        working-directory: tools/harness
        run: |
          cp ../../tw.css /tmp/tw.committed.css
          npm run css
          if ! cmp -s /tmp/tw.committed.css ../../tw.css; then
            echo "::error::tw.css is stale — run 'cd tools/harness && npm run css', commit tw.css and bump tw.css?v= on the five pages"
            exit 1
          fi

      - name: Mount every page
        working-directory: tools/harness
        run: |
          export CHROME="$(ls -d /ms-playwright/chromium-*/chrome-linux/chrome | head -1)"
          node ci-mount.js
''')

write('.github/workflows/pipeline-watchdog.yml', '''name: Pipeline watchdog

# Audit IV e22 (2026-10-23). Every 3 h: fails (→ GitHub's failure e-mail to the owner) when the hourly data pipeline has stopped —
# not run for 3 h (the Cloudflare Worker's hourly dispatch or its DISPATCH_TOKEN died; GitHub's own schedule fires only a few
# times a day), or a step has not succeeded within twice its gate + 3 h. Reads the published files only; needs no secret.

on:
  schedule:
    - cron: '23 */3 * * *'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  watch:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Is the data pipeline running?
        run: |
          B="https://raw.githubusercontent.com/${{ github.repository }}/main"
          curl -fsSL "$B/scripts/pipeline-watchdog.mjs" -o pipeline-watchdog.mjs
          curl -fsSL "$B/scripts/pipeline-run.mjs"      -o pipeline-run.mjs
          curl -fsSL "$B/data/pipeline-status.json"     -o pipeline-status.json
          node pipeline-watchdog.mjs pipeline-status.json pipeline-run.mjs
''')

D = '.github/workflows/deploy.yml'
edit(D, '''jobs:
  deploy:
    environment:''', '''jobs:
  # Audit IV e20 (2026-10-23): a page that does not compile is a BLANK site. This compiles every page (~15 s) and the deploy below
  # waits for it — a broken edit never reaches ptgc-ufo.com; the site stays on the last good version and GitHub e-mails the failure.
  check:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Checkout
        uses: actions/checkout@v7

      - name: Setup Node
        uses: actions/setup-node@v7
        with:
          node-version: '22'

      - name: Compile every page
        run: |
          mkdir -p /tmp/babel && cd /tmp/babel && npm init -y > /dev/null && npm install --no-audit --no-fund @babel/standalone@7.26.4 > /dev/null
          cd "$GITHUB_WORKSPACE" && NODE_PATH=/tmp/babel/node_modules node tools/harness/compile.js

  deploy:
    needs: check
    environment:''')
print(f'audit4-ci: {n} edit(s)')
