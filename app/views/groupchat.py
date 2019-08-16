from aiohttp import web
from models.groupchat import GroupChat
from models.relations import UsersGroup
from models.user import User
from middleware import login_required
from database import Database


@login_required
async def create_groupchat(request):
    if request.content_type == 'application/json':
        raw_data = await request.json()
    elif request.content_type == 'application/x-www-form-urlencoded':
        raw_data = await request.post()
    else:
        return web.Response(status=400, text='content type must be json or urlencoded')
    try:
        admin = request.user['id']
        if raw_data['name'].strip():
            async with Database.pool.acquire() as connection:
                name = await connection.fetch('''SELECT id, name FROM public.groupchat WHERE name = $1''', raw_data['name'])
                if name:
                    return web.Response(status=400, text='name is busy')
                groupchat = GroupChat(name=raw_data['name'].strip(), admin=admin)
                await groupchat.save_to_db()
                groupchat = await connection.fetch('''SELECT id, name, admin FROM public.groupchat WHERE name = $1 AND admin = $2''', raw_data['name'].strip(), admin)
                data = {
                    "id": groupchat[0]['id'],
                    "name": groupchat[0]['name'],
                    "admin_id": groupchat[0]['admin']
                }
                return web.json_response(status=201, data=data)
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
async def get_all_groupchat(request):
    try:
        async with Database.pool.acquire() as connection:
            groupchat_list = await connection.fetch('''SELECT id, name, admin FROM public.groupchat''')
            if groupchat_list is None:
                return web.Response(status=404, text='group is not found')
            data = []
            for group in groupchat_list:
                one = {
                    "id": group['id'],
                    "name": group['name'],
                    "admin": group["admin"]
                }
                data.append(one)
            return web.json_response(status=200, data=data)
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
async def update_groupchat(request):
    groupchat_id = request.match_info['id']
    user = request.user['id']
    if request.content_type == 'application/json':
        raw_data = await request.json()
    elif request.content_type == 'application/x-www-form-urlencoded':
        raw_data = await request.post()
    else:
        return web.Response(status=400, text='content type must be json or urlencoded')
    try:
        async with Database.pool.acquire() as connection:
            if raw_data['name'].strip():
                check_name = await connection.fetch('''SELECT name FROM public.groupchat WHERE name = $1''', raw_data['name'].strip())
                if check_name:
                    return web.Response(status=400, text='name is busy')
            else:
                return web.Response(status=400, text='name must be not null')
            groupchat = await connection.fetch('''SELECT id FROM public.groupchat WHERE id = $1 AND admin = $2''', int(groupchat_id), user)
            if groupchat is None:
                return web.Response(status=403, text='no permission or community not found')
            else:
                await connection.execute('''UPDATE public.groupchat SET name = $1 WHERE id =$2 AND admin = $3''', raw_data['name'].strip(), int(groupchat_id), user)
                return web.Response(status=200, text='updated')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
async def delete_groupchat(request):
    groupchat_id = request.match_info['id']
    user = request.user['id']
    try:
        async with Database.pool.acquire() as connection:
            groupchat = await connection.fetch('''SELECT id, name, admin FROM public.groupchat WHERE id = $1 and admin = $2''', int(groupchat_id), user)
            if groupchat is None:
                return web.Response(status=403, text='community not found or you not have permission')
            else:
                await connection.execute('''DELETE FROM public.groupchat WHERE id = $1 AND admin = $2''', int(groupchat_id), user)
                return web.Response(status=200, text='deleted')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
async def add_user_to_groupchat(request):
    groupchat_id = request.match_info['id']
    user = request.user['id']
    if request.content_type == 'application/json':
        raw_data = await request.json()
    elif request.content_type == 'application/x-www-form-urlencoded':
        raw_data = await request.post()
    else:
        return web.Response(status=400, text='content type must be json or urlencoded')
    try:
        async with Database.pool.acquire() as connection:
            group = await connection.fetch('''SELECT id, name, admin FROM public.groupchat WHERE id = $1 AND admin = $2''', int(groupchat_id), user)
            if group is None:
                return web.Response(status=404, text='groupchat not found or you not have permissions')
            if raw_data['user']:
                if User.load_from_db(raw_data['user']):
                    subscribe_check = await connection.fetch('''SELECT user_id, groupchat_id FROM public.users_groupchat WHERE groupchat_id = $1 AND user_id = $2''', int(groupchat_id), raw_data['user'])
                    if subscribe_check:
                        return web.Response(status=400, text='user already subscribe')
                    sub = UsersGroup(user_id=raw_data['user'], groupchat_id=int(groupchat_id))
                    await sub.save_to_db()
                    return web.Response(status=200, text='user id={} is added to groupchat'.format(raw_data['user']))
                else:
                    return web.Response(status=400, text='user not found')
            else:
                return web.Response(status=400, text='user must be not None')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
async def delete_user_from_groupchat(request):
    groupchat_id = request.match_info['id']
    user = request.user['id']
    if request.content_type == 'application/json':
        raw_data = await request.json()
    elif request.content_type == 'application/x-www-form-urlencoded':
        raw_data = await request.post()
    else:
        return web.Response(status=400, text='content type must be json or urlencoded')
    try:
        async with Database.pool.acquire() as connection:
            group = await connection.fetch('''SELECT id, name, admin FROM public.groupchat WHERE id = $1 AND admin = $2''', int(groupchat_id), user)
            if group is None:
                return web.Response(status=404, text='groupchat not found or you not have permissions')
            if raw_data['user']:
                if User.load_from_db(raw_data['user']):
                    await connection.execute('''DELETE FROM public.users_groupchat WHERE user_id = $1 AND groupchat_id = $2''', raw_data['user'], int(groupchat_id))
                    return web.Response(status=200, text='user id={} is deleted from groupchat'.format(raw_data['user']))
                else:
                    return web.Response(status=400, text='user not found')
            else:
                return web.Response(status=400, text='user must be not None')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


