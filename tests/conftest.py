import pytest
from selenium import webdriver
from dotenv import load_dotenv


@pytest.fixture(scope='session')
def driver():
    load_dotenv()
    driver = webdriver.Firefox()
    yield driver

    driver.close()

