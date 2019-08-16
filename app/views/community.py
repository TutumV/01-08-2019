from aiohttp import web
from database import Database
from models.community import Community
from models.relations import UsersCommunity
from middleware import login_required


@login_required
async def create_community(request):
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
                name = await connection.fetch('''SELECT id, name FROM public.community WHERE name = $1''', raw_data['name'])
                if name:
                    return web.Response(status=400, text='name is busy')
                community = Community(name=raw_data['name'].strip(), admin=admin)
                await community.save_to_db()
                community = await connection.fetch('''SELECT id, name, admin FROM public.community WHERE name = $1 AND admin = $2''', raw_data['name'].strip(), admin)
                data = {
                    "id": community[0]['id'],
                    "name": community[0]['name'],
                    "admin_id": community[0]['admin']
                }
                return web.json_response(status=201, data=data)
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
async def get_all_community(request):
    try:
        async with Database.pool.acquire() as connection:
            community_list = await connection.fetch('''SELECT id, name, admin FROM public.community''')
            if community_list:
                data = []
                for community in community_list:
                    one = {
                        "id": community['id'],
                        "name": community['name'],
                        'admin_id': community['admin']
                    }
                    data.append(one)
                return web.json_response(status=200, data=data)
            else:
                return web.Response(status=404, text='community not found')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
async def get_community_by_id(request):
    community_id = request.match_info['id']
    try:
        async with Database.pool.acquire() as connection:
            community = await connection.fetch('''SELECT id, name, admin FROM public.community WHERE id = $1''', int(community_id))
            if community:
                data = {
                        "id": community[0]['id'],
                        "name": community[0]['name'],
                        'admin_id': community[0]['admin']
                    }
                return web.json_response(status=200, data=data)
            else:
                return web.Response(status=404, text='community not found')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
async def subscribe_to_community(request):
    community_id = request.match_info['id']
    user = request.user['id']
    try:
        async with Database.pool.acquire() as connection:
            community = await connection.fetch('''SELECT id, name, admin FROM public.community WHERE id = $1''', int(community_id))
            if community is None:
                return web.Response(status=404, text='community not found')
            subscribe_check = await connection.fetch('''SELECT user_id, community_id FROM public.users_community WHERE community_id = $1 AND user_id = $2''', int(community_id), user)
            if subscribe_check:
                return web.Response(status=400, text='you already subscribe')
            else:
                sub = UsersCommunity(user_id=user, community_id=int(community_id))
                await sub.save_to_db()
                return web.Response(status=200, text='you are subscribe')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
async def unsubscribe_from_community(request):
    community_id = request.match_info['id']
    user = request.user['id']
    try:
        async with Database.pool.acquire() as connection:
            community = await connection.fetch('''SELECT id, name, admin FROM public.community WHERE id = $1''', int(community_id))
            if community is None:
                return web.Response(status=404, text='community not found')
            subscribe_check = await connection.fetch('''SELECT user_id, community_id FROM public.users_community WHERE community_id = $1 AND user_id = $2''', int(community_id), user)
            if subscribe_check:
                await connection.execute('''DELETE FROM public.users_community WHERE user_id = $1 AND community_id = $2''', user, int(community_id))
                return web.Response(status=200, text='you are unsubscribe')
            else:
                return web.Response(status=400, text='you are not subscribe')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
async def update_community(request):
    community_id = request.match_info['id']
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
                check_name = await connection.fetch('''SELECT name FROM public.community WHERE name = $1''', raw_data['name'].strip())
                if check_name:
                    return web.Response(status=400, text='name is busy')
            else:
                return web.Response(status=400, text='name must be not null')
            community = await connection.fetch('''SELECT id FROM public.community WHERE id = $1 AND admin = $2''', int(community_id), user)
            if community is None:
                return web.Response(status=403, text='no permission or community not found')
            else:
                await connection.execute('''UPDATE public.community SET name = $1 WHERE id =$2 AND admin = $3''', raw_data['name'].strip(),  int(community_id), user)
                return web.Response(status=200, text='updated')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
async def delete_community(request):
    community_id = request.match_info['id']
    user = request.user['id']
    try:
        async with Database.pool.acquire() as connection:
            community = await connection.fetch('''SELECT id, name, admin FROM public.community WHERE id = $1 and admin = $2''', int(community_id), user)
            if community is None:
                return web.Response(status=403, text='community not found or you not have permission')
            else:
                await connection.execute('''DELETE FROM public.community WHERE id = $1 AND admin = $2''', int(community_id), user)
                return web.Response(status=200, text='deleted')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))

