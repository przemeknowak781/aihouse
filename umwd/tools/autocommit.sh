#!/bin/bash
# Periodic commit & push of team work (background).
cd /home/user/aihouse
while true; do
  if [ -n "$(git status --porcelain)" ]; then
    git add -A >/dev/null 2>&1
    git commit -qm "UMWD: prace robocze zespołów (autocommit)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01ULAuXU15ZK9PB4XdqzfV5P" >/dev/null 2>&1
    for i in 1 2 3 4; do git push -q -u origin claude/wroclaw-marshal-office-project-ktx37s >/dev/null 2>&1 && break; sleep $((2**i)); done
  fi
  sleep 120
done
