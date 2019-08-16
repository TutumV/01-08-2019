from aiohttp import web
from middleware import login_required, check_subscribe
from models.message import Message
from database import Database
import time


@login_required
async def create_chat_message(request):
    chat_id = request.match_info['chat_id']
    user_id = request.user['id']
    try:
        async with Database.pool.acquire() as connection:
            chat = await connection.fetch('''SELECT id, name FROM public.chat WHERE id = $1 AND creator = $2 OR participant = $2''', int(chat_id), user_id)
            if chat is None:
                return web.Response(status=404, text='chat is not found or you not have permission')
            if request.content_type == 'application/json':
                raw_data = await request.json()
            elif request.content_type == 'application/x-www-form-urlencoded':
                raw_data = await request.post()
            else:
                return web.Response(status=400, text='content type must be json or urlencoded')
            try:
                if raw_data['content'].strip() and len(raw_data['content'].strip()) <= 4096:
                    date = time.time()
                    message = Message(chat_id=chat[0]['id'], sender=user_id, content=raw_data['content'], date=int(date), group_id=None)
                    await message.save_to_db()
                    return web.Response(status=200, text=raw_data['content'])
                else:
                    return web.Response(status=400, text='message must be not Empty')
            except Exception as error:
                return web.Response(status=400, text=str(error))
    except Exception as error:
        return web.Response(status=400, text=str(error))


@login_required
async def get_chat_messages(request):
    user_id = request.user['id']
    chat_id = request.match_info['chat_id']
    try:
        async with Database.pool.acquire() as connection:
            chat = await connection.fetch('''SELECT id  FROM public.chat WHERE id = $1 AND participant = $2 OR creator =$2''', int(chat_id), user_id)
            if chat:
                messages = await connection.fetch('''SELECT id, content, date FROM public.message WHERE chat_id = $1 ORDER BY date ASC''', int(chat_id))
        if messages:
            message_list = []
            for message in messages:
                one = {
                    'id': message['id'],
                    'chat_name': chat['name'],
                    'text': message['content'],
                    'date': message['date']
                }
                message_list.append(one)
            return web.json_response(status=200, data=message_list)
    except Exception as error:
        return web.Response(status=400, text=str(error))


@login_required
async def delete_chat_message_by_id(request):
    user_id = request.user['id']
    chat_id = request.match_info['chat_id']
    message_id = request.match_info['message_id']
    try:
        async with Database.pool.acquire() as connection:
            chat = await connection.fetch('''SELECT id  FROM public.chat WHERE id = $1 AND participant = $2 OR creator =$2''', int(chat_id), user_id)
            if chat:
                message = await connection.fetch('''SELECT id, content, sender FROM public.message WHERE sender = $1 AND chat_id = $2 AND id = $3''', user_id, int(chat_id), int(message_id))
                if message:
                    await connection.execute('''DELETE FROM public.message WHERE id= $1''', int(message_id))
                    return web.Response(status=200, text='deleted')
    except Exception as error:
        return web.Response(status=404, text=str(error))


@login_required
async def delete_chat_messages(request):
    user_id = request.user['id']
    chat_id = request.match_info['chat_id']
    try:
        async with Database.pool.acquire() as connection:
            chat = await connection.fetch('''SELECT id  FROM public.chat WHERE id = $1 AND participant = $2 OR creator =$2''', int(chat_id), user_id)
            if chat:
                await connection.execute('''DELETE FROM public.message WHERE sender = $1 AND chat_id = $2''', user_id, int(chat_id))
                return web.Response(status=200, text='ok')
    except Exception as error:
        return web.Response(status=400, text=str(error))


@login_required
async def edit_chat_message(request):
    user_id = request.user['id']
    chat_id = request.match_info['chat_id']
    message_id = request.match_info['message_id']
    if request.content_type == 'application/json':
        raw_data = await request.json()
    elif request.content_type == 'application/x-www-form-urlencoded':
        raw_data = await request.post()
    else:
        return web.Response(status=400, text='content type must be json or urlencoded')
    if raw_data['content'].strip():
        try:
            async with Database.pool.acquire() as connection:
                chat = await connection.fetch('''SELECT id  FROM public.chat WHERE id = $1 AND participant = $2 OR creator =$2''', int(chat_id), user_id)
                if chat is None:
                    return web.Response(status=404, text='chat is not found')
                message = await connection.fetch('''SELECT id, content, sender FROM public.message WHERE sender = $1 AND chat_id = $2 AND id = $3''', user_id, int(chat_id), int(message_id))
                if message is None:
                    return web.Response(status=404, text='message is not found')
                await connection.execute('''UPDATE public.message SET content = $1 WHERE id = $2''', raw_data['content'], int(message_id))
                return web.Response(status=200, text='updated')
        except Exception as error:
            return web.Response(status=404, text=str(error))
    else:
        return web.Response(status=400, text='content must be not NULL')


@login_required
@check_subscribe
async def get_group_messages(request):
    group_id = request.match_info['group_id']
    try:
        async with Database.pool.acquire() as connection:
            messages_list = await connection.fetch('''SELECT id, group_id, content, sender, date FROM public.message WHERE group_id = $1 ORDER BY date ASC''', int(group_id))
            data = []
            if messages_list is None:
                return web.json_response(status=200, data=data)
            for message in messages_list:
                one = {
                    "id": message['id'],
                    "group_id": message['group_id'],
                    "content": message['content'],
                    "sender": message['sender'],
                    "date": message['date']
                }
                data.append(one)
            return web.json_response(status=200, data=data)
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
@check_subscribe
async def create_group_message(request):
    group_id = request.match_info['group_id']
    user = request.user['id']
    if request.content_type == 'application/json':
        raw_data = await request.json()
    elif request.content_type == 'application/x-www-form-urlencoded':
        raw_data = await request.post()
    else:
        return web.Response(status=400, text='content type must be json or urlencoded')
    try:
        if raw_data['content'].strip() and len(raw_data['content'].strip()) <= 4096:
            date = time.time()
            message = Message(group_id=int(group_id), sender=user, content=raw_data['content'], date=int(date), chat_id=None)
            await message.save_to_db()
            return web.Response(status=200, text=raw_data['content'])
        else:
            return web.Response(status=400, text='message must be not Empty')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
@check_subscribe
async def delete_group_message(request):
    group_id = request.match_info['group_id']
    user = request.user['id']
    try:
        async with Database.pool.acquire() as connection:
            await connection.execute('''DELETE FROM public.message WHERE group_id = $1 AND sender = $2''', int(group_id), user)
            return web.Response(status=200, text='deleted')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
@check_subscribe
async def delete_group_message_by_id(request):
    group_id = request.match_info['group_id']
    user = request.user['id']
    message_id = request.match_info['message_id']
    try:
        async with Database.pool.acquire() as connection:
            message = await connection.fetch('''SELECT id FROM public.message WHERE id = $1''', int(message_id))
            if message is None:
                return web.Response(status=404, text='message not found')
            await connection.execute('''DELETE FROM public.message WHERE group_id = $1 AND sender = $2 AND id = $3''', int(group_id), user, int(message_id))
            return web.Response(status=200, text='deleted')
    except Exception as error:
        print(error)
        return web.Response(status=400, text=str(error))


@login_required
@check_subscribe
async def edit_group_message(request):
    group_id = request.match_info['group_id']
    user = request.user['id']
    message_id = request.match_info['message_id']
    if request.content_type == 'application/json':
        raw_data = await request.json()
    elif request.content_type == 'application/x-www-form-urlencoded':
        raw_data = await request.post()
    else:
        return web.Response(status=400, text='content type must be json or urlencoded')
    if raw_data['content'].strip():
        try:
            async with Database.pool.acquire() as connection:
                message = await connection.fetch('''SELECT id FROM public.message WHERE id = $1 AND sender = $2 AND group_id = $3''', int(message_id), user, int(group_id))
                if message is None:
                    return web.Response(status=404, text='message not found or you not have permissions')
                await connection.execute('''UPDATE public.message SET content = $1 WHERE id = $2''', raw_data['content'], int(message_id))
                return web.Response(status=200, text='updated')
        except Exception as error:
            print(error)
            return web.Response(status=400, text=str(error))
