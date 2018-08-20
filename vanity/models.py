from flaskbb.extensions import db
from flaskbb.forum.models import Post
from flaskbb.user.models import User
from sqlalchemy.ext.associationproxy import association_proxy


def _Post_allowed_to_like(self, user):
    return all((
        self,
        self.topic,
        not self.topic.locked,
        not self.topic.forum.locked,
        not user.is_anonymous,
        not self.user == user,
        ({g.id for g in self.topic.forum.groups} &
            {g.id for g in user.groups})
    ))


Post.allowed_to_like = _Post_allowed_to_like


User.likes_received = db.Column(db.Integer, nullable=False, default=0)
User.likes_given = db.Column(db.Integer, nullable=False, default=0)


def _get_userlike(user):
    return UserLike.query.filter(UserLike.id == user.id).first()


class PostLike(db.Model):
    __tablename__ = 'vanity_postlikes'

    post_id = db.Column(db.ForeignKey('posts.id'), primary_key=True)
    post = db.relationship(Post, backref=db.backref("liked_by_users", cascade='all, delete-orphan'))
    user_like_id = db.Column(db.ForeignKey('vanity_userlikes.id'), primary_key=True)
    user = association_proxy(
        "user_likes", "user",
        creator=_get_userlike
    )


# this model exists to break the cyclic references
class UserLike(db.Model):
    __tablename__ = 'vanity_userlikes'

    id = db.Column(db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(
        User,
        uselist=False,
        backref=db.backref(
            "user_liked_posts",
            lazy='joined',
            uselist=False
        ),
    )
    post_likes = db.relationship(
        PostLike,
        backref=db.backref(
            "user_likes",
            lazy="joined",
        ),
        primaryjoin="UserLike.id == PostLike.user_like_id"
    )

    liked_posts = association_proxy("post_likes", "post")


#User.liked_posts = association_proxy("user_liked_posts", "liked_posts")
Post.likers = association_proxy(
    "liked_by_users", "user",
    creator=lambda user: PostLike(user=user)
)
