from django import template
from django.utils.safestring import mark_safe

from mainapp.models import Smartphone


register = template.Library()

TABLE_HEAD = """
                <table class="table">
                  <tbody>
  
             """
TABLE_TAIL = """
                  </tbody>
                </table>
             """
TABLE_CONTENT = """
              <tr>
                <td>{name}</td>
                <td>{value}</td>
            </tr>
                """
PRODUCT_SPEC = {
    'notebook': {
        'Діагональ': 'diagonal',
        'Тип дисплея': 'display',
        'Частота процессора': 'processor_freq',
        "Оперативна пам'ять": "ram",
        'Відеокарта': 'video',
        'Час роботи батареї': 'time_without_charge'
    },
    'smartphone': {
        'Діагональ': 'diagonal',
        'Тип дисплея': 'display',
        'Розширення екрана': 'resolution',
        "об'єм батареї": "accum_volume",
        "Оперативна пам'ять": 'ram',
        'Наявність слота для sd карти': 'sd',
        "Максимальний об'єм встроєної пам'яті": 'sd_volume_max',
        'Головна камера': 'main_cam_mp',
        'Фронтальна камера': 'frontal_cam_mp'


    }
}


def get_product_spec(product, model_name):
    table_content = ""
    for name, value in PRODUCT_SPEC[model_name].items():
        table_content += TABLE_CONTENT.format(name=name, value=getattr(product, value))
    return table_content

@register.filter()
def product_spec(product):
    model_name = product.__class__._meta.model_name
    if isinstance(product, Smartphone):
        if not product.sd:
            PRODUCT_SPEC['smartphone'].pop("Максимальний об'єм встроєної пам'яті")
        else:
            PRODUCT_SPEC['smartphone']["Максимальний об'єм встроєної пам'яті"] = 'sd_volume_max'
    return mark_safe(TABLE_HEAD + get_product_spec(product, model_name) + TABLE_TAIL)