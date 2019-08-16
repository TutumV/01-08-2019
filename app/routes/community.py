from views.community import *


def community_setup_routes(app):
    # create new community
    app.router.add_post('/api/community/', create_community)
    # get all communities
    app.router.add_get('/api/community/', get_all_community)
    # get communities by id
    app.router.add_get('/api/community/{id}/', get_community_by_id)
    # sub
    app.router.add_post('/api/community/{id}/subscribe/', subscribe_to_community)
    # unsub
    app.router.add_post('/api/community/{id}/unsubscribe/', unsubscribe_from_community)
    # update community
    app.router.add_patch('/api/community/{id}/', update_community)
    # delete community
    app.router.add_delete('/api/community/{id}/', delete_community)