from aiohttp import web
import settings
import jwt
from models.user import User
from models.token import Token
from datetime import datetime
from database import Database


@web.middleware
async def auth_middleware(request, handler):
    request.user = None
    jwt_token = request.headers.get('token', None)
    if jwt_token:
        try:
            payload = jwt.decode(jwt_token, settings.JWT_SECRET_KEY,
                                 algorithms=[settings.JWT_ALGORITHM])
        except:
            return web.json_response({"message": "Token is invalid"}, status=400)
        if await Token.load_from_db(payload['user_id']):
            raw_user = await User.load_from_db(payload['user_id'])
            user = {
                "id": raw_user['id'],
                "name": raw_user['name'],
                "email": raw_user["email"]
            }
            request.user = user
    return await handler(request)


@web.middleware
async def request_middleware(request, handler):
    request_data = {
        'url': request.raw_path,
        'method': request.method,
        'user': request.user,
        'content-type': request.content_type,
        'time': datetime.now().isoformat(timespec='minutes')
    }
    print(request_data)
    return await handler(request)


def check_subscribe(func):
    async def wrapper(request):
        group_id = request.match_info['group_id']
        user = request.user['id']
        try:
            async with Database.pool.acquire() as connection:
                subscribe = await connection.fetch('''SELECT user_id, groupchat_id FROM public.users_groupchat WHERE user_id = $1 AND groupchat_id = $2''', user, int(group_id))
                if subscribe is None:
                    return web.Response(status=403, text='you are not subscribe')
                else:
                    return await func(request)
        except Exception as error:
            print(error)
            return web.Response(status=400)

    return wrapper


def login_required(func):
    async def wrapper(request):
        if not request.user:
            return web.json_response({'message': 'please sign-in'}, status=401)
        return await func(request)

    return wrapper


def setup_middlewares(app):
    app.middlewares.append(auth_middleware)
    app.middlewares.append(request_middleware)
