# Generated by Django 4.1.7 on 2024-06-01 14:11

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('INA', 'Inactivo'), ('ACT', 'Activo')], max_length=3)),
                ('name', models.CharField(max_length=100)),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('slug', models.SlugField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('estado', models.CharField(choices=[('ACT', 'Activo'), ('BAN', 'Baneado'), ('INA', 'Inactivo')], default='ACT', max_length=3)),
                ('cedula', models.CharField(max_length=11, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('password', models.CharField(default=12345, max_length=128, verbose_name='password')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('first_name', models.CharField(max_length=20, unique=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ListaInvitados',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(choices=[('#008744', 'Green'), ('#0057e7', 'Blue'), ('#d62d20', 'Red'), ('#ffa700', 'Yellow'), ('#ffffff', 'White')], default='#0057e7', max_length=9)),
                ('administradores', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
                ('evento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventos.evento')),
                ('nombre', models.CharField(default='Prueba', max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Invitacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('ACT', 'Activa'), ('RES', 'Reservada'), ('USA', 'Usada'), ('CAN', 'Cancelada')], default='ACT', max_length=3)),
                ('evento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='eventos.evento')),
                ('vendedor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('lista', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='eventos.listainvitados')),
                ('cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='eventos.persona')),
            ],
        ),
        migrations.AddField(
            model_name='listainvitados',
            name='personas',
            field=models.ManyToManyField(blank=True, related_name='invitados', through='eventos.Invitacion', to='eventos.persona'),
        ),
        migrations.AlterField(
            model_name='listainvitados',
            name='nombre',
            field=models.CharField(max_length=15),
        ),
        migrations.RemoveField(
            model_name='listainvitados',
            name='evento',
        ),
        migrations.CreateModel(
            name='Free',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('ACT', 'Activa'), ('RES', 'Reservada'), ('USA', 'Usada'), ('CAN', 'Cancelada')], max_length=3)),
                ('administrador', models.ManyToManyField(related_name='frees', to=settings.AUTH_USER_MODEL)),
                ('cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='eventos.persona')),
                ('evento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='eventos.evento')),
                ('lista', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eventos.listainvitados')),
                ('vendedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='listainvitados',
            name='color',
            field=models.CharField(choices=[('#008744', 'Green'), ('#0057e7', 'Blue'), ('#d62d20', 'Red'), ('#ffa700', 'Yellow')], default='#0057e7', max_length=9),
        ),
        migrations.AddField(
            model_name='listainvitados',
            name='personas_free',
            field=models.ManyToManyField(blank=True, related_name='invitados_free', through='eventos.Free', to='eventos.persona'),
        ),
        migrations.AlterField(
            model_name='listainvitados',
            name='nombre',
            field=models.CharField(max_length=25, unique=True),
        ),
        migrations.AddField(
            model_name='listainvitados',
            name='slug',
            field=models.SlugField(blank=True),
        ),
        migrations.AlterField(
            model_name='free',
            name='lista',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='eventos.listainvitados'),
        ),
        migrations.AlterField(
            model_name='free',
            name='vendedor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='invitacion',
            name='lista',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='eventos.listainvitados'),
        ),
        migrations.AlterField(
            model_name='invitacion',
            name='vendedor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='free',
            name='evento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventos.evento'),
        ),
        migrations.AlterField(
            model_name='invitacion',
            name='evento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventos.evento'),
        ),
        migrations.CreateModel(
            name='HistoricalUsuario',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(db_index=True, error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('first_name', models.CharField(db_index=True, max_length=20)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical user',
                'verbose_name_plural': 'historical users',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalPersona',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('estado', models.CharField(choices=[('ACT', 'Activo'), ('BAN', 'Baneado'), ('INA', 'Inactivo')], default='ACT', max_length=3)),
                ('cedula', models.CharField(db_index=True, max_length=11, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical persona',
                'verbose_name_plural': 'historical personas',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalInvitacion',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('estado', models.CharField(choices=[('ACT', 'Activa'), ('RES', 'Reservada'), ('USA', 'Usada'), ('CAN', 'Cancelada')], default='ACT', max_length=3)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('cliente', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='eventos.persona')),
                ('evento', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='eventos.evento')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('lista', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='eventos.listainvitados')),
                ('vendedor', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical invitacion',
                'verbose_name_plural': 'historical invitacions',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalFree',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('estado', models.CharField(choices=[('ACT', 'Activa'), ('RES', 'Reservada'), ('USA', 'Usada'), ('CAN', 'Cancelada')], max_length=3)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('cliente', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='eventos.persona')),
                ('evento', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='eventos.evento')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('lista', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='eventos.listainvitados')),
                ('vendedor', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical free',
                'verbose_name_plural': 'historical frees',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalEvento',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('estado', models.CharField(choices=[('INA', 'Inactivo'), ('ACT', 'Activo')], max_length=3)),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('slug', models.SlugField(blank=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical evento',
                'verbose_name_plural': 'historical eventos',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AddIndex(
            model_name='invitacion',
            index=models.Index(fields=['evento', 'cliente', 'vendedor', 'estado'], name='eventos_inv_evento__5dc332_idx'),
        ),
        migrations.AddIndex(
            model_name='free',
            index=models.Index(fields=['evento', 'cliente', 'vendedor', 'estado'], name='eventos_fre_evento__3ca6c3_idx'),
        ),
        migrations.AddIndex(
            model_name='persona',
            index=models.Index(fields=['estado'], name='eventos_per_estado_a9e59c_idx'),
        ),
    ]
