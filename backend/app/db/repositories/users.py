from typing import Optional
from fastapi.exceptions import HTTPException
from pydantic.networks import EmailStr
from sqlalchemy.orm.session import Session
from starlette import status
from app.db.repositories.base import BaseRepository
from app.db.repositories.profiles import ProfilesRepository
from app.models.profile import ProfileCreate, ProfilePublic
from app.models.user import UserCreate, UserPublic, UserUpdate, UserInDB
from app.db.metadata import User
from app.services import auth_service

class UsersRepository(BaseRepository):

    def __init__(self, db: Session) -> None:
        super().__init__(db)
        self.auth_service = auth_service
        self.profiles_repo = ProfilesRepository(db)  

    def get_user_by_email(self, *, email: EmailStr, populate: bool = True) -> UserInDB:
        user_record = self.db.query(User).filter(User.email == email).first()
        if not user_record:
            return None
        if populate:
            return self.populate_user(user=user_record)
        return UserInDB(**user_record.as_dict())
        
    def get_user_by_username(self, *, username: str, populate: bool = True) -> UserInDB:
        user_record = self.db.query(User).filter(User.username == username).first()
        if not user_record:
            return None
        if populate:
            return self.populate_user(user=user_record)
        return UserInDB(**user_record.as_dict())
        
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

        
        user_password_update = self.auth_service.create_salt_and_hashed_password(plaintext_password=new_user.password)
        created_user = User(**dict(new_user.dict(),**user_password_update.dict()))
        self.db.add(created_user)
        self.db.commit()
        self.db.refresh(created_user)

        self.profiles_repo.create_profile_for_user(profile_create=ProfileCreate(user_id=created_user.id))

        return self.populate_user(user = created_user)

    def authenticate_user(self, *, email: EmailStr, password: str) -> Optional[UserInDB]:
        # make user user exists in db
        user = self.get_user_by_email(email=email, populate=False)
        print(str(user))
        if not user:
            return None
        # if submitted password doesn't match
        if not self.auth_service.verify_password(password=password, salt=user.salt, hashed_pw=user.password):
            return None
        return user

    def populate_user(self, *, user: User) -> UserInDB:
        return UserPublic(
            # unpack the user in db dict into the UserPublic model
            # which will remove "password" and "salt"
            **user.as_dict(),
            # fetch the user's profile from the profiles repo
            profile=ProfilePublic(**user.profile.as_dict())
        )