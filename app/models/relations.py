from models.base import Base
from database import Database


class UsersGroupchat(Base):
    def __init__(self, user_id, groupchat_id):
        self.user_id = user_id
        self.groupchat_id = groupchat_id

    def __repr__(self):
        return 'user id={} group id={}'.format(self.user_id, self.groupchat_id)

    async def save_to_db(self):
        async with Database.pool.acquire() as connection:
            await connection.execute('''INSERT INTO public.users_groupchat (user_id, groupchat_id) VALUES($1, $2)''', self.user_id, self.groupchat_id)

# users_groupchat = """CREATE TABLE IF NOT EXISTS users_groupchat (
#   user_id int NOT NULL,
#   groupchat_id int NOT NULL,
#   PRIMARY KEY (user_id, groupchat_id),
#   FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE,
#   FOREIGN KEY (groupchat_id) REFERENCES groupchat(id) ON UPDATE CASCADE
# );"""


class UsersCommunity(Base):
    def __init__(self, user_id, community_id):
        self.user_id = user_id
        self.community_id = community_id

    def __repr__(self):
        return 'user id={} community id={}'.format(self.user_id, self.community_id)

    async def save_to_db(self):
        async with Database.pool.acquire() as connection:
            await connection.execute('''INSERT INTO public.users_community (user_id, community_id) VALUES($1, $2)''', self.user_id, self.community_id)


# users_community = """CREATE TABLE IF NOT EXISTS users_community (
#   user_id int NOT NULL,
#   community_id int NOT NULL,
#   PRIMARY KEY (user_id, community_id),
#   FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE,
#   FOREIGN KEY (community_id) REFERENCES community(id) ON UPDATE CASCADE
# );"""
