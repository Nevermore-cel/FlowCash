from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Transaction(models.Model):
    """Основная модель транзакций"""

    class Status(models.TextChoices):
        BUSINESS = 'business', 'Бизнес'
        PERSONAL = 'personal', 'Личное'
        TAX = 'tax', 'Налог'

    class Type(models.TextChoices):
        INCOME = 'income', 'Поступление'
        EXPENSE = 'expense', 'Списание'

    class Category(models.TextChoices):
        # Категории для поступлений
        SALARY = 'salary', 'Зарплата'
        FREELANCE = 'freelance', 'Фриланс'
        INVESTMENTS = 'investments', 'Инвестиции'
        SALES = 'sales', 'Продажи'

        # Категории для списаний
        INFRASTRUCTURE = 'infrastructure', 'Инфраструктура'
        MARKETING = 'marketing', 'Маркетинг'
        FOOD = 'food', 'Еда'
        TRANSPORT = 'transport', 'Транспорт'
        ENTERTAINMENT = 'entertainment', 'Развлечения'

    class Subcategory(models.TextChoices):
        # Подкатегории для инфраструктуры
        VPS = 'vps', 'VPS'
        PROXY = 'proxy', 'Proxy'
        DOMAINS = 'domains', 'Домены'
        SSL = 'ssl', 'SSL-сертификаты'

        # Подкатегории для маркетинга
        FARPOST = 'farpost', 'Farpost'
        AVITO = 'avito', 'Avito'
        YANDEX_DIRECT = 'yandex_direct', 'Яндекс.Директ'
        GOOGLE_ADS = 'google_ads', 'Google Ads'

        # Подкатегории для еды
        PRODUCTS = 'products', 'Продукты'
        RESTAURANTS = 'restaurants', 'Рестораны'
        DELIVERY = 'delivery', 'Доставка'

        # Подкатегории для транспорта
        FUEL = 'fuel', 'Топливо'
        PUBLIC_TRANSPORT = 'public_transport', 'Общественный транспорт'
        TAXI = 'taxi', 'Такси'

        # Подкатегории для развлечений
        CINEMA = 'cinema', 'Кино'
        GAMES = 'games', 'Игры'
        BOOKS = 'books', 'Книги'
        SUBSCRIPTIONS = 'subscriptions', 'Подписки'

        # Подкатегории для поступлений
        MAIN_SALARY = 'main_salary', 'Основная зарплата'
        BONUS = 'bonus', 'Премия'
        WEB_DEV = 'web_dev', 'Веб-разработка'
        DESIGN = 'design', 'Дизайн'
        DIVIDENDS = 'dividends', 'Дивиденды'
        GOODS_SALES = 'goods_sales', 'Продажа товаров'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name="Пользователь"
    )
    date = models.DateField(verbose_name="Дата")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        verbose_name="Статус"
    )
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        verbose_name="Тип"
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        verbose_name="Категория"
    )
    subcategory = models.CharField(
        max_length=20,
        choices=Subcategory.choices,
        verbose_name="Подкатегория"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Сумма"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} - {self.amount}₽ - {self.user.username}"

    # Логические зависимости для категорий и подкатегорий
    CATEGORY_SUBCATEGORY_MAP = {
        # Поступления
        'salary': ['main_salary', 'bonus'],
        'freelance': ['web_dev', 'design'],
        'investments': ['dividends'],
        'sales': ['goods_sales'],

        # Списания
        'infrastructure': ['vps', 'proxy', 'domains', 'ssl'],
        'marketing': ['farpost', 'avito', 'yandex_direct', 'google_ads'],
        'food': ['products', 'restaurants', 'delivery'],
        'transport': ['fuel', 'public_transport', 'taxi'],
        'entertainment': ['cinema', 'games', 'books', 'subscriptions'],
    }

    TYPE_CATEGORY_MAP = {
        'income': ['salary', 'freelance', 'investments', 'sales'],
        'expense': ['infrastructure', 'marketing', 'food', 'transport', 'entertainment'],
    }

    def clean(self):
        """Валидация логических связей на уровне модели"""
        # Эта валидация должна быть, она важна для целостности данных.
        # Она вызывается через self.full_clean()
        if self.type and self.category:
            allowed_categories = self.TYPE_CATEGORY_MAP.get(self.type)
            if allowed_categories is not None and self.category not in allowed_categories:
                raise ValidationError(
                    {'category': f'Категория "{self.get_category_display()}" не относится к типу "{self.get_type_display()}"'}
                )

        if self.category and self.subcategory:
            allowed_subcategories = self.CATEGORY_SUBCATEGORY_MAP.get(self.category)
            # Проверяем, что subcategory вообще существует, если она не пустая.
            # Если поле subcategory_id пустое (None или пустая строка), то это нормально.
            if self.subcategory and (allowed_subcategories is None or self.subcategory not in allowed_subcategories):
                raise ValidationError(
                    {'subcategory': f'Подкатегория "{self.get_subcategory_display()}" не относится к категории "{self.get_category_display()}"'}
                )

    def save(self, *args, **kwargs):
        # Вызываем валидацию перед сохранением.
        # Ошибки ValidationError, поднятые clean(), будут пойманы здесь.
        try:
            self.full_clean()
        except ValidationError as e:
            error_details = []
            for field, messages_list in e.message_dict.items():
                for msg in messages_list:
                    error_details.append(f"{field}: {msg}")
            raise ValueError(f"Ошибка валидации данных транзакции: {'; '.join(error_details)}")
        super().save(*args, **kwargs)