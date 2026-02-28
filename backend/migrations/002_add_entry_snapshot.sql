-- Migration: add entry_snapshot_json to trades (record-time market snapshot)
-- Run when upgrading. New deployments with create_all will have the column.

ALTER TABLE trades ADD COLUMN IF NOT EXISTS entry_snapshot_json TEXT;
