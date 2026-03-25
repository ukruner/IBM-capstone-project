from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import CarDealer, CarReview, CarMake, CarModel
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import requests
from .restapis import get_dealers_from_cf, get_reviews_from_cf, post_request, analyze_review_sentiments
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
# Create an `about` view to render a static about page
# def about(request):
# ...


# Create a `contact` view to return a static contact page
#def contact(request):

# Create a `login_request` view to handle sign in request
# def login_request(request):

def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)

# Create a `logout_request` view to handle sign out request
# def logout_request(request):

def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        id = request.GET.get('id', '')  # Get id from request.GET, default to empty string if not provided
        state = request.GET.get('state', '')
        url = f"https://urmaskryner-3000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/dealership?id={id}&state={state}"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ', '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        context = {"dealerships": dealerships}
        return render(request, 'djangoapp/index.html', context)


def get_dealerships_by_id(id):
        url = f"https://urmaskryner-3000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/dealership?id={id}"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_name = dealerships[0]
        # Return a list of dealer short name
        return dealer_name

def review_template(request, id):
     
        dealerships = get_dealerships_by_id(id)

def add_review(request, id):
    url = 'https://urmaskryner-5000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/review'
    context = {}
    dealer_name = get_dealerships_by_id(id).full_name
    context['dealer_name']=dealer_name
    context['dealer_id']=id
    if request.method == 'POST':
        if User.is_authenticated:
            review_date=datetime.utcnow().isoformat()
            review_content = request.POST["content"]
            review_dealerid = id
            review_id = request.POST["reviewid"]
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            car_name = car.car_make.name
            car_model_name = car.model_name
            car_year = int(car.model_year.strftime("%Y"))
            # review_purchase_tickbox = False
            # if "purchasecheck" in request.POST:
            #     review_purchase_tickbox = request.POST["purchasecheck"]
            review_purchase_tickbox = request.POST.get("purchasecheck", False)
            review_purchasedate = request.POST["purchasedate"]
            review_body = dict()
            review_body = {"id":review_id, "name":dealer_name,"review":review_content, "dealership":id, "purchase":bool(review_purchase_tickbox), "purchase_date":review_purchasedate, "sentiment":analyze_review_sentiments(review_content), "car_make":car_name, "car_model":car_model_name, "car_year":car_year}
            data = json.dumps(review_body)
            # response = requests.post(url, data=data, headers=headers)
            response = post_request(url, data)
            
            if response.status_code >= 200:
                # Handle successful response
                HttpResponse("Review submitted successfully")
                return redirect("djangoapp:dealer_details", id=id)
            else:
                # Handle unsuccessful response
                HttpResponse("Failed to submit review", status=response.status_code)
        else:
            context['message']="Only authenticated users can post reviews, please login"
            return render(request, 'djangoapp/login.html', context)
    elif request.method == "GET":
        cars = CarModel.objects.all()
        context['cars']=cars
        for car in cars:
            print(f"Car ID: {car.pk}")
            print(f"Make: {car.car_make.name}")
            print(f"Model: {car.model_name}")
            print(f"Year: {car.model_year}")
    # Add more attributes as needed
            print("\n")  # Add a new line for readability
        return render(request, 'djangoapp/add_review.html', context)


def get_reviews(request, id):
    if request.method == "GET":
        # id = request.GET.get('id')  
        url = f"https://urmaskryner-5000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/review?id={id}"
        # Get dealers from the URL
        context={}
        dealer_name = get_dealerships_by_id(id)
        context["dealer_name"]=dealer_name
        context["id"]=id
        reviews = get_reviews_from_cf(url)
        if reviews:
            review_content = ', '.join([review.review for review in reviews])
            context["reviews"]=reviews
            print(reviews)
            return render(request, 'djangoapp/dealer_details.html', context)
        else:
            return render(request, 'djangoapp/noreviews.html', context)
            
def about_us(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

def contact_us(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

