import bcrypt
import re
from database import Database
from models.base import Base
import settings


class User(Base):
    def __init__(self, name, email, password):
        self.set_name(name)
        self.set_email(email)
        self.set_password(password)

    def __repr__(self):
        return '<User name={}, email={}>'.format(self.name, self.email)

    async def to_json(self):
        async with Database.pool.acquire() as connection:
            user = await connection.fetch('''SELECT id, name, email FROM public.users WHERE email = $1''', self.email)
        return {"id": user[0][0], "name": user[0][1], "email": user[0][2]}

    def set_name(self, name: str):
        name = name.strip()
        if len(name) >= 1:
            self.name = name
        else:
            raise Exception('Name must be not None')

    def set_email(self, email):
        if User.validate_email(email):
            self.email = email
        else:
            raise Exception("Not valid email")
    
    @staticmethod
    def validate_email(email: str):
        email = email.strip()
        if len(email) >= 1:
            email = bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email))
            return email

    def set_password(self, password):
        try:
            password = User.hash_password(password)
            self.password = password.decode('utf-8')
        except Exception as error:
            print(error)

    def hash_password(password: str):
        password = password.strip()
        if len(password) >= 1:
            hash_password = bcrypt.hashpw(password.encode('utf-8'), settings.SALT.encode('utf-8'))
            return hash_password

    @staticmethod
    async def load_from_db(id):
        async with Database.pool.acquire() as connection:
            try:
                user = await connection.fetch('''SELECT id, name, email FROM public.users WHERE id=$1''', int(id))
                return user[0]
            except Exception as error:
                print(error)

    async def save_to_db(self):
        async with Database.pool.acquire() as connection:
            await connection.execute('''INSERT INTO public.users (name, email, password) VALUES($1, $2, $3)''', self.name, self.email, self.password)

    @staticmethod
    async def delete(id):
        async with Database.pool.acquire() as connection:
            try:
                await connection.execute('''DELETE FROM public.users WHERE id = $1''', int(id))
            except Exception as error:
                print(error)

    @staticmethod
    async def all():
        async with Database.pool.acquire() as connection:
            users = await connection.fetch('''SELECT id, name, email FROM public.users''')
            data = []
            for user in users:
                data.append({
                    "id": user[0],
                    "name": user[1],
                    "email": user[2]
                })
            return data

    @staticmethod
    async def update(field, value, id):
        try:
            async with Database.pool.acquire() as connection:
                await connection.execute('''UPDATE public.users SET {} = $1 WHERE id = $2'''.format(field), value, int(id))
        except Exception as error:
            print(error)

# user = """CREATE TABLE IF NOT EXISTS users(
#         id serial PRIMARY KEY NOT NULL UNIQUE,
#         name varchar(150) NOT NULL,
#         email varchar(150) UNIQUE NOT NULL,
#         password varchar(150) NOT NULL
#     );"""