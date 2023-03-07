# ejumina
App para gestionar invitados a eventos. 

Para hacer el setup, copia el archivo .env.example y completalo con la info apropiada.

- `GOOGLE_RECAPTCHA_SITE_KEY/SECRET_KEY` las podes crear vos mismo para tu localhost en [este link](https://www.google.com/recaptcha/admin/create).
Tambien puedo pasarte las mias si no queres o no te sale hacerlo.


- `MAIL_*` no hace falta configurar, pero te va a dar error cuando quiera enviar un mail el servidor.


- `DB_ENGINE` puede ser `SQLITE3` o `MYSQL`. Si elegis `SQLITE3` (recomendado fuera de produccion), no hace falta 
completar el resto de variables `DB_*`


Una vez hecho eso, 

    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

deberia funcionar.



Comisionado por: Barbarella