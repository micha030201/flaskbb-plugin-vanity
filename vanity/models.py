from flaskbb.extensions import db
from flaskbb.forum.models import Post
from flaskbb.user.models import User


association_table = db.Table(
    'vanity_association', db.Model.metadata,
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
)


Post.likers = db.relationship(
    "User", secondary=association_table, lazy="joined")


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
