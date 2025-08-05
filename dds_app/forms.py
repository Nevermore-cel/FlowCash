from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Transaction
from datetime import datetime


class TransactionForm(forms.ModelForm):
    """Форма для создания/редактирования транзакций с поддержкой AJAX"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Автозаполнение даты текущей датой при создании
        if not self.instance.pk:
            self.fields['date'].initial = datetime.now().date()

        # Настройка выборов для полей category и subcategory
        self._setup_dynamic_fields()

    def _setup_dynamic_fields(self):
        """Настройка динамических полей в зависимости от режима формы"""
        
        if self.instance.pk:
            # Режим редактирования
            print(f"Setting up form for editing transaction {self.instance.pk}")
            print(f"Original values: type={self.instance.type}, category={self.instance.category}, subcategory={self.instance.subcategory}")
            
            # В режиме редактирования оставляем все варианты доступными
            # Django автоматически выберет правильные значения из instance
            # AJAX будет работать только при изменении пользователем
            
            # Устанавливаем полные списки выборов
            self.fields['category'].choices = [('', '---------')] + list(Transaction.Category.choices)
            self.fields['subcategory'].choices = [('', '---------')] + list(Transaction.Subcategory.choices)
            
        else:
            # Режим создания
            print("Setting up form for creating new transaction")
            
            # При создании начинаем с пустых выборов для AJAX
            self.fields['category'].choices = [('', '---------')]
            self.fields['subcategory'].choices = [('', '---------')]

    def clean(self):
        """Расширенная валидация с детальным логированием"""
        print("\n" + "="*50)
        print("FORM VALIDATION STARTED")
        print("="*50)
        
        # Логируем исходные данные
        if hasattr(self, 'data'):
            print("Raw POST data:")
            for key, value in self.data.items():
                if key != 'csrfmiddlewaretoken':
                    print(f"  {key}: {value}")
        
        # Вызываем родительскую валидацию
        cleaned_data = super().clean()
        
        print(f"\nCleaned data after super().clean():")
        for key, value in cleaned_data.items():
            print(f"  {key}: {repr(value)}")
        
        # Получаем значения для проверки зависимостей
        transaction_type = cleaned_data.get('type')
        category = cleaned_data.get('category')
        subcategory = cleaned_data.get('subcategory')
        
        print(f" Validating dependencies:")
        print(f"  Type: {repr(transaction_type)}")
        print(f"  Category: {repr(category)}")
        print(f"  Subcategory: {repr(subcategory)}")
        
        # Валидация 1: Тип -> Категория
        if transaction_type and category:
            allowed_categories = Transaction.TYPE_CATEGORY_MAP.get(transaction_type, [])
            print(f"  Allowed categories for type '{transaction_type}': {allowed_categories}")
            
            if category not in allowed_categories:
                category_display = dict(Transaction.Category.choices).get(category, category)
                type_display = dict(Transaction.Type.choices).get(transaction_type, transaction_type)
                error_msg = f'Категория "{category_display}" не относится к выбранному типу "{type_display}"'
                
                print(f"  VALIDATION ERROR: {error_msg}")
                self.add_error('category', error_msg)
            else:
                print(f" Category validation passed")

        # Валидация 2: Категория -> Подкатегория
        if category and subcategory:
            allowed_subcategories = Transaction.CATEGORY_SUBCATEGORY_MAP.get(category, [])
            print(f"  Allowed subcategories for category '{category}': {allowed_subcategories}")
            
            if subcategory not in allowed_subcategories:
                subcategory_display = dict(Transaction.Subcategory.choices).get(subcategory, subcategory)
                category_display = dict(Transaction.Category.choices).get(category, category)
                error_msg = f'Подкатегория "{subcategory_display}" не относится к выбранной категории "{category_display}"'
                
                print(f"  VALIDATION ERROR: {error_msg}")
                self.add_error('subcategory', error_msg)
            else:
                print(f" Subcategory validation passed")

        # Логируем финальные ошибки
        if self.errors:
            print(f"\nFinal form errors:")
            for field, errors in self.errors.items():
                print(f"  {field}: {errors}")
        else:
            print(f" Form validation successful - no errors")
        
        print("="*50)
        print("FORM VALIDATION COMPLETED")
        print("="*50 + "\n")
        
        return cleaned_data

    def _get_category_choices(self, transaction_type_value):
        """Получить варианты категорий для типа транзакции"""
        choices = [('', '---------')]
        allowed_categories = Transaction.TYPE_CATEGORY_MAP.get(transaction_type_value, [])
        for value, label in Transaction.Category.choices:
            if value in allowed_categories:
                choices.append((value, label))
        return choices

    def _get_subcategory_choices(self, category_value):
        """Получить варианты подкатегорий для категории"""
        choices = [('', '---------')]
        allowed_subcategories = Transaction.CATEGORY_SUBCATEGORY_MAP.get(category_value, [])
        for value, label in Transaction.Subcategory.choices:
            if value in allowed_subcategories:
                choices.append((value, label))
        return choices

    class Meta:
        model = Transaction
        fields = ['date', 'status', 'type', 'category', 'subcategory', 'amount', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_type'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_category'
            }),
            'subcategory': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_subcategory'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительная информация (необязательно)'
            }),
        }


class TransactionFilterForm(forms.Form):
    """Форма фильтрации транзакций"""

    FILTER_CHOICES = (
        ('and', 'Все выбранные (AND)'),
        ('or', 'Любое из выбранных (OR)'),
    )

    filter_mode = forms.ChoiceField(
        choices=FILTER_CHOICES,
        initial='and',
        label="Режим фильтрации",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    status = forms.MultipleChoiceField(
        choices=Transaction.Status.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    type = forms.MultipleChoiceField(
        choices=Transaction.Type.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    category = forms.MultipleChoiceField(
        choices=Transaction.Category.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    subcategory = forms.MultipleChoiceField(
        choices=Transaction.Subcategory.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    date_from = forms.DateField(
        label="Дата с",
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        label="Дата по",
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user