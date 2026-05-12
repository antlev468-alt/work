from django import template
from orders.translations import TRANSLATIONS

register = template.Library()

@register.filter(name='translate')
def translate(text, lang):
    if lang in TRANSLATIONS and text in TRANSLATIONS[lang]:
        return TRANSLATIONS[lang][text]
    return text