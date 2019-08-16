from models.base import Base
from database import Database


class Message(Base):
    def __init__(self, chat_id, group_id, content, sender, date):
        self.chat_id = chat_id
        self.group_id = group_id
        self.content = content
        self.sender = sender
        self.date = date

    def __repr__(self):
        return 'Chat id ={}, Group id ={}, sender id={}'.format(self.chat_id, self.group_id, self.sender)

    async def save_to_db(self):
        async with Database.pool.acquire() as connection:
            await connection.execute('''INSERT INTO public.message (chat_id, group_id, content, sender, date) VALUES($1, $2, $3, $4, $5)''', self.chat_id, self.group_id, self.content, self.sender, self.date)


# message = """CREATE TABLE IF NOT EXISTS message(
#            id serial PRIMARY KEY NOT NULL UNIQUE,
#            chat_id INTEGER REFERENCES chat(id),
#            group_id INTEGER REFERENCES groupchat(id),
#            content varchar(4096) NOT NULL,
#            sender INTEGER NOT NULL REFERENCES users(id),
#            date INTEGER NOT NULL
#       );"""
