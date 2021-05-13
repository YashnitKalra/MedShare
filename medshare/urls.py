from django.urls import path
from . import views

urlpatterns = [
    path('', views.medshare),
    path('signup', views.signup),
    path('sendOtp', views.sendOtp),
    path('verifyOtp', views.verifyOtp),
    path('verifyUsername', views.verifyUsername),
    path('logout', views.logout),
    path('uploadMedicinalProduct', views.uploadMedicinalProduct),
    path('searchProducts', views.searchProducts),
    path('requestProduct', views.requestProduct),
    path('requests', views.requests),
    path('withdrawRequest', views.withdrawRequest),
    path('acceptRequest', views.acceptRequest),
    path('rejectRequest', views.rejectRequest),
    path('cancelRequest', views.cancelRequest),
    path('sendOtpToReceiver', views.sendOtpToReceiver),
    path('confirmExchange', views.confirmExchange),
    path('myDonations', views.myDonations),
    path('profile', views.profile),
    path('contactUs', views.contactUs),
]