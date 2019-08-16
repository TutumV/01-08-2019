from models.base import Base
from database import Database


class Post(Base):
    def __init__(self, community_id, header, text, date):
        self.community_id = community_id
        self.header = header
        self.text = text
        self.date = date

    def __repr__(self):
        return 'Post id={} header id={}'.format(self.community_id, self.header)

    async def save_to_db(self):
        async with Database.pool.acquire() as connection:
            await connection.execute('''INSERT INTO public.post (community_id, header, text, date) VALUES($1, $2, $3, $4)''', self.community_id, self.header, self.text, self.date)


# post = """CREATE TABLE IF NOT EXISTS post(
#            id serial PRIMARY KEY NOT NULL UNIQUE,
#            community_id INTEGER NOT NULL REFERENCES community(id),
#            header varchar(128) NOT NULL,
#            text varchar(4096) NOT NULL,
#            date INTEGER NOT NULL
#       );"""
