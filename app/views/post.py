from aiohttp import web
from models.post import Post
from middleware import login_required
from models.relations import UsersCommunity
from database import Database
import time


@login_required
async def create_post(request):
    community_id = request.match_info['community_id']
    user = request.user['id']
    try:
        if request.content_type == 'application/json':
            raw_data = await request.json()
        elif request.content_type == 'application/x-www-form-urlencoded':
            raw_data = await request.post()
        else:
            return web.Response(status=400, text='content type must be json or urlencoded')
        if raw_data['header'].strip() and raw_data['text'].strip() is None:
            return web.Response(status=400, text='header or text must be not None')
        async with Database.pool.acquire() as connection:
            community = await connection.fetch('''SELECT id, name, admin FROM public.community WHERE id = $1 AND admin = $2''', int(community_id), user)
            if community is None:
                return web.Response(status=403, text='you are not have permission or community not found')
            else:
                post = Post(community_id=int(community_id), header=raw_data['header'].strip(), text=raw_data['text'].strip(), date=time.time())
                await post.save_to_db()
                return web.Response(status=200, text='created')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
async def get_all_posts(request):
    community_id = request.match_info['community_id']
    user = request.user['id']
    try:
        async with Database.pool.acquire() as connection:
            community = await connection.fetch('''SELECT id, name, admin FROM public.community WHERE id = $1''', int(community_id))
            if community is None:
                return web.Response(status=404, text='community not found')
            subscribe_check = await connection.fetch('''SELECT user_id, community_id FROM public.users_community WHERE community_id = $1 AND user_id = $2''',int(community_id), user)
            if subscribe_check is None:
                return web.Response(status=403, text='you are not subscribe')
            else:
                post_list = await connection.fetch('''SELECT header, text, date FROM public.post WHERE community_id = $1 ORDER BY date ASC''', int(community_id))
                if post_list is None:
                    return web.Response(status=404, text='post not found')
                else:
                    data = []
                    for post in post_list:
                        one = {
                            "header": post['header'],
                            "text": post['text'],
                            "date": post['date']
                        }
                        data.append(one)
                    return web.json_response(status=200, data=data)
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
async def get_post_by_id(request):
    community_id = request.match_info['community_id']
    user = request.user['id']
    post_id = request.match_info['id']
    try:
        async with Database.pool.acquire() as connection:
            community = await connection.fetch('''SELECT id, name, admin FROM public.community WHERE id = $1''', int(community_id))
            if community is None:
                return web.Response(status=404, text='community not found')
            subscribe_check = await connection.fetch('''SELECT user_id, community_id FROM public.users_community WHERE community_id = $1 AND user_id = $2''', int(community_id), user)
            if subscribe_check is None:
                return web.Response(status=403, text='you are not subscribe')
            else:
                post = await connection.fetch('''SELECT header, text, date FROM public.post WHERE community_id = $1 AND id = $2''', int(community_id), int(post_id))
                if post is None:
                    return web.Response(status=404, text='post not found')
                else:
                    data = {
                        "header": post[0]['header'],
                        "text": post[0]['text'],
                        "date": post[0]['date']
                    }
                    return web.json_response(status=200, data=data)
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
async def update_post(request):
    community_id = request.match_info['community_id']
    user = request.user['id']
    post_id = request.match_info['id']
    try:
        if request.content_type == 'application/json':
            raw_data = await request.json()
        elif request.content_type == 'application/x-www-form-urlencoded':
            raw_data = await request.post()
        else:
            return web.Response(status=400, text='content type must be json or urlencoded')
        if raw_data['text'].strip() is None:
            return web.Response(status=400, text='header or text must be not None')
        async with Database.pool.acquire() as connection:
            community = await connection.fetch('''SELECT id, name, admin FROM public.community WHERE id = $1 AND admin = $2''', int(community_id), user)
            if community is None:
                return web.Response(status=403, text='You are not have permissions or community not found')
            await connection.execute('''UPDATE public.post SET text = $1 WHERE id = $2 AND community_id = $3''', raw_data['text'].strip(), int(post_id), int(community_id))
            return web.Response(status=200, text='updated')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
async def delete_post(request):
    community_id = request.match_info['community_id']
    user = request.user['id']
    post_id = request.match_info['id']
    try:
        async with Database.pool.acquire() as connection:
            community = await connection.fetch('''SELECT id, name, admin FROM public.community WHERE id = $1 AND admin = $2''', int(community_id), user)
            if community is None:
                return web.Response(status=403, text='You are not have permissions or community not found')
            await connection.execute('''DELETE FROM public.post WHERE community_id = $1 AND id = $2''', int(community_id), int(post_id))
            return web.Response(status=200, text='deleted')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
async def delete_all_posts(request):
    community_id = request.match_info['community_id']
    user = request.user['id']
    try:
        async with Database.pool.acquire() as connection:
            community = await connection.fetch('''SELECT id, name, admin FROM public.community WHERE id = $1 AND admin = $2''', int(community_id), user)
            if community is None:
                return web.Response(status=403, text='You are not have permissions or community not found')
            await connection.execute('''DELETE FROM public.post WHERE community_id = $1''', int(community_id))
            return web.Response(status=200, text='deleted')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))
