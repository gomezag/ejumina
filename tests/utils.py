from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from constants import *
import re


def login_as_user(driver, username):
    url = BASE_URL
    driver.get(url)
    navbar = driver.find_element_by_id('navbarBasicExample')
    navbar_items = navbar.find_elements_by_class_name('navbar-item')
    navbar_items[-1].click()
    driver.find_element_by_id('id_username').send_keys(username)
    driver.find_element_by_id('id_password').send_keys(username)
    driver.find_element_by_css_selector("button[type='submit']").click()


def create_evento(driver, evento_name, fecha=None):
    driver.get(BASE_URL)
    driver.find_element_by_id('add-form').click()
    modal = driver.find_element(By.CSS_SELECTOR, '.modal.is-active')
    fields = modal.find_elements_by_class_name('field')
    name_input = fields[0].find_element_by_id('id_name')
    name_input.send_keys(evento_name)  # Set event name.
    if fecha:
        fecha_input = fields[1].find_element_by_id('id_fecha')
        fecha_input.send_keys(evento_name)  # Set event name.

    send_btn = modal.find_element(By.CSS_SELECTOR, 'div.control input.button')

    send_btn.click()


def delete_evento(driver, event_name):
    event_row = find_evento_in_table(driver, event_name)
    pencil = event_row.find_element(By.CSS_SELECTOR, 'button.plus-button i.fa.fa-pencil')
    pencil.click()  # Open the edit modal

    modal = driver.find_element(By.CSS_SELECTOR, '.modal.is-active')
    modal.find_element_by_id('delete_evento_btn').click()  # Click on delete option

    del_modal = driver.find_element_by_id('delete-dialog')
    del_modal.find_element(By.CSS_SELECTOR, 'input#nombre').send_keys(event_name)  # Enter event name verification.

    del_btn = del_modal.find_element(By.CSS_SELECTOR, 'div.control input.button.is-danger')
    del_btn.click()  # Click on confirm delete.


def find_evento_in_table(driver, event_name):
    # Get the TR element for the evento in eventos view.
    tabla_eventos = driver.find_element_by_id('tabla_personas')
    event_rows = tabla_eventos.find_elements_by_tag_name('tr')[1:]
    event_row = None
    for row in event_rows:
        try:
            el = row.find_element(By.CSS_SELECTOR, 'td a')
            if el.text == event_name:
                event_row = row
                break
        except NoSuchElementException:
            pass
    if not event_row:
        raise NoSuchElementException('No event with that name found.')

    return event_row


def invite_person(driver, event, person, user, as_user):
    login_as_user(driver, as_user)
    event_row = find_evento_in_table(driver, event)
    event_row.find_element(By.CSS_SELECTOR, 'td a').click()
    driver.find_element_by_id('add-lista').click()
    modal = driver.find_element(By.CSS_SELECTOR, '.modal.is-active')

    modal.find_element_by_id('invi_persona').send_keys(person[0])
    modal.find_element_by_id('invi_cedula').send_keys(person[1])

    modal.find_element(By.CSS_SELECTOR, 'div.plus-button i.fa.fa-plus-circle').click()
    confirm_btn = modal.find_element(By.CSS_SELECTOR, 'input[type="submit"].button')
    confirm_btn.click()

    login_as_user(driver, user)


def find_persona_in_page(driver, persona):
    # Get the TR element for the evento in eventos view.
    persona_name, persona_ci = persona
    persona_table = driver.find_element_by_id('tabla_personas')
    persona_rows = persona_table.find_elements_by_tag_name('tr')[1:]
    persona_row = None
    for row in persona_rows:
        try:
            name_el = row.find_element(By.CSS_SELECTOR, 'td a')
            ci_el = row.find_elements_by_tag_name('td')[3]
            if name_el.text == persona_name and ci_el.text == persona_ci:
                persona_row = row
                break
        except NoSuchElementException:
            pass
    if not persona_row:
        raise NoSuchElementException('No person with that name and ci found.')

    return persona_row


def find_invitacion_from_user(driver, user):
    # Get the TR element for the evento in eventos view.
    invi_table = driver.find_element(By.CSS_SELECTOR, 'table.table.tabla-personas')
    invi_rows = invi_table.find_elements_by_tag_name('tr')[1:]
    invi_row = None
    for row in invi_rows:
        try:
            name_el = row.find_elements_by_tag_name('td')[0]
            el_user = re.search("(?<=\().*?(?=\))", name_el.text).group()
            if el_user == user:
                invi_row = row
                break
        except NoSuchElementException:
            pass
    if not invi_row:
        raise NoSuchElementException('No person with that name and ci found.')

    return invi_row


