from django.urls import path

from tickets import views

app_name = "tickets"

urlpatterns = [
    path("", views.ticket_list, name="ticket_list"),
    path("new/", views.ticket_create, name="ticket_create"),
    path("<int:pk>/", views.ticket_detail, name="ticket_detail"),
    path("<int:pk>/status/", views.ticket_update_status, name="ticket_update_status"),
    path("<int:pk>/comments/", views.comment_create, name="comment_create"),
]
