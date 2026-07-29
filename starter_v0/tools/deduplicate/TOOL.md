---
name: deduplicate
track: core
kind: local_formatter
requires_env: []
inputs: [items]
outputs: [items, input_count, item_count, removed_count]
side_effect: false
---
# deduplicate

Removes duplicate items from an already-collected list while preserving order.
It keeps the first occurrence, compares normalized URLs when available, and
falls back to normalized titles for items without a URL. It does not fetch,
rank, summarize, or otherwise rewrite item content.
