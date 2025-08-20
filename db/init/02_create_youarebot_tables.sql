-- db/init/02_create_youarebot_tables.sql
-- Participants in each dialog
CREATE TABLE IF NOT EXISTS participants (
    dialog_id          TEXT        NOT NULL,
    participant_index  INTEGER     NOT NULL CHECK (participant_index >= 0),
    is_bot             BOOLEAN     NULL, -- labeled in ytrain, null for test
    PRIMARY KEY (dialog_id, participant_index)
);

-- Messages exchanged in dialogs
CREATE TABLE IF NOT EXISTS messages (
    dialog_id          TEXT        NOT NULL,
    message_index      INTEGER     NOT NULL CHECK (message_index >= 0),
    participant_index  INTEGER     NOT NULL CHECK (participant_index >= 0),
    text               TEXT        NOT NULL,
    text_len           INTEGER     GENERATED ALWAYS AS (char_length(text)) STORED,
    PRIMARY KEY (dialog_id, message_index),
    CONSTRAINT fk_messages_participant
      FOREIGN KEY (dialog_id, participant_index)
      REFERENCES participants (dialog_id, participant_index)
      ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_messages_participant
  ON messages (dialog_id, participant_index);

CREATE INDEX IF NOT EXISTS idx_messages_text_len
  ON messages (text_len);
