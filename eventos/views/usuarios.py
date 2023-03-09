"""
/*
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
*/
"""
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render
from smtplib import SMTPRecipientsRefused

from eventos.forms import NewUserForm, FreeAssignToUserForm, EditUserForm
from eventos.models import Usuario, Evento
from .basic_view import BasicView
from eventos.utils import validate_in_group


class PanelUsuario(BasicView):
    template_name = 'eventos/panel_usuario.html'

    def test_func(self):
        return self.request.user.is_authenticated and validate_in_group(self.request.user, ('admin', 'entrada'))

    def get_context_data(self, user, *args, **kwargs):
        c = super().get_context_data(user)
        id_usuario = kwargs.pop('id_usuario')
        c['id_usuario'] = Usuario.objects.get(id=id_usuario)
        c['id_eventos'] = []
        c['back'] = '/usuarios'
        c['persona'] = user
        for evento in Evento.objects.all():
            c['id_eventos'].append({'frees_total': evento.free_set.filter(vendedor=c['id_usuario']).count(),
                                    'frees': evento.free_set.filter(vendedor=c['id_usuario'],
                                                                    cliente__isnull=False).count(),
                                    'invis': evento.invitacion_set.filter(vendedor=c['id_usuario']).count(),
                                    'checked': evento.invitacion_set.filter(vendedor=c['id_usuario'],
                                                                            estado='USA').count() +
                                               evento.free_set.filter(vendedor=c['id_usuario'],
                                                                      estado='USA').count(),
                                    'nombre': evento.name,
                                    'slug': evento.slug})

        return c

    def get(self, request, *args, **kwargs):
        user = request.user
        c = self.get_context_data(user, *args, **kwargs)
        if validate_in_group(user, ('admin',)):
            c['form'] = FreeAssignToUserForm()

        return super().get(request, c)

    def post(self, request, *args, **kwargs):
        id_vendedor = kwargs.get('id_usuario')
        vendedor = Usuario.objects.get(id=id_vendedor)
        user = request.user
        if validate_in_group(user, ('admin',)):
            form = FreeAssignToUserForm(request.POST)
            if form.is_valid():
                form.save(user, vendedor)
        c = self.get_context_data(request.user, *args, **kwargs)
        if form:
            c['form'] = form
        return super().get(request, c)


class ListaUsuarios(BasicView):
    template_name = 'eventos/lista_usuarios.html'

    def test_func(self):
        return self.request.user.is_authenticated and validate_in_group(self.request.user, ('admin', 'entrada'))

    def get_context_data(self, user, *args, **kwargs):
        c = super().get_context_data(user)
        c['usuarios'] = Usuario.objects.filter(is_superuser=False).order_by('-is_active')
        return c

    def get(self, request, *args, **kwargs):
        c = self.get_context_data(request.user)
        if validate_in_group(request.user, ('admin',)):
            c['form'] = NewUserForm()
            c['edit_form'] = EditUserForm(auto_id='edit')
        return super().get(request, c)

    def post(self, request, *args, **kwargs):
        if validate_in_group(request.user, ('admin',)):
            delete = request.POST.get('delete', None)
            reactivate = request.POST.get('reactivate', None)
            reset = request.POST.get('reset', None)
            edit = request.POST.get('edit', None)
            msg = []
            if delete:
                user = Usuario.objects.get(pk=delete)
                user.is_active = False
                user.save()
                form = NewUserForm()
                edit_form = EditUserForm()
            elif reactivate:
                user = Usuario.objects.get(pk=reactivate)
                user.is_active = True
                user.save()
                form = NewUserForm()
                edit_form = EditUserForm()
            elif edit:
                user = Usuario.objects.get(pk=edit)
                edit_form = EditUserForm(request.POST, instance=user)
                if edit_form.is_valid():
                    edit_form.save()
                form = NewUserForm()
            elif reset:
                target = Usuario.objects.get(pk=reset)
                pwd_form = PasswordResetForm(data={
                    'email': target.email
                })
                if pwd_form.is_valid():
                    try:
                        pwd_form.save(
                            request=request,
                            use_https=True,
                            email_template_name='registration/password_reset_email.html'
                        )
                        msg = 'Mail enviado!'
                    except SMTPRecipientsRefused:
                        msg.append('La dirección de email fue rechazada por el servidor.')
                        msg.append('Verificá la dirección de correo e intentá de vuelta.')
                form = NewUserForm()
                edit_form = EditUserForm()
            else:
                form = NewUserForm(request.POST)
                if form.is_valid():
                    form.save()
                edit_form = EditUserForm()
            c = self.get_context_data(request.user)
            c['form'] = form
            c['edit_form'] = edit_form
            c['alert_msg'] = msg
        else:
            c = self.get_context_data(request.user)
        return render(request, self.template_name, context=c)
