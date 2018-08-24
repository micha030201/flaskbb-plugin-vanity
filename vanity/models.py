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


class PostLike(db.Model):
    __tablename__ = 'vanity_association'

    post_id = db.Column(db.ForeignKey('posts.id'), primary_key=True)
    post = db.relationship(
        Post,
        backref=db.backref(
            "liked_by_users",
            lazy='joined',
            cascade='all, delete-orphan'
        )
    )
    user_id = db.Column(db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(
        User,
        uselist=False,
        #lazy='joined',  # see: https://github.com/flaskbb/flaskbb/issues/503#issuecomment-415713742
        backref=db.backref(
            "user_liked_posts",
            cascade="all, delete-orphan",
        ),
    )


Post.likers = association_proxy(
    "liked_by_users", "user",
    creator=lambda user: PostLike(user=user)
)
