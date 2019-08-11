from aiohttp import web
from middleware import login_required
from models.message import Message
from database import Database
from models.user import User
from models.chat import Chat
import datetime
import time

async def create_message(request):
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
            try:
                if raw_data['content'] and len(raw_data['content']) <= 4096:
                    date = time.time()
                    message = Message(chat_id=chat[0]['id'], sender=user_id, content=raw_data['content'], date=int(date))
                    await message.save_to_db()
                    return web.Response(status=200, text=raw_data['content'])
                else:
                    return web.Response(status=400, text='message must be not Empty')
            except Exception as error:
                return web.Response(status=400, text=str(error))
    except Exception as error:
        return web.Response(status=400, text=str(error))


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
                    'text': message['content'],
                    'date': message['date']
                }
                message_list.append(one)
            return web.json_response(status=200, data=message_list)
    except Exception as error:
        return web.Response(status=400, text=str(error))
