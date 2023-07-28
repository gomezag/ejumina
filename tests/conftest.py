import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from constants import TEST_EVENT_NAME


@pytest.fixture(scope='session')
def driver():
    load_dotenv()
    driver = webdriver.Firefox()
    yield driver

    driver.close()


@pytest.fixture(scope='module', params=['admin', 'rrpp', 'entrada'])
def user(driver, request):
    username = request.param
    url = 'http://127.0.0.1:8000/'
    driver.get(url)
    navbar = driver.find_element_by_id('navbarBasicExample')
    navbar_items = navbar.find_elements_by_class_name('navbar-item')
    navbar_items[-1].click()
    driver.find_element_by_id('id_username').send_keys(username)
    driver.find_element_by_id('id_password').send_keys(username)
    driver.find_element_by_css_selector("button[type='submit']").click()

    yield username


@pytest.fixture
def evento(driver, user):
    url = 'http://127.0.0.1:8000/'
    driver.get(url)
    navbar = driver.find_element_by_id('navbarBasicExample')
    navbar_items = navbar.find_elements_by_class_name('navbar-item')
    navbar_items[-1].click()
    driver.find_element_by_id('id_username').send_keys('admin')
    driver.find_element_by_id('id_password').send_keys('admin')
    driver.find_element_by_css_selector("button[type='submit']").click()
    driver.find_element_by_id('add-form').click()
    field = driver.find_element_by_id('id_name')
    field.send_keys(TEST_EVENT_NAME)

    modal = driver.find_element(By.CSS_SELECTOR, '.modal.is-active')
    modal.find_element(By.CSS_SELECTOR, 'div.control input.button').click()

    url = 'http://127.0.0.1:8000/'
    driver.get(url)
    navbar = driver.find_element_by_id('navbarBasicExample')
    navbar_items = navbar.find_elements_by_class_name('navbar-item')
    navbar_items[-1].click()
    driver.find_element_by_id('id_username').send_keys(user)
    driver.find_element_by_id('id_password').send_keys(user)
    driver.find_element_by_css_selector("button[type='submit']").click()

    yield TEST_EVENT_NAME
