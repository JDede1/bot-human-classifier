-- 1) Create mlflow role if not exists
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'mlflow') THEN
      CREATE ROLE mlflow LOGIN PASSWORD 'mlflow';
   END IF;
END
$$;

-- 2) Create message_history table in appdb
CREATE TABLE IF NOT EXISTS message_history (
    id             BIGSERIAL PRIMARY KEY,
    conversation_id TEXT,
    sender         TEXT NOT NULL,    -- 'user' | 'bot'
    message_text   TEXT NOT NULL,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_message_history_conv ON message_history(conversation_id);
