from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from helper import get_newest_articles
from .models import Activity, register_notification, Notification
# from .apps import DashboardConfig
from mailer import send_mail_with_template
from userinformation import UserInformation


# Create your views here.

@login_required
def index(request):
    """ Index page: Lists activities und notifications """

    context = {
    }

    return render(request, 'dashboard/index.html', context)


@login_required
def api_information(request):
    # Load activities
    activities = Activity.objects.filter(user=request.user).order_by('-created_at')[:5]

    # Load notifications
    notifications = request.user.notifications.all().filter(user=request.user).order_by('-created_at')[:5]
    unread_notifications = request.user.notifications.all().filter(user=request.user, read=False).order_by(
        '-created_at')
    # user_type = UserInformation.user_type(request.user)
    newest_articles = get_newest_articles("https://katharineum-zu-luebeck.de", 1, [22])
    if len(newest_articles) >= 0:
        newest_article = newest_articles[0]
    else:
        newest_article = None
    print(newest_articles)
    context = {
        'activities': list(activities.values()),
        'notifications': list(notifications.values()),
        "unread_notifications": list(unread_notifications.values()),
        'user_type': UserInformation.user_type(request.user),
        'user_type_formatted': UserInformation.user_type_formatted(request.user),
        'classes': UserInformation.user_classes(request.user),
        'courses': UserInformation.user_courses(request.user),
        'subjects': UserInformation.user_subjects(request.user),
        'has_wifi': UserInformation.user_has_wifi(request.user),
        "newest_article": newest_article,
    }
    print(context)
    return JsonResponse(context)


@login_required
def api_read_notification(request, id):
    notification = get_object_or_404(Notification, id=id, user=request.user)
    notification.read = True
    notification.save()
    return JsonResponse({"success": True})


@login_required
def test_notification(request):
    """ Sends a test mail """
    # send_mail_with_template("Test", [request.user.email], 'mail/email.txt', 'mail/email.html', {'user': request.user})
    register_notification(user=request.user, title="Ihr Antrag wurde genehmigt",
                          description="Ihr Antrag XY wurde von der Schulleitung genehmigt.", app="AUB",
                          link=reverse("aub_details", args=[1]))
    print(reverse("aub_details", args=[1]))
    return redirect(reverse('dashboard'))


def error_404(request, exception):
    return render(request, 'common/404.html')
