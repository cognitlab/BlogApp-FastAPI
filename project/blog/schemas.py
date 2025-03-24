from pydantic import BaseModel, validator, EmailStr
from fastapi import FastAPI
from typing import  Optional, List


app = FastAPI()

class Images(BaseModel):
    filename: str
    path: str
    size: int
    user_id: Optional[int] = None
    blog_id: Optional[int] = None

    class Config:
        orm_mode = True

class Blog(BaseModel):
    title: str 
    body: str
    class Config:
        from_attributes = True

class ShowUser(BaseModel):
    name: str
    email: str
    blogs: List[Blog] = []
    class Config:
        from_attributes = True


class User(BaseModel):
    name: str
    email: str
    password: str
    
class Login(BaseModel):
    username:str
    password:str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None

class ChangePassword(BaseModel):
    current_password: str
    new_password:str
    confirm_password:str

    @validator("confirm_password")
    def passwords_match(cls, confirm_password, values):
        """
        Ensure that the new password and confirm password match.
        """
        if "new_password" in values and confirm_password != values["new_password"]:
            raise ValueError("New password and confirm password do not match")
        return confirm_password
    
class ForgetPasswordRequest(BaseModel):
    email: EmailStr  # Expecting a valid email string


class ResetPasswordRequest(BaseModel):
    new_password: str
    confirm_password: str

class ShowLike(BaseModel):
    id: int
    blog_id: int
    user_id: int

class LikeBase(BaseModel):
    blog_id: int  # User will send the blog ID they want to like

class CommentBase(BaseModel):
    blog_id: int
    comment: str
    
class ReplyBase(BaseModel):
    blog_id: int
    reply: str
    parent_comment_id: Optional[int] = None

class ShowComment(BaseModel):
    id: int
    blog_id: int
    # user_id: int
    comment: str
    comment_by: int
    reply: Optional[str] = None
    reply_by: Optional[int] = None
    parent_comment_id: Optional[int]
    replies: List["ShowComment"] = []  # Nested replies

    class Config:
        from_attributes = True

class CommentUpdate(BaseModel):
    comment: str  # Only the comment text can be updated

class ReplyUpdate(BaseModel):
    reply: str  # New reply content

    class Config:
        from_attributes = True

class ShowBlog(BaseModel):

    title:str
    body: str
    creator: ShowUser
    images: List[Images] = Optional
    comments: List[ShowComment] = []
    likes: List[ShowLike] = []

    class Config:
        from_attributes = True