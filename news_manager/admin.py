from django.contrib import admin
from .models import NewsSource, BotSetting, Subscription

@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'source_type')
    search_fields = ('name', 'url')

@admin.register(BotSetting)
class BotSettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
    search_fields = ('name',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_premium', 'premium_expiry')
    search_fields = ('user__username',)
    list_filter = ('is_premium',)