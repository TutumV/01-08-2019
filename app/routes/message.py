from views.message import *


def message_setup_routes(app):
    # get all messages in chat
    app.router.add_get('/api/message/{chat_id}/', get_chat_messages)
    # send message
    app.router.add_post('/api/message/{chat_id}/', create_message)
