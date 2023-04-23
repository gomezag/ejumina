import re
import os
import csv
from io import StringIO

from openpyxl import load_workbook

from django.template.defaultfilters import slugify
from django.core.mail import EmailMessage


def parse_excel_import(f):
    extension = os.path.splitext(str(f))[1]
    if extension != '.xlsx':
        raise ValueError('Archivo tiene que tener extension .xlsx')
    try:
        wb = load_workbook(f)
        ws = wb.worksheets[0]
    except Exception as e:
        raise ValueError('Error al leer el archivo. Asegurate que tenga una hoja y los datos esten ahí')
    results = []
    rows = ws.rows
    header = next(rows)
    try:
        assert header[0].value.lower() == 'nombre', "Primera columna tiene que llamarse Nombre"
        assert header[1].value.lower() == 'cedula', "Segunda columna tiene que llamarse Cedula"
        assert header[2].value.lower() == 'frees', "Tercera columna tiene que llamarse Frees"
        assert header[3].value.lower() == 'invitaciones', "Cuarta columna tiene que llamarse Invitaciones"
        assert header[4].value.lower() == 'lista', "Quinta columna tiene que llamarse Lista"
    except Exception as e:
        raise ValueError(str(e))
    frees = 0
    for row in rows:
        if any([r.value is not None for r in row]):
            results.append({'nombre': str(row[0].value).rstrip(' ').lstrip(' '),
                            'invis': row[3].value,
                            'frees': row[2].value,
                            'lista': str(row[4].value).rstrip(' ').lstrip(' '),
                            'cedula': str(row[1].value).rstrip(' ').lstrip(' ')
                            })
            frees += row[2].value

    return frees, results


def unique_slugify(instance, value, slug_field_name='slug', queryset=None,
                   slug_separator='-'):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len-len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator='-'):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ''
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub('%s+' % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != '-':
            re_sep = re.escape(separator)
        value = re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)
    return value


def validate_in_group(user, valids):
    groups = [g.name for g in user.groups.all()]
    return any([g in groups for g in valids])


def mail_event_attendees(user, personas):
    # Create a StringIO object to write CSV data to
    csv_buffer = StringIO()
    for persona in personas:
        listas = ",".join([p.nombre for p in persona['listas']])
        persona.update(listas=str(listas))
    # Create a CSV writer object using the StringIO object
    writer = csv.DictWriter(csv_buffer, fieldnames=personas[0].keys())

    # Write the header row based on the keys of the first dictionary
    writer.writeheader()

    # Write the data rows based on the dictionaries in the list
    for data_dict in personas:
        writer.writerow(data_dict)

    # Reset the StringIO object to the beginning
    csv_buffer.seek(0)

    # Return the CSV string
    csv_data=csv_buffer.read()
    # Create the email message and attach the CSV file
    email = EmailMessage(
        subject='Query Results Email',
        body='Please find the attached CSV file with the query results.',
        from_email='from@example.com',
        to=[user.email],
    )
    email.attach('query_results.csv', csv_data, 'text/csv')
    email.send()
    raise Exception('No implementado')
