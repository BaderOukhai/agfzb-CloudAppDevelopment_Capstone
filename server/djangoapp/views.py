from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

import requests
from .models import CarDealer
from requests.auth import HTTPBasicAuth

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    # Perform a GET request with the specified dealer id
    json_result = get_request(url, dealerId=dealer_id)

    if json_result:
        # Get all review data from the response
        reviews = json_result
        # For every review in the response
        for review in reviews:
            # Create a DealerReview object from the data
            # These values must be present
            review_content = review["review"]
            id = review["_id"]
            name = review["name"]
            purchase = review["purchase"]
            dealership = review["dealership"]

            try:
                # These values may be missing
                car_make = review["car_make"]
                car_model = review["car_model"]
                car_year = review["car_year"]
                purchase_date = review["purchase_date"]

                # Creating a review object
                review_obj = DealerReview(dealership=dealership, id=id, name=name, 
                                          purchase=purchase, review=review_content, car_make=car_make, 
                                          car_model=car_model, car_year=car_year, purchase_date=purchase_date
                                          )

            except KeyError:
                print("Something is missing from this review. Using default values.")
                # Creating a review object with some default values
                review_obj = DealerReview(
                    dealership=dealership, id=id, name=name, purchase=purchase, review=review_content)

            # Analysing the sentiment of the review object's review text and saving it to the object attribute "sentiment"
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            print(f"sentiment: {review_obj.sentiment}")

            # Saving the review object to the list of results
            results.append(review_obj)

    return results


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def base(request):
    context = {}
    if (request.method == 'GET'):
        return render(request, 'base.html', context)

# Create an `about` view to render a static about page
def about(request):
    context = {}
    if (request.method == 'GET'):
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if (request.method == 'GET'):
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:base')
        else:
            # If not, return to login page again
            return redirect('djangoapp:base')
    else:
        return render(request, 'djangoapp/base.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:base')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:base")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://baderoukhai-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        # Get dealers from the URL
        context["dealerships"] = get_dealers_from_cf(url)
        # Concat all dealer's short name
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Context for rendering
        #context = {'dealer_names': dealer_names}
        # Render the index page with the dealer names
        return render(request, 'base.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = 'https://baderoukhai-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews?id=15'
        reviews = get_dealer_reviews_from_cf(url, dealer_id=dealer_id)
        context = {
            "reviews":  reviews, 
            "dealer_id": dealer_id
        }

        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...

