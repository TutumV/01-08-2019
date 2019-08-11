from models.base import Base
from database import Database

class Chat(Base):
    def __init__(self, name, creator, participants):
        self.name = name
        self.creator = creator
        self.paticipants = participants

    def __repr__(self):
        return  'Chat name={}'.format(self.name)

    async def save_to_db(self):
        async with Database.pool.acquire() as connection:
            await connection.execute('''INSERT INTO public.chat (name, creator, participant) VALUES($1, $2, $3)''', self.name, self.creator, self.paticipants)

# chat = """CREATE TABLE IF NOT EXISTS chat(
#           id serial PRIMARY KEY NOT NULL UNIQUE,
#           name varchar(150) NOT NULL,
#           creator INTEGER NOT NULL REFERENCES users(id),
#           participant INTEGER NOT NULL REFERENCES users(id)
#      );"""