FROM python:3.9

WORKDIR /code
ARG TEST

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./api /code/api
COPY ./conf /code/conf
COPY ./eventos /code/eventos
COPY ./templates /code/templates
COPY ./.env /code/.env
COPY ./db.sqlite3 /code/db.sqlite3
COPY ./manage.py /code/manage.py

VOLUME /db
EXPOSE 8000:8000

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]