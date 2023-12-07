from django.contrib import admin
from .models import CarMake, CarModel  # Adjust the import path if necessary

# Register your models here.

# CarModelInline class
class CarModelInline(admin.TabularInline):  # or use admin.StackedInline if preferred
    model = CarModel
    extra = 1  # Number of extra blank forms

# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'car_make', 'dealer_id', 'type', 'year']  # Customize as needed
    list_filter = ['car_make', 'type', 'year']  # Customize as needed
    search_fields = ['name', 'car_make__name']  # Customize as needed

# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
    list_display = ['name', 'description']  # Customize as needed
    search_fields = ['name']  # Customize as needed

# Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)  # Optional, if you want separate management for CarModel
