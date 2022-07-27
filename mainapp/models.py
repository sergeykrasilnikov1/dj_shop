from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Q
from django.urls import reverse

User = get_user_model()


def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]


def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


class LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(*args):
        products = []
        limit_products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.select_related('category').all().order_by('-buy_count')[:8]
            model_limit_products  =ct_model.model_class()._base_manager.select_related('category').all().filter(limit=True)[:16]
            products.extend(model_products)
            limit_products.extend(model_limit_products)
        return sorted(products, key=lambda x: x.buy_count, reverse=True)[:8], limit_products[:16]


class CatalogManager:

    @staticmethod
    def get_products_for_catalog(*args, **kwargs):
        query = kwargs.get('query')
        products = dict()
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.select_related('category').all()
            category = model_products.first().category
            if query:
                products[category] = model_products.filter(
                    Q(title__icontains=query) | Q(description__icontains=query) | Q(price__icontains=query)
        )
            else:
                products[category] = model_products
        return products


class Catalog:

    objects = CatalogManager()


class LatestProducts:

    objects = LatestProductsManager()


class CategoryManager(models.Manager):

    CATEGORY_NAME_COUNT_NAME = {
        'Ноутбуки': 'notebook__count',
        'Смартфоны': 'smartphone__count',
        'Персональные компьютеры': 'desktop__count',
        'Наушники': 'headphones__count',
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_left_sidebar(self):
        models = get_models_for_count('notebook', 'smartphone', 'desktop', 'headphones')
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME_COUNT_NAME[c.name]))
            for c in qs
        ]
        return data


class Category(models.Model):

    name = models.CharField(max_length=255, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug, 'sort': 'price'})


class Product(models.Model):

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Наименование')
    slug = models.SlugField(unique=True)
    image = models.ImageField(null=True)
    description = models.TextField(verbose_name='Описание', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    limit = models.BooleanField(default=False)
    free_delivery = models.BooleanField(default=False)
    in_stock = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    buy_count = models.PositiveIntegerField(default=0)
    reviews = models.ManyToManyField('Review', blank=True)

    def __str__(self):
        return self.title

    def get_model_name(self):
        return self.__class__.__name__.lower()


class Notebook(Product):

    diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
    display_type = models.CharField(max_length=255, verbose_name='Тип дисплея')
    processor_freq = models.CharField(max_length=255, verbose_name='Частота процессора')
    ram = models.CharField(max_length=255, verbose_name='Оперативная память')
    video = models.CharField(max_length=255, verbose_name='Видеокарта')
    time_without_charge = models.CharField(max_length=255, verbose_name='Время работы аккумулятора')

    def default(self):
        return self.images.first()

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class NotebookGallery(models.Model):
    notebook = models.ForeignKey(Notebook, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(verbose_name='Изображение')

    def __str__(self):
        return f'Изображение {self.id}'


class Desktop(Product):
    processor_model = models.CharField(max_length=255, verbose_name='Модель процессора')
    size = models.CharField(max_length=255, verbose_name='Габариты')
    processor_freq = models.CharField(max_length=255, verbose_name='Частота процессора')
    ram = models.CharField(max_length=255, verbose_name='Оперативная память')
    video = models.CharField(max_length=255, verbose_name='Видеокарта')
    color = models.CharField(max_length=255, verbose_name='Цвет')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class DesktopGallery(models.Model):
    desktop = models.ForeignKey(Desktop, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(verbose_name='Изображение')


class Smartphone(Product):

    diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
    display_type = models.CharField(max_length=255, verbose_name='Тип дисплея')
    resolution = models.CharField(max_length=255, verbose_name='Разрешение экрана')
    accum_volume = models.CharField(max_length=255, verbose_name='Объем батареи')
    ram = models.CharField(max_length=255, verbose_name='Оперативная память')
    sd = models.BooleanField(default=True, verbose_name='Наличие SD карты')
    sd_volume_max = models.CharField(
        max_length=255, null=True, blank=True, verbose_name='Максимальный объем встраивамой памяти'
    )
    main_cam_mp = models.CharField(max_length=255, verbose_name='Главная камера')
    frontal_cam_mp = models.CharField(max_length=255, verbose_name='Фронтальная камера')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class SmartphoneGallery(models.Model):
    smartphone = models.ForeignKey(Smartphone, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(verbose_name='Изображение')


class Headphones(Product):

    weight = models.CharField(max_length=255, verbose_name='Вес')
    color = models.CharField(max_length=255, verbose_name='Цвет')
    max_freq = models.CharField(max_length=255, verbose_name='Максимальная частота')
    power = models.CharField(max_length=255, verbose_name='Мощность')
    microphone = models.CharField(max_length=255, verbose_name='Микрофон')
    noise_reduction = models.BooleanField(verbose_name='Шумоподавление', default=False)

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class HeadphonesGallery(models.Model):
    headphones = models.ForeignKey(Headphones, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(verbose_name='Изображение')


class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE, null=True)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')

    def __str__(self):
        return "Продукт: {} (для корзины)".format(self.content_object.title)

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)


class Cart(models.Model):

    owner = models.ForeignKey('Customer', null=True, verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    tel = models.CharField(max_length=20, verbose_name='Номер телефона', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Заказы покупателя', related_name='related_order', blank=True)
    avatar = models.ImageField(null=True, verbose_name='Аватар')

    def __str__(self):
        return "Покупатель: {} {}".format(self.user.first_name, self.user.last_name)


class Order(models.Model):

    NOT_PAYMENT = 'not_payment'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'

    STATUS_CHOICES = (
        (NOT_PAYMENT, 'Не оплачен'),
        (STATUS_IN_PROGRESS, 'Доставляется'),
        (STATUS_READY, 'Заказ готов'),
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупатель', related_name='related_orders', on_delete=models.CASCADE)
    city = models.CharField(max_length=30, verbose_name='Город', null=True)
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Адрес', null=True, blank=True)

    payment_method = models.CharField(
        max_length=100,
        verbose_name='Способ оплаты',
    )
    delivery_method = models.CharField(
        max_length=100,
        verbose_name='Способ доставки',
    )
    status = models.CharField(
        max_length=100,
        verbose_name='Статус заказ',
        choices=STATUS_CHOICES,
        default='Не оплачен'
    )

    created_at = models.DateField(auto_now_add=True, verbose_name='Дата создания заказа')

    def __str__(self):
        return str(self.id)


class Review(models.Model):
    text = models.TextField(verbose_name='Комментарий')
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, verbose_name='Комментатор')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'комментарий {}'.format(self.user.user.username)
