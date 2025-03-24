from ..hashing import Hash
from .. import schemas, models
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, BackgroundTasks
from passlib.context import CryptContext
from .. import token, config
from fastapi_mail import MessageSchema, FastMail


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create(request:schemas.User, db:Session):
    new_user = models.User(name=request.name, email=request.email, password = Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def show(id:int, db:Session):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail = f"User with id -> {id} not found...")
    return user

def change_user_password(request: schemas.ChangePassword, db: Session, current_user: models.User):
    # Find the user in the database by their email (from the current_user)
    user = db.query(models.User).filter(models.User.email == current_user.email).first()

    # Raise a 404 error if user does not exist
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )

    # Verify if the old password matches
    if not pwd_context.verify(request.current_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )

    # Hash the new password before updating the database
    hashed_password = pwd_context.hash(request.new_password)
    user.password = hashed_password

    # Commit the changes to the database
    db.commit()
    db.refresh(user)

    return user

async def forget_password(request:schemas.ForgetPasswordRequest, db:Session, background_tasks:BackgroundTasks):
    # Find the user in the database by their email (from the current_user)
    user = db.query(models.User).filter(models.User.email == request.email).first()

    # Raise a 404 error if user does not exist
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )
    if user:
        reset_token = token.create_access_token(data={"sub": user.email})

        reset_link = f"http://127.0.0.1:8000/user/forget-reset-password?access_token={reset_token}"

        # Send reset email
        message = MessageSchema(
        subject="Password Reset Request",
        recipients=[user.email],
        body=f"Click the link to reset your password:- <br><br>{reset_link}<br><br><b>Reset Token ➡ </b>{reset_token}<h1>Thankyou...</h1>",
        subtype="html"
    )
        fm = FastMail(config.conf)
        await fm.send_message(message)
      
        return {"message": "Password reset email sent"}
        

# def update(id:int,request:schemas.User, db:Session):
#     user = db.query(models.User).filter(models.User.id == id).first()
#     # print("title", blog.title)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
#         detail = f"User with id -> {id} not found...")
    
#     db.query(models.User).filter(models.User.id == id).update({"name" : request.name, "email" : request.email, "password":request.password})
#     db.commit()
#     return 'updated user'