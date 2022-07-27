Репозиторий интернет-магазина на Django 3.

Установка :

1. Открыть терминал или консоль и перейти в нужную Вам директорию
2. Прописать команду `git clone git@gitlab.com:PyCoding1/django3-ecommerce.git`
3. Если Вы используете https, то: `git clone https://gitlab.com/PyCoding1/django3-ecommerce.git`
4. Создать виртуальное окружение
-  Перейти в директорию **shop**
- `pip install -r requirements.txt`
- `python manage.py migrate`
5. Установить тестовые товары:
- `python manage.py loaddata desktops.json`
- `python manage.py loaddata notebooks.json`
- `python manage.py loaddata headphones.json`
- `python manage.py loaddata smartphones.json`
6. Запустить сервер - `python manage.py runserver`
7. Не забудьте создать директорию **media**, куда будут сохраняться изображения