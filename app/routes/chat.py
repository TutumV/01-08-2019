from views.chat import *


def chat_setup_routes(app):
    # create chat
    app.router.add_post('/api/chat/', create_chat)
    # get all user chats
    app.router.add_get('/api/chat/all/', get_all_chats)
    # delete chat by id
    app.router.add_delete('/api/chat/{id}/', delete_chat_by_id)
    # get chat detail
    app.router.add_get('/api/chat/{id}/', get_chat_by_id)
    # update chat name
    app.router.add_put('/api/chat/{id}/', update_chat_by_id)
