from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from allaccess.views import OAuthRedirect, OAuthCallback
from Laulutunkki.views import AssociateCallback, AdditionalPermissionsRedirect

from Laulutunkki.models import ForgotPasswordForm, CrispySetPasswordForm, CrispyChangePasswordForm

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'WSD.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # Admin
    url(r'^admin/', include(admin.site.urls)),


    # User authentication URLs
    url(r'^accounts/login/$', 'Laulutunkki.views.login', name='login'),
    url(r'^accounts/auth/$', 'Laulutunkki.views.auth_view'),
    url(r'^accounts/logout/$', 'Laulutunkki.views.logout', name='logout'),
    url(r'^accounts/invalid_login/$', 'Laulutunkki.views.invalid_login'),
    url(r'^accounts/register/$', 'Laulutunkki.views.register', name='register'),
    url(r'^accounts/register_success/$', 'Laulutunkki.views.register_success'),


    # OAuth
    url(r'^oauth/accounts/login/(?P<provider>(\w|-)+)/$', AdditionalPermissionsRedirect.as_view(), name='allaccess-login'),
    url(r'^oauth/accounts/callback/(?P<provider>(\w|-)+)/$', AssociateCallback.as_view(), name='allaccess-callback'),


    # Site
    url(r'^$', 'Laulutunkki.views.index', name='index'),

    url(r'^song/(?P<id>\d+)/$', 'Laulutunkki.views.song', name='song'),
    url(r'^song_list/$', 'Laulutunkki.views.song_list', name='song_list'),
    url(r'^create_song/$', 'Laulutunkki.views.create_song', name='create_song'),
    url(r'^edit_song/(?P<id>\d+)/$', 'Laulutunkki.views.edit_song', name='edit_song'),
    url(r'^delete_song/(?P<id>\d+)/$', 'Laulutunkki.views.delete_song', name='delete_song'),
    url(r'^like_song/(?P<id>\d+)/$', 'Laulutunkki.views.like_song', name='like_song'),
    url(r'^dislike_song/(?P<id>\d+)/$', 'Laulutunkki.views.dislike_song', name='dislike_song'),

    url(r'^search/$', 'Laulutunkki.views.search', name='search'),
    url(r'^getSongs/$', 'Laulutunkki.views.getSongs'),

    url(r'^view_profile/$', 'Laulutunkki.views.view_profile', name='view_profile'),
    url(r'^edit_profile/$', 'Laulutunkki.views.edit_profile', name='edit_profile'),

    url(r'^booklet/(?P<id>\d+)/$', 'Laulutunkki.views.booklet', name='booklet'),
    url(r'^booklet_list/$', 'Laulutunkki.views.booklet_list', name='booklet_list'),
    url(r'^create_booklet/$', 'Laulutunkki.views.create_booklet', name='create_booklet'),
    url(r'^edit_booklet/(?P<id>\d+)/$', 'Laulutunkki.views.edit_booklet', name='edit_booklet'),
    url(r'^delete_booklet/(?P<id>\d+)/$', 'Laulutunkki.views.delete_booklet', name='delete_booklet'),
    url(r'^get_booklet/(?P<id>\d+)/$', 'Laulutunkki.views.get_booklet_pdf', name='get_booklet_pdf'),
    url(r'^update_booklet/(?P<id>\d+)/$', 'Laulutunkki.views.update_booklet', name='update_booklet'),




    # Comments : required by fluent-comments
    url(r'^comments/', include('fluent_comments.urls')),


    # Search : required by haystack
    url(r'^search/', include('haystack.urls')),
)

urlpatterns += patterns('',
      #override the default urls
      url(r'^password/change/$',
                    auth_views.password_change,
                    {
                          'template_name' : 'password/password_change.html',
                          'password_change_form' : CrispyChangePasswordForm,
                    },
                    name='password_change'),
      url(r'^password/change/done/$',
                    auth_views.password_change_done,
                    {
                        'template_name' : 'password/password_change_complete.html',
                    },
                    name='password_change_done'),
      url(r'^password/reset/$',
                    auth_views.password_reset,
                    {
                        'template_name': 'password/password_reset.html',
                        'email_template_name': 'password/password_reset_email.html',
                        'password_reset_form': ForgotPasswordForm,
                    },
                    name='password_reset'),
      url(r'^password/reset/done/$',
                    auth_views.password_reset_done,
                    {
                        'template_name': 'password/password_reset_done.html'
                    },
                    name='password_reset_done'),
      url(r'^password/reset/complete/$',
                    auth_views.password_reset_complete,
                    {
                        'template_name': 'password/password_reset_complete.html'
                    },
                    name='password_reset_complete'),
      url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
                    auth_views.password_reset_confirm,
          {
              'template_name': 'password/password_reset_confirm.html',
              'set_password_form': CrispySetPasswordForm,
          },
                    name='password_reset_confirm'),

)

from WSD import settings
urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )