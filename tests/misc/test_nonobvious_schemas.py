from faker import Faker

from src.schemas.event_groups import ListEventGroupsResponse, ViewEventGroup

fake = Faker()
i = 0


def get_fake_event_group():
    global i
    i += 1
    return ViewEventGroup(id=i, alias=fake.slug(), path=fake.word(), name=fake.word(), description=fake.word(), tags=[])


def test_list_event_groups_from_iterable():
    groups = (get_fake_event_group() for _ in range(10))
    response = ListEventGroupsResponse.from_iterable(groups)
    assert response is not None
    assert isinstance(response, ListEventGroupsResponse)
    assert response.groups is not None
    assert isinstance(response.groups, list)
    assert len(response.groups) == 10
