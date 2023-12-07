from django.db import models
from django.utils.timezone import now

class CarMake(models.Model):
    # Fields for the CarMake
    name = models.CharField(max_length=255)
    description = models.TextField()

    # Other fields can be added here

    def __str__(self):
        return self.name

class CarModel(models.Model):
    # Choices for the CarModel type
    SEDAN = 'sedan'
    SUV = 'suv'
    WAGON = 'wagon'
    TYPE_CHOICES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (WAGON, 'Wagon'),
    ]

    # Fields for the CarModel
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    dealer_id = models.IntegerField()
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    year = models.DateField()

    # Other fields can be added here

    def __str__(self):
        return f"{self.name} - {self.get_type_display()}"

# Plain Python classes CarDealer and DealerReview can be added here following similar patterns
