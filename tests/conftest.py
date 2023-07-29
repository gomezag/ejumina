import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from constants import *
from utils import *
import pdb


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


@pytest.fixture(scope='module')
def evento(driver, user):

    try:
        if user != 'admin':
            # Login as admin
            login_as_user(driver, 'admin')

        # Create event
        create_evento(driver, TEST_EVENT_NAME)
    finally:
        if user != 'admin':
            # Login again as user
            login_as_user(driver, user)

    yield TEST_EVENT_NAME

    try:
        if user != 'admin':
            # Login as admin
            login_as_user(driver, 'admin')
        # Delete event
        delete_evento(driver, TEST_EVENT_NAME)
    finally:
        if user != 'admin':
            # Login as user
            login_as_user(driver, user)


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
