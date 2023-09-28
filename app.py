from flask import Flask, g, render_template, flash, redirect, url_for, abort, request
from flask_bcrypt import check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

import forms
import models

DEBUG = True
PORT = 8080
HOST = 'localhost'

app = Flask(__name__)
app.secret_key = "Your only limit is your mind."

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None
    

@app.before_request
def before_request():
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('stream'))
    
    # If validation fails, collect the validation errors
    validation_errors = form.errors
    
    return render_template('register.html', form=form, validation_errors=validation_errors)


@app.route('/search_users', methods=['GET', 'POST'])
@login_required
def search_users():
    ...
    return url_for('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Invalid email or password.", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Logged in.", 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password', 'error')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out, See you soon', 'success')
    return redirect(url_for('index'))


@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def post():
    form = forms.PostForm(request.form)
    if request.method == 'POST' and form.validate():
        models.Post.create(user=g.user._get_current_object(),
                           content=form.content.data.strip())
        flash('Posted.', 'success')
        return redirect(url_for('index'))
    return render_template('post.html', form=form)


@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    template = 'stream.html'
    if username and username != current_user.username:
        try: 
            user = models.User.select().where(
                # case-insensitive "like" search in peewee
                models.User.username**username   
            ).get()
        except models.DoesNotExist:
            abort(404)
        else:
            stream = user.get_stream().limit(100)
            # user = current_user
        if username:
            template = 'user_stream.html'
        return render_template(template, stream=stream, user=user)
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>')
def view_post(post_id):
    posts = models.Post.select().where(models.Post.id == post_id)
    if posts.count() == 0:
        abort(404)
    return render_template('stream.html', tsream=posts)


@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.create(
                from_user=g.user._get_current_object(),
                to_user=to_user
            )
        except models.IntegrityError:
            pass
        else:
            flash(f'You are following {to_user.username}, success')
    return redirect(url_for('stream', username=to_user.username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.get(
                from_user=g.user._get_current_object(),
                to_user=to_user
            ).delete_instance()
        except models.IntegrityError:
            pass
        else:
            flash(f'You have unfollowed {to_user.username}', 'success')
    return redirect(url_for('stream', username=to_user.username))


@app.route('/')
def index():
    stream = models.Post.select().limit(100)
    return render_template('stream.html', stream=stream)



@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.route('/following')
@login_required
def following():
    # Get the current user's followees (users being followed)
    followees = models.User.select().join(
        models.Relationship, on=(models.User.id == models.Relationship.to_user)
    ).where(models.Relationship.from_user == g.user._get_current_object())

    user_ids = [followee.id for followee in followees]
    user_ids.append(g.user._get_current_object().id)

    stream = models.Post.select().where(models.Post.user_id.in_(user_ids)).limit(100)

    return render_template('stream.html', stream=stream)
