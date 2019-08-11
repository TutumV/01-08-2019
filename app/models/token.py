from database import Database
from models.base import Base


class Token(Base):
    def __init__(self, user_id, token, date):
        self.set_user_id(user_id)
        self.set_token(token)
        self.set_date(date)

    def __repr__(self):
        return '<Token user_id={}, token={}, date={}>'.format(self.user_id, self.token, self.date)

    async def to_json(self):
        try:
            async with Database.pool.acquire() as connection:
                token = await connection.fetch('''SELECT user_id, token, date FROM public.token WHERE user_id = $1''', self.user_id)
            return {"user_id": token[0][0], "token": token[0][1], "date": token[0][2]}
        except Exception as error:
            pass

    def set_date(self, date):
        if self.validate_date(date):
            self.date = date
        else:
            raise Exception('Date must be string')

    def validate_date(self, date):
        if type(date) == str:
            return True
        else:
            return False

    def set_token(self, token):
        if token:
            self.token = token
        else:
            raise Exception('Bad token')

    def set_user_id(self, user_id):
        if type(user_id) == int:
            self.user_id = user_id
        else:
            raise TypeError("user id is not integer")

    @staticmethod
    async def load_from_db(user_id):
        try:
            async with Database.pool.acquire() as connection:
                token = await connection.fetch('''SELECT user_id, token, date FROM public.token WHERE user_id=$1''', int(user_id))
                return token
        except Exception as error:
            pass
            
    async def save_to_db(self):
        try:
            async with Database.pool.acquire() as connection:
                await connection.execute('''INSERT INTO public.token (token, date, user_id) VALUES ($1, $2, $3)''', self.token, self.date, self.user_id)
        except Exception as error:
            pass

    @staticmethod
    async def delete(id):
        try:
            async with Database.pool.acquire() as connection:
                await connection.execute('''DELETE FROM public.token WHERE user_id = $1''', int(id))
        except Exception as error:
            pass

# token = """CREATE TABLE IF NOT EXISTS token(
#         user_id INTEGER PRIMARY KEY NOT NULL REFERENCES users(id),
#         token varchar(512) UNIQUE NOT NULL DEFAULT NULL,
#         date varchar(200) NOT NULL
#     );"""