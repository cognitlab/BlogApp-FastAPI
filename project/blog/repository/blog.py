from .. import models, schemas
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import os, shutil


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure upload folder exists

def get_user(user, db):
    user_id = db.query(models.User.id).filter(models.User.email == user.email).first()
    return user_id[0]


def create(request: schemas.Blog, db:Session, current_user:schemas.User, files=None):
    # Step 1: Create the Blog
    new_blog = models.Blog(
        title=request.title,
        body=request.body,
        user_id= get_user(current_user, db)  # Assign logged-in user
    )
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)

    uploaded_files = []

    # Step 2: Upload Images (if provided)
    if files:
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)

            # Save file to disk
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Save image details in the database
            new_image = models.Images(
                filename=file.filename,
                path=file_path,
                size=file.size,
                user_id=get_user(current_user, db),  # Assign logged-in user
                blog_id=new_blog.id       # Link image to the blog
            )
            db.add(new_image)
            db.commit()
            db.refresh(new_image)

            uploaded_files.append(new_image)

    return {"blog": new_blog, "images": uploaded_files}


def destroy(id: int, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {id} is not available")

    blog.delete(synchronize_session=False)
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK, detail=f"Blog with id -> {id} is deleted...")

def get_all(db: Session, page: int, size: int):
    blog_query = db.query(models.Blog).order_by(models.Blog.id)
    print('blog_query->', blog_query)
    total_blogs = blog_query.count()
    print('total_blog->', total_blogs)
    blogs = blog_query.offset((page - 1) * size).limit(size).all()

    next_page = f"/blog/all_blogs?page={page + 1}&size={size}" if (page * size) < total_blogs else None
    previous_page = f"/blog/all_blogs?page={page - 1}&size={size}" if page > 1 else None

    return {
        "blogs": blogs,
        "total_blogs": total_blogs,
        "next_page": next_page,
        "previous_page": previous_page
    }

def like_blog(request: schemas.LikeBase, db: Session, current_user: schemas.User):
    """
    Allows a logged-in user to like a blog post.
    Ensures a user can like a blog only once.
    """

    # Check if the blog exists
    blog_id = db.query(models.Blog).filter(models.Blog.id == request.blog_id).first()
    if not blog_id:
        raise HTTPException(status_code=404, detail="Blog not found")

    # Check if the user has already liked this blog
    existing_like = db.query(models.Likes).filter(
        models.Likes.blog_id == request.blog_id,
        models.Likes.user_id == get_user(current_user, db)
    ).first()

    if existing_like:
        raise HTTPException(status_code=400, detail="You have already liked this blog")

    # Create a new like
    new_like = models.Likes(blog_id=request.blog_id, user_id=get_user(current_user, db))
    db.add(new_like)
    db.commit()
    db.refresh(new_like)

    return new_like

def destroylike(id: int, db: Session):
    like = db.query(models.Likes).filter(models.Likes.id == id)
    if not like.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Like with id {id} is not available")

    like.delete(synchronize_session=False)
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK, detail=f"Like with id -> {id} is deleted...")

def update(id:int, request:schemas.Blog, db:Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    # print("title", blog.title)
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail = f"Blog with id -> {id} not found...")
    
    db.query(models.Blog).filter(models.Blog.id == id).update({"title" : request.title, "body" : request.body})
    db.commit()
    return 'updated'

def show(id:int,db:Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with the id {id} is not available")
    return blog 

def add_comment(request: schemas.CommentBase, db: Session, current_user: schemas.User):
    """
    Adds a comment or reply.
    """
    # Check if the blog exists
    blog = db.query(models.Blog).filter(models.Blog.id == request.blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    
    # Create a new comment or reply
    new_comment = models.Comments(
        blog_id=request.blog_id,
        comment=request.comment,
        comment_by=get_user(current_user, db)
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

def add_reply(request: schemas.ReplyBase, db: Session, current_user: schemas.User):

    """
    Adds a comment or reply.
    - If `parent_comment_id` is provided, it's a reply.
    """

    # Check if the blog exists
    blog = db.query(models.Blog).filter(models.Blog.id == request.blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    
    # If it's a reply, check if the parent comment exists
    parent_comment = None
    if request.parent_comment_id:
        parent_comment = db.query(models.Comments).filter(models.Comments.id == request.parent_comment_id).first()
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        
    # Update the parent comment with the reply
    parent_comment.reply = request.reply
    parent_comment.reply_by = get_user(current_user, db)  # Save the user who replied
    parent_comment.parent_comment_id=request.parent_comment_id

    db.commit()  # Save changes
    db.refresh(parent_comment)  # Refresh the updated object

    return parent_comment  # Return the updated comment with the reply added

def update_comment(comment_id: int, request: schemas.CommentUpdate, db: Session, current_user: schemas.User):
    """
    Updates an existing comment. Only the comment author can update their comment.
    """

    # Fetch the comment
    comment = db.query(models.Comments).filter(models.Comments.id == comment_id).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Check if the logged-in user is the author of the comment
    if comment.comment_by != get_user(current_user, db):
        raise HTTPException(status_code=403, detail="You are not allowed to update this comment")

    # Update the comment text
    comment.comment = request.comment  # Update the comment content
    db.commit()
    db.refresh(comment)  # Refresh the updated object

    raise HTTPException(status_code=200, detail="Comment Updated...")
    # return comment # Return the updated comment

def delete_comment(comment_id: int, db: Session, current_user: schemas.User):
    """
    Deletes a comment. Only the comment author or an admin can delete it.
    """
    
    # Fetch the comment
    comment = db.query(models.Comments).filter(models.Comments.id == comment_id).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Check if the logged-in user is the author or an admin
    if comment.comment_by != get_user(current_user, db):
        raise HTTPException(status_code=403, detail="You are not allowed to delete this comment")

    # Delete the comment
    db.delete(comment)
    db.commit()

    return {"detail": "Comment deleted successfully"}

def update_reply(reply_id: int, request: schemas.ReplyUpdate, db: Session, current_user: schemas.User):
    """
    Updates an existing reply. Only the reply author can update their reply.
    """

    # Fetch the comment/reply
    reply = db.query(models.Comments).filter(models.Comments.id == reply_id).first()
    
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    # Check if the logged-in user is the author of the reply
    if reply.reply_by != get_user(current_user, db):
        raise HTTPException(status_code=403, detail="You are not allowed to update this reply")

    # Update the reply text
    reply.reply = request.reply
    db.commit()
    db.refresh(reply)  # Refresh ensures we return an updated object

    return reply  # FastAPI can now correctly serialize it

def delete_reply(reply_id: int, db: Session, current_user: schemas.User):
    """
    Deletes a reply. Only the reply author or an admin can delete it.
    """

    # Fetch the reply
    reply = db.query(models.Comments).filter(models.Comments.id == reply_id).first()

    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    # Check if the logged-in user is the author of the reply or an admin
    if reply.reply_by != get_user(current_user, db):
        raise HTTPException(status_code=403, detail="You are not allowed to delete this reply")

    # Clear only the reply-related fields
    reply.reply = None
    reply.reply_by = None

    db.commit()
    db.refresh(reply)  # Refresh to return updated data


    return {"detail": "Reply deleted successfully"}
