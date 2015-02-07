from django.http import HttpResponseRedirect, StreamingHttpResponse, HttpResponse
from django.shortcuts import render, render_to_response
from django.template.response import TemplateResponse
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.core.context_processors import csrf

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views.decorators.debug import sensitive_variables
from django.contrib.auth.decorators import login_required
from haystack.query import SearchQuerySet
from django.core import serializers
from django.core.files import File

from Laulutunkki.models import Song, SongForm, UserProfile, UserProfileForm, UserProfileSocialForm,Booklet, LoginForm, UserCreateForm, SongLike
import Laulutunkki.booklet as bookletpy
import os

# Miscellaneous views

def index(request):
    args = {}
    args.update(csrf(request))
    args['user'] = request.user
    return render(request, "index.html", args)


def search(request):
    # Songs are Haystack objects now
    query_title = SearchQuerySet().autocomplete(title_auto=request.POST.get('search_text', ''))
    query_lyrics = SearchQuerySet().autocomplete(lyrics_auto=request.POST.get('search_text', ''))
    query_category = SearchQuerySet().autocomplete(category_auto=request.POST.get('search_text', ''))
    query_author = SearchQuerySet().autocomplete(author_auto=request.POST.get('search_text', ''))
    objects = query_title | query_lyrics | query_category | query_author

    songs = filter(lambda x : type(x.object) is Song, objects)
    booklets = filter(lambda x: type(x.object) is Booklet, objects)

    return render(request, 'search/search.html', {'songs': songs, 'booklets': booklets})



def getSongs(request):
    songs = serializers.serialize("json", Song.objects.all())
    return StreamingHttpResponse(songs, content_type="application/json")


# User authentication views

def login(request):
    args = {}
    args.update(csrf(request))
    args['form'] = LoginForm()
    return render(request, 'accounts/login.html', args)


@sensitive_variables('password')
def auth_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            if not request.POST.get('id_remember_me', None):
                request.session.set_expiry(0)
            return redirect('index')
        else:
            return HttpResponseRedirect('/accounts/invalid_login/')
    return HttpResponseRedirect('/accounts/login/')


@sensitive_variables('request')
def invalid_login(request):
    form = LoginForm(request.POST)
    return render(request, "accounts/login.html", {'user': request.user, 'form': form})


def logout(request):
    auth.logout(request)
    return render(request, 'index.html', {'user': request.user})


@sensitive_variables('password')
def register(request):
    args = {}

    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            username = form.clean_username()
            password = form.clean_password2()
            form.save()
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect('index')
        else:
            args['form'] = form
            return render(request, 'accounts/register.html', args)
    else:
        args.update(csrf(request))
        args['form'] = UserCreateForm()
        return render(request, 'accounts/register.html', args)


def register_success(request):
    return render_to_response('accounts/register_success.html')


# Song related views

def song(request, id):
    instance = get_object_or_404(Song, pk=id)

    song_likes = SongLike.objects.filter(song=instance)
    likes = len(song_likes.filter(value=True))
    dislikes = len(song_likes.filter(value=False))
    total_likes = likes-dislikes

    return render(request, "songs/song.html", {'song': instance, 'user': request.user, 'total_likes': total_likes})


def song_list(request):
    song_list = Song.objects.all().order_by("title")
    paginator = Paginator(song_list, 10)

    try:
        page = int(request.GET.get("page", '1'))
    except ValueError:
        page = 1

    try:
        song_list = paginator.page(page)
    except (InvalidPage, EmptyPage):
        song_list = paginator.page(paginator.num_pages)


    return render(request, "songs/song_list.html", {'song_list': song_list, 'user': request.user})


@login_required
def create_song(request):
    if request.method == 'POST':        # If the form has been submitted
        form = SongForm(request.POST)   # A form bound to the POST data
        if form.is_valid():             # All validation rules pass
            new_song = form.save(commit=False)
            new_song.author = request.user

            try:
                new_song.full_clean()
            except ValidationError as e:
                print(e)                # TODO: handle errors better

            new_song.save()
            return HttpResponseRedirect(reverse('song_list'))   # Redirect after POST
        else:
            print(form.errors)
    else:                               # If the form has not been submitted
        form = SongForm()

    return render(request, "songs/create_song.html", {'user': request.user, 'form': form})


@login_required
def edit_song(request, id):
    instance = get_object_or_404(Song, pk=id)
    form = SongForm(request.POST or None, instance=instance)
    if form.is_valid():             # All validation rules pass
        new_song = form.save(commit=False)
        new_song.author = request.user

        try:
            new_song.full_clean()
        except ValidationError as e:
            print(e)                # TODO: handle errors better

        new_song.save()
        return HttpResponseRedirect(reverse('song_list'))   # Redirect after POST
    else:
        print(form.errors)
    return render(request, "songs/edit_song.html", {'user': request.user, 'form': form, 'id': id})


@login_required
def delete_song(request, id):
    instance = get_object_or_404(Song, pk=id)
    instance.delete()
    return HttpResponseRedirect(reverse('song_list'))

# Booklet related views

def booklet(request, id):
    instance = get_object_or_404(Booklet, pk=id)
    pages = instance.pages.all()
    return render(request, "booklets/booklet.html", {'booklet': instance, 'user': request.user, 'pages': pages.all()})


def get_booklet_pdf(request, id):
    instance = get_object_or_404(Booklet, pk=id)
    f = None
    try:
        f = open(instance.pdf_file.file.name, 'r')
    except IOError:
        #recreate file
        bookletpy.convert_booklet_to_pdf(instance)
        f = open(instance.pdf_file.file.name, 'r')
    myfile = File(f)
    response = StreamingHttpResponse(myfile, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename={}'.format(instance)
    response['X-Sendfile'] = '{}'.format(myfile)
    return response

def booklet_list(request):
    booklet_list = Booklet.objects.filter(updated_version__isnull=True).order_by("title")
    paginator = Paginator(booklet_list, 10)

    try:
        page = int(request.GET.get("page", '1'))
    except ValueError:
        page = 1

    try:
        booklet_list = paginator.page(page)
    except (InvalidPage, EmptyPage):
        booklet_list = paginator.page(paginator.num_pages)

    return render(request, "booklets/booklet_list.html", {'booklet_list': booklet_list, 'user': request.user})


@login_required
def create_booklet(request):
    if request.method == 'POST':
        song_list = request.POST.getlist("songs[]")
        front_page_text = request.POST.get("front_page_text")
        front_page_image = request.POST.get("front_page_image_url")
        songs = Song.objects.filter(id__in=song_list)
        user = request.user
        title = request.POST["title"]
        book = bookletpy.update_or_create_booklet(songs, user, title, song_list, front_page_text, front_page_image)
        bookletpy.convert_booklet_to_pdf(book)
        return HttpResponse(reverse('booklet', kwargs={"id":book.id}))
    return render(request, "booklets/create_booklet.html")


@login_required
def edit_booklet(request, id):
    book = get_object_or_404(Booklet, pk=id)
    songs = []
    for page in book.pages.all():
        for song in page.songs.all():
            songs.append(song.song)
    return render(request, "booklets/edit_booklet.html", {'booklet': book, 'songs': songs})
    

@login_required
def update_booklet(request, id):
    if request.method == 'POST':
        original = get_object_or_404(Booklet, pk=id)
        try:
            song_list = request.POST.getlist("songs[]")
            songs = Song.objects.filter(id__in=song_list)
            front_page_text = request.POST.get("front_page_text")
            front_page_image = request.POST.get("front_page_image_url")
            title = request.POST["title"]
            user = request.user
        except Exception, e:
            return HttpResponseBadRequest("Recieved JSON didn't contain all required information")
        try:
            new_booklet = bookletpy.update_or_create_booklet(songs, user, title, song_list, front_page_text, front_page_image, original)
            return HttpResponse(reverse('booklet', kwargs={"id": new_booklet.id}))
        except Exception, e:
            return HttpResponseBadRequest("Updating booklet failed")
    return HttpResponseNotAllowed("Only POST calls allowed")


@login_required
def delete_booklet(request, id):
    instance = get_object_or_404(Booklet, pk=id)
    previous = instance.previous_version
    for newer in instance.updated_version.all():
        newer.previous_version = previous
        newer.save()
    instance.pdf_file.delete()
    instance.delete()
    return HttpResponseRedirect(reverse('booklet_list'))


# Profile related views

@login_required
def view_profile(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'accounts/view_profile.html', {'profile': profile})


@login_required
def edit_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    args = {}

    if request.method == 'POST':
        if not request.user.has_usable_password():
            form = UserProfileSocialForm(request.POST, instance=user_profile, user=request.user)
        else:
            form = UserProfileForm(request.POST, instance=user_profile, user=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_profile'))
        else:
            args['form'] = form
            return render(request, 'accounts/edit_profile.html', args)

    args.update(csrf(request))
    if not request.user.has_usable_password():
        args['form'] = UserProfileSocialForm(instance=user_profile)
    else:
        args['form'] = UserProfileForm(instance=user_profile)
    args['profile'] = user_profile
    return render(request, 'accounts/edit_profile.html', args)


from allaccess.views import OAuthCallback


class AssociateCallback(OAuthCallback):

    def get_or_create_user(self, provider, access, info):
        # Define some variables
        username = "undefined"
        email = "undefined"
        first_name = "undefined"
        last_name = "undefined"
        User = auth.get_user_model()

        # Parse the relevant user information from the provider info
        if provider.name == 'facebook':
            first_name = info['first_name']
            last_name = info['last_name']
            email = info['email']
        elif provider.name == 'google':
            first_name = info['given_name']
            last_name = info['family_name']
            email = info['email']
        else:
            print("ERROR: Unknown authentication provider")

        username = first_name + "_" + last_name

        # Ensure that the username is unique
        original_username = username
        i = 1
        while len(User.objects.filter(username=username)) != 0:
            username = original_username + "_" + str(i)
            i += 1

        # Create the user object
        kwargs = {
            User.USERNAME_FIELD: username,
            'email': email,
            'password': None
        }
        user_object = None
        if User.objects.filter(email=email).exists():
            user_object = User.objects.get(email=email)
        else:
            user_object = User.objects.create_user(**kwargs)

            # Add the information to the custom UserProfile
            profile = UserProfile.objects.get(user=user_object)
            profile.email = email
            profile.first_name = first_name
            profile.last_name = last_name
            profile.save()
        return user_object


from allaccess.views import OAuthRedirect


class AdditionalPermissionsRedirect(OAuthRedirect):

    def get_additional_parameters(self, provider):
        if provider.name == 'facebook':
            # Request permission to see user's email
            return {'scope': 'email'}
        if provider.name == 'google':
            # Request permission to see user's profile and email
            perms = ['userinfo.profile', 'userinfo.email']
            scope = ' '.join(['https://www.googleapis.com/auth/' + p for p in perms])
            return {'scope': scope}
        return super(AdditionalPermissionsRedirect, self).get_additional_parameters(provider)


@login_required
def like_song(request, id):
    user = request.user
    if user.is_authenticated():
        song = get_object_or_404(Song, pk=id)

        try:
            user_liked = SongLike.objects.get(song=song, user=user)
        except:
            user_liked = None

        if not user_liked:
            like = SongLike.objects.create(song=song, user=user, value=True)
            like.save()
        elif user_liked.value is False:
            user_liked.value = True
            user_liked.save()

    return HttpResponseRedirect('/song/'+id)


@login_required
def dislike_song(request, id):
    user = request.user
    if user.is_authenticated():
        song = get_object_or_404(Song, pk=id)

        try:
            user_liked = SongLike.objects.get(song=song, user=user)
        except:
            user_liked = None

        if not user_liked:
            like = SongLike.objects.create(song=song, user=user, value=False)
            like.save()
        elif user_liked.value is True:
            user_liked.value = False
            user_liked.save()

    return HttpResponseRedirect('/song/'+id)

