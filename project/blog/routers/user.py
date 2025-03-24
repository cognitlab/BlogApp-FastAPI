from fastapi import APIRouter,Depends, HTTPException, BackgroundTasks, UploadFile, File
from .. import schemas, database, oauth2, models
from sqlalchemy.orm import Session
from ..repository import user
from ..repository.user import change_user_password, forget_password
from .. import token, hashing
import os, shutil
from typing_extensions import List

get_db = database.get_db

router = APIRouter(
     tags=['Users']
) 

UPLOAD_DIR = "img"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Create folder if it doesn't exist

@router.post("/upload-multiple-images/")
async def upload_multiple_images(files: List[UploadFile] = File(...),
                                 db: Session = Depends(get_db),
                                 user_id: int = None,
                                 blog_id: int = None):
    """
    API to upload multiple image files.
    
    - Accepts multiple files as input.
    - Saves each file in the "uploads" folder.
    - Returns the filenames and file sizes in the response.
    """
    if not user_id and not blog_id:
        return {"error": "Provide either user_id or blog_id"}

    uploaded_files = []
    
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        uploaded_files.append({
            "filename": file.filename,
            "size": file.size
        })
    
         # Save image details in the database
        new_image = models.Images(
            filename=file.filename,
            path=file_path,
            size=file.size,
            user_id=user_id,
            blog_id=blog_id
        )
        db.add(new_image)
        db.commit()
        db.refresh(new_image)

        uploaded_files.append({
            "filename": new_image.filename,
            "size": new_image.size,
            "path": new_image.path
        })

    return {"message": "Images uploaded successfully!", "files": uploaded_files}




@router.patch("/user/change-password(after login)")
def change_password(
    request: schemas.ChangePassword,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    API endpoint to allow users to change their password.
    This endpoint requires the old password to be verified,
    and the new password must match the confirmation password.
    """
    return change_user_password(request, db, current_user)

@router.post("/user/sendmail")
async def forget_passwords(background_tasks:BackgroundTasks,request: schemas.ForgetPasswordRequest, db: Session = Depends(database.get_db)):
    """Check if user existed"""
    return await forget_password(request, db, background_tasks)

@router.post("/user/forget-reset-password")
def reset_password(access_token, request: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    # Verify token and extract email
    email = token.verify_new_token(access_token)

    # Find user by email
    user: object = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")

    # Update password
    user.password = hashing.Hash.bcrypt(request.new_password)
    db.commit()

    return {"message": "Password has been reset successfully"}


@router.post('/user', response_model=schemas.ShowUser)
def create_user(request: schemas.User, db:Session = Depends(get_db)):
    return user.create(request, db)


@router.get('/user/{id}', response_model=schemas.ShowUser)
def get_user(id:int, db:Session = Depends(get_db)):
    return user.show(id, db)

# @router.put('/user/{id}', response_model=schemas.ShowUser)
# def update_user(id:int,request: schemas.User, db:Session = Depends(get_db)):
#     return user.update(id, db, request)