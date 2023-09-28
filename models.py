import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('social.db')


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    
    """
    In Peewee models, the class Meta block is used to define metadata 
    and configuration options for the model. In this case, it's used to 
    specify settings related to the database table associated with the User model.
    """
    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    @classmethod
    def search_users(cls, query):
        return cls.select().where(cls.username.contains(query))

    def get_post(self):
        return Post.select().where(Post.user == self)

    # stream of posts for user whom he/she is following or his/her own posts
    def get_stream(self):
        return Post.select().where(
            (Post.user << self.following()) |
            (Post.user == self)
        )
    
    def following(self):
        return (
            User.select().join(
                Relationship, on=Relationship.to_user
            ).where(
                Relationship.from_user == self
            )
        )
    
    def followers(self):
        return (
            User.select().join(
                Relationship, on=Relationship.from_user
            ).where(
                Relationship.to_user == self
            )
        )
    
    """
    Transactions are a way to group one or more database operations into a single unit of work. 
    They ensure that a series of operations either succeed completely or fail entirely. 
    In the context of a transaction, if any operation within it fails (e.g., due to a database 
    constraint violation or an error), all changes made by previous operations within the same 
    transaction are rolled back, ensuring data consistency.
    """
    @classmethod
    def create_user(cls, username, email, password):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password)
                )
        except IntegrityError:
            raise ValueError('User already exists.')
        

class Post(Model):
    timestamp = TimestampField(default=datetime.datetime.now)
    user = ForeignKeyField(
        model=User,
        related_name='posts'
    )
    content = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp')


class Relationship(Model):
    from_user = ForeignKeyField(User, related_name='relationships')
    to_user = ForeignKeyField(User, related_name='related_to')

    class Meta:
        database = DATABASE
        indexes = (
            (('from_user', 'to_user'), True),
        )


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Relationship], safe=True)
    DATABASE.close()

"""
Setting safe=True means that Peewee will perform a check before creating 
each table to ensure that the table does not already exist in the database. 
If a table with the same name already exists, Peewee will skip the creation 
of that table to avoid overwriting or modifying an existing table's structure 
or data. This is a safety feature to prevent accidental data loss or corruption.
"""