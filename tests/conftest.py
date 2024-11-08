import pytest
from selenium import webdriver
from dotenv import load_dotenv
from constants import *
from utils import *


@pytest.fixture(scope='session')
def driver():
    load_dotenv()
    driver = webdriver.Firefox()
    yield driver

    driver.close()


@pytest.fixture(scope='module', params=['admin', 'rrpp', 'entrada'])
def user(driver, request):
    username = request.param
    login_as_user(driver, username)

    yield username


@pytest.fixture(scope='package')
def evento(driver):

    login_as_user(driver, 'admin')

    # Create event
    create_evento(driver, TEST_EVENT_NAME)

    yield TEST_EVENT_NAME

    # Login as admin
    login_as_user(driver, 'admin')
    # Delete event
    delete_evento(driver, TEST_EVENT_NAME)


@pytest.fixture(scope='class')
def invi_person(driver, user, evento):
    person = TEST_PERSONAS[0]
    if user in ['admin', 'rrpp']:
        as_user = user
    else:
        as_user = 'rrpp'
    invite_person(driver, evento, person, user, as_user)
    try:
        yield person
    finally:
        remove_invitation_from_user(driver, as_user, person, evento)


@pytest.fixture(scope='function')
def checkin_person(driver, user, evento, invi_person):
    checkin_invi_person(driver, evento, invi_person, n_invis=1)
    yield invi_person
    checkin_invi_person(driver, evento, invi_person, n_invis=-1)


@pytest.fixture
def free_assign(driver, user, evento):
    if user == 'admin':
        yield None
    elif user == 'rrpp':
        assign_free_to_user(driver, evento, user, n_frees=1)
        yield 1
        assign_free_to_user(driver, evento, user, n_frees=-1)
    else:
        yield None


@pytest.fixture(scope='session')
def persona(driver):
    person = TEST_PERSONAS[1]
    create_persona(driver, person)
    yield person
    delete_persona(driver, person)
