from settings import config
import asyncpg


class Database:

    pool = None

    @classmethod
    async def connect(cls):
        try:
            user = config['postgres']['user']
            password = config['postgres']['password']
            host = config['postgres']['host']
            port = config['postgres']['port']
            database = config['postgres']['database']
            dsn = 'postgres://{}:{}@{}:{}/{}'.format(user, password, host, port, database)
            cls.pool = await asyncpg.create_pool(dsn, command_timeout=60)
        except Exception as error:
            print(error)
