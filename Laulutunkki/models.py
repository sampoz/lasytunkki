# -*- coding: utf8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import admin
from django.forms import ModelForm, Textarea, URLInput

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from datetime import datetime
###### SONG RELATED MODELS #######


# A class for songs
class Song(models.Model):
    title = models.CharField(max_length=120)
    category = models.CharField(max_length=120)
    lyrics = models.TextField()
    extra_verses = models.TextField(blank=True, null=True)

    melody = models.CharField(max_length=120, blank=True, null=True)
    example = models.URLField(blank=True, null=True)
    other_info = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User)

    def __unicode__(self):
        return self.title


class SongLike(models.Model):
    user = models.ForeignKey(User, related_name='likes')
    song = models.ForeignKey(Song, related_name='likes')
    created = models.DateTimeField(auto_now_add=True)
    value = models.BooleanField()


class SongForm(ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'category', 'lyrics', 'extra_verses', 'melody', 'example', 'other_info']
        labels = {
            'title' : "Laulun nimi",
            'category' : "Laulun luokka",
            'lyrics' : "Säkeistöt",
            'extra_verses' : "Lisäsäkeistöt",
            'melody' : "Melodia",
            'example' : "Esimerkki laulusta",
            'other_info' : "Lisätietoja",
        }

    def __init__(self, *args, **kwargs):
        super(SongForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class SongAdmin(admin.ModelAdmin):
    search_fields = ["title", "lyrics", "author"]

admin.site.register(Song, SongAdmin)


# A category for songs: e.g. wine songs, water songs, etc.
class Category(models.Model):
    # Should there be a set of choices instead of a free field? E.g. Wine songs, Water songs, etc.
    name = models.CharField(max_length=120)
    description = models.TextField()
    song = models.ForeignKey(Song, related_name='categories')

    def __unicode__(self):
        return self.name


###### BOOKLET RELATED MODELS #######

# A booklet which contains multiple songs in a specific order
class Booklet(models.Model):
    title = models.CharField(max_length=120)
    author = models.ForeignKey(User, related_name='booklet_author')
    pdf_file = models.FileField(upload_to="booklet_pdfs/")
    front_page_image = models.URLField(blank=True, null=True)
    front_page_text = models.CharField(max_length=450, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    previous_version = models.ForeignKey("self", related_name="updated_version", blank=True, null=True)

    def __unicode__(self):
        return self.title


class BookletAdmin(admin.ModelAdmin):
    search_fields = ["title", "author", "pdf_file"]

admin.site.register(Booklet, BookletAdmin)

# Booklet page 
class BookletPage(models.Model):
    booklet = models.ForeignKey(Booklet, related_name='pages')
    page_number = models.IntegerField()

    def __unicode__(self):
        return str(self.page_number)


# An adapter class to enable an ordered list of songs within a booklet
class BookletSong(models.Model):
    booklet_page = models.ForeignKey(BookletPage, related_name='songs')
    song = models.ForeignKey(Song, related_name='booklet_songs')
    order_no = models.IntegerField()

    def __unicode__(self):
        return self.song.title


# Events such as sittnings, which booklets are associated with
class Event(models.Model):
    booklet = models.ForeignKey(Booklet, related_name='events')
    name = models.CharField(max_length=120)
    date = models.DateField()

    def __unicode__(self):
        return self.name


###### USER RELATED MODELS #######

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())

    def __unicode__(self):
        str = ""
        str += u"username : " + self.user.username + u", "
        str += u"email : " + self.email + u", "
        str += u"first_name : " + self.first_name + u", "
        str += u"last_name : " + self.last_name
        return str

# Create a user profile automatically when a user is created
from django.db.models.signals import post_save


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance, email=instance.email)
post_save.connect(create_user_profile, sender=User)


class UserProfileForm(forms.ModelForm):

    error_messages = {
        'duplicate_username': "Käyttäjänimi on jo käytössä.",
        'email_in_use': "Sähköpostiosoite on jo käytössä.",
        'password_incorrect': "Virheellinen salasana.",
    }

    email = forms.EmailField(
        label="Sähköpostiosoite",
        widget=forms.EmailInput,
        required=True
    )

    password = forms.CharField(
        label="Salasana",
        widget=forms.PasswordInput,
        required=True,
    )

    class Meta:
        model = User

        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        labels = {
            'username' : 'Käyttäjänimi',
            'email' : "Sähköposti",
            'first_name' : "Etunimi",
            'last_name' : "Sukunimi",
            'password' : 'Salasana',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'edit-profile'
        self.helper.form_role = 'form'
        self.helper.form_action = 'edit_profile'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('save', 'Tallenna'))

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]

        if username != self.user.username:
            try:
                User._default_manager.get(username=username)
            except User.DoesNotExist:
                return username
            raise forms.ValidationError(
                self.error_messages['duplicate_username'],
                code='duplicate_username',
            )
        return username

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        if (not self.user.has_usable_password() or self.user.check_password(self.cleaned_data["password"])):
            return self.cleaned_data["password"]
        else:
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if email != self.user.email:
            try:
                User._default_manager.get(email=email)
            except User.DoesNotExist:
                return email
            raise forms.ValidationError(
                self.error_messages['email_in_use'],
                code='email_in_use',
            )
        return email

    def save(self, commit=True):

        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        email = self.cleaned_data.get('email')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')

        self.user.username = username
        self.user.password = password
        self.user.email = email
        self.user.first_name = first_name
        self.user.last_name = last_name

        self.user.profile.email = email
        self.user.profile.first_name = first_name
        self.user.profile.last_name = last_name

        if commit:
            self.user.save()
            self.user.profile.save()


class UserProfileSocialForm(forms.ModelForm):

    error_messages = {
        'duplicate_username': "Käyttäjänimi on jo käytössä.",
        'email_in_use': "Sähköpostiosoite on jo käytössä.",
        'password_incorrect': "Virheellinen salasana.",
    }

    email = forms.EmailField(
        label="Sähköpostiosoite",
        widget=forms.EmailInput,
        required=True
    )

    class Meta:
        model = User

        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username' : 'Käyttäjänimi',
            'email' : "Sähköposti",
            'first_name' : "Etunimi",
            'last_name' : "Sukunimi",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(UserProfileSocialForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'edit-profile'
        self.helper.form_role = 'form'
        self.helper.form_action = 'edit_profile'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('save', 'Tallenna'))

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]

        if username != self.user.username:
            try:
                User._default_manager.get(username=username)
            except User.DoesNotExist:
                return username
            raise forms.ValidationError(
                self.error_messages['duplicate_username'],
                code='duplicate_username',
            )
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if email != self.user.email:
            try:
                User._default_manager.get(email=email)
            except User.DoesNotExist:
                return email
            raise forms.ValidationError(
                self.error_messages['email_in_use'],
                code='email_in_use',
            )
        return email

    def save(self, commit=True):

        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')

        self.user.username = username
        self.user.email = email
        self.user.first_name = first_name
        self.user.last_name = last_name

        self.user.profile.email = email
        self.user.profile.first_name = first_name
        self.user.profile.last_name = last_name

        if commit:
            self.user.save()
            self.user.profile.save()


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(
        label="Sähköpostiosoite",
        widget=forms.EmailInput,
        required=True
    )

    error_messages = UserCreationForm.error_messages
    error_messages['email_in_use'] = "Sähköpostiosoite on jo käytössä."

    class Meta:
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-register-form'
        self.helper.form_class = 'form-register'
        self.helper.form_method = 'post'
        self.helper.form_action = '/accounts/register/'

        self.helper.add_input(Submit('submit', 'Rekisteröidy'))

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages['email_in_use'],
            code='email_in_use',
        )

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Käyttäjätunnus",
        widget=forms.TextInput,
        required=True,
    )

    password = forms.CharField(
        label="Salasana",
        widget=forms.PasswordInput,
        required=True,
    )

    remember_me = forms.BooleanField(
        label="Muista minut",
        widget=forms.CheckboxInput,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-signin-form'
        self.helper.form_class = 'form-sigin'
        self.helper.form_method = 'post'
        self.helper.form_action = '/accounts/auth/'

        self.helper.add_input(Submit('submit', 'Kirjaudu'))

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, PasswordChangeForm, UserChangeForm


class ForgotPasswordForm(PasswordResetForm):
    email = forms.EmailField(
        label="Sähköpostiosoite",
        widget=forms.EmailInput,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-resetpassword-form'
        self.helper.form_method = 'post'
        self.helper.form_action = ''

        self.helper.add_input(Submit('submit', 'Lähetä'))


class CrispySetPasswordForm(SetPasswordForm):

    new_password1 = forms.CharField(
        label="Uusi salasana",
        widget=forms.PasswordInput,
        required=True
    )

    new_password2 = forms.CharField(
        label="Uusi salasana uudestaan",
        widget=forms.PasswordInput,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super(CrispySetPasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-setpassword-form'
        self.helper.form_method = 'post'
        self.helper.form_action = ''

        self.helper.add_input(Submit('submit', 'Lähetä'))


class CrispyChangePasswordForm(PasswordChangeForm):


    def __init__(self, *args, **kwargs):
        super(CrispyChangePasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-changepassword-form'
        self.helper.form_method = 'post'
        self.helper.form_action = ''

        self.helper.add_input(Submit('submit', 'Lähetä'))