from django.core.management.base import BaseCommand
from dds_app.models import Transaction  # Import the Transaction model
from django.contrib.auth.models import User # Import User model

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **options):
        # Create a default user
        default_user, created = User.objects.get_or_create(
            username='defaultuser',
            defaults={'password': 'defaultpassword'}  # Replace with a secure password in production
        )
        if created:
            default_user.set_password('defaultpassword')  # Hash the password
            default_user.save()


        # Create some transactions for the default user
        Transaction.objects.create(
            user=default_user,
            date='2025-08-03',
            status=Transaction.Status.BUSINESS,
            type=Transaction.Type.INCOME,
            category=Transaction.Category.SALARY,
            subcategory=Transaction.Subcategory.MAIN_SALARY,
            amount=50000.00,
            comment='Зарплата за июль'
        )

        Transaction.objects.create(
            user=default_user,
            date='2025-08-02',
            status=Transaction.Status.PERSONAL,
            type=Transaction.Type.EXPENSE,
            category=Transaction.Category.FOOD,
            subcategory=Transaction.Subcategory.PRODUCTS,
            amount=5000.00,
            comment='Продукты в Ашане'
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database'))