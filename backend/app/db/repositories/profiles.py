from app.db.repositories.base import BaseRepository
from app.models.profile import ProfileCreate, ProfileInDB, ProfileUpdate
from app.db.metadata import Profile, User
from app.models.user import UserInDB


class ProfilesRepository(BaseRepository):
    def create_profile_for_user(self, *, profile_create: ProfileCreate) -> ProfileInDB:
        created_profile = Profile(**profile_create.dict())
        self.db.add(created_profile)
        self.db.commit()
        self.db.refresh(created_profile)
        return created_profile

    def get_profile_by_user_id(self, *, user_id: int) -> ProfileInDB:
        profile_record = self.db.query(Profile).filter(Profile.user_id == user_id).first()
        #need to figure out how to return user information as well (just username and email)
        if not profile_record:
            return None

        return profile_record

    def get_profile_by_username(self, *, username: str) -> ProfileInDB:
        profile_record = self.db.query(Profile).join(User.profile).filter(User.username == username).first()
        if profile_record:
            return profile_record

    def update_profile(self, *, profile_update: ProfileUpdate, requesting_user: UserInDB) -> ProfileInDB:
        profile = self.db.query(Profile).filter(Profile.user_id == requesting_user.id).first()
        for var,value in vars(profile_update).items():
            if value or str(value) == 'False':
                setattr(profile, var, value) 
        
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile