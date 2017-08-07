# Redzza


## Api endpoints
| Endpoint | Parametros | Metodos | Retorno | Descripción |
| --- | --- | --- | --- | --- |
| / |  |  |  | Admin Django - WEB |
| /rest-auth/login/ | username, email, password | POST | token | Login api |
| /rest-auth/logout/ |  | POST |  | Logout api |
| /rest-auth/registration/ | username, password1, password2, email | POST | token | Registro api |
| /api-auth/login/ |  |  |  | Login browser Api - WEB |
| /api-auth/login/ |  |  |  | Logout browser Api - WEB |
| /api/v1/ |  | GET | Lista de CRUDs | Modelos de la base de datos del negocio |
| /api/v1/apiServices/validateEmail/ | email | POST | exists, data | Verificacion de existencia de correo en modelo user |
| /api/v1/apiServices/createUser/ | email, first_name, last_name, password, place, i_search, i_have, suggesting | POST | token, success, msg, err | Creacion de un nuevo usuario |

## Paquetes pip

| Paquete       | Descripción   |
| ------------- | --------------|
| Django==1.11 | Django |
| pytz==2017.2 | Dependencia Django |
| psycopg2==2.7.3 | Paquete para gestion de base de datos PostgreSQL |
| Pillow==4.2.1 | Manejo de imagenes  |
| olefile==0.44 | Dependencia Pillow |
| gunicorn==19.7.1 | Ejecución en heroku |
| dj-database-url==0.4.2 | Ejecuión en heroku, base de datos |
| djangorestframework==3.4.6 | Django REST framework - Api |
| django-cors-headers==2.1.0 | Configuracion de CORS |
| django-rest-auth==0.9.1 | Autenticacion para Api |
| six==1.10.0 | Depencencia django-rest-auth |
| django-allauth==0.32.0 | Autenticacion para api |
| urllib3==1.22 | Dependencia django-allauth |
| requests-oauthlib==0.8.0 | Dependencia django-allauth |
| python3-openid==3.1.0 | Dependencia django-allauth |
| requests==2.18.3 | Dependencia django-allauth |
| defusedxml==0.5.0 | Dependencia django-allauth |
| oauthlib==2.0.2 | Dependencia django-allauth |
| chardet==3.0.4 | Dependencia django-allauth |
| certifi==2017.7.27.1 | Dependencia django-allauth |
| idna==2.5 | Dependencia django-allauth |
| djangorestframework-expiring-authtoken==0.1.4 | Token con expiracion de tiempo |



