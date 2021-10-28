from django.core.checks.messages import Error
from django.http.request import RAISE_ERROR
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message
from .forms import RoomForm


def renderView(req: HttpRequest, template: str, context: dict) -> HttpResponse:
    return render(req, f"base/{template}.django.html", context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect("base:home")

    page = "login"
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request=request, message="User doesn't exist.")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("base:home")
        messages.error(request, "Invalid credentials.")

    context = {
        "page": page
    }
    return renderView(request, "login_register", context)


def logoutUser(request):
    logout(request)
    return redirect("base:home")


def registerUser(request):
    page = "register"

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if not form.is_valid():
            messages.error(request, "An error occurred during registration.")
        else:
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("base:home")

    form = UserCreationForm()
    return renderView(request, "login_register", {"page": page, "form": form})


def home(request: HttpRequest):
    q = request.GET.get("q")
    if not q:
        rooms = Room.objects.all()
    else:
        rooms = Room.objects.filter(
            Q(topic__name__icontains=q)
            | Q(name__icontains=q)
            | Q(description__icontains=q)
        )
    topics = Topic.objects.all()
    roomCount = rooms.count()
    context = {
        "rooms": rooms,
        "topics": topics,
        "roomCount": roomCount
    }
    return renderView(request, "home", context)


def room(request, pk):
    try:
        room = Room.objects.get(id=pk)
    except:
        return HttpResponseNotFound(f"<h1>No room with id {pk} was found.</h1>")

    if request.method == "POST":
        try:
            body = request.POST.get("body")
            if not body:
                messages.error(request, "Message can't be empty.")
                raise Error()
            Message.objects.create(
                user=request.user,
                room=room,
                body=request.POST.get("body")
            )
        except:
            messages.error(request, "Message couldn't be saved.")
        room.participants.add(request.user)
        return redirect("base:room", pk=room.id)

    roomMessages = room.message_set.all().order_by("-created")
    participants = room.participants.all()
    context = {
        "room": room,
        "roomMessages": roomMessages,
        "participants": participants
    }
    return renderView(request, "room", context)


@login_required(login_url="base:login")
def createRoom(request):
    """
    request.POST =
    <QueryDict: {
        'csrfmiddlewaretoken': ...,
        'host': ['1'],
        'topic': ['1'],
        'name': ['...'],
        'description': ['...']
    }>
    """

    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("base:home")
        return redirect("base:create-room")

    form = RoomForm()
    context = {
        "form": form
    }
    return renderView(request, "room_form", context)


@login_required(login_url="base:login")
def updateRoom(request: HttpRequest, pk: int):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("You're not the host of this room.")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if not form.is_valid():
            return redirect("base:update-room", pk=pk)
        form.save()
        return redirect("base:room", pk=pk)

    form = RoomForm(instance=room)
    context = {"form": form}
    return renderView(request, "room_form", context)


@login_required(login_url="base:login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.method == "POST":
        room.delete()
        return redirect("base:home")

    return renderView(request, "delete", {"obj": room})


@login_required(login_url="base:login")
def deleteMessage(request, pk):
    # try:
    message = Message.objects.get(id=pk)
    # except:
    #     return HttpResponseNotFound(f"No message with id {pk} was found.")

    reqUser = request.user
    if reqUser != message.user and not reqUser.is_superuser:
        return redirect("base:room", pk=message.room.id)

    message.delete()
    return renderView(request, "delete", {"obj": message})
