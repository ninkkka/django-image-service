### Установка
```bash
# 1. Клонирование репозитория
git clone https://github.com/ninkkka/django-image-service.git
cd django-image-service

# 2. Настройка виртуального окружения
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# 3. Установка зависимостей
pip install -r requirements.txt

# 4. Настройка окружения
cp .env.example .env
# Отредактируйте .env файл при необходимости

# 5. Миграции базы данных
python manage.py migrate

# 6. Создание суперпользователя (для админки)
python manage.py createsuperuser

# 7. Запуск сервера
python manage.py runserver