from .models import Category


def categories_processor(request):
    categories = Category.objects.all()
    return {
        'all_categories': categories
    }
