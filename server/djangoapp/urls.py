from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
urlpatterns = [
    path(route='', view=views.get_dealerships, name='index'),
    path(route='post/review/<int:id>/', view=views.add_review, name='add_review'),
    path(route='registration/', view=views.registration_request, name='registration'),
    path(route='login/', view=views.login_request, name='login'),
    path(route='logout/', view=views.logout_request, name='logout'),
    path(route='about/', view=views.about_us, name='about'),
    path(route='dealer_details/<int:id>', view=views.get_reviews, name='dealer_details'),
    path(route='noreviews/', view=views.get_reviews, name='noreviews'),
    path(route='contact/', view=views.contact_us, name='contact'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)