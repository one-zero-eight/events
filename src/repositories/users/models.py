from typing import Optional

from pydantic import BaseModel, Field


class Group(BaseModel):
    name: str
    type: Optional[str]


class InJsonUser(BaseModel):
    # "Group": "B22-CS-02",
    # "Name": "Пичугина Анастасия Вячеславовна",
    # "E-mail": "a.pichugina@innopolis.university",
    # "Tech Elective": "Programming in Python",
    # "Hum Elective": "Personal Efficiency Skills of IT-specialist"
    email: str
    ru_name: Optional[str]
    groups: list[Group] = Field(default_factory=list)
    favorites: list[str] = Field(default_factory=list)

    commonname: str | None
    status: str | None = Field(alias="Status")
