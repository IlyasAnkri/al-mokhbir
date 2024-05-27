from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('news_sources/', views.news_source_list, name='news_source_list'),
    path('news_sources/add/', views.add_news_source, name='add_news_source'),
    path('news_sources/edit/<int:pk>/', views.edit_news_source, name='edit_news_source'),
    path('news_sources/delete/<int:pk>/', views.delete_news_source, name='delete_news_source'),
    path('bot_settings/', views.bot_setting_list, name='bot_setting_list'),
    path('bot_settings/edit/<int:pk>/', views.edit_bot_setting, name='edit_bot_setting'),
    path('subscription/', views.manage_subscription, name='manage_subscription'),
    path('subscription/success/', views.subscription_success, name='subscription_success'),
    path('subscription/cancel/', views.subscription_cancel, name='subscription_cancel'),
    path('pricing/', views.pricing, name='pricing'),
    path('subscribe/', views.subscribe, name='subscribe'),
]
