from django.db import models
from django.utils.timezone import now

# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object

class CarMake(models.Model):
    name = models.CharField(null=False, max_length=50, default='enter car make')
    country_origin = models.CharField(null=False, max_length=50, default='country of origin')
    desc = models.CharField(max_length=1000)
    def __str__(self):
        return "Car make: " + self.name + "," + \
                "Country of origin: " + self.country_origin + "," + \
               "Description: " + self.desc    


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object

class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, on_delete = models.CASCADE)
    dealer_id = models.IntegerField()
    model_name = models.CharField(null=False, max_length=50, default='enter car model')
    SEDAN = "sedan"
    SUV = "suv"
    WAGON = "wagon"
    HATCHBACK = "hatchback"
    UNIVERSAL = "universal"
    MINIVAN = "minivan"
    CABRIOLET = "cabriolet"
    MODEL_CHOICES = [
        (SEDAN, "Sedan"),
        (SUV, "SUV"),
        (WAGON, "WAGON"),
        (HATCHBACK, "Hatchback"),
        (UNIVERSAL, "Universal"),
        (MINIVAN, "Minivan"),
        (CABRIOLET, "Cabriolet")
    ]
    model_type = models.CharField(
        null=False,
        max_length=20,
        choices=MODEL_CHOICES,
        default=SEDAN
    )
    model_year = models.DateField()
    is_used = models.BooleanField(default=False)
    def __str__(self):
        return "Car make: " + self.car_make.name + "," + \
        "Car model: " + self.model_name + "," + \
        "Car dealership id: " + str(self.dealer_id) + "," + \
        "Car type: " + self.model_type + "," + \
        "Car year: " + str(self.model_year) + "," + \
        "Car new or not: " + str(self.is_used) + "," + \
        f"Car images are available on URL https://www.google.com/search?q={self.car_make.name}+{self.model_name}&tbm=isch"

# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:
    def __init__(self, address, state, city, full_name, id, lat, long, short_name, st, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer state
        self.state = state
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name

# <HINT> Create a plain Python class `DealerReview` to hold review data
class CarReview:
    def __init__(self, dealership=None, time=None, name=None, id=None, review=None, purchase=None, purchase_date=None, car_make=None, car_model=None, car_year=None, sentiment=None):
        self.dealership = dealership
        self.name = name
        self.id = id
        self.review = review
        self.purchase = purchase
        self.purchase_date = purchase_date
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.time = time
        self.sentiment = sentiment

    def __str__(self):
        return f"Reviews of the car dealership with id of {str(self.dealership)}: {self.review} {self.sentiment} "