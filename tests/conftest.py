import pytest
from selenium import webdriver
from dotenv import load_dotenv


@pytest.fixture
def driver():
    load_dotenv()
    driver = webdriver.Firefox()
    yield driver

    driver.close()

