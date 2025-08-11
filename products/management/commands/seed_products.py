# products/management/commands/seed_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Product, Comment, Category
from accounts.models import UserProfile
from products.factories import UserFactory, UserProfileFactory, ProductFactory, CommentFactory, PRODUCT_DATA, \
    COMMENT_REVIEWS
from django.utils.text import slugify
import random
import factory


class Command(BaseCommand):
    help = 'Seeds the database with realistic fake data for an online shop.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding the database with realistic data...")
        self.cleanup_old_data()
        self.create_users_with_profiles()
        self.create_products()
        self.create_comments()
        self.stdout.write(self.style.SUCCESS("Database seeding complete!"))

    def cleanup_old_data(self):
        """Cleans up all existing data to prevent duplicates."""
        self.stdout.write("Cleaning up old data...")
        Comment.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        UserProfile.objects.all().delete()
        # Clean up fake users
        get_user_model().objects.filter(username__startswith='user_').delete()
        self.stdout.write(self.style.SUCCESS("Old data cleaned."))

    def create_users_with_profiles(self):
        """Creates a batch of fake users with a corresponding user profile."""
        self.stdout.write("Creating users and profiles...")



        # Create a batch of users with profiles using the factory
        # This will automatically create a User and a UserProfile for each
        UserProfileFactory.create_batch(10)
        self.stdout.write(self.style.SUCCESS("Users and profiles created."))

    def create_products(self):
        """
        Creates categories and products using factories, ensuring consistency.
        """
        self.stdout.write("Creating products and their categories...")
        # Create products using the factory.
        # This will automatically handle category creation/retrieval
        ProductFactory.create_batch(len(PRODUCT_DATA))
        self.stdout.write(self.style.SUCCESS("Products created."))

    def create_comments(self):
        """
        Creates realistic comments for each product,
        using both specific data and random factory-generated comments.
        """
        self.stdout.write("Creating comments for products...")
        users = list(get_user_model().objects.all())
        products = list(Product.objects.all())

        for product in products:
            # Get a list of relevant comments from the factory data
            comments_data = COMMENT_REVIEWS.get(product.title, [])

            # Create comments from the predefined data for that product
            for comment_data in comments_data:
                # Use a random user for each predefined comment
                Comment.objects.create(
                    product=product,
                    user=random.choice(users),
                    text=comment_data['text'],
                    stars=comment_data['stars'],
                    is_verified=True,
                )

            # Add a few extra random comments for good measure
            for _ in range(random.randint(0, 2)):
                CommentFactory(product=product, user=random.choice(users))

        self.stdout.write(self.style.SUCCESS("Comments created."))