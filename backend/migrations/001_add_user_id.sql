-- Migration: add user_id to trades, reviews, checklist
-- Run this if upgrading from pre-multi-tenant schema.
-- New deployments with create_all will have user_id from start.

-- trades
ALTER TABLE trades ADD COLUMN IF NOT EXISTS user_id TEXT;
UPDATE trades SET user_id = 'default' WHERE user_id IS NULL;
ALTER TABLE trades ALTER COLUMN user_id SET NOT NULL;
CREATE INDEX IF NOT EXISTS ix_trades_user_id ON trades(user_id);

-- reviews
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS user_id TEXT;
UPDATE reviews SET user_id = 'default' WHERE user_id IS NULL;
ALTER TABLE reviews ALTER COLUMN user_id SET NOT NULL;
CREATE INDEX IF NOT EXISTS ix_reviews_user_id ON reviews(user_id);

-- checklist
ALTER TABLE checklist ADD COLUMN IF NOT EXISTS user_id TEXT;
UPDATE checklist SET user_id = 'default' WHERE user_id IS NULL;
ALTER TABLE checklist ALTER COLUMN user_id SET NOT NULL;
CREATE INDEX IF NOT EXISTS ix_checklist_user_id ON checklist(user_id);
