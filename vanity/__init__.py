# -*- coding: utf-8 -*-
"""
    vanity
    ~~~~~~

    A vanity Plugin for FlaskBB.

    :copyright: (c) 2018 by Михаил Лебедев.
    :license: BSD License, see LICENSE for more details.
"""
import os

from flask import Blueprint, redirect, abort, request
from flaskbb.utils.helpers import render_template
from flaskbb.display.navigation import NavigationLink
from flaskbb.utils.settings import flaskbb_config
from flaskbb.forum.models import Topic, Forum
from flaskbb.user.models import Group
from flask_login import current_user

from .models import Post, User, PostLike


__version__ = "0.1.0"


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
        if post.user:
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
        if post.user:
            post.user.likes_received -= 1
        current_user.likes_given -= 1
        post.save()
        return redirect(post.url)
    else:
        abort(403)


@bp.route('/<username>/liked_posts')
def liked_posts(username):
    page = request.args.get('page', 1, type=int)

    group_ids = [g.id for g in current_user.groups]

    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.outerjoin(
        PostLike, Post.id == PostLike.post_id
    ).filter(
        PostLike.user_id == user.id,
        Post.topic_id == Topic.id,
        Topic.forum_id == Forum.id,
        Forum.groups.any(Group.id.in_(group_ids))
    ).order_by(
        Post.id.desc()
    ).paginate(page, flaskbb_config['POSTS_PER_PAGE'], False)

    return render_template('liked_posts.html', user=user, posts=posts)


def flaskbb_tpl_profile_sidebar_links(user):
    return NavigationLink(
        endpoint='vanity.liked_posts',
        name='Liked posts',
        icon='fa fa-heart',
        urlforkwargs={'username': user.username},
    ),


SETTINGS = {}
