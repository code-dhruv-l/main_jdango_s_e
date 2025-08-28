from django.contrib import admin
from .models import Product, ReviewRating
from .models import UserMessage
from .models import PriceInquiry

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'is_available', 'category', 'created_date', 'modified_date')
    prepopulated_fields = {'slug': ('product_name',)}

admin.site.register(Product, ProductAdmin)


class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'message', 'created_at')
    search_fields = ('name', 'message')
    ordering = ('-created_at',)

admin.site.register(UserMessage, UserMessageAdmin)


class PriceInquiryAdmin(admin.ModelAdmin):
    list_display = ('purpose', 'created_at')
    search_fields = ('purpose', 'requirement')
    ordering = ('-created_at',)

admin.site.register(PriceInquiry, PriceInquiryAdmin)

admin.site.register(ReviewRating)