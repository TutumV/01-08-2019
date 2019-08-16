from models.base import Base
from database import Database


class GroupChat(Base):
    def __init__(self, name, admin):
        self.name = name
        self.admin = admin

    def __repr__(self):
        return 'GroupChat name={}'.format(self.name)

    async def save_to_db(self):
        async with Database.pool.acquire() as connection:
            await connection.execute('''INSERT INTO public.groupchat (name, admin) VALUES($1, $2)''', self.name, self.admin)

# group_chat = """CREATE TABLE IF NOT EXISTS groupchat(
#           id serial PRIMARY KEY NOT NULL UNIQUE,
#           name varchar(150) NOT NULL,
#           admin INTEGER NOT NULL REFERENCES users(id)
#      );"""
