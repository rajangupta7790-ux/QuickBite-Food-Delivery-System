from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name    = models.CharField(max_length=100)
    emoji   = models.CharField(max_length=10, default="🍽️")
    slug    = models.SlugField(unique=True)
    order   = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    name          = models.CharField(max_length=200)
    slug          = models.SlugField(unique=True)
    cuisine       = models.CharField(max_length=200)
    location      = models.CharField(max_length=200, default='Mumbai')
    description   = models.TextField(blank=True)
    image         = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    emoji         = models.CharField(max_length=10, default="🍽️")
    rating        = models.DecimalField(max_digits=3, decimal_places=1, default=4.0)
    delivery_time = models.PositiveIntegerField(default=30, help_text="Minutes")
    min_order     = models.PositiveIntegerField(default=99)
    avg_cost      = models.PositiveIntegerField(default=200, help_text="Cost for two")
    delivery_fee  = models.PositiveIntegerField(default=40)
    discount      = models.CharField(max_length=100, blank=True, help_text="e.g. 40% OFF")
    offer         = models.CharField(max_length=200, blank=True)
    is_pure_veg   = models.BooleanField(default=False)
    is_active     = models.BooleanField(default=True)
    categories    = models.ManyToManyField(Category, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-rating']

    def __str__(self):
        return self.name

    @property
    def rating_count(self):
        return self.orders.count() * 12 + 100


class MenuCategory(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_categories')
    name       = models.CharField(max_length=100)
    order      = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Menu Categories"

    def __str__(self):
        return f"{self.restaurant.name} — {self.name}"

    @property
    def item_count(self):
        return self.items.count()


class MenuItem(models.Model):
    restaurant    = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    menu_category = models.ForeignKey(MenuCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    name          = models.CharField(max_length=200)
    description   = models.TextField(blank=True)
    price         = models.DecimalField(max_digits=8, decimal_places=2)
    original_price= models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    image         = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    emoji         = models.CharField(max_length=10, default="🍛")
    is_veg        = models.BooleanField(default=True)
    is_available  = models.BooleanField(default=True)
    is_bestseller = models.BooleanField(default=False)
    order         = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.restaurant.name} — {self.name}"


class UserProfile(models.Model):
    user    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone   = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    dob     = models.DateField(null=True, blank=True)
    avatar  = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('confirmed',   'Confirmed'),
        ('preparing',   'Preparing'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered',   'Delivered'),
        ('cancelled',   'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('cod',         'Cash on Delivery'),
        ('upi',         'UPI'),
        ('card',        'Credit/Debit Card'),
        ('netbanking',  'Net Banking'),
    ]

    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    restaurant      = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    order_id        = models.CharField(max_length=20, unique=True)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method  = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    full_name       = models.CharField(max_length=200)
    phone           = models.CharField(max_length=15)
    address         = models.TextField()
    city            = models.CharField(max_length=100)
    pincode         = models.CharField(max_length=10)
    instructions    = models.TextField(blank=True)
    subtotal        = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee    = models.DecimalField(max_digits=8,  decimal_places=2, default=0)
    platform_fee    = models.DecimalField(max_digits=8,  decimal_places=2, default=5)
    discount        = models.DecimalField(max_digits=8,  decimal_places=2, default=0)
    total           = models.DecimalField(max_digits=10, decimal_places=2)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_id} by {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            import random, string
            for _ in range(10):
                candidate = 'QB' + ''.join(random.choices(string.digits, k=6))
                if not Order.objects.filter(order_id=candidate).exists():
                    self.order_id = candidate
                    break
            else:
                # fallback to 8-digit if all 6-digit attempts collide
                self.order_id = 'QB' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order     = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    name      = models.CharField(max_length=200)
    price     = models.DecimalField(max_digits=8, decimal_places=2)
    quantity  = models.PositiveIntegerField(default=1)


# Add ye models.py mein (existing models k baad)

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, choices=[('Home', 'Home'), ('Work', 'Work'), ('Other', 'Other')])
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.label}"


class PaymentMethod(models.Model):
    CARD_TYPES = [('debit', 'Debit Card'), ('credit', 'Credit Card'), ('upi', 'UPI')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    card_type = models.CharField(max_length=20, choices=CARD_TYPES)
    last_4_digits = models.CharField(max_length=4)
    cardholder_name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.card_type} (*{self.last_4_digits})"


class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preference')
    order_updates = models.BooleanField(default=True)
    promotions = models.BooleanField(default=True)
    reviews = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Notification Preferences"

    @property
    def total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.name}"