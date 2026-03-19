from sqlalchemy.orm import Session
from . import models
from .auth import hash_password

def create_user(db: Session, user):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise ValueError("Email already registered")
    new_user = models.User(name=user.name, email=user.email, password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_users(db: Session):
    return db.query(models.User).all()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user

def create_post(db: Session, title: str, body: str):
    post = models.Post(title=title, body=body)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def get_posts(db: Session):
    return db.query(models.Post).all()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()