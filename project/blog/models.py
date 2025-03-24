from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Blog(Base):
    __tablename__ = 'blogs'
    id = Column(Integer, primary_key=True, index = True)
    title = Column(String)
    body = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    creator = relationship("User", back_populates="blogs")
    # Relationship: One Blog -> Many Images
    images = relationship("Images", back_populates="blog", cascade="all, delete")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index = True)
    name = Column(String)
    email = Column(String)
    password = Column(String)

    blogs = relationship('Blog', back_populates="creator")
    # Relationship: One User -> Many Images
    images = relationship("Images", back_populates="user", cascade="all, delete")

class Likes(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, index = True)
    blog_id = Column(String, ForeignKey('blogs.id', ondelete="CASCADE"))
    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"))

class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index = True)
    comment = Column(String)
    comment_by = Column(Integer, ForeignKey('users.id'))
    reply = Column(String)
    reply_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    blog_id = Column(String, ForeignKey('blogs.id'))
    parent_comment_id = Column(Integer, ForeignKey('comments.id', ondelete="CASCADE"), nullable=True)  # For nested replies


class Images(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)
    size = Column(Integer, nullable=False)

    # Foreign keys to associate images with Users or Blogs
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    blog_id = Column(Integer, ForeignKey("blogs.id", ondelete="CASCADE"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="images")
    blog = relationship("Blog", back_populates="images")