from pydantic import BaseModel, Field, validator


class InJsonUser(BaseModel):
    # "Group": "B22-CS-02",
    # "Name": "Пичугина Анастасия Вячеславовна",
    # "E-mail": "a.pichugina@innopolis.university",
    # "Tech Elective": "Programming in Python",
    # "Hum Elective": "Personal Efficiency Skills of IT-specialist"
    group: str = Field(alias="Group")
    name: str = Field(alias="Name")
    email: str = Field(alias="E-mail")
    tech_electives: list[str] = Field(default_factory=list, alias="Tech Elective")
    hum_electives: list[str] = Field(default_factory=list, alias="Hum Elective")

    @validator("tech_electives", "hum_electives", pre=True)
    def split_by_line_break(cls, v: str):
        if isinstance(v, str):
            v = [new_v.strip(", ") for new_v in v.split("\n")]
        return v

    @validator("tech_electives", "hum_electives")
    def remove_empty_strings(cls, v: list[str]):
        return list(filter(lambda x: x and x != "[passed]", v))
