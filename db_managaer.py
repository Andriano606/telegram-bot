import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class DBManager:
  def __init__(self, db_name, user, password):
    self.db_name = db_name
    self.user = user
    self.password = password

  def connect(self):
    self.conn = psycopg2.connect(f"dbname={self.db_name} user={self.user} password={self.password}")
    self.cur = self.conn.cursor()

  def create_database(self):
    conn = psycopg2.connect(f"dbname=postgres user={self.user} password={self.password}")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.db_name,))
    if cur.fetchone() is None:
      cur.execute(f"CREATE DATABASE {self.db_name}")
    cur.close()
    conn.close()

  def create_users_table(self):
    self.cur.execute("""
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE NOT NULL,
        instagram_channels TEXT[] NOT NULL
      )
    """)
    self.conn.commit()

  def get_channel_by_name(self, channel, user_id):
    self.cur.execute("""
        SELECT instagram_channels
        FROM users
        WHERE telegram_id = %s
    """, (user_id,))
    result = self.cur.fetchone()

    if result is not None:
        channels = result[0]
        if channel in channels:
            return channel

    return None

  def add_new_instagram_channel(self, channel, user_id):
    existing_channel = self.get_channel_by_name(channel, user_id)  

    if existing_channel is None:
      self.cur.execute("""
        UPDATE users
        SET instagram_channels = array_append(instagram_channels, %s)
        WHERE telegram_id = %s
      """, (channel, user_id))
      self.conn.commit()

  def add_user(self, user_id, instagram_channels=None):
    channels = instagram_channels if instagram_channels is not None else []
    self.cur.execute("""
        INSERT INTO users (telegram_id, instagram_channels)
        VALUES (%s, %s)
        ON CONFLICT (telegram_id) DO NOTHING
    """, (user_id, channels))
    self.conn.commit()

  def create_table(self):
    self.cur.execute("""
      CREATE TABLE IF NOT EXISTS posts (
        id SERIAL PRIMARY KEY,
        post_id VARCHAR(255) NOT NULL,
        user_id INT NOT NULL,
        instagram_channel VARCHAR(255) NOT NULL
      )
    """)
    self.conn.commit()

  def get_all_users(self):
    self.cur.execute("SELECT telegram_id, instagram_channels FROM users")
    return self.cur.fetchall()

  def get_post_ids(self):
    self.cur.execute("SELECT post_id, user_id FROM posts")
    return [row for row in self.cur.fetchall()]

  def add_post(self, post_id, user_id, instagram_channel):
    self.cur.execute("""
        SELECT post_id, user_id, instagram_channel 
        FROM posts 
        WHERE post_id=%s AND user_id=%s AND instagram_channel=%s
    """, (post_id, user_id, instagram_channel))
    result = self.cur.fetchall()

    if not result:
        self.cur.execute("""
            INSERT INTO posts (post_id, user_id, instagram_channel) 
            VALUES (%s, %s, %s)
        """, (post_id, user_id, instagram_channel,))
        self.conn.commit()
        return True
    
    return False

  def close(self):
    self.cur.close()
    self.conn.close()