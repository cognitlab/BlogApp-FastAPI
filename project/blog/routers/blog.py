from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from .. import schemas, database, oauth2
from typing import List
from sqlalchemy.orm import Session
from ..repository import blog


router = APIRouter(
    tags=['Blogs']
)
get_db = database.get_db


# @router.get('/blog', response_model=List[schemas.ShowBlog])
# def all(db: Session = Depends(database.get_db), current_user:schemas.User = Depends(oauth2.get_current_user)):
#     return blog.get_all(db)

@router.get("/blogs/")
def get_blogs(page: int = 1, size: int = 5, db: Session = Depends(get_db), current_user:schemas.User = Depends(oauth2.get_current_user)):
    return blog.get_all(db, page, size)

#get according to id
@router.get('/blog/{id}', status_code=200, response_model=schemas.ShowBlog)
def show(id:int, db: Session = Depends(get_db), current_user:schemas.User = Depends(oauth2.get_current_user)):
    return blog.show(id, db)

#create a new blog
@router.post('/blog', status_code = status.HTTP_201_CREATED)
def create( 
    title: str = Form(...),
    body: str= Form(...),
    files: List[UploadFile] = File(None), 
    db:Session = Depends(get_db), 
    current_user = Depends(oauth2.get_current_user)):
    # print("request",request)
    print("files", files)
    request = schemas.Blog(title=title, body=body)
    return blog.create(request, db, current_user, files)


#delete according to id
@router.delete('/blog/{id}', status_code=status.HTTP_204_NO_CONTENT)
def destroy(id:int, db: Session = Depends(get_db), current_user:schemas.User = Depends(oauth2.get_current_user)):
    return blog.destroy(id, db)


@router.put('/blog/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id:int, request:schemas.Blog, db:Session = Depends(get_db), current_user:schemas.User = Depends(oauth2.get_current_user)):
    return blog.update(id, request, db)

@router.post('/like', status_code=status.HTTP_201_CREATED)
async def like_blog(
    request: schemas.LikeBase,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user)
):
    """
    API to like a blog post.
    - User must be logged in.
    - User can like a blog only once.
    """
    return blog.like_blog(request, db, current_user)

@router.delete('/like/delete', status_code=status.HTTP_204_NO_CONTENT)
def destroy(id:int, db: Session = Depends(get_db), current_user:schemas.User = Depends(oauth2.get_current_user)):
    return blog.destroylike(id, db)

@router.post('/comment', status_code=status.HTTP_201_CREATED)
async def add_comment(
    request: schemas.CommentBase,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user)
):
    """
    API to add a comment or reply.
    - User must be logged in.
    """
    return blog.add_comment(request, db, current_user)

@router.put("/comment/{comment_id}", response_model=schemas.ShowComment)
def update_comment(
    comment_id: int,
    request: schemas.CommentUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user)
):
    """
    API to update an existing comment.
    """
    return blog.update_comment(comment_id, request, db, current_user)

@router.delete("/comments/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    """
    Deletes a comment by ID. Only the comment author can delete it.
    """
    return blog.delete_comment(comment_id, db, current_user)


@router.post('/reply', status_code=status.HTTP_201_CREATED)
def add_reply(
    request: schemas.ReplyBase,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user)
):

    """
    API to add a comment or reply.
    - User must be logged in.
    - If `parent_comment_id` is provided, it's a reply.
    """
    return blog.add_reply(request, db, current_user)

@router.put("/replies/{reply_id}", status_code=status.HTTP_200_OK)
def update_reply(reply_id: int, request: schemas.ReplyUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    """
    Updates a reply by ID. Only the reply author can update it.
    """
    return blog.update_reply(reply_id, request, db, current_user)

@router.delete("/replies/{reply_id}", status_code=status.HTTP_200_OK)
def delete_reply(reply_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    """
    Deletes a reply by ID. Only the reply author can delete it.
    """
    return blog.delete_reply(reply_id, db, current_user)



