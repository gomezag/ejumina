from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from constants import *
import re


def login_as_user(driver, username):
    driver.get(BASE_URL)
    navbar = driver.find_element_by_id('navbarBasicExample')
    navbar_items = navbar.find_elements_by_class_name('navbar-item')
    navbar_items[-1].click()
    driver.find_element_by_id('id_username').send_keys(username)
    driver.find_element_by_id('id_password').send_keys(username)
    driver.find_element_by_css_selector("button[type='submit']").click()


def current_user(driver):
    username_on_top = driver.find_element(By.CSS_SELECTOR,
                                          'div.navbar-brand').find_element(By.CSS_SELECTOR,
                                                                           'a.navbar-item').text
    return username_on_top.split(', ')[1]


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
    driver.get(BASE_URL)
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
    try:
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
    finally:
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


def find_invitacion_from_user(driver, user, person, event):
    driver.get(BASE_URL)
    # Go to event
    event_row = find_evento_in_table(driver, event)
    event_row.find_element(By.CSS_SELECTOR, 'td a').click()

    # Find person in list
    person_row = find_persona_in_page(driver, person)
    person_row.find_element(By.CSS_SELECTOR, 'td a').click()

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


def find_user_in_page(driver, user):
    # Get the TR element for the evento in eventos view.
    persona_table = driver.find_element_by_class_name('tabla-personas')
    persona_rows = persona_table.find_elements_by_tag_name('tr')[1:]
    persona_row = None
    for row in persona_rows:
        try:
            name_el = row.find_element(By.CSS_SELECTOR, 'td')
            if name_el.text == user:
                persona_row = row
                break
        except NoSuchElementException:
            pass
    if not persona_row:
        raise NoSuchElementException('No person with that name and ci found.')

    return persona_row


def remove_invitation_from_user(driver, user, person, event):
    cuser = current_user(driver)
    try:
        if user != cuser and user != 'admin':
            login_as_user(driver, user)

        # Find invitation and delete
        invi_row = find_invitacion_from_user(driver, user, person, event)

        invi_row.find_element(By.CSS_SELECTOR, 'button.plus-button.in-table.red').click()
        alert = driver.switch_to.alert
        alert.accept()

    finally:
        if user != cuser and user != 'admin':
            login_as_user(driver, cuser)


def checkin_invi_person(driver, evento, person, n_invis=1, n_frees=0):
    cuser = current_user(driver)
    try:
        if cuser not in ['admin', 'entrada']:
            login_as_user(driver, 'entrada')
        driver.get(BASE_URL)
        invi_person = person
        # Go to event
        event_row = find_evento_in_table(driver, evento)
        event_row.find_element(By.CSS_SELECTOR, 'td a').click()

        # Find person in list
        person_row = find_persona_in_page(driver, invi_person)

        # Click Checkin button
        person_row.find_element(By.CSS_SELECTOR, 'button.plus-button.green i.fa.fa-check').click()

        # Get modal
        modal = driver.find_element_by_id('checkin-dialog')

        # Check in
        modal.find_element_by_id('id_check_invis').clear()
        modal.find_element_by_id('id_check_invis').send_keys(str(n_invis))
        modal.find_element_by_id('id_check_frees').clear()
        modal.find_element_by_id('id_check_frees').send_keys(str(n_frees))
        modal.find_element(By.CSS_SELECTOR, 'input[type="submit"].button.is-info').click()

        # Close alert message
        driver.find_element_by_id('alert-dialog').find_element_by_id('alert-close').click()

    finally:
        if cuser not in ['admin', 'entrada']:
            login_as_user(driver, cuser)


def assign_free_to_user(driver, evento, user, n_frees=1):
    cuser = current_user(driver)
    if cuser != 'admin':
        login_as_user(driver, 'admin')
    driver.get(BASE_URL)
    event_row = find_evento_in_table(driver, evento)
    event_row.find_element(By.CSS_SELECTOR, 'td a').click()
    driver.find_element(By.CSS_SELECTOR, 'a.plus-button.yellow i.fa.fa-ticket').click()
    driver.find_element_by_id('{}_frees'.format(user)).clear()
    driver.find_element_by_id('{}_frees'.format(user)).send_keys(str(n_frees))
    driver.find_element(By.CSS_SELECTOR, 'div.field input[type="submit"].button.is-info').click()

    if cuser != 'admin':
        login_as_user(driver, cuser)
