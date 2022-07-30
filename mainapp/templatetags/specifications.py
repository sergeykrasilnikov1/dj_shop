from django import template
from django.utils.safestring import mark_safe

from mainapp.models import Smartphone


register = template.Library()

TABLE_CONTENT = """
                    <tr>
                      <td>{name}</td>
                      <td>{value}</td>
                    </tr>
                """

PRODUCT_SPEC = {
    'notebook': {
        'Диагональ': 'diagonal',
        'Тип дисплея': 'display_type',
        'Частота процессора': 'processor_freq',
        'Оперативная память': 'ram',
        'Видеокарта': 'video',
        'Время работы аккумулятора': 'time_without_charge'
    },
    'smartphone': {
        'Диагональ': 'diagonal',
        'Тип дисплея': 'display_type',
        'Разрешение экрана': 'resolution',
        'Заряд аккумулятора': 'accum_volume',
        'Оперативная память': 'ram',
        'Наличие слота для SD карты': 'sd',
        'Максимальный объем SD карты': 'sd_volume_max',
        'Камера (МП)': 'main_cam_mp',
        'Фронтальная камера (МП)': 'frontal_cam_mp'
    },

    'desktop': {
        'Модель процессора': 'processor_model',
        'Габариты': 'size',
        'Частота процессора': 'processor_freq',
        'Оперативная память': 'ram',
        'Видеокарта': 'video',
        'Цвет': 'color'
    },

    'headphones': {
        'Вес': 'weight',
        'Мощность': 'power',
        'Частота максимальная': 'max_freq',
        'микрофон': 'microphone',
        'Цвет': 'color'
    },
    'fridge': {
        'Вес': 'weight',
        'Мощность': 'power',
        'Энергопотребление': 'energy_consumption',
        'Хладагент': 'refrigerant',
        'Цвет': 'color'
    },
    'washer': {
            'Вес': 'weight',
            'Мощность': 'power',
            'Энергопотребление': 'energy_consumption',
            'Уровень шума': 'noise_level',
            'Цвет': 'color'
        },
    'tv': {
            'Вес': 'weight',
            'Мощность': 'power',
            'Энергопотребление': 'energy_consumption',
            'Экран': 'display',
            'Цвет': 'color'
        },
    'smartwatch': {
            'Вес': 'weight',
            'Мощность': 'power',
            'Энергопотребление': 'energy_consumption',
            'Время работы аккумулятора': 'time_without_charge',
            'Цвет': 'color',
            'Экран': 'display',
    },
}


def get_product_spec(product, model_name, flag=False):
    table_content = ''
    count = 0
    for name, value in PRODUCT_SPEC[model_name].items():
        table_content += TABLE_CONTENT.format(name=name, value=getattr(product, value))
        if flag:
            count += 1
            if count == 3:
                break
    return table_content


@register.filter
def product_spec(product):
    model_name = product.__class__._meta.model_name
    if isinstance(product, Smartphone):
        if not product.sd:
            PRODUCT_SPEC['smartphone'].pop('Максимальный объем SD карты', None)
        else:
            PRODUCT_SPEC['smartphone']['Максимальный объем SD карты'] = 'sd_volume_max'
    return mark_safe(get_product_spec(product, model_name))


@register.filter
def product_spec_short(product):
    model_name = product.__class__._meta.model_name
    return mark_safe(get_product_spec(product, model_name, flag=True))

