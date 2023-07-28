import pytest
import logging
from selenium.webdriver.common.by import By
from time import sleep
from constants import *
import pdb

logger = logging.getLogger(__name__)


def test_navbar_without_login(driver):
    url = 'http://127.0.0.1:8000/'
    driver.get(url)
    navbar = driver.find_element_by_id('navbarBasicExample')
    navbar_items = navbar.find_elements_by_class_name('navbar-item')

    # Assert only element present in navbar is login
    assert len(navbar_items) == 1, "There are more elements in the navbar than " \
                                   "exepected: %s ".format(navbar_items)

    assert navbar_items[0].find_elements_by_tag_name('a')[0].get_attribute('href').endswith(LOGIN_URI)


def test_login(driver, user):
    username_on_top = driver.find_element(By.CSS_SELECTOR,
                                          'div.navbar-brand').find_element(By.CSS_SELECTOR,
                                                                           'a.navbar-item').text
    assert username_on_top == 'Bienvenido, {}'.format(user)


def test_navbar_logged_in(driver, user):
    navbar = driver.find_element_by_id('navbarBasicExample')
    navbar_start = navbar.find_elements_by_class_name('navbar-start')[0]
    eventos = navbar_start.find_element(By.CSS_SELECTOR, 'div.navbar-item.is-hoverable.has-dropdown')
    eventos_label = eventos.find_element(By.CSS_SELECTOR, 'a.navbar-link').text
    assert eventos_label == 'Eventos'

    other_items = navbar_start.find_elements_by_xpath('./a[@class="navbar-item"]')
    if user == 'admin':
        assert [el.text for el in other_items] == ['Importar Excel', 'Personas', 'Usuarios', 'Listas', 'Admin Panel']
    elif user == 'rrpp':
        assert [el.text for el in other_items] == []
    elif user == 'entrada':
        assert [el.text for el in other_items] == ['Usuarios', ]


def test_create_evento_modal_opens(driver, user):
    if user != 'admin':
        pytest.skip('Skipping test for user {}'.format(user))
    url = 'http://127.0.0.1:8000/'
    driver.get(url)
    driver.find_element_by_id('add-form').click()

    # Check there are no leftover events
    tabla_eventos = driver.find_element_by_id('tabla_personas')
    event_rows = tabla_eventos.find_elements_by_tag_name('tr')[1:]
    assert len(event_rows) == 0

    # Create a new test event
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

    # Check there is one event in the list now
    tabla_eventos = driver.find_element_by_id('tabla_personas')
    event_rows = tabla_eventos.find_elements_by_tag_name('tr')[1:]
    assert len(event_rows) == 1

    # Delete the event
    event_row = event_rows[0]
    pencils = event_row.find_elements(By.CSS_SELECTOR, 'button.plus-button i.fa.fa-pencil')
    assert len(pencils) == 1
    pencil = pencils[0]
    pencil.click()

    modal = driver.find_element(By.CSS_SELECTOR, '.modal.is-active')
    assert modal.get_attribute('id') == 'edit-dialog'

    modal.find_element_by_id('delete_evento_btn').click()

    del_modal = driver.find_element_by_id('delete-dialog')
    assert 'is-active' in del_modal.get_attribute('class')

    del_modal.find_element(By.CSS_SELECTOR, 'input#nombre').send_keys(TEST_EVENT_NAME)

    del_btn = del_modal.find_element(By.CSS_SELECTOR, 'div.control input.button.is-danger')
    assert del_btn.get_attribute('value') == 'Borrar Evento'
    del_btn.click()

    tabla_eventos = driver.find_element_by_id('tabla_personas')
    event_rows = tabla_eventos.find_elements_by_tag_name('tr')[1:]
    assert len(event_rows) == 0


def test_crear_usuario(driver, user):
    if user != '':
        pytest.skip('Skipping test for user {}'.format(user))
    url = 'http://127.0.0.1:8000/'
    driver.get(url)

    navbar = driver.find_element_by_id('navbarBasicExample')
    navbar_start = navbar.find_elements_by_class_name('navbar-start')[0]
    other_items = navbar_start.find_elements_by_xpath('./a[@class="navbar-item"]')
    usuarios_btn = [item for item in other_items if item.text == 'Usuarios'][0]
    usuarios_btn.click()

    driver.find_element_by_id('add-form').click()
    modal = driver.find_element(By.CSS_SELECTOR, 'div.modal.is-active')
    assert modal.get_attribute('id') == 'form-dialog'
    forms = modal.find_elements_by_tag_name('form')
    assert len(forms) == 1
    form = forms[0]
    fields = form.find_elements_by_tag_name('input')
    assert len(fields) == 5

    form.find_element_by_id('id_username').send_keys(TEST_USER)
    form.find_element_by_id('id_first_name').send_keys(TEST_USER)
    form.find_element_by_id('id_email').send_keys(TEST_EMAIL)
    form.find_element(By.CSS_SELECTOR, 'input.button.is-info[type="submit"]').click()

    users_els = driver.find_elements(By.CSS_SELECTOR, 'div.card.user-card')
    users = [[0] for el in users_els]
    assert any([u == TEST_USER for u in users])
