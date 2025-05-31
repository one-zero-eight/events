__all__ = ["JsonPredefinedUsers"]

from pydantic import BaseModel, Field, TypeAdapter, field_validator


class JsonPredefinedUsers(BaseModel):
    class InJsonUser(BaseModel):
        email: str
        groups: list[str] = Field(default_factory=list)

    class InJsonGroup(BaseModel):
        name_in_innohassle_accounts: str
        groups: list[str] = Field(default_factory=list)

    users: list[InJsonUser] = Field(default_factory=list)
    academic_groups: list[InJsonGroup] = Field(default_factory=list)

    @field_validator("users")
    def _should_be_unique(cls, v):
        emails = set()
        for user in v:
            if user.email in emails:
                raise ValueError(f"User email {user.email} is not unique")
            emails.add(user.email)
        return v

    @field_validator("academic_groups")
    def _should_be_unique(cls, v):
        names = set()
        for group in v:
            if group.name_in_innohassle_accounts in names:
                raise ValueError(f"Group name {group.name_in_innohassle_accounts} is not unique")
            names.add(group.name_in_innohassle_accounts)
        return v

    @classmethod
    def from_jsons(cls, user_json: dict):
        type_adapter = TypeAdapter(cls)
        user_storage = type_adapter.validate_python(user_json)
        return user_storage

    def get_users(self) -> list[InJsonUser]:
        return self.users.copy()

    def get_user(self, email: str) -> InJsonUser | None:
        for user in self.users:
            if user.email == email:
                return user
        return None

    def get_academic_group(self, name_in_innohassle_accounts: str) -> InJsonGroup | None:
        for group in self.academic_groups:
            if group.name_in_innohassle_accounts == name_in_innohassle_accounts:
                return group
        return None
