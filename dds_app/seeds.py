from .models import Category, Subcategory, Status, TransactionType

def seed_data():
    # Создаем статусы
    status_business = Status.objects.create(name="Бизнес")
    status_personal = Status.objects.create(name="Личное")
    status_tax = Status.objects.create(name="Налог")

    # Создаем типы транзакций
    type_income = TransactionType.objects.create(name="Пополнение")
    type_expense = TransactionType.objects.create(name="Списание")

    # Создаем категории
    category_infrastructure = Category.objects.create(name="Инфраструктура")
    category_marketing = Category.objects.create(name="Маркетинг")

    # Создаем подкатегории
    Subcategory.objects.create(category=category_infrastructure, name="VPS")
    Subcategory.objects.create(category=category_infrastructure, name="Proxy")
    Subcategory.objects.create(category=category_marketing, name="Farpost")
    Subcategory.objects.create(category=category_marketing, name="Avito")


if __name__ == '__main__':
    seed_data()
    print("База данных заполнена начальными данными.")