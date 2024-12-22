from django.contrib import admin
from .models import Product, Variation,ReviewRating,ProductGallery
import admin_thumbnails
from .models import UserInteraction


@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'is_black_friday_sale', 'stock', 'is_available')
    list_editable = ('is_black_friday_sale',)
    prepopulated_fields = {"slug": ("product_name",)}
    inlines = [ProductGalleryInline]

    # Custom action to set 'is_black_friday_sale' for all products
    def make_all_black_friday_sale(self, request, queryset):
        updated_count = Product.objects.all().update(is_black_friday_sale=True)
        self.message_user(request, f'{updated_count} products marked as Black Friday Sale.')

     # Custom action to set 'is_black_friday_sale' to False for all products
    def make_no_black_friday_sale(self, request, queryset):
        updated_count = Product.objects.all().update(is_black_friday_sale=False)
        self.message_user(request, f'{updated_count} products removed from Black Friday Sale.')

    # Add custom action to the admin
    actions = ['make_all_black_friday_sale','make_no_black_friday_sale']



class VariationAdmin(admin.ModelAdmin):
    list_display = ("product", "variation_category", "variation_value", "is_active")
    list_editable = ("is_active",)
    list_filter = ("product", "variation_category", "variation_value")


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)
admin.site.register(UserInteraction)