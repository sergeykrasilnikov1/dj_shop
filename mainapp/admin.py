from django.forms import ModelChoiceField, ModelForm, ModelMultipleChoiceField
from django.contrib import admin

from .models import *


class SmartphoneAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and not instance.sd:
            self.fields['sd_volume_max'].widget.attrs.update({
                'readonly': True, 'style': 'background: lightgray;'
            })

    def clean(self):
        if not self.cleaned_data['sd']:
            self.cleaned_data['sd_volume_max'] = None
        return self.cleaned_data


class NotebookGalleryInline(admin.TabularInline):
    model = NotebookGallery
    extra = 5

@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):

    inlines = [NotebookGalleryInline, ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='notebooks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SmartphoneGalleryInline(admin.TabularInline):
    model = SmartphoneGallery
    extra = 5


@admin.register(Smartphone)
class SmartphoneAdmin(admin.ModelAdmin):

    form = SmartphoneAdminForm

    inlines = [SmartphoneGalleryInline, ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='smartphones'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class DesktopGalleryInline(admin.TabularInline):
    model = DesktopGallery
    extra = 5

@admin.register(Desktop)
class DesktopAdmin(admin.ModelAdmin):

    inlines = [DesktopGalleryInline, ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='desktops'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class HeadphonesInline(admin.TabularInline):
    model = HeadphonesGallery
    extra = 5

@admin.register(Headphones)
class HeadphonesAdmin(admin.ModelAdmin):

    inlines = [HeadphonesInline, ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='headphones'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)




admin.site.register(Category)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Review)
