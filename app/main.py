from aiohttp import web
from settings import config
from routes.user import user_setup_routes
from routes.chat import chat_setup_routes
from routes.message import message_setup_routes
from routes.community import community_setup_routes
from routes.post import post_setup_routes
from middleware import setup_middlewares
import asyncio
from database import Database


def init_app():
    app = web.Application()
    app['config'] = config
    asyncio.get_event_loop().run_until_complete(Database.connect())
    user_setup_routes(app)
    chat_setup_routes(app)
    message_setup_routes(app)
    community_setup_routes(app)
    post_setup_routes(app)
    setup_middlewares(app)
    return app


if __name__ == '__main__':
    app = init_app()
    web.run_app(app, host=app['config']['host'], port=app['config']['port'])
