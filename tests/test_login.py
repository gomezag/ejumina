import logging
import selenium.common.exceptions as sel_exceptions
from selenium.webdriver.common.by import By
import pdb
from time import sleep

logger = logging.getLogger(__name__)
LOGIN_URI = 'accounts/login'


def test_login_page(driver):
    url = 'http://127.0.0.1:8000/'
    driver.get(url)
    navbar = driver.find_element_by_id('navbarBasicExample')
    navbar_items = navbar.find_elements_by_class_name('navbar-item')

    # Assert only element present in navbar is login
    assert len(navbar_items) == 1, "There are more elements in the navbar than " \
                                   "exepected: %s ".format(navbar_items)

    assert navbar_items[0].find_elements_by_tag_name('a')[0].get_attribute('href').endswith(LOGIN_URI)

    driver.find_element_by_id('id_username').send_keys('admin')
    driver.find_element_by_id('id_password').send_keys('admin')
    driver.find_element_by_css_selector("button[type='submit']").click()

    navbar = driver.find_element_by_id('navbarBasicExample')
    navbar_start = navbar.find_elements_by_class_name('navbar-start')[0]
    eventos = navbar_start.find_element(By.CSS_SELECTOR, 'div.navbar-item.is-hoverable.has-dropdown')
    eventos_label = eventos.find_element(By.CSS_SELECTOR, 'a.navbar-link').text
    assert eventos_label == 'Eventos'

    other_items = navbar_start.find_elements_by_xpath('./a[@class="navbar-item"]')
    assert [el.text for el in other_items] == ['Importar Excel', 'Personas', 'Usuarios', 'Listas', 'Admin Panel']
