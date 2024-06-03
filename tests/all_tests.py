import pytest
import logging
from utils import *
import time

logger = logging.getLogger(__name__)


def test_navbar_without_login(driver):
    """
    Test that the navbar without authentication shows only the Login button
    """
    url = BASE_URL
    driver.get(url)
    navbar = driver.find_element_by_id('navbarBasicExample')
    navbar_items = navbar.find_elements_by_class_name('navbar-item')

    # Assert only element present in navbar is login
    assert len(navbar_items) == 1, "There are more elements in the navbar than " \
                                   "exepected: %s ".format(navbar_items)

    assert navbar_items[0].find_elements_by_tag_name('a')[0].get_attribute('href').endswith(LOGIN_URI)


def test_login(driver, user):
    """
    Test that a user can login using the fixture user.
    """
    username_on_top = driver.find_element(By.CSS_SELECTOR,
                                          'div.navbar-brand').find_element(By.CSS_SELECTOR,
                                                                           'a.navbar-item').text
    assert username_on_top == 'Bienvenido, {}'.format(user)


def test_navbar_logged_in(driver, user):
    """
    Test that the navbar elements for an user matches the definition.

    """
    navbar = driver.find_element_by_id('navbarBasicExample')
    navbar_start = navbar.find_elements_by_class_name('navbar-start')[0]
    eventos = navbar_start.find_element(By.CSS_SELECTOR, 'div.navbar-item.is-hoverable.has-dropdown')
    eventos_label = eventos.find_element(By.CSS_SELECTOR, 'a.navbar-link').text
    assert eventos_label == 'Eventos'

    other_items = navbar_start.find_elements_by_xpath('./a[@class="navbar-item"]')
    if user == 'admin':
        assert [el.text for el in other_items] == ['Importar Excel', 'Personas', 'Usuarios', 'Listas']
    elif user == 'rrpp':
        assert [el.text for el in other_items] == []
    elif user == 'entrada':
        assert [el.text for el in other_items] == ['Usuarios', ]


def test_create_and_delete_evento(driver, user):
    """
    Test create evento for admin and not allowed for other users.
    """
    url = BASE_URL
    driver.get(url)

    # Check how many events are
    tabla_eventos = driver.find_element_by_id('tabla_personas')
    event_rows = tabla_eventos.find_elements_by_tag_name('tr')[1:]
    old_len = len(event_rows)

    # Create a new test event
    driver.get(BASE_URL)
    if user == 'admin':
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
    else:
        with pytest.raises(NoSuchElementException):
            driver.find_element_by_id('add-form')
        ajax_injection(driver)
        alert = driver.switch_to.alert
        assert alert.text == '403'
        alert.accept()


def test_can_invite_someone_new(driver, user, evento):
    event_row = find_evento_in_table(driver, evento)
    event_row.find_element(By.CSS_SELECTOR, 'td a').click()
    if user in ['rrpp', 'admin']:
        # Open form
        driver.find_element_by_id('add-lista').click()
        modal = driver.find_element(By.CSS_SELECTOR, '.modal.is-active')
        test_person = TEST_PERSONAS[0]

        # Fillout form
        modal.find_element_by_id('invi_persona').send_keys(test_person[0])
        modal.find_element_by_id('invi_cedula').send_keys(test_person[1])

        input_invi = modal.find_element_by_id('invi_invitaciones')
        old_val = int(input_invi.get_attribute('value'))

        # Check number buttons work
        modal.find_element(By.CSS_SELECTOR, 'div.plus-button i.fa.fa-plus-circle').click()
        new_val = int(input_invi.get_attribute('value'))
        assert new_val == old_val+1

        modal.find_element(By.CSS_SELECTOR, 'div.plus-button i.fa.fa-minus-circle').click()
        new_val = int(input_invi.get_attribute('value'))
        assert new_val == old_val

        # Add one invite
        modal.find_element(By.CSS_SELECTOR, 'div.plus-button i.fa.fa-plus-circle').click()

        confirm_btn = modal.find_element(By.CSS_SELECTOR, 'input[type="submit"].button')
        assert confirm_btn.get_attribute('value') == 'Invitar'

        confirm_btn.click()

        # Remove invitation
        invi_row = find_invitacion_from_user(driver, user, test_person, evento)

        invi_row.find_element(By.CSS_SELECTOR, 'button.plus-button.in-table.red').click()
        alert = driver.switch_to.alert
        assert alert.text == 'Seguro que queres borrar estas entradas?'

        alert.accept()
    else:
        with pytest.raises(NoSuchElementException):
            driver.find_element_by_id('add-lista')
        ajax_injection(driver)
        alert = driver.switch_to.alert
        assert alert.text == '403'
        alert.accept()


class TestsWithInvite:

    def test_checkin_person(self, driver, user, evento, invi_person):
        """
        Test the checkin workflow.
        With an invited person, go to the Event page, find the person in the table
        and check in said person.
        Afterwards, check the person out.
        """
        # Go to event
        event_row = find_evento_in_table(driver, evento)
        event_row.find_element(By.CSS_SELECTOR, 'td a').click()

        # Find person in list
        person_row = find_persona_in_page(driver, invi_person)

        # Get number of checked in invitations
        invis = person_row.find_elements_by_tag_name('td')[0].text
        checked_in_invis = int(re.search("(?<=\().*?(?=\))", invis).group())
        assert checked_in_invis == 0

        if user in ['admin', 'entrada']:
            # Click Checkin button
            person_row.find_element(By.CSS_SELECTOR, 'button.plus-button.green i.fa.fa-check').click()

            # Get modal
            modal = driver.find_element_by_id('checkin-dialog')
            assert 'is-active' in modal.get_attribute('class')

            check_invi_input = modal.find_element_by_id('id_check_invis')
            old_input = check_invi_input.get_attribute('value')
            modal.find_element(By.CSS_SELECTOR, 'div.plus-button i.fa.fa-plus-circle').click()
            new_input = check_invi_input.get_attribute('value')
            assert int(old_input)+1 == int(new_input)

            modal.find_element(By.CSS_SELECTOR, 'div.plus-button i.fa.fa-minus-circle').click()
            new_input = check_invi_input.get_attribute('value')
            assert int(old_input) == int(new_input)

            modal.find_element(By.CSS_SELECTOR, 'div.plus-button i.fa.fa-plus-circle').click()
            modal.find_element(By.CSS_SELECTOR, 'input[type="submit"].button.is-info').click()

            # Get alert message
            modal = driver.find_element_by_id('alert-dialog')
            assert 'is-active' in modal.get_attribute('class')
            assert modal.find_elements(By.CSS_SELECTOR, 'div.modal-card-body p')[1].text == '1 Invitados y 0 Frees'
            modal.find_element_by_id('alert-close').click()

            # Find person in list
            person_row = find_persona_in_page(driver, invi_person)

            # Get number of checked in invitations
            invis = person_row.find_elements_by_tag_name('td')[0].text
            checked_in_invis = int(re.search("(?<=\().*?(?=\))", invis).group())
            assert checked_in_invis == 1

            # Click Checkin button
            person_row.find_element(By.CSS_SELECTOR, 'button.plus-button.green i.fa.fa-check').click()

            # Get modal
            modal = driver.find_element_by_id('checkin-dialog')
            modal.find_element(By.CSS_SELECTOR, 'div.plus-button i.fa.fa-minus-circle').click()
            modal.find_element(By.CSS_SELECTOR, 'input[type="submit"].button.is-info').click()

            # Get alert message
            modal = driver.find_element_by_id('alert-dialog')
            assert 'is-active' in modal.get_attribute('class')
            assert modal.find_elements(By.CSS_SELECTOR, 'div.modal-card-body p')[1].text == '-1 Invitados y 0 Frees'
            modal.find_element_by_id('alert-close').click()

            # Find person in list
            person_row = find_persona_in_page(driver, invi_person)

            # Get number of checked in invitations
            invis = person_row.find_elements_by_tag_name('td')[0].text
            checked_in_invis = int(re.search("(?<=\().*?(?=\))", invis).group())
            assert checked_in_invis == 0
        else:
            with pytest.raises(NoSuchElementException):
                person_row.find_element(By.CSS_SELECTOR, 'button.plus-button.green i.fa.fa-check').click()

    def test_cant_delete_checked_in_invi(self, driver, user, evento, invi_person, checkin_person):
        if user in ['admin', 'rrpp']:
            remove_invitation_from_user(driver, user, invi_person, evento)
            modal = driver.find_element_by_id('alert-dialog')
            err_cnt = 0
            while err_cnt < 2:
                try:
                    modal = driver.find_element_by_id('alert-dialog')
                    assert 'is-active' in modal.get_attribute('class')
                    break
                except AssertionError:
                    time.sleep(0.2)
                    err_cnt += 1
            if err_cnt == 2:
                time.sleep(0.5)
                modal = driver.find_element_by_id('alert-dialog')
                assert 'is-active' in modal.get_attribute('class')
            msg = modal.find_element(By.CSS_SELECTOR, 'div.modal-card-body p').text
            assert msg == 'No se puede borrar una entrada usada!'

            modal.find_element_by_id('alert-close').click()
            assert find_invitacion_from_user(driver, user, invi_person, evento) is not None
        else:
            with pytest.raises(NoSuchElementException):
                remove_invitation_from_user(driver, user, invi_person, evento)

    def test_rrpp_invites_not_in_rrpp2_list(self, driver, user, evento, invi_person):
        if user != 'rrpp':
            pytest.skip('Does not apply for user {}'.format(user))

        try:
            login_as_user(driver, 'rrpp2')
            with pytest.raises(NoSuchElementException):
                find_invitacion_from_user(driver, user, invi_person, evento)
        finally:
            login_as_user(driver, 'rrpp')


def test_can_assign_frees_to_rrpp(driver, user, evento):
    driver.get(BASE_URL)
    event_row = find_evento_in_table(driver, evento)
    event_row.find_element(By.CSS_SELECTOR, 'td a').click()
    if user == 'admin':
        driver.find_element(By.CSS_SELECTOR, 'a.plus-button.yellow i.fa.fa-ticket').click()

        user_row = find_user_in_page(driver, 'rrpp')
        frees_old = user_row.find_elements_by_tag_name('td')[2].text.split('/')[1]
        driver.find_element_by_id('rrpp_frees').send_keys('4')
        driver.find_element(By.CSS_SELECTOR, 'div.field input[type="submit"].button.is-info').click()
        modal = driver.find_element_by_id('alert-dialog')
        assert 'is-active' in modal.get_attribute('class')
        assert modal.find_elements(By.CSS_SELECTOR, 'div.modal-card-body p')[0].text == 'Free(s) asignado(s) con éxito.'
        modal.find_element_by_id('alert-close').click()
        user_row = find_user_in_page(driver, 'rrpp')
        frees_now = user_row.find_elements_by_tag_name('td')[2].text.split('/')[1]
        assert int(frees_now) - int(frees_old) == 4
        driver.find_element_by_id('rrpp_frees').send_keys('-4')
        driver.find_element(By.CSS_SELECTOR, 'div.field input[type="submit"].button.is-info').click()
        modal = driver.find_element_by_id('alert-dialog')
        assert 'is-active' in modal.get_attribute('class')
        assert modal.find_elements(By.CSS_SELECTOR, 'div.modal-card-body p')[0].text == 'Free(s) borrado(s) con éxito.'
        modal.find_element_by_id('alert-close').click()
        user_row = find_user_in_page(driver, 'rrpp')
        frees_now = user_row.find_elements_by_tag_name('td')[2].text.split('/')[1]
        assert int(frees_now) - int(frees_old) == 0

    else:
        with pytest.raises(NoSuchElementException):
            driver.find_element(By.CSS_SELECTOR, 'a.plus-button.yellow i.fa.fa-ticket')


def test_cant_give_frees_not_assigned(driver, user, evento):
    driver.get(BASE_URL)
    event_row = find_evento_in_table(driver, evento)
    event_row.find_element(By.CSS_SELECTOR, 'td a').click()
    if user == 'rrpp':
        # Open form
        driver.find_element_by_id('add-lista').click()
        modal = driver.find_element(By.CSS_SELECTOR, '.modal.is-active')
        test_person = TEST_PERSONAS[0]

        # Fillout form
        modal.find_element_by_id('invi_persona').send_keys(test_person[0])
        modal.find_element_by_id('invi_cedula').send_keys(test_person[1])

        input_frees = modal.find_element_by_id('invi_frees')
        old_val = int(input_frees.get_attribute('value'))

        # Check plus button wont work
        modal.find_elements(By.CSS_SELECTOR, 'div.plus-button i.fa.fa-plus-circle')[1].click()
        new_val = int(input_frees.get_attribute('value'))
        assert new_val == old_val
        input_frees.clear()
        input_frees.send_keys('1')

        confirm_btn = modal.find_element(By.CSS_SELECTOR, 'input[type="submit"].button')
        confirm_btn.click()

        assert 'is-active' in modal.get_attribute('class')
    elif user == 'admin':
        pytest.skip('Admins can always give out frees.')
    else:
        with pytest.raises(NoSuchElementException):
            driver.find_element_by_id('add-lista')


def test_can_give_frees(driver, user, evento, free_assign):
    driver.get(BASE_URL)
    event_row = find_evento_in_table(driver, evento)
    event_row.find_element(By.CSS_SELECTOR, 'td a').click()
    if user in ['admin', 'rrpp']:
        # Open form
        driver.find_element_by_id('add-lista').click()
        modal = driver.find_element(By.CSS_SELECTOR, '.modal.is-active')
        test_person = TEST_PERSONAS[0]

        # Fillout form
        modal.find_element_by_id('invi_persona').send_keys(test_person[0])
        modal.find_element_by_id('invi_cedula').send_keys(test_person[1])

        input_frees = modal.find_element_by_id('invi_frees')
        old_val = int(input_frees.get_attribute('value'))

        # Check number buttons work
        modal.find_elements(By.CSS_SELECTOR, 'div.plus-button i.fa.fa-plus-circle')[1].click()
        new_val = int(input_frees.get_attribute('value'))
        assert new_val == old_val + 1

        modal.find_elements(By.CSS_SELECTOR, 'div.plus-button i.fa.fa-minus-circle')[1].click()
        new_val = int(input_frees.get_attribute('value'))
        assert new_val == old_val

        # Add one invite
        modal.find_elements(By.CSS_SELECTOR, 'div.plus-button i.fa.fa-plus-circle')[1].click()

        confirm_btn = modal.find_element(By.CSS_SELECTOR, 'input[type="submit"].button')
        assert confirm_btn.get_attribute('value') == 'Invitar'

        confirm_btn.click()
        modal = driver.find_element_by_id('alert-dialog')
        modal.find_element_by_id('alert-close').click()
        # Remove invitation
        invi_row = find_invitacion_from_user(driver, user, test_person, evento)

        invi_row.find_element(By.CSS_SELECTOR, 'button.plus-button.in-table.red').click()
        alert = driver.switch_to.alert
        assert alert.text == 'Seguro que queres borrar estas entradas?'

        alert.accept()
    else:
        with pytest.raises(NoSuchElementException):
            driver.find_element_by_id('add-lista')


def test_create_and_delete_person(driver, user):
    driver.get(BASE_URL+'personas')
    person = ('askdfj', '12039')
    if user == 'admin':
        driver.find_element_by_id('add-form').click()
        modal = driver.find_element_by_id('form-dialog')

        modal.find_element_by_id('id_nombre').send_keys(person[0])
        modal.find_element_by_id('id_cedula').send_keys(person[1])
        modal.find_element(By.CSS_SELECTOR, 'input[type="submit"].button').click()

        # Deactivate person

        persona_row = find_persona_in_page(driver, person, ci_row=1, name_row=0)
        persona_row.find_element(By.CSS_SELECTOR,
                                 'button[type="submit"].plus-button.in-table.red i.fa.fa-times').click()
        driver.switch_to.alert.accept()

        # Delete person
        driver.get(driver.current_url)
        persona_row = find_persona_in_page(driver, person, ci_row=1, name_row=0)
        persona_row.find_element(By.CSS_SELECTOR,
                                 'button[type="submit"].plus-button.in-table.red i.fa.fa-trash').click()
        driver.switch_to.alert.accept()
        with pytest.raises(NoSuchElementException):
            driver.get(driver.current_url)
            find_persona_in_page(driver, person, ci_row=1, name_row=0)
    else:
        assert driver.current_url == BASE_URL


def test_banned_person(driver, user, evento, persona):
    if user in ['admin', 'rrpp']:
        ban_persona(driver, persona)
        try:
            invite_person(driver, evento, persona, user, user)
            driver.get(BASE_URL)
            event_row = find_evento_in_table(driver, evento)
            event_row.find_element(By.CSS_SELECTOR, 'td a').click()
            with pytest.raises(NoSuchElementException):
                find_persona_in_page(driver, persona)
        finally:
            unban_persona(driver, persona)
    else:
        pytest.skip('Not applicable for user {}'.format(user))


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
