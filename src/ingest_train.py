import os
import json
import psycopg2
import pandas as pd
from pathlib import Path

# 1. Connect to Postgres
def get_connection():
    db_user = os.getenv("POSTGRES_USER", "app")
    db_pass = os.getenv("POSTGRES_PASSWORD", "app")
    db_host = os.getenv("POSTGRES_HOST", "db")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "appdb")

    conn = psycopg2.connect(
        dbname=db_name, user=db_user, password=db_pass,
        host=db_host, port=db_port
    )
    conn.autocommit = True
    return conn

def ingest_participants(conn, ytrain_path):
    df = pd.read_csv(ytrain_path)
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO participants (dialog_id, participant_index, is_bot)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (row['dialog_id'], int(row['participant_index']), bool(row['is_bot'])))
    print(f"Inserted {len(df)} participants from {ytrain_path}")


def ingest_messages(conn, train_json_path):
    total = 0
    with open(train_json_path, "r") as f:
        data = json.load(f)   # load the whole JSON object

    with conn.cursor() as cur:
        for dialog_id, messages in data.items():
            for msg in messages:
                message_index = msg["message"]
                text = msg["text"]
                participant_index = int(msg["participant_index"])

                cur.execute("""
                    INSERT INTO messages (dialog_id, message_index, participant_index, text)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                """, (dialog_id, message_index, participant_index, text))
                total += 1

    print(f"Inserted {total} messages from {train_json_path}")

if __name__ == "__main__":
    conn = get_connection()
    data_dir = Path(__file__).resolve().parents[1] / "data"

    ingest_participants(conn, data_dir / "ytrain.csv")
    ingest_messages(conn, data_dir / "train.json")

    # Quick counts
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM participants;")
        print("Participants in DB:", cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) FROM messages;")
        print("Messages in DB:", cur.fetchone()[0])

    conn.close()
