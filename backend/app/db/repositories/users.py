from fastapi.exceptions import HTTPException
from pydantic.networks import EmailStr
from sqlalchemy.sql.functions import user
from starlette import status
from app.db.repositories.base import BaseRepository
from app.models.user import UserCreate, UserUpdate, UserInDB
from app.db.metadata import User

class UsersRepository(BaseRepository):
    def get_user_by_email(self, *, email: EmailStr) -> UserInDB:
        user_record = self.db.query(User).filter(User.email == email).first()
        if not user_record:
            return None
        return user_record
        
    def get_user_by_username(self, *, username: str) -> UserInDB:
        user_record = self.db.query(User).filter(User.username == username).first()
        if not user_record:
            return None
        return user_record
        
    def register_new_user(self, *, new_user: UserCreate) -> UserInDB:
        # make sure email isn't already taken
        if self.get_user_by_email(email=new_user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="That email is already taken. Login with that email or register with another one."
            )
        # make sure username isn't already taken
        if self.get_user_by_username(username=new_user.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="That username is already taken. Please try another one."                
            )
        created_user = User(**dict(new_user.dict(),**{"salt": "123"}))
        self.db.add(created_user)
        self.db.commit()
        self.db.refresh(created_user)
        return created_user


