# coding:utf-8
from mongoengine import (
    connect,
    Document,
    StringField,
    ReferenceField,
    ListField,
    DateTimeField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    CASCADE,
)
import datetime
import settings


connect(**settings.mongodb_options)


__all__ = [
    'User',
    'Comment',
    'Post',
]


class User(Document):
    email = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)


class Comment(EmbeddedDocument):
    content = StringField()
    name = StringField(max_length=120)


class Post(Document):
    title = StringField(max_length=120, required=True)
    content = StringField()
    author = ReferenceField(User, reverse_delete_rule=CASCADE)
    tags = ListField(StringField(max_length=30))
    comments = ListField(EmbeddedDocumentField(Comment))
    created_at = DateTimeField(default=datetime.datetime.utcnow)


if __name__ == '__main__':
    alice = User(
        email='alice@lawley.com',
        first_name='alice',
        last_name='Lawley',
    ).save()
    bob = User(
        email='bob@lawley.com',
        first_name='bob',
        last_name='Lawley',
    ).save()

    post1 = Post(
        title='Fun with MongoEngine',
        author=alice
    )
    post1.content = 'Took a look at MongoEngine today, looks pretty cool.'
    post1.tags = ['mongodb', 'mongoengine']
    post1.save()

    post2 = Post(
        title='MongoEngine Documentation',
        author=bob
    )
    post2.content = 'http://docs.mongoengine.com/'
    post2.tags = ['mongoengine']
    post2.save()
