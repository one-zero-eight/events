import datetime

import pytest
from faker import Faker

from src.schemas.workshops import CreateWorkshop, CreateTimeslot

fake = Faker()


@pytest.mark.asyncio
async def test_create_workshop(workshop_repository):
    workshop = CreateWorkshop(
        alias=fake.word(),
        name=fake.word(),
        location=fake.word(),
        timeslots=[
            CreateTimeslot(
                start=datetime.time(hour=10),
                end=datetime.time(hour=11),
            )
        ],
        date=datetime.date.today(),
    )
    created_workshop = await workshop_repository.create_or_update(workshop)
    assert created_workshop.alias == workshop.alias
    assert created_workshop.name == workshop.name
