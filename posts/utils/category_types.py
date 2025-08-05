from posts.models import Category

def get_category_by_type(category_name: str):
    mapping = {
        'product': 'Product',
        'service': 'Service',
        'labor': 'Labor',
    }
    return Category.objects.get_or_create(name=mapping[category_name.lower()])[0]
