from flask_login import current_user
from app import app
from flask import render_template, request, redirect, url_for, flash



from .models import User

import requests

@app.route('/')
def index():
    users = User.query.order_by(User.username).all()
    new_list = []
    following_set = set()
    if current_user.is_authenticated:
        following = current_user.followed.all()
        following_set = {f.id for f in following}
    for u in users:
        if u.id in following_set:
            u.flag = True        

    return render_template('index.html', names=users)

