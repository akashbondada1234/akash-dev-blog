from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    posts = relationship("Post", back_populates="author")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    posts = relationship("Post", back_populates="category")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(220), nullable=False)
    slug = Column(String(240), unique=True, index=True, nullable=False)
    excerpt = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    cover_image = Column(String(500), nullable=True)
    status = Column(String(20), default="draft", nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    category = relationship("Category", back_populates="posts")
    author = relationship("User", back_populates="posts")
