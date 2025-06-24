from django import template

register = template.Library()

@register.filter
def format_price(value):
    try:
        value = float(value)
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", " ")
        # удаляем ",00" если копеек нет
        if formatted.endswith(",00"):
            formatted = formatted[:-3]
        return formatted
    except (ValueError, TypeError):
        return value
