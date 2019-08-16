from views.groupchat import *


def groupchat_setup_routes(app):
    # create groupchat
    app.router.add_post('/api/groupchat/', create_groupchat)
    # get all groupchat
    app.router.add_get('/api/groupchat/', get_all_groupchat)
    # update groupchat
    app.router.add_patch('/api/groupchat/{id}/', update_groupchat)
    #delete groupchat
    app.router.add_delete('/api/groupchat/{id}/', delete_groupchat)
    # add new users to groupchat
    app.router.add_post('/api/groupchat/{id}/', add_user_to_groupchat)
    # kick user from groupchat
    app.router.add_delete('/api/groupchat/{id}/', delete_user_from_groupchat)