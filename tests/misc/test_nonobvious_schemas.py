from faker import Faker

from src.schemas.event_groups import ListEventGroupsResponse, ViewEventGroup, CreateEventGroup

fake = Faker()
i = 0


def get_fake_event_group():
    global i
    i += 1
    return ViewEventGroup(id=i, path=fake.word(), name=fake.word(), type=fake.word(), satellite=fake.json())


def test_list_event_groups_from_iterable():
    groups = (get_fake_event_group() for _ in range(10))
    response = ListEventGroupsResponse.from_iterable(groups)
    assert response is not None
    assert isinstance(response, ListEventGroupsResponse)
    assert response.groups is not None
    assert isinstance(response.groups, list)
    assert len(response.groups) == 10


def test_event_group_with_dict_satellite():
    event_group = CreateEventGroup(path=fake.word(), name=fake.word(), type=fake.word(), satellite={"key": "value"})
    assert event_group is not None
    assert isinstance(event_group, CreateEventGroup)
    assert event_group.satellite is not None
    assert isinstance(event_group.satellite, dict)
    assert event_group.satellite == {"key": "value"}
