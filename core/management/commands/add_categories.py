"""
Management command to add default menu categories to restaurants without any.
Run: python manage.py add_categories
"""
from django.core.management.base import BaseCommand
from core.models import Restaurant, MenuCategory


class Command(BaseCommand):
    help = 'Add default menu categories to restaurants that have none'

    def handle(self, *args, **options):
        default_categories = [
            'Bestsellers',
            'Appetizers',
            'Main Course',
            'Sides',
            'Desserts',
            'Beverages'
        ]
        
        restaurants = Restaurant.objects.all()
        count = 0
        
        for restaurant in restaurants:
            # Check if this restaurant already has categories
            if restaurant.menu_categories.exists():
                self.stdout.write(
                    f"⏭️  Skipping {restaurant.name} (already has categories)"
                )
                continue
            
            # Create default categories
            for idx, cat_name in enumerate(default_categories, 1):
                MenuCategory.objects.create(
                    restaurant=restaurant,
                    name=cat_name,
                    order=idx
                )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Added {len(default_categories)} categories to {restaurant.name}"
                )
            )
            count += 1
        
        if count == 0:
            self.stdout.write(
                self.style.WARNING("ℹ️  All restaurants already have categories!")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\n✨ Done! Updated {count} restaurant(s)")
            )
