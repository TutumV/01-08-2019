from views.message import *


def message_setup_routes(app):
    # get all messages in chat
    app.router.add_get('/api/chat/message/{chat_id}/', get_chat_messages)
    # send message in chat
    app.router.add_post('/api/chat/message/{chat_id}/', create_chat_message)
    # delete all messages from chat
    app.router.add_delete('/api/chat/message/{chat_id}/', delete_chat_messages)
    # delete message by id from chat
    app.router.add_delete('/api/chat/message/{chat_id}/{message_id}/', delete_chat_message_by_id)
    # edit message in chat
    app.router.add_patch('/api/chat/message/{chat_id}/{message_id}/', edit_chat_message)
    # get all message in group
    app.router.add_get('/api/group/message/{group_id}/', get_group_messages)
    # create message in group
    app.router.add_post('/api/group/message/{group_id}/', create_group_message)
    # delete group message
    app.router.add_delete('/api/group/message/{group_id}/', delete_group_message)
    # delete group message by id
    app.router.add_delete('/api/group/{group_id}/message/{message_id}/', delete_group_message_by_id)
    # edit group message by id
    app.router.add_patch('/api/group/{group_id}/message/{message_id}/', edit_group_message)