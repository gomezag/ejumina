"""
/*
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
*/
"""
from django.contrib.auth.forms import PasswordResetForm

from eventos.forms import *
from eventos.views.basic_view import *


class PanelUsuario(AdminView):
    template_name = 'eventos/panel_usuario.html'

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
                                    'nombre': evento.name,
                                    'slug': evento.slug})

        return c

    def get(self, request, *args, **kwargs):
        user = request.user
        c = self.get_context_data(user, *args, **kwargs)
        c['form'] = FreeAssignToUserForm()

        return super().get(request, c)

    def post(self, request, *args, **kwargs):
        id_vendedor = kwargs.get('id_usuario')
        vendedor = Usuario.objects.get(id=id_vendedor)
        user = request.user
        form = FreeAssignToUserForm(request.POST)
        if form.is_valid():
            form.save(user, vendedor)
        c = self.get_context_data(request.user, *args, **kwargs)
        c['form'] = form
        return super().get(request, c)


class ListaUsuarios(AdminView):
    template_name = 'eventos/lista_usuarios.html'

    def get_context_data(self, user, *args, **kwargs):
        c = super().get_context_data(user)
        c['usuarios'] = Usuario.objects.all()
        return c

    def get(self, request, *args, **kwargs):
        c = self.get_context_data(request.user)
        form = NewUserForm()
        c['form'] = form
        return super().get(request, c)

    def post(self, request, *args, **kwargs):
        delete = request.POST.get('delete', None)
        reset = request.POST.get('reset', None)
        if delete:
            print('deleting: {}'.format(delete))
            form = NewUserForm()
        elif reset:
            target = Usuario.objects.get(pk=reset)
            pwd_form = PasswordResetForm(data={
                'email': target.email
            })
            if pwd_form.is_valid():
                print('password reset sent!')
                pwd_form.save(
                    request=request,
                    use_https=True,
                    email_template_name='registration/password_reset_email.html'
                )
            form = NewUserForm()
        else:
            form = NewUserForm(request.POST)
            if form.is_valid():
                form.save()

        c = self.get_context_data(request.user)
        c['form'] = form
        return render(request, self.template_name, context=c)