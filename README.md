# FlowCash - Система управления транзакциями

FlowCash - это веб-приложение на Django для управления финансовыми транзакциями с поддержкой категоризации, фильтрации и динамических форм.

## Особенности

- **Управление транзакциями**: Создание, редактирование, удаление транзакций
- **Динамические формы**: AJAX-подгрузка категорий и подкатегорий
- **Система фильтрации**: Расширенная фильтрация по датам, статусам, типам
- **Валидация данных**: Проверка логических связей между полями
- **Пользовательская система**: Регистрация и аутентификация

##  Требования

- Python 3.8+
- Django 4.2+
- SQLite (по умолчанию) или PostgreSQL/MySQL

## 🛠 Установка и запуск

### 1. Клонирование проекта

```bash
git clone https://github.com/Nevermore-cel/FlowCash.git
cd flowcash
```

### 2. Создание виртуального окружения

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

Если файл `requirements.txt` отсутствует, установите зависимости вручную:

```bash
pip install django>=4.2
pip install python-dotenv  # для переменных окружения (опционально)
```

### 4. Настройка базы данных

```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate
```

### 5. Создание суперпользователя

```bash
python manage.py createsuperuser
```

Следуйте инструкциям для создания администратора.

### 6. Запуск сервера разработки

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: http://127.0.0.1:8000/

##  Структура проекта

```
flowcash/
├── manage.py
├── dds_project/                 # Основные настройки проекта
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── dds_app/                  # Основное приложение
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py             # Формы с динамическими полями
│   ├── models.py            # Модель Transaction
│   ├── views.py             # Представления и AJAX-обработчики
│   ├── urls.py
│   ├── migrations/
│   └── templates/
│       ├── dds_app/
│       │       ├── login.html
│       │       ├── register.html
│       │       ├── transaction_create.html
│       │       ├── transaction_edit.html
│       │       ├── transaction_list.html
│       │       ├── transaction_form.html
│       │       └── transaction_delete.html
│       └── base.html
└── readme.md                

```

##  Конфигурация

### Основные URL-адреса

- `/` - Главная страница (список транзакций)
- `/accounts/login/` - Вход в систему
- `/accounts/logout/` - Выход из системы
- `/register/` - Регистрация нового пользователя
- `/admin/` - Админ-панель Django

### Переменные окружения (опционально)

Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

##  Модель данных

### Transaction (Транзакция)

```python
class Transaction(models.Model):
    user = models.ForeignKey(User)           # Пользователь
    date = models.DateField()                # Дата транзакции
    status = models.CharField()              # Статус: business/personal/tax
    type = models.CharField()                # Тип: income/expense
    category = models.CharField()            # Категория
    subcategory = models.CharField()         # Подкатегория
    amount = models.DecimalField()           # Сумма
    comment = models.TextField()             # Комментарий
    created_at = models.DateTimeField()      # Дата создания
    updated_at = models.DateTimeField()      # Дата обновления
```

### Логические связи

**Типы → Категории:**
- `income` (Поступления): salary, freelance, investments, sales
- `expense` (Списания): infrastructure, marketing, food, transport, entertainment

**Категории → Подкатегории:**
- `salary`: main_salary, bonus
- `freelance`: web_dev, design
- `investments`: dividends
- `sales`: goods_sales
- `infrastructure`: vps, proxy, domains, ssl
- `marketing`: farpost, avito, yandex_direct, google_ads
- `food`: products, restaurants, delivery
- `transport`: fuel, public_transport, taxi
- `entertainment`: cinema, games, books, subscriptions

## Использование

### Создание транзакции

1. Перейдите на главную страницу
2. Нажмите кнопку "Добавить транзакцию"
3. Заполните форму:
   - Выберите тип транзакции
   - Категория загрузится автоматически
   - Выберите категорию
   - Подкатегория загрузится автоматически
   - Укажите сумму и другие данные
4. Нажмите "Создать транзакцию"

### Редактирование транзакции

1. В списке транзакций нажмите кнопку "Редактировать"
2. Измените необходимые поля
3. При смене типа/категории зависимые поля обновятся автоматически
4. Нажмите "Сохранить изменения"

### Фильтрация транзакций

1. Используйте форму фильтров на странице списка
2. Выберите режим фильтрации (AND/OR)
3. Установите нужные фильтры
4. Нажмите "Применить фильтры"


