import argparse

from src.config import settings
from src.repositories.users.repository import user_repository
from src.storages.sql import SQLAlchemyStorage


async def _setup_repository():
    storage = SQLAlchemyStorage.from_url(settings.db_url.get_secret_value())
    user_repository.update_storage(storage)


# _id: xxxxxxxxxx
# innopolis_sso:
#   email: "xxx.xxxxxxx@innopolis.university"
#   name: "XXXX XXXXX"
async def main():
    parser = argparse.ArgumentParser(description="Migrate users from events to accounts.")
    parser.add_argument("--output_file", type=str, help="The filename of the output file")
    args = parser.parse_args()

    await _setup_repository()
    users = await user_repository.read_all()

    users_to_migrate = []

    for user in users:
        if user.name:
            users_to_migrate.append(user)

    mongo_queries = []

    for user in users_to_migrate:
        mongo_queries.append(
            {
                "updateOne": {
                    "filter": {"innopolis_sso.email": user.email},
                    "update": {
                        "$set": {
                            "innopolis_sso": {
                                "email": user.email,
                                "name": user.name,
                            },
                            "innohassle_admin": False,
                        }
                    },
                    "upsert": True,
                }
            }
        )

    import json

    if args.output_file:
        with open(args.output_file, "w") as file:
            file.write(json.dumps(mongo_queries, indent=2, ensure_ascii=False))

    else:
        print(json.dumps(mongo_queries, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
