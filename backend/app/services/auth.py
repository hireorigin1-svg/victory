from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.repositories.users import UserRepository


class AuthService:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    def register(
        self, email: str, name: str, password: str, role: UserRole = UserRole.viewer
    ) -> User:
        existing = self.users.get_by_email(email)
        if existing:
            raise ValueError("A user with this email already exists")
        return self.users.create(
            {
                "email": email,
                "name": name,
                "password_hash": hash_password(password),
                "role": role,
            }
        )

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def issue_token(self, user: User) -> str:
        return create_access_token(user.id, {"role": user.role.value})
