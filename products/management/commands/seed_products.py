# products/management/commands/seed_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Product, Comment, Category
from products.factories import PRODUCT_DATA, COMMENT_REVIEWS, UserFactory, ProductFactory, CommentFactory
from django.utils.text import slugify
import random
import factory


class Command(BaseCommand):
    help = 'Seeds the database with realistic fake data for an online shop.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding the database with realistic data...")
        self.cleanup_old_data()
        self.create_users()
        self.create_products()
        self.create_comments()
        self.stdout.write(self.style.SUCCESS("Database seeding complete!"))

    def cleanup_old_data(self):
        """Cleans up all existing data to prevent duplicates."""
        self.stdout.write("Cleaning up old data...")
        Comment.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        # Clean up fake users
        get_user_model().objects.filter(username__startswith='user_').delete()

    def create_users(self):
        """Creates a batch of fake users."""
        self.stdout.write("Creating 10 fake users...")
        UserFactory.create_batch(10)
        self.stdout.write(self.style.SUCCESS("Users created."))

    def create_products(self):
        """
        Creates categories and then products based on the predefined PRODUCT_DATA.
        This ensures products and categories are consistent.
        """
        self.stdout.write("Creating categories and products...")
        # Create categories from the factory
        for category_name in sorted(list(set(item['category_name'] for item in PRODUCT_DATA))):
            Category.objects.get_or_create(
                name=category_name,
                slug=slugify(category_name, allow_unicode=True)
            )

        # Create products using the factory.
        for item in PRODUCT_DATA:
            category = Category.objects.get(name=item['category_name'])
            # Create a single product instance for each item in the list
            Product.objects.create(
                title=item['title'],
                short_description=item['short_description'],
                description=item['description'],
                key_features=item.get('key_features', ''),
                price=item['price'],
                category=category,
                discount_percent=random.choice([0, 0, 0, 10, 15, 20, 25, 30]),
                status='avl',
                stock_quantity=random.randint(1, 50)
            )
        self.stdout.write(self.style.SUCCESS("Products created."))

    def create_comments(self):
        """Creates realistic comments for each product."""
        self.stdout.write("Creating comments for products...")
        users = list(get_user_model().objects.all())
        products = list(Product.objects.all())

        for product in products:
            # Get a list of relevant comments from the factory data, or use a default if none exist
            comments_data = COMMENT_REVIEWS.get(product.title, [])

            # Create comments from the predefined data
            for comment_data in comments_data:
                Comment.objects.create(
                    product=product,
                    user=random.choice(users),
                    text=comment_data['text'],
                    stars=comment_data['stars'],
                    is_verified=True,
                )

            # Also add a few random comments for good measure
            for _ in range(random.randint(0, 2)):
                CommentFactory(product=product, user=random.choice(users))

        self.stdout.write(self.style.SUCCESS("Comments created."))
