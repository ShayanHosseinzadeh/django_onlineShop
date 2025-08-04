# products/admin.py
from django.contrib import admin
from .models import Product, Comment, Category # Import the new Category model


# --- New Category Admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class CommentInline(admin.StackedInline):
    model = Comment
    fields = ('user', 'text', 'stars', 'is_verified')
    readonly_fields = ('user',) # Assuming user is automatically set on comment creation
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'stock_quantity', 'status', 'datetime_created')
    list_filter = ('status', 'category', 'datetime_created')
    search_fields = ('title', 'description', 'short_description')
    list_editable = ('price', 'stock_quantity', 'status')
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'stars', 'is_verified', 'datetime_created')
    list_filter = ('is_verified', 'stars', 'datetime_created')
    list_editable = ('is_verified',)
    search_fields = ('user__username', 'text')
    actions = ['verify_comments', 'unverify_comments']

    @admin.action(description='Mark selected comments as verified')
    def verify_comments(self, request, queryset):
        queryset.update(is_verified=True)

    @admin.action(description='Mark selected comments as unverified')
    def unverify_comments(self, request, queryset):
        queryset.update(is_verified=False)