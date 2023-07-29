import pytest
import logging
from utils import *

logger = logging.getLogger(__name__)


def test_navbar_without_login(driver):
    url = BASE_URL
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


def test_create_and_delete_evento(driver, user):
    url = BASE_URL
    driver.get(url)

    # Check how many events are
    tabla_eventos = driver.find_element_by_id('tabla_personas')
    event_rows = tabla_eventos.find_elements_by_tag_name('tr')[1:]
    old_len = len(event_rows)

    # Create a new test event
    driver.get(BASE_URL)
    if user != 'admin':
        with pytest.raises(NoSuchElementException):
            driver.find_element_by_id('add-form')
    else:
        driver.find_element_by_id('add-form').click()
        modal = driver.find_element(By.CSS_SELECTOR, '.modal.is-active')
        fields = modal.find_elements_by_class_name('field')
        name_label = fields[0].find_element_by_tag_name('label').text
        name_input = fields[0].find_element_by_id('id_name')
        assert name_label == 'Nombre'
        name_input.send_keys(TEST_EVENT_NAME)  # Set event name.
        fecha_label = fields[1].find_element_by_tag_name('label').text
        assert fecha_label == 'Fecha'

        send_btn = modal.find_element(By.CSS_SELECTOR, 'div.control input.button')
        assert send_btn.get_attribute('value') == 'Crear Evento'

        send_btn.click()
        # Check there is one event in the list now
        tabla_eventos = driver.find_element_by_id('tabla_personas')
        event_rows = tabla_eventos.find_elements_by_tag_name('tr')[1:]
        assert len(event_rows) == old_len+1

        # Delete the event
        event_row = find_evento_in_table(driver, TEST_EVENT_NAME)
        pencils = event_row.find_elements(By.CSS_SELECTOR, 'button.plus-button i.fa.fa-pencil')
        assert len(pencils) == 1
        pencil = pencils[0]
        pencil.click()  # Open the edit modal

        modal = driver.find_element(By.CSS_SELECTOR, '.modal.is-active')
        assert modal.get_attribute('id') == 'edit-dialog'

        modal.find_element_by_id('delete_evento_btn').click()  # Click on delete option

        del_modal = driver.find_element_by_id('delete-dialog')
        assert 'is-active' in del_modal.get_attribute('class')

        # Enter event name verification.
        del_modal.find_element(By.CSS_SELECTOR, 'input#nombre').send_keys(TEST_EVENT_NAME)

        del_btn = del_modal.find_element(By.CSS_SELECTOR, 'div.control input.button.is-danger')
        assert del_btn.get_attribute('value') == 'Borrar Evento'
        del_btn.click()  # Click on confirm delete.

        # Test there are no events left.
        tabla_eventos = driver.find_element_by_id('tabla_personas')
        event_rows = tabla_eventos.find_elements_by_tag_name('tr')[1:]
        assert len(event_rows) == old_len


@pytest.mark.skip(reason="can't delete user after creating it")
def test_crear_usuario(driver, user):

    pytest.skip('Skipping as long we can''t delete created test users')

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
    users = [el[0] for el in users_els]
    assert any([u == TEST_USER for u in users])


def test_can_invite_someone_new(driver, user, evento):
    event_row = find_evento_in_table(driver, evento)
    event_row.find_element(By.CSS_SELECTOR, 'td a').click()
    if user == 'entrada':
        with pytest.raises(NoSuchElementException):
            driver.find_element_by_id('add-lista')
    elif user == 'admin':
        pytest.skip('Admin not tested ftm.')
    elif user == 'rrpp':
        driver.find_element_by_id('add-lista').click()
        modal = driver.find_element(By.CSS_SELECTOR, '.modal.is-active')
        test_person = TEST_PERSONAS[0]

        modal.find_element_by_id('invi_persona').send_keys(test_person[0])
        modal.find_element_by_id('invi_cedula').send_keys(test_person[1])

        input_invi = modal.find_element_by_id('invi_invitaciones')
        old_val = int(input_invi.get_attribute('value'))

        modal.find_element(By.CSS_SELECTOR, 'div.plus-button i.fa.fa-plus-circle').click()
        new_val = int(input_invi.get_attribute('value'))
        assert new_val == old_val+1

        modal.find_element(By.CSS_SELECTOR, 'div.plus-button i.fa.fa-minus-circle').click()
        new_val = int(input_invi.get_attribute('value'))
        assert new_val == old_val

        modal.find_element(By.CSS_SELECTOR, 'div.plus-button i.fa.fa-plus-circle').click()

        confirm_btn = modal.find_element(By.CSS_SELECTOR, 'input[type="submit"].button')
        assert confirm_btn.get_attribute('value') == 'Invitar'

        confirm_btn.click()

        person_row = find_persona_in_page(driver, test_person)
        person_row.find_element(By.CSS_SELECTOR, 'td a').click()

        invi_row = find_invitacion_from_user(driver, user)

        invi_row.find_element(By.CSS_SELECTOR, 'button.plus-button.in-table.red').click()
        alert = driver.switch_to.alert
        assert alert.text == 'Seguro que queres borrar estas entradas?'

        alert.accept()


@pytest.mark.skip(reason="Not done yet.")
def test_checkin_person(driver, user, evento):
    pass


@pytest.mark.skip(reason="Not done yet.")
def test_cant_give_frees_not_assigned(driver, user, evento):
    pass


@pytest.mark.skip(reason="Not done yet.")
def test_can_assign_frees(driver, user, evento):
    pass


@pytest.mark.skip(reason="Not done yet.")
def test_can_give_frees(driver, user, evento):
    pass


@pytest.mark.skip(reason="Not done yet.")
def test_rrpp_invites_are_not_in_rrpp2_list(driver, user, evento):
    pass


@pytest.mark.skip(reason="Not done yet.")
def test_cant_invite_banned_person(driver, user, evento):
    pass
