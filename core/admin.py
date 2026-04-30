from django.contrib import admin
from .models import (
    Category, Restaurant, MenuCategory,
    MenuItem, UserProfile, Order, OrderItem,
    Address, PaymentMethod, NotificationPreference
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'emoji', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    ordering      = ('order',)


class MenuCategoryInline(admin.TabularInline):
    model = MenuCategory
    extra = 1


class MenuItemInline(admin.TabularInline):
    model  = MenuItem
    extra  = 1
    fields = ('name', 'price', 'is_veg', 'is_available', 'is_bestseller')


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display   = ('name', 'cuisine', 'rating', 'delivery_time', 'is_active', 'is_pure_veg')
    list_filter    = ('is_active', 'is_pure_veg')
    search_fields  = ('name', 'cuisine')
    prepopulated_fields = {'slug': ('name',)}
    inlines        = [MenuCategoryInline]
    list_editable  = ('is_active',)


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'order')
    list_filter  = ('restaurant',)
    inlines      = [MenuItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display  = ('name', 'restaurant', 'menu_category', 'price', 'is_veg', 'is_available', 'is_bestseller')
    list_filter   = ('restaurant', 'is_veg', 'is_available', 'is_bestseller')
    search_fields = ('name', 'restaurant__name')
    list_editable = ('is_available', 'is_bestseller')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')


class OrderItemInline(admin.TabularInline):
    model     = OrderItem
    extra     = 0
    readonly_fields = ('name', 'price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display   = ('order_id', 'user', 'restaurant', 'total', 'status', 'payment_method', 'created_at')
    list_filter    = ('status', 'payment_method', 'created_at')
    search_fields  = ('order_id', 'user__username', 'restaurant__name')
    readonly_fields = ('order_id', 'created_at', 'updated_at')
    list_editable  = ('status',)
    inlines        = [OrderItemInline]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'city', 'is_default', 'created_at')
    list_filter = ('label', 'is_default', 'city')
    search_fields = ('user__username', 'city')


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_type', 'last_4_digits', 'is_default', 'created_at')
    list_filter = ('card_type', 'is_default')
    search_fields = ('user__username', 'cardholder_name')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_updates', 'promotions', 'reviews')
    list_filter = ('order_updates', 'promotions', 'reviews')
    search_fields = ('user__username',)