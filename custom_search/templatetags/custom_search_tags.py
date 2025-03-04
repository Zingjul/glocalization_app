from django import template
from custom_search.forms import CustomSearchForm

register = template.Library()

@register.inclusion_tag('custom_search/custom_search_form.html', takes_context=True)
def custom_search_form(context):
    form = CustomSearchForm(context.get('request').GET)
    return {'form': form}