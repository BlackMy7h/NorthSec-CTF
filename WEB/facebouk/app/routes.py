import os
import base64

import jwt as pyjwt
from flask import (
    render_template, request, redirect, url_for,
    flash, session, jsonify, make_response,
)
from sqlalchemy import or_, and_
from app import app, db
from app.models import User, Post, Comment, Friendship
from datetime import date, datetime


def _require_login():
    if 'user_id' not in session:
        return False
    return True


def _set_session_user(user: User) -> None:
    session['user_id'] = user.id
    session['user_full_name'] = user.full_name
    session['user_first_name'] = user.first_name


def _issue_jwt(user: User) -> str:
    payload = {
        'user_id': user.id,
        'is_admin': user.is_admin,
        'iat': int(datetime.utcnow().timestamp()),
    }
    return pyjwt.encode(payload, app.config['JWT_SECRET'], algorithm='HS256')


def _friend_ids(user_id: int) -> list[int]:
    rows = Friendship.query.filter(
        and_(Friendship.status == 'accepted', or_(Friendship.user_id_1 == user_id, Friendship.user_id_2 == user_id))
    ).all()

    ids: list[int] = []
    for r in rows:
        ids.append(r.user_id_2 if r.user_id_1 == user_id else r.user_id_1)
    return ids


@app.context_processor
def inject_current_user():
    return {
        'current_user_id': session.get('user_id'),
        'current_user_name': session.get('user_first_name'),
        'current_user_full_name': session.get('user_full_name'),
    }


@app.route('/robots.txt')
def robots_txt():
    resp = make_response("User-agent: *\nDisallow: /api/\n", 200)
    resp.headers['Content-Type'] = 'text/plain'
    return resp


@app.route('/api/v1/debug/config')
def debug_config():
    # Legacy debug endpoint — leaks the JWT signing secret encoded as base64
    ref = base64.b64encode(app.config['JWT_SECRET'].encode()).decode()
    return jsonify({'_ref': ref})


@app.route('/')
@app.route('/index.php')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login.php', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('pass')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        _set_session_user(user)
        resp = make_response(redirect(url_for('dashboard')))
        resp.set_cookie('fb_token', _issue_jwt(user), httponly=False, samesite='Lax')
        return resp

    flash('Invalid email or password.', 'error')
    return redirect(url_for('index'))


@app.route('/r.php', methods=['POST'])
def register():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('reg_email__')
    password = request.form.get('reg_passwd__')
    sex_val = request.form.get('sex')

    month = int(request.form.get('birthday_month', 1))
    day = int(request.form.get('birthday_day', 1))
    year = int(request.form.get('birthday_year', 2010))

    if not (firstname and lastname and email and password):
        flash('All primary fields required.', 'error')
        return redirect(url_for('index'))

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('That email is already registered.', 'error')
        return redirect(url_for('index'))

    gender = "Female" if sex_val == "1" else "Male" if sex_val == "2" else "Unknown"

    try:
        birthday_date = date(year, month, day)
    except ValueError:
        birthday_date = None

    new_user = User(
        first_name=firstname,
        last_name=lastname,
        email=email,
        gender=gender,
        birthday=birthday_date,
        profile_pic_url="https://i.pravatar.cc/200?img=8",
        cover_quote=None,
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    _set_session_user(new_user)
    resp = make_response(redirect(url_for('dashboard')))
    resp.set_cookie('fb_token', _issue_jwt(new_user), httponly=False, samesite='Lax')
    return resp


@app.route('/home.php')
def dashboard():
    if not _require_login():
        return redirect(url_for('index'))

    uid = int(session['user_id'])
    fids = _friend_ids(uid)

    visible_authors = fids + [uid]

    feed_posts = (
        Post.query
        .filter(Post.author_id.in_(visible_authors))
        .order_by(Post.timestamp.desc())
        .limit(40)
        .all()
    )

    return render_template('dashboard.html', feed_posts=feed_posts)


@app.route('/post.php', methods=['POST'])
def create_post():
    if not _require_login():
        return redirect(url_for('index'))

    content = (request.form.get('content') or '').strip()
    if not content:
        return redirect(url_for('dashboard'))

    uid = int(session['user_id'])
    p = Post(author_id=uid, target_user_id=None, content=content, timestamp=datetime.utcnow())
    db.session.add(p)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/profile.php', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST' and 'user_id' not in session:
        return redirect(url_for('index'))

    default_id = session.get('user_id', 1)
    try:
        profile_id = int(request.args.get('id', default_id))
    except (TypeError, ValueError):
        profile_id = int(default_id)

    if request.method == 'POST':
        content = (request.form.get('content') or '').strip()
        if content:
            uid = int(session['user_id'])
            p = Post(author_id=uid, target_user_id=profile_id, content=content, timestamp=datetime.utcnow())
            db.session.add(p)
            db.session.commit()
        return redirect(f"/profile.php?id={profile_id}")

    profile_user = User.query.get_or_404(profile_id)

    fids = _friend_ids(profile_user.id)
    friends = User.query.filter(User.id.in_(fids)).order_by(User.first_name.asc()).all() if fids else []

    wall_posts = (
        Post.query
        .filter(or_(Post.target_user_id == profile_user.id, and_(Post.author_id == profile_user.id, Post.target_user_id.is_(None))))
        .order_by(Post.timestamp.desc())
        .limit(40)
        .all()
    )

    show_flag = False
    flag_b64 = ''
    token = request.cookies.get('fb_token')
    if token and profile_user.is_admin:
        try:
            payload = pyjwt.decode(token, app.config['JWT_SECRET'], algorithms=['HS256'])
            if payload.get('is_admin'):
                show_flag = True
                flag = os.environ.get('FLAG', 'NSC{flag_not_set}')
                flag_b64 = base64.b64encode(flag.encode()).decode()
        except pyjwt.PyJWTError:
            pass

    return render_template(
        'profile.html',
        profile_user=profile_user,
        friends=friends,
        wall_posts=wall_posts,
        show_flag=show_flag,
        flag_b64=flag_b64,
    )


@app.route('/logout.php')
def logout():
    session.clear()
    resp = make_response(redirect(url_for('index')))
    resp.delete_cookie('fb_token')
    return resp


@app.before_request
def _legacy_php_normalization():
    """Normalize historic php-style endpoints."""
    return None
