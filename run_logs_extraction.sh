#!/bin/bash
set -e

mkdir -p "$HOME/pronoun-proofer/logs"

journalctl --user -u pronoun-proofer.service --since "$(date -d yesterday +%F) 00:00" --until "$(date -d today +%F) 00:00" \
  --no-pager --output=cat \
  > "$HOME/pronoun-proofer/logs/pronoun-proofer-$(date -d yesterday +%F).log"

find "$HOME/pronoun-proofer/logs" -type f -name 'pronoun-proofer-*.log' -mtime +180 -delete
