@echo off
call venv\Scripts\activate

python manage.py create_initial_users
python manage.py seed_products

