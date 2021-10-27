from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.db.models import Q
from .models import Room, Topic
from .forms import RoomForm


def renderView(req: HttpRequest, template: str, context: dict) -> HttpResponse:
    return render(req, f"base/{template}.django.html", context)


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
    return renderView(request, "room", {"room": room})


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


def updateRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if not form.is_valid():
            return redirect("base:update-room", pk=pk)
        form.save()
        return redirect("base:room", pk=pk)

    form = RoomForm(instance=room)
    context = {"form": form}
    return renderView(request, "room_form", context)


def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.method == "POST":
        room.delete()
        return redirect("base:home")

    return renderView(request, "delete", {"obj": room})
