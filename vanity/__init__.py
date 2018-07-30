# -*- coding: utf-8 -*-
"""
    vanity
    ~~~~~~

    A vanity Plugin for FlaskBB.

    :copyright: (c) 2018 by Михаил Лебедев.
    :license: BSD License, see LICENSE for more details.
"""
import os

from flask import Blueprint, request, redirect, url_for, abort
from flaskbb.utils.helpers import render_template
from flask_login import current_user

from .models import Post, User


__version__ = "0.0.1"


# connect the hooks
def flaskbb_load_migrations():
    return os.path.join(os.path.dirname(__file__), "migrations")


def flaskbb_tpl_post_menu_before(post):
    return render_template("vanity_like_button.html", post=post)


def flaskbb_tpl_post_author_info_after(user, post):
    return ('<div>Likes given: {}</div><div>Likes received: {}</div>'
            .format(user.likes_given, user.likes_received))



def flaskbb_load_blueprints(app):
    app.register_blueprint(
        bp,
        url_prefix="/vanity"
    )


bp = Blueprint("vanity", __name__, template_folder="templates")


@bp.route('/like/<int:id>', methods=['POST'])
def like(id):
    post = Post.query.filter(Post.id == id).first_or_404()
    if current_user not in post.likers and post.allowed_to_like(current_user):
        post.likers.append(current_user)
        post.user.likes_received += 1
        current_user.likes_given += 1
        post.save()
        return redirect(post.url)
    else:
        abort(403)


@bp.route('/withdraw_like/<int:id>', methods=['POST'])
def withdraw_like(id):
    post = Post.query.filter(Post.id == id).first_or_404()
    if current_user in post.likers and post.allowed_to_like(current_user):
        post.likers.remove(current_user)
        post.user.likes_received -= 1
        current_user.likes_given -= 1
        post.save()
        return redirect(post.url)
    else:
        abort(403)


SETTINGS = {}
