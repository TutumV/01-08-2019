from views.post import *


def post_setup_routes(app):
    # create post
    app.router.add_post('/api/community/{community_id}/post/', create_post)
    # get all posts by community
    app.router.add_get('/api/community/{community_id}/post/', get_all_posts)
    # get post by id
    app.router.add_get('/api/community/{community_id}/post/{id}/', get_post_by_id)
    # update post
    app.router.add_patch('/api/community/{community_id}/post/{id}/', update_post)
    # delete post
    app.router.add_delete('/api/community/{community_id}/post/{id}/', delete_post)
    # delete all posts
    app.router.add_delete('/api/community/{community_id}/post/', delete_all_posts)
