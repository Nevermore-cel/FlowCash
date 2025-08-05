from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'get_status_display', 'get_type_display', 
                    'get_category_display', 'get_subcategory_display', 'amount', 'created_at')
    list_filter = ('status', 'type', 'category', 'user', 'date', 'created_at')
    search_fields = ('comment', 'user__username', 'user__email')
    ordering = ('-date', '-created_at')
    date_hierarchy = 'date'
    list_per_page = 25
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'date', 'status', 'amount')
        }),
        ('Категоризация', {
            'fields': ('type', 'category', 'subcategory')
        }),
        ('Дополнительно', {
            'fields': ('comment',),
            'classes': ('collapse',)
        }),
    )
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    get_status_display.short_description = 'Статус'
    get_status_display.admin_order_field = 'status'

    def get_type_display(self, obj):
        return obj.get_type_display()
    get_type_display.short_description = 'Тип'
    get_type_display.admin_order_field = 'type'

    def get_category_display(self, obj):
        return obj.get_category_display()
    get_category_display.short_description = 'Категория'
    get_category_display.admin_order_field = 'category'

    def get_subcategory_display(self, obj):
        return obj.get_subcategory_display()
    get_subcategory_display.short_description = 'Подкатегория'
    get_subcategory_display.admin_order_field = 'subcategory'