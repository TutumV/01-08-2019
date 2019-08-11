from views.user import get_all_users, create_user, profile, login, logout, get_user_by_id, \
                        update_user_by_id, delete_user_by_id


def user_setup_routes(app):
    # get all
    app.router.add_get('/api/users/', get_all_users)
    # create new user
    app.router.add_post('/api/users/', create_user)
    # get profile
    app.router.add_get('/api/users/me/', profile)
    # login
    app.router.add_post('/api/users/login/', login)
    # logout
    app.router.add_post('/api/users/logout/', logout)
    # get user by id
    app.router.add_get('/api/users/{id}/', get_user_by_id)
    # update user by id
    app.router.add_put('/api/users/{id}/', update_user_by_id)
    # delete user by id
    app.router.add_delete('/api/users/{id}/', delete_user_by_id)
