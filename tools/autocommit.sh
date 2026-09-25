#!/bin/bash
# Okresowy commit i push prac roboczych agentów (działających w tle).
cd /home/user/aihouse
while true; do
  if [ -n "$(git status --porcelain)" ]; then
    git add -A >/dev/null 2>&1
    git commit -qm "Prace robocze zespołów (autocommit)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01FusXBHKDYGFEzgisqwGYyr" >/dev/null 2>&1
    for i in 1 2 3 4; do git push -q origin claude/single-family-house-project-2pkn7l >/dev/null 2>&1 && break; sleep $((2**i)); done
  fi
  sleep 90
done
