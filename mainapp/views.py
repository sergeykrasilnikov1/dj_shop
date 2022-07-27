from django.core.mail import send_mail
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View, ListView
from .models import Notebook, Smartphone, Category, LatestProducts, Customer,\
    CartProduct, Review, Order, Desktop, Headphones, Catalog
from .mixins import CategoryDetailMixin, CartMixin
from .forms import OrderForm, RestorePasswordForm, UserRegistrationForm, UserUpdateForm, AuthForm
from .utils import recalc_cart
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.views import  LogoutView
from django.contrib.auth import login, authenticate, get_user_model
from PIL import Image
from django.contrib.auth.backends import ModelBackend
from shop.settings import DEFAULT_FROM_EMAIL, RECIPIENTS_EMAIL


class BaseView(CartMixin, View):

    def get(self, request):
        products, limit_products = LatestProducts.objects.get_products_for_main_page(
            'notebook', 'smartphone', 'desktop', 'headphones'
        )
        context = self.get_context()
        context['limit_products'] = limit_products
        context['products'] = products
        context['cart'] = self.cart
        return render(request, 'index.html', context)


class ProductDetailView(CartMixin, CategoryDetailMixin, DetailView):

    CT_MODEL_MODEL_CLASS = {
        'notebook': Notebook,
        'smartphone': Smartphone,
        'desktop': Desktop,
        'headphones': Headphones
    }

    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_context())
        context['ct_model'] = self.model._meta.model_name
        context['cart'] = self.cart
        return context


class CatalogView(CartMixin, ListView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'catalog.html'

    def get_context_data(self, **kwargs):
        sort = self.kwargs.get('sort')
        query = self.request.GET.get('query')
        products = Catalog.objects.get_products_for_catalog(
            'notebook', 'smartphone', 'desktop', 'headphones', query=query
        )
        context = super().get_context_data(**kwargs)
        context.update(self.get_context())
        context['cart'] = self.cart
        context['products'] = products
        if self.request.GET.get('price'):
            min_price, max_price = self.request.GET.getlist('price')[0].split(';')
            context['products'] = dict(map(lambda x: (x[0], x[1].filter(
                price__range=(int(min_price), int(max_price)))), products.items()))
            if self.request.GET.getlist('in_stock'):
                context['products'] = dict(map(lambda x: (x[0], x[1].filter(
                    in_stock__in=self.request.GET.getlist('in_stock'),
                    price__range=(int(min_price), int(max_price)))), products.items()))
            if self.request.GET.getlist('free_delivery'):
                context['products'] = dict(map(lambda x: (x[0], x[1].filter(
                    free_delivery__in=self.request.GET.getlist('free_delivery'),
                    price__range=(int(min_price), int(max_price)))), products.items()))
            if self.request.GET.getlist('title')[0] != '':
                context['products'] = dict(map(lambda x: (x[0], x[1].filter(
                    title__icontains=self.request.GET.get('title'),
                    price__range=(int(min_price), int(max_price)))), products.items()))
            if self.request.GET.getlist('free_delivery') and self.request.GET.getlist('in_stock'):
                context['products'] = dict(map(lambda x: (x[0], x[1].filter(
                    in_stock__in=self.request.GET.getlist('in_stock'),
                    free_delivery__in=self.request.GET.getlist('free_delivery'),
                    price__range=(int(min_price), int(max_price)))), products.items()))
            if self.request.GET.getlist('free_delivery') and self.request.GET.getlist('title')[0] != '':
                context['products'] = dict(map(lambda x: (x[0], x[1].filter(
                    in_stock__in=self.request.GET.getlist('in_stock'),
                    title__icontains=self.request.GET.get('title'),
                    price__range=(int(min_price), int(max_price)))), products.items()))
            if self.request.GET.getlist('free_delivery') and self.request.GET.getlist('title')[0] != '':
                context['products'] = dict(map(lambda x: (x[0], x[1].filter(
                    title__icontains=self.request.GET.get('title'),
                    free_delivery__in=self.request.GET.getlist('free_delivery'),
                    price__range=(int(min_price), int(max_price)))), products.items()))
            if self.request.GET.getlist('free_delivery') and self.request.GET.getlist('in_stock') and \
                    self.request.GET.getlist('title')[0] != '':
                context['products'] = dict(map(lambda x: (x[0], x[1].filter(
                    in_stock__in=self.request.GET.getlist('in_stock'),
                    title__icontains=self.request.GET.get('title'),
                    free_delivery__in=self.request.GET.getlist('free_delivery'),
                    price__range=(int(min_price), int(max_price)))), products.items()))
            context['min_price'] = min_price
            context['max_price'] = max_price
            context['filter'] = self.request.get_full_path().split('/')[-1]
        if sort:
            context['products'] = dict(map(lambda x: (x[0], x[1].order_by(sort)), context['products'].items()))
            sort_inc = sort.replace('-', '0')
            context[sort_inc] = sort
        return context


class SearchView(CartMixin, ListView):

    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'catalog.html'

    def get_context_data(self, **kwargs):
        query = self.request.GET.get('query')
        products = Catalog.objects.get_products_for_catalog(
             'notebook', 'smartphone', 'desktop', 'headphones', query=query
        )
        context = super().get_context_data(**kwargs)
        context.update(self.get_context())
        context['cart'] = self.cart
        context['products'] = products
        return context


class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):

    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'catalog_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        sort = self.kwargs.get('sort')
        context = super().get_context_data(**kwargs)
        context.update(self.get_context())
        context['cart'] = self.cart
        model = self.CATEGORY_SLUG2PRODUCT_MODEL[self.get_object().slug]
        if self.request.GET.get('price'):
            min_price, max_price = self.request.GET.getlist('price')[0].split(';')
            context['category_products'] = model.objects.all().filter(
                price__range=(int(min_price), int(max_price)))
            if self.request.GET.getlist('in_stock'):
                context['category_products'] = model.objects.all().filter(
                    in_stock__in=self.request.GET.getlist('in_stock'),
                    price__range=(int(min_price), int(max_price)))
            if self.request.GET.getlist('free_delivery'):
                context['category_products'] = model.objects.all().filter(
                    free_delivery__in=self.request.GET.getlist('free_delivery'),
                    price__range=(int(min_price), int(max_price)))
            if self.request.GET.getlist('title')[0] != '':
                context['category_products'] = model.objects.all().filter(
                    title__icontains=self.request.GET.get('title'),
                    price__range=(int(min_price), int(max_price)))
            if self.request.GET.getlist('free_delivery') and self.request.GET.getlist('in_stock'):
                context['category_products'] = model.objects.all().filter(
                    in_stock__in=self.request.GET.getlist('in_stock'),
                    free_delivery__in=self.request.GET.getlist('free_delivery'),
                    price__range=(int(min_price), int(max_price)))
            if self.request.GET.getlist('free_delivery') and self.request.GET.getlist('title')[0] != '':
                context['category_products'] = model.objects.all().filter(
                    in_stock__in=self.request.GET.getlist('in_stock'),
                    title__icontains=self.request.GET.get('title'),
                    price__range=(int(min_price), int(max_price)))
            if self.request.GET.getlist('free_delivery') and self.request.GET.getlist('title')[0] != '':
                context['category_products'] = model.objects.all().filter(
                    title__icontains=self.request.GET.get('title'),
                    free_delivery__in=self.request.GET.getlist('free_delivery'),
                    price__range=(int(min_price), int(max_price)))
            if self.request.GET.getlist('free_delivery') and self.request.GET.getlist('in_stock') and \
                    self.request.GET.getlist('title')[0] != '':
                context['category_products'] = model.objects.all().filter(
                    in_stock__in=self.request.GET.getlist('in_stock'),
                    title__icontains=self.request.GET.get('title'),
                    free_delivery__in=self.request.GET.getlist('free_delivery'),
                    price__range=(int(min_price), int(max_price)))
            context['min_price'] = min_price
            context['max_price'] = max_price
            context['filter'] = self.request.get_full_path().split('/')[-1]
        if sort:
            context['category_products'] = context['category_products'].order_by(sort)
            sort_inc = sort.replace('-', '0')
            context[sort_inc] = sort
        return context


class AddReview(CartMixin, View):
    def post(self, request, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        text = request.POST.get('text')
        review = Review.objects.create(text=text, user=self.cart.owner)
        product.reviews.add(review)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class AddToCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        if created:
            self.cart.products.add(cart_product)
        recalc_cart(self.cart)
        return HttpResponseRedirect('/cart/')


class DeleteFromCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар успешно удален")
        return HttpResponseRedirect('/cart/')


class ChangeQTYView(CartMixin, View):

    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        recalc_cart(self.cart)
        return HttpResponseRedirect('/cart/')


class CartView(CartMixin, View):

    def get(self, request):
        context = {
            'cart': self.cart,
        }
        context.update(self.get_context())
        return render(request, 'cart.html', context)


def sale(request):
    return render(request, 'goods/sale.html')


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None


class AccountView(CartMixin, View):
    def get(self, request):
        user = Customer.objects.get(user=request.user)
        order = Order.objects.all().filter(customer=user).order_by('-id').first()
        context = {'profile': user, 'cart': self.cart, 'order': order, 'not_pay': ['Не оплачен',]}
        context.update(self.get_context())
        return render(request, 'users/account.html', context)


class AboutView(CartMixin, View):
    def get(self, request):
        context = {'cart': self.cart}
        context.update(self.get_context())
        return render(request, 'users/about.html', context)


class UserLogoutView(LogoutView):
    next_page = '/'


class ProfileView(CartMixin, View):
    def post(self, request):
        request_copy = request.POST.copy()
        a = User.objects.get(id=request.user.id)
        flag = False
        if not request_copy.get('password1'):
            request_copy['password1'] = a.password
            request_copy['password2'] = a.password
            flag = True
        form = UserUpdateForm(request_copy, request.FILES, instance=request.user)
        email = request.POST.get('email')
        User.objects.get(id=request.user.id).delete()
        context = {'form': form, 'cart': self.cart}
        context.update(self.get_context())
        if User.objects.all().filter(email=email).exists():
            context['email'] = True
            return render(request, 'users/profile.html', context)
        tel = request.POST.get('tel')[2:]
        if Customer.objects.all().filter(tel=tel).exists():
            context['tel'] = True
            return render(request, 'users/profile.html', context)
        a.save()
        if form.is_valid():
            if flag:
                a.save(update_fields=['email', 'first_name', 'email'])
            else:
                form.save()
            if request.FILES.get('avatar'):
                if len(Image.open(request.FILES.get('avatar')).fp.read()) > 3145728:
                    context['avatar_flag'] = True
                    Customer.objects.create(
                        user=request.user,
                        tel=tel)
                    return render(request, 'users/profile.html', context)
                avatar = form.cleaned_data['avatar']
            else:
                avatar = None
            Customer.objects.create(
                user=request.user,
                tel=tel,
                avatar=avatar,
            )
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=email, password=raw_password)
            login(request, user)
            context['flag'] = True
            return render(request, 'users/profile.html', context)

    def get(self, request):
        form = UserUpdateForm()
        context = {'form': form, 'cart': self.cart}
        context.update(self.get_context())
        return render(request, 'users/profile.html', context)


class RegisterView(CartMixin, View):
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        email = request.POST.get('email')
        context = {'form': form, 'cart': self.cart}
        context.update(self.get_context())
        if User.objects.all().filter(email=email).exists():
            context['email'] = True
            return render(request, 'users/register.html', context)
        tel = request.POST.get('tel')[2:]
        if Customer.objects.all().filter(tel=tel).exists():
            context['tel'] = True
            return render(request, 'users/register.html', context)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(
                user=user,
                tel=tel,
            )
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=email, password=raw_password)
            login(request, user)
            new_cart = self.cart
            new_cart.owner = Customer.objects.get(user=request.user)
            new_cart.for_anonymous_user = False
            new_cart.save()
            return redirect('../../')
        else:
            messages.add_message(request, messages.INFO, "Неправильное написание емэйла")
            return HttpResponseRedirect('/users/register')

    def get(self, request):
        form = UserRegistrationForm()
        context = {'form': form, 'cart': self.cart}
        context.update(self.get_context())
        return render(request, 'users/register.html', context)


class UserLoginView(CartMixin, View):

    def post(self, request, **kwargs):
        auth_form = AuthForm(request.POST)
        if auth_form.is_valid():
            username = auth_form.cleaned_data['username']
            password = auth_form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    next = request.POST.get('next', '/')
                    return HttpResponseRedirect(next)
                else:
                    auth_form.add_error('__all__', 'Ошибка! Учетная запись пользователя неактивна.')
            else:
                auth_form.add_error('__all__', 'Ошибка! Проверьте правильность написания логина и пароля.')

    def get(self, request, **kwargs):
        flag = kwargs.get('flag')
        auth_form = AuthForm()
        context = {
            'form': auth_form,
            'cart': self.cart
        }
        context.update(self.get_context())
        if flag:
            context['flag'] = True
        return render(request, 'users/login.html', context=context)


class RestorePassword(CartMixin, View):
    def post(self, request):
        form = RestorePasswordForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            new_password = User.objects.make_random_password()
            current_user = User.objects.filter(email=user_email).first()
            RECIPIENTS_EMAIL.append(form.cleaned_data['email'])
            if current_user:
                current_user.set_password(new_password)
                current_user.save()
                message = f'Новый пароль: {new_password}'
                send_mail(f'Восстановление пароля от {DEFAULT_FROM_EMAIL}', message,
                              DEFAULT_FROM_EMAIL, RECIPIENTS_EMAIL)
                messages.add_message(request, messages.INFO,
                                     f"Это сообщение должно прийти на почту, но мне лень подключать Email-сервис, "
                                     f"вот новый пароль - {new_password}")
                return HttpResponseRedirect('../login/0/')

    def get(self, request):
        restore_password_form = RestorePasswordForm()
        context = {
            'form': restore_password_form
        }
        return render(request, 'users/restore_password.html', context=context)


class CheckoutView(CartMixin, View):

    def get(self, request):
        form = UserRegistrationForm()
        context = {'form': form, 'cart': self.cart}
        context.update(self.get_context())
        return render(request, 'orders/order.html', context)


class Register(CartMixin, View):

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        email = request.POST.get('email')
        context = {'form': form, 'cart': self.cart}
        context.update(self.get_context())
        if User.objects.all().filter(email=email).exists():
            context['email'] = True
            return render(request, 'orders/order.html', context)
        tel = request.POST.get('tel')[2:]
        if Customer.objects.all().filter(tel=tel).exists():
            context['tel'] = True
            return render(request, 'orders/order.html', context)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(
                user=user,
                tel=tel,
            )
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=email, password=raw_password)
            login(request, user)
            new_cart = self.cart
            new_cart.owner = Customer.objects.get(user=request.user)
            new_cart.for_anonymous_user = False
            new_cart.save()
            return HttpResponseRedirect('/orders/order')
        else:
            messages.add_message(request, messages.INFO, "Неправильное написание емэйла")
            return HttpResponseRedirect('/orders/order')


class MakeOrderView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.address = form.cleaned_data['address']
            new_order.payment_method = form.cleaned_data['payment_method']
            new_order.delivery_method = form.cleaned_data['delivery_method']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            context = {'form': form, 'cart': self.cart, 'order': new_order}
            context.update(self.get_context())
            return HttpResponseRedirect(request.path)
        return HttpResponseRedirect('/')

    def get(self, request):
        customer = Customer.objects.get(user=request.user)
        context = {
            'cart': self.cart,
            'order': Order.objects.all().filter(customer=customer).last()
        }
        context.update(self.get_context())
        return render(request, 'orders/order_confirmation.html', context)


class OneOrderView(CartMixin, View):
    def get(self, request, **kwargs):
        id = kwargs.get('pk')
        context = {
            'cart': self.cart,
            'order': Order.objects.all().get(id=id),
            'not_pay': ['Не оплачен', ]
        }
        context.update(self.get_context())
        return render(request, 'orders/oneorder.html', context)


class PaymentOrder(CartMixin, View):
    def post(self, request):
        context = {'cart': self.cart}
        context.update(self.get_context())
        return render(request, 'orders/payment.html', context)

    def get(self, request):
        customer = Customer.objects.get(user=request.user)
        order = Order.objects.all().filter(customer=customer).order_by('-id')[0]
        context = {'cart': self.cart, 'order': order}
        context.update(self.get_context())
        if order.payment_method == 'Онлайн картой':
            return render(request, 'orders/payment.html', context)
        else:
            return render(request, 'orders/paymentsomeone.html', context)


class FictionPayment(CartMixin, View):
    def get(self, request):
        messages.add_message(request, messages.INFO, "Заказ успешно оплачен!")
        return render(request, 'orders/progressPayment.html',
                          {'cart': self.cart})

    def post(self, request, **kwargs):
        id = kwargs.get('pk')
        number = request.POST.get('numero1')
        if number.endswith('0'):
            messages.add_message(request, messages.INFO, "Ошибка оплаты!")
        else:
            order = Order.objects.get(id=id)
            order.status = 'Доставляется'
            order.save(update_fields=('status',))
            messages.add_message(request, messages.INFO, "Заказ успешно оплачен!")
        return render(request, 'orders/progressPayment.html',
                          {'cart': self.cart})


class RepeatPayment(CartMixin, View):
    def post(self, request, **kwargs):
        method = request.POST.get('method')
        id = kwargs.get('pk')
        order = Order.objects.get(id=id)
        order.payment_method = method
        order.save(update_fields=('payment_method',))
        return HttpResponseRedirect(f'../../../orders/order_payment/')

    def get(self, request, **kwargs):
        id = kwargs.get('pk')
        context = {'cart': self.cart, 'id':id}
        context.update(self.get_context())
        return render(request, 'orders/repeat_payment.html',
                          context)


class HistoryOrders(CartMixin, View):
    def get(self, request):
        customer = Customer.objects.get(user=request.user)
        orders = Order.objects.all().filter(customer=customer).order_by('-id')
        context = {'cart': self.cart, 'orders': orders, 'not_pay': ['Не оплачен',]}
        context.update(self.get_context())
        return render(request, 'users/historyorder.html',
                          context)



# from mainapp.models import *
# import random
#
# category = Category.objects.get(slug="smartphones")
# a = Smartphone.objects.all().first()
# image=a.image
# for i in range(2,100):
#     b = Smartphone.objects.create(
#     category=category,
#     title = f'phone{i}',
#     image=a.image,
#     slug = f'phone{i}',
#     description = f'text{i}',
#     price = random.randint(20,300),
#     diagonal= f'test{i}',
#     display_type = f'test{i}',
#     resolution = f'test{i}',
#     accum_volume = f'test{i}',
#     ram = f'test{i}',
#     sd  =True,
#     sd_volume_max = f'test{i}',
#     main_cam_mp = f'test{i}',
#     frontal_cam_mp = f'test{i}'
#     )
#     SmartphoneGallery.objects.create(smartphone=b, image=image)
#     SmartphoneGallery.objects.create(smartphone=b, image=image)
#     SmartphoneGallery.objects.create(smartphone=b, image=image)


# from mainapp.models import *
# import random
# category = Category.objects.get(slug="notebooks")
# a = Notebook.objects.all().first()
# image=a.image
# for i in range(2,100):
#
#     b = Notebook.objects.create(
#     category=category,
#     title = f'Notebook{i}',
#     slug = f'Notebook{i}',
#     description = f'text{i}',
    # image = image,
#     price = random.randint(20,1000),
#     diagonal= f'test{i}',
#     display_type = f'test{i}',
#     processor_freq = f'test{i}',
#     ram = f'test{i}',
#     video = f'test{i}',
#     time_without_charge = f'test{i}',
#     )
#     NotebookGallery.objects.create(notebook=b, image=image)
#     NotebookGallery.objects.create(notebook=b, image=image)
#     NotebookGallery.objects.create(notebook=b, image=image)


# from mainapp.models import *
# import random
#
# category = Category.objects.get(slug="desktops")
# a = Desktop.objects.all().first()
# image=a.image
# for i in range(2,100):
#
#     b = Desktop.objects.create(
#     category=category,
#     title = f'Desktop{i}',
#     slug = f'Desktop{i}',
#     description = f'text{i}',
#     image=image,
#     price = random.randint(20,1000),
#     processor_model= f'test{i}',
#     processor_freq = f'test{i}',
#     ram = f'test{i}',
#     video = f'test{i}',
#     size = f'test{i}',
#     )
#     DesktopGallery.objects.create(desktop=b, image=image)
#     DesktopGallery.objects.create(desktop=b, image=image)
#     DesktopGallery.objects.create(desktop=b, image=image)


# from mainapp.models import *
# import random
#
# category = Category.objects.get(slug="headphones")
# a = Headphones.objects.all().first()
# image=a.image
# for i in range(2,100):
#
#     b = Headphones.objects.create(
#     category=category,
#     title = f'Headphones{i}',
#     slug = f'Headphones{i}',
#     description = f'text{i}',
#     image=image,
#     price = random.randint(20,1000),
#     weight= f'test{i}',
#     power = f'test{i}',
#     max_freq = f'test{i}',
#     microphone = f'test{i}',
#     color = f'test{i}',
#     )
#     HeadphonesGallery.objects.create(headphones=b, image=image)
#     HeadphonesGallery.objects.create(headphones=b, image=image)
#     HeadphonesGallery.objects.create(headphones=b, image=image)