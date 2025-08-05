from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.db.models import Q
from .models import Transaction
from .forms import TransactionForm, TransactionFilterForm, UserRegistrationForm
from django.urls import reverse

# ================ AJAX Views для динамических селектов ================

@login_required
def load_categories(request):
    """AJAX загрузка категорий по типу транзакции"""
    type_value = request.GET.get('type_value')
    print(f" AJAX: Loading categories for type '{type_value}'")
    
    categories = []

    if type_value:
        allowed_categories = Transaction.TYPE_CATEGORY_MAP.get(type_value, [])
        print(f"   Allowed categories: {allowed_categories}")
        
        for value, label in Transaction.Category.choices:
            if value in allowed_categories:
                categories.append({'id': value, 'name': label})
        
        print(f"   Returning {len(categories)} categories: {[c['id'] for c in categories]}")
    else:
        print("   No type value provided, returning empty list")

    return JsonResponse(categories, safe=False)


@login_required
def load_subcategories(request):
    """AJAX загрузка подкатегорий по категории"""
    category_value = request.GET.get('category_value')
    print(f" AJAX: Loading subcategories for category '{category_value}'")
    
    subcategories = []

    if category_value:
        allowed_subcategories = Transaction.CATEGORY_SUBCATEGORY_MAP.get(category_value, [])
        print(f"   Allowed subcategories: {allowed_subcategories}")
        
        for value, label in Transaction.Subcategory.choices:
            if value in allowed_subcategories:
                subcategories.append({'id': value, 'name': label})
        
        print(f"   Returning {len(subcategories)} subcategories: {[s['id'] for s in subcategories]}")
    else:
        print("   No category value provided, returning empty list")

    return JsonResponse(subcategories, safe=False)


# ================ Основные представления транзакций ================

class TransactionListView(LoginRequiredMixin, View):
    """Список транзакций с фильтрацией"""

    def get(self, request):
        transactions_queryset = Transaction.objects.filter(
            user=request.user
        ).order_by('-date', '-created_at')

        filter_form = TransactionFilterForm(request.GET)

        if filter_form.is_valid():
            transactions_queryset = self._apply_filters(
                transactions_queryset, filter_form.cleaned_data
            )

        context = {
            'transactions': transactions_queryset,
            'filter_form': filter_form,
        }
        return render(request, 'dds_app/transaction_list.html', context)

    def _apply_filters(self, queryset, cleaned_data):
        """Применение фильтров к queryset"""
        filter_mode = cleaned_data.get('filter_mode', 'and')

        # Получаем значения фильтров
        statuses = cleaned_data.get('status', [])
        types = cleaned_data.get('type', [])
        categories = cleaned_data.get('category', [])
        subcategories = cleaned_data.get('subcategory', [])
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')

        # Строим Q-объекты для фильтрации
        queries = []

        if statuses:
            queries.append(Q(status__in=statuses))
        if types:
            queries.append(Q(type__in=types))
        if categories:
            queries.append(Q(category__in=categories))
        if subcategories:
            queries.append(Q(subcategory__in=subcategories))

        # Фильтр по датам применяется всегда
        date_query = Q()
        if date_from:
            date_query &= Q(date__gte=date_from)
        if date_to:
            date_query &= Q(date__lte=date_to)

        # Объединяем запросы
        if queries:
            if filter_mode == 'or':
                main_query = queries[0]
                for query in queries[1:]:
                    main_query |= query
            else:  # AND
                main_query = queries[0]
                for query in queries[1:]:
                    main_query &= query

            main_query &= date_query
        else:
            main_query = date_query

        return queryset.filter(main_query)


class TransactionCreateView(LoginRequiredMixin, View):
    """Создание новой транзакции"""

    def get(self, request):
        print(f" GET: Creating new transaction form")
        form = TransactionForm()
        return render(request, 'dds_app/transaction_form.html', {
            'form': form,
            'title': 'Добавить транзакцию',
            'action': 'create'
        })

    def post(self, request):
        print(f" POST: Processing new transaction creation")
        print(f"POST data keys: {list(request.POST.keys())}")
        
        form = TransactionForm(request.POST)
        
        if form.is_valid():
            print(" Form is valid, saving transaction...")
            transaction = form.save(commit=False)
            transaction.user = request.user
            
            try:
                transaction.save()
                print(f" Transaction saved successfully with ID: {transaction.pk}")
                messages.success(request, 'Транзакция успешно создана!')
                return redirect('dds_app:transaction_list')
            except Exception as e:
                print(f" Error saving transaction: {str(e)}")
                form.add_error(None, f"Ошибка при сохранении транзакции: {str(e)}")
        else:
            print(" Form validation failed:")
            for field, errors in form.errors.items():
                print(f"   {field}: {errors}")

        return render(request, 'dds_app/transaction_form.html', {
            'form': form,
            'title': 'Добавить транзакцию',
            'action': 'create'
        })


@login_required
def transaction_edit(request, pk):
    """Редактирование транзакции с улучшенным логированием"""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        print(f"  POST: Editing transaction {pk}")
        print("="*60)
        
        # Логируем POST данные
        print(" Received POST data:")
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                print(f"   {key}: {repr(value)}")
        
        # Логируем исходные данные транзакции
        print(f" Original transaction data:")
        print(f"   ID: {transaction.pk}")
        print(f"   Type: {repr(transaction.type)}")
        print(f"   Category: {repr(transaction.category)}")
        print(f"   Subcategory: {repr(transaction.subcategory)}")
        print(f"   Amount: {transaction.amount}")
        print(f"   Status: {repr(transaction.status)}")
        
        # Создаем форму
        print(f" Creating form with POST data...")
        form = TransactionForm(request.POST, instance=transaction)
        
        print(f" Checking form validity...")
        is_valid = form.is_valid()
        print(f" Form validation result: {is_valid}")
        
        if is_valid:
            print(" Form is valid, attempting to save...")
            
            try:
                # Сохраняем изменения
                updated_transaction = form.save(commit=False)
                updated_transaction.user = request.user  # Убеждаемся, что пользователь не изменился
                
                print(f" Saving updated transaction:")
                print(f"   Type: {repr(updated_transaction.type)}")
                print(f"   Category: {repr(updated_transaction.category)}")
                print(f"   Subcategory: {repr(updated_transaction.subcategory)}")
                print(f"   Amount: {updated_transaction.amount}")
                print(f"   Status: {repr(updated_transaction.status)}")
                
                updated_transaction.save()
                
                print(f" Transaction {pk} updated successfully!")
                messages.success(request, 'Транзакция успешно обновлена!')
                return redirect('dds_app:transaction_list')
                
            except ValueError as e:
                print(f" ValueError during save: {str(e)}")
                form.add_error(None, f"Ошибка валидации: {str(e)}")
            except Exception as e:
                print(f" Unexpected error during save: {str(e)}")
                form.add_error(None, f"Неизвестная ошибка: {str(e)}")
        else:
            print(" Form validation failed!")
            print(" Form errors:")
            for field, errors in form.errors.items():
                print(f"   {field}: {errors}")
            
            if form.non_field_errors():
                print(" Non-field errors:")
                for error in form.non_field_errors():
                    print(f"   {error}")
        
        print("="*60 + "\n")

    else:  # GET request
        print(f" GET: Loading edit form for transaction {pk}")
        print(f"   Original values: type={transaction.type}, category={transaction.category}, subcategory={transaction.subcategory}")
        
        form = TransactionForm(instance=transaction)

    return render(request, 'dds_app/transaction_form.html', {
        'form': form,
        'transaction': transaction,
        'title': 'Редактировать транзакцию',
        'action': 'edit'
    })


@login_required
def transaction_delete(request, pk):
    """Удаление транзакции"""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        print(f"  Deleting transaction {pk}")
        transaction.delete()
        messages.success(request, 'Транзакция успешно удалена!')
        return redirect('dds_app:transaction_list')

    return render(request, 'dds_app/transaction_delete.html', {
        'transaction': transaction
    })


# ================ Прочие представления ================

def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'dds_app/register.html', {'form': form})