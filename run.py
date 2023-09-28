from app import *


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(username='testuser',
                                email='example@example.com',
                                password='password')
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)
    app.config['WTF_CSRF_ENABLED'] = True