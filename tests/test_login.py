import logging
import selenium.common.exceptions as sel_exceptions
from selenium.webdriver.common.by import By
import pdb
from time import sleep

logger = logging.getLogger(__name__)
LOGIN_URI = 'accounts/login'
TEST_EVENT_NAME = 'Test Evento'


def test_navbar_without_login(driver):
    url = 'http://127.0.0.1:8000/'
    driver.get(url)
    navbar = driver.find_element_by_id('navbarBasicExample')
    navbar_items = navbar.find_elements_by_class_name('navbar-item')

    # Assert only element present in navbar is login
    assert len(navbar_items) == 1, "There are more elements in the navbar than " \
                                   "exepected: %s ".format(navbar_items)

    assert navbar_items[0].find_elements_by_tag_name('a')[0].get_attribute('href').endswith(LOGIN_URI)


def test_login(driver):
    url = 'http://127.0.0.1:8000/'
    driver.get(url)
    driver.find_element_by_id('id_username').send_keys('admin')
    driver.find_element_by_id('id_password').send_keys('admin')
    driver.find_element_by_css_selector("button[type='submit']").click()
    username_on_top = driver.find_element(By.CSS_SELECTOR,
                                          'div.navbar-brand').find_element(By.CSS_SELECTOR,
                                                                           'a.navbar-item').text
    assert username_on_top == 'Bienvenido, admin'


def test_navbar_logged_in(driver):
    navbar = driver.find_element_by_id('navbarBasicExample')
    navbar_start = navbar.find_elements_by_class_name('navbar-start')[0]
    eventos = navbar_start.find_element(By.CSS_SELECTOR, 'div.navbar-item.is-hoverable.has-dropdown')
    eventos_label = eventos.find_element(By.CSS_SELECTOR, 'a.navbar-link').text
    assert eventos_label == 'Eventos'

    other_items = navbar_start.find_elements_by_xpath('./a[@class="navbar-item"]')
    assert [el.text for el in other_items] == ['Importar Excel', 'Personas', 'Usuarios', 'Listas', 'Admin Panel']


def test_create_evento_modal_opens(driver):
    url = 'http://127.0.0.1:8000/'
    driver.get(url)
    driver.find_element_by_id('add-form').click()
    tabla_eventos = driver.find_element_by_id('tabla_personas')
    event_rows = tabla_eventos.find_elements_by_tag_name('tr')[1:]
    assert len(event_rows) == 0

    modal = driver.find_element(By.CSS_SELECTOR, '.modal.is-active')
    fields = modal.find_elements_by_class_name('field')
    name_label = fields[0].find_element_by_tag_name('label').text
    name_input = fields[0].find_element_by_id('id_name')
    assert name_label == 'Nombre'
    name_input.send_keys(TEST_EVENT_NAME)
    fecha_label = fields[1].find_element_by_tag_name('label').text
    fecha_input = fields[1].find_element_by_id('id_fecha')
    assert fecha_label == 'Fecha'

    send_btn = modal.find_element(By.CSS_SELECTOR, 'div.control input.button')
    assert send_btn.get_attribute('value') == 'Crear Evento'

    send_btn.click()

    tabla_eventos = driver.find_element_by_id('tabla_personas')
    event_rows = tabla_eventos.find_elements_by_tag_name('tr')[1:]
    assert len(event_rows) == 1


def test_borrar_eventos(driver):
    url = 'http://127.0.0.1:8000/'
    driver.get(url)

    tabla_eventos = driver.find_element_by_id('tabla_personas')
    event_row = tabla_eventos.find_elements_by_tag_name('tr')[1]
    pencils = event_row.find_elements(By.CSS_SELECTOR, 'button.plus-button i.fa.fa-pencil')
    assert len(pencils) == 1
    pencil = pencils[0]
    pencil.click()

    modal = driver.find_element(By.CSS_SELECTOR, '.modal.is-active')
    assert modal.get_attribute('id') == 'edit-dialog'

    delete_btn = modal.find_element_by_id('delete_evento_btn').click()

    del_modal = driver.find_element_by_id('delete-dialog')
    assert 'is-active' in del_modal.get_attribute('class')

    del_modal.find_element(By.CSS_SELECTOR, 'input#nombre').send_keys(TEST_EVENT_NAME)

    del_btn = del_modal.find_element(By.CSS_SELECTOR, 'div.control input.button.is-danger')
    assert del_btn.get_attribute('value') == 'Borrar Evento'
    del_btn.click()

    tabla_eventos = driver.find_element_by_id('tabla_personas')
    event_rows = tabla_eventos.find_elements_by_tag_name('tr')[1:]
    assert len(event_rows) == 0
