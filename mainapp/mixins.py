from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View
from .models import Category, Cart, Customer, Notebook, Smartphone, Desktop, Headphones, Fridge, SmartWatch, TV, Washer


class CategoryDetailMixin(SingleObjectMixin):

    CATEGORY_SLUG2PRODUCT_MODEL = {
        'notebooks': Notebook,
        'smartphones': Smartphone,
        'desktops': Desktop,
        'headphones': Headphones,
        'fridges': Fridge,
        'tvs': TV,
        'washers': Washer,
        'smartwatches': SmartWatch,

    }

    def get_context_data(self, **kwargs):
        if isinstance(self.get_object(), Category):
            model = self.CATEGORY_SLUG2PRODUCT_MODEL[self.get_object().slug]
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.get_categories_for_left_sidebar()
            context['category_products'] = model.objects.select_related('category').all()
            return context
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.get_categories_for_left_sidebar()
        return context


class CartMixin(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer)
        else:
            cart = Cart.objects.filter(for_anonymous_user=True).first()
            if not cart:
                cart = Cart.objects.create(for_anonymous_user=True)
        self.cart = cart
        return super().dispatch(request, *args, **kwargs)

    def get_context(self):
        categories = Category.objects.get_categories_for_left_sidebar()
        context = dict()
        context['computers'] = list(filter(lambda x: x['name'] == 'Персональные компьютеры' or x['name'] == 'Ноутбуки', categories))
        context['mobiles'] = list(filter(lambda x: x['name'] == 'Наушники' or x['name'] == 'Смартфоны', categories))
        context['appliances'] = list(filter(lambda x: x['name'] == 'Холодильники' or x['name'] == 'Стиральные машины', categories))
        context['tvs'] = list(filter(lambda x: x['name'] == 'Телевизоры', categories))
        context['smartwatches'] = list(filter(lambda x: x['name'] == 'Умные часы', categories))
        return context


