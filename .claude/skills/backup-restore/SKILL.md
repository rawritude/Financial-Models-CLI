---
name: backup-restore
description: Manage point-in-time snapshots of a deal's model.xlsx — take manual snapshots, list snapshots, and restore the model from a snapshot. Use for explicit pre-flight backups, post-incident rollback, or to vet a "what changed?" investigation.
---

# Backup and restore

## How auto-backup works

Every mutating CLI command (`update`, `sensitivity`) snapshots the model
before writing. Snapshots live in `data/deals/<deal>/.backups/` and are
named:

```
model_<UTC-timestamp>_<reason>_<sha-prefix>.xlsx
```

Up to 50 snapshots per deal are retained (env var `FMCLI_BACKUP_RETAIN`).
Older snapshots are pruned automatically.

## Take a manual snapshot

Tag clearly so you can find it later:

```
fmcli backup <deal_id> --reason pre-quarter-close
fmcli backup <deal_id> --reason pre-amendment-rate-cut
fmcli backup <deal_id> --reason before-experiment
```

The snapshot is appended to the audit log.

## List snapshots

```
fmcli backups <deal_id>
```

Shows snapshot name, timestamp, reason, and SHA prefix.

## Restore

```
fmcli restore <deal_id> <snapshot_name_or_substring>
```

The CLI takes a `pre-restore` snapshot first, so you can always get back to
the state immediately before the rollback.

If the substring is ambiguous, the CLI errors out with the candidate count.
Be specific.

## When to take an extra manual snapshot

- **Before a multi-step manual analysis.** Even though every CLI command
  auto-snapshots, an explicit `pre-X` tag is easier to find afterwards than
  scanning timestamps.
- **Before opening the file in Excel.** Excel can silently change formula
  precision or named ranges.
- **At quarter-close.** Pin the closed-period state with a clear tag.

## When NOT to rely on backups

- **For audit evidence.** The audit log + backup is the evidence trail; do
  not rely on backups alone.
- **For long-term retention.** Backups beyond `FMCLI_BACKUP_RETAIN` are
  pruned. For long-term retention, copy the snapshot somewhere durable.
