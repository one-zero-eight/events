import argparse
import asyncio

from pydantic import BaseModel, TypeAdapter, model_validator

from src.config import settings
from src.modules.users.repository import user_repository
from src.storages.sql import SQLAlchemyStorage


class InputUser(BaseModel):
    # {
    #     "_id": {
    #         "$oid": "65f6ef2847289ea08482e3bb"
    #     },
    #     "innopolis_sso": {
    #         "email": "a.romanova@innopolis.university"
    #     }
    # }

    innohassle_id: str
    email: str

    @model_validator(mode="before")
    def extract_fields(cls, values):
        return {
            "innohassle_id": values["_id"]["$oid"],
            "email": values["innopolis_sso"]["email"],
        }


async def _setup_repository():
    storage = SQLAlchemyStorage.from_url(settings.db_url.get_secret_value())
    user_repository.update_storage(storage)


async def main():
    parser = argparse.ArgumentParser(description="Migrate users from accounts to events.")

    parser.add_argument("input_file", type=str, help="The filename of the input file")
    args = parser.parse_args()

    type_adapter = TypeAdapter(list[InputUser])

    with open(args.input_file) as file:
        data = file.read()
        users = type_adapter.validate_json(data)

    await _setup_repository()
    existing_users = await user_repository.read_mapping_by_emails([user.email for user in users])
    for user in users:
        await user_repository.update_innohassle_id(existing_users[user.email], user.innohassle_id)


if __name__ == "__main__":
    asyncio.run(main())
