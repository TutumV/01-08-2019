from aiohttp import web
from middleware import login_required
from datetime import datetime
from models.user import User
from models.token import Token
from database import Database
import bcrypt
import settings
import jwt


@login_required
async def create_user(request):
    if request.content_type == 'application/json':
        raw_data = await request.json()
    elif request.content_type == 'application/x-www-form-urlencoded':
        raw_data = await request.post()
    else:
        return web.Response(status=400, text='content type must be json or urlencoded')
    try:
        name = raw_data['name']
        email = raw_data['email']
        password = raw_data['password']
        user = User(name, email, password)
        await user.save_to_db()
        data = await user.to_json()
        return web.json_response(data)
    except Exception as e:
        return web.Response(status=400, text=str(e))


@login_required
async def get_all_users(request):
    try:
        users = await User.all()
        return web.json_response(users)
    except Exception as error:
        return  web.Response(status=404)


@login_required
async def profile(request):
    data = {
        "id": request.user['id'],
        "name": request.user['name'],
        "email": request.user['email']
    }
    return web.json_response(data)


async def login(request):
    if request.content_type == 'application/json':
        raw_data = await request.json()
    elif request.content_type == 'application/x-www-form-urlencoded':
        raw_data = await request.post()
    else:
        return web.Response(status=400, text='content type must be json or urlencoded')
    headers = request.headers.get('token')
    if headers:
        return web.json_response({'message': 'you already sign-in'})
    async with Database.pool.acquire() as connection:
        user = await connection.fetch('''SELECT id, password FROM public.users WHERE email = $1''', raw_data['email'])
        pass_db = user[0][1].encode('utf-8')
        password = raw_data['password']
        if bcrypt.hashpw(password.encode('utf-8'), settings.SALT.encode('utf-8')) == pass_db:
            user_id = user[0][0]
        else:
            return web.Response(status=400, text="NOT VALID EMAIL OR PASSWORD")
    token = await Token.load_from_db(user_id)
    if token:
        await Token.delete(token[0][0])
    time = str(datetime.now())
    create_token = jwt.encode({
                            'user_id': user_id,
                            'create_date': time
                            }, settings.JWT_SECRET_KEY).decode('utf-8')
    headers = {'Token': '{}'.format(create_token)}
    try:
        token = Token(token=create_token, date=time, user_id=user_id)
        await token.save_to_db()
        return web.json_response(headers=headers, text="Hello!")
    except Exception as error:
        return web.Response(text="Unexpected error")


@login_required
async def logout(request):
    if request.user:
        try:
            user = request.user
            await Token.delete(user['id'])
            return web.Response(status=200, text="all right")
        except Exception as e:
            return web.Response(status=400, text="bad request")
    else:
        return web.Response(status=401, text="you are not sign-in")


@login_required
async def get_user_by_id(request):
    user_id = request.match_info['id']
    try:
        user = await User.load_from_db(user_id)
        data = {
            'id': user['id'],
            'email': user['email'],
            'name': user['name']
        }
        return web.json_response(status=200, data=data)
    except Exception as error:
        return web.Response(status=400)


@login_required
async def update_user_by_id(request):
    user_id = request.match_info['id']
    if request.content_type == 'application/json':
        raw_data = await request.json()
    elif request.content_type == 'application/x-www-form-urlencoded':
        raw_data = await request.post()
    else:
        return web.Response(status=400, text='content type must be json or urlencoded')
    try:
        user = await User.load_from_db(user_id)
        if 'name' in raw_data:
            await User.update(field='name', value=raw_data['name'], id=user_id)
        elif 'email' in raw_data:
            await User.update(field='email', value=raw_data['email'], id=user_id)
        elif 'password' in raw_data:
            await User.update(field='password', value=raw_data['password'], id=user_id)
        else:
            return web.Response(status=400, text='BAD REQUEST')
        return web.Response(status=200, text="UPDATED")
    except Exception as error:
        return web.Response(status=400, text='BAD REQUEST OR NOT FOUND')


@login_required
async def delete_user_by_id(request):
    user_id = request.match_info['id']
    try:
        await User.delete(user_id)
        return web.Response(status=200, text="OK")
    except:
        return web.Response(status=404, text="NOT FOUND")


