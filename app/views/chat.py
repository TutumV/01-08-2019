from aiohttp import web
from middleware import login_required
from models.chat import Chat
from database import Database
from models.user import User


@login_required
async def create_chat(request):
    if request.content_type == 'application/json':
        raw_data = await request.json()
    elif request.content_type == 'application/x-www-form-urlencoded':
        raw_data = await request.post()
    else:
        return web.Response(status=400, text='content type must be json or urlencoded')
    try:
        creator = await User.load_from_db(request.user['id'])
        participant = await User.load_from_db(raw_data['member'])
        if creator and participant:
            creator_id = request.user['id']
            participant_id = raw_data['member']
            if creator_id == participant_id:
                return web.Response(status=400, text='you cannot create chat with yourself')
            async with Database.pool.acquire() as connection:
                chat_maker = await connection.fetch('''SELECT id, name FROM PUBLIC.chat WHERE creator = $1 AND participant = $2 ''', creator_id, participant_id)
                chat_participant = await connection.fetch('''SELECT id, name FROM PUBLIC.chat WHERE creator = $1 AND participant = $2''', participant_id, creator_id)
            if chat_maker:
                data = {
                    "id": chat_maker[0]['id'],
                    "name": chat_maker[0]['name']
                }
                return web.json_response(status=200, data=data)
            elif chat_participant:
                data = {
                    "id": chat_participant[0]['id'],
                    "name": chat_participant[0]['name']
                }
                return web.json_response(status=200, data=data)
            else:
                if raw_data['name'].strip():
                    name = raw_data['name']
                    chat = Chat(creator=creator_id, participants=participant_id, name=name)
                    await chat.save_to_db()
                    return web.json_response(status=201, text='chat created')
    except Exception as error:
        return web.Response(status=400, text=str(error))


@login_required
async def get_all_chats(request):
    try:
        user_id = request.user['id']
        chat_list = []
        async with Database.pool.acquire() as connection:
            chats = await connection.fetch('''SELECT id, name FROM public.chat WHERE creator= $1 OR participant = $1''', user_id)
            if chats:
                for chat in chats:
                    data = {
                        "id": chat['id'],
                        "name": chat['name']
                    }
                    chat_list.append(data)
        return web.json_response(status=200, data=chat_list)
    except Exception as error:
        return web.Response(status=404, text=str(error))


@login_required
async def get_chat_by_id(request):
    user_id = request.user['id']
    chat_id = request.match_info['id']
    try:
        async with Database.pool.acquire() as connection:
            chat = await connection.fetch('''SELECT id, name FROM public.chat WHERE id = $1 AND creator = $2 OR participant = $2''', int(chat_id), user_id)
            if chat:
                data = {
                    "id": chat[0]['id'],
                    'name': chat[0]['name']
                }
        return  web.json_response(status=200, data=data)
    except Exception as error:
        return  web.Response(status=404, text=str(error))


@login_required
async def delete_chat_by_id(request):
    chat_id = request.match_info['id']
    user_id = request.user['id']
    try:
        async with Database.pool.acquire() as connection:
            await connection.execute('''DELETE FROM public.chat WHERE id = $1 AND creator = $2 OR participant = $2''', int(chat_id), user_id)
            return web.json_response(status=200, text='chat deleted')
    except Exception as error:
        return web.Response(status=404, text=str(error))


@login_required
async def update_chat_by_id(request):
    chat_id = request.match_info['id']
    user_id = request.user['id']
    if request.content_type == 'application/json':
        raw_data = await request.json()
    elif request.content_type == 'application/x-www-form-urlencoded':
        raw_data = await request.post()
    else:
        return web.Response(status=400, text='content type must be json or urlencoded')
    try:
        if raw_data['name'].strip():
            async with Database.pool.acquire() as connection:
                await connection.execute('''UPDATE public.chat SET name = $1 WHERE id = $2 AND creator = $3 OR participant = $3''', raw_data['name'], int(chat_id), user_id)
                chat = await connection.fetch('''SELECT id, name FROM public.chat WHERE id = $1''', int(chat_id))
                data = {
                    "id": chat[0]['id'],
                    "name": chat[0]['name']
                }
                return web.json_response(status=200, data=data)
        else:
            return web.Response(status=400, text='name must be not None')
    except Exception as error:
        return web.Response(status=404, text=str(error))