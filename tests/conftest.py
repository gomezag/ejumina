import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
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


@pytest.fixture(scope='module')
def evento(driver, user):

    # Login as admin
    login_as_user(driver, 'admin')

    # Create event
    create_evento(driver, TEST_EVENT_NAME)

    # Login again as user
    login_as_user(driver, user)

    yield TEST_EVENT_NAME

    # Login as admin
    login_as_user(driver, 'admin')

    # Delete event
    delete_evento(driver, TEST_EVENT_NAME)

    # Login as user
    login_as_user(driver, user)
