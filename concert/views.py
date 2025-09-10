from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.hashers import make_password
import os

from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending
import requests as req


# Create your views here.

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {"form": SignUpForm(), "message": "user already exist"})
        else:
            user = User.objects.create(
                username=username, password=make_password(password))
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
    return render(request, "signup.html", {"form": SignUpForm()})


def index(request):
    return render(request, "index.html")


def songs(request):
    # For local testing, ensure your Songs microservice is running
    # The URL might be http://localhost:5000 if you are running it locally
    songs_url = os.environ.get("SONGS_URL", "http://localhost:5000")
    try:
        response = req.get(f"{songs_url}/song")
        response.raise_for_status()  # Raise an exception for bad status codes
        songs_data = response.json()
        return render(request, "songs.html", {"songs": songs_data.get("songs", [])})
    except (req.exceptions.RequestException, ValueError):
        # Handle cases where the service is down or returns invalid JSON
        return render(request, "songs.html", {"songs": [], "error": "Could not connect to the Songs service."})


def photos(request):
    # For local testing, ensure your Pictures microservice is running
    # The URL might be http://localhost:8080 if you are running it locally
    photos_url = os.environ.get("PHOTOS_URL", "http://localhost:8080")
    try:
        response = req.get(f"{photos_url}/picture")
        response.raise_for_status() # Raise an exception for bad status codes
        photos_data = response.json()
        return render(request, "photos.html", {"photos": photos_data})
    except (req.exceptions.RequestException, ValueError):
        # Handle cases where the service is down or returns invalid JSON
        return render(request, "photos.html", {"photos": [], "error": "Could not connect to the Photos service."})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def concerts(request):
    if request.user.is_authenticated:
        lst_of_concert = []
        concert_objects = Concert.objects.all()
        for item in concert_objects:
            try:
                status = item.attendee.filter(
                    user=request.user).first().attending
            except:
                status = "-"
            lst_of_concert.append({
                "concert": item,
                "status": status
            })
        return render(request, "concerts.html", {"concerts": lst_of_concert})
    else:
        return HttpResponseRedirect(reverse("login"))


def concert_detail(request, id):
    if request.user.is_authenticated:
        obj = Concert.objects.get(pk=id)
        try:
            status = obj.attendee.filter(user=request.user).first().attending
        except:
            status = "-"
        return render(request, "concert_detail.html", {"concert_details": obj, "status": status, "attending_choices": ConcertAttending.AttendingChoices.choices})
    else:
        return HttpResponseRedirect(reverse("login"))
    pass


def concert_attendee(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            concert_id = request.POST.get("concert_id")
            attendee_status = request.POST.get("attendee_choice")
            concert_attendee_object = ConcertAttending.objects.filter(
                concert_id=concert_id, user=request.user).first()
            if concert_attendee_object:
                concert_attendee_object.attending = attendee_status
                concert_attendee_object.save()
            else:
                ConcertAttending.objects.create(concert_id=concert_id,
                                                user=request.user,
                                                attending=attendee_status)

        return HttpResponseRedirect(reverse("concerts"))
    else:
        return HttpResponseRedirect(reverse("index"))
