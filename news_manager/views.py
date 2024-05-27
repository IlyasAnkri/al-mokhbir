import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import NewsSource, BotSetting, Subscription
from .forms import NewsSourceForm, BotSettingForm, SignUpForm, SubscriptionForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
import datetime

def index(request):
    return render(request, 'news_manager/index.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            # Create a Subscription record for the new user
            Subscription.objects.create(user=user, is_premium=False)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'news_manager/signup.html', {'form': form})

@login_required
def news_source_list(request):
    # Check if the user has a subscription and is premium
    if not hasattr(request.user, 'subscription') or not request.user.subscription.is_premium:
        return redirect('pricing')

    news_sources = NewsSource.objects.filter(user=request.user) if request.user.subscription.is_premium else NewsSource.objects.filter(user=None)  # Default sources
    return render(request, 'news_manager/news_source_list.html', {'news_sources': news_sources})

@login_required
def add_news_source(request):
    if request.user.subscription.is_premium:
        if request.method == 'POST':
            form = NewsSourceForm(request.POST)
            if form.is_valid():
                news_source = form.save(commit=False)
                news_source.user = request.user
                news_source.save()
                return redirect('news_source_list')
        else:
            form = NewsSourceForm()
        return render(request, 'news_manager/add_news_source.html', {'form': form})
    else:
        return redirect('pricing')

@login_required
def edit_news_source(request, pk):
    news_source = NewsSource.objects.get(pk=pk)
    if request.method == 'POST':
        form = NewsSourceForm(request.POST, instance=news_source)
        if form.is_valid():
            form.save()
            return redirect('news_source_list')
    else:
        form = NewsSourceForm(instance=news_source)
    return render(request, 'news_manager/edit_news_source.html', {'form': form})

@login_required
def delete_news_source(request, pk):
    news_source = NewsSource.objects.get(pk=pk)
    if request.method == 'POST':
        news_source.delete()
        return redirect('news_source_list')
    return render(request, 'news_manager/delete_news_source.html', {'news_source': news_source})

@login_required
def bot_setting_list(request):
    bot_settings = BotSetting.objects.all()
    return render(request, 'news_manager/bot_setting_list.html', {'bot_settings': bot_settings})

@login_required
def edit_bot_setting(request, pk):
    bot_setting = BotSetting.objects.get(pk=pk)
    if request.method == 'POST':
        form = BotSettingForm(request.POST, instance=bot_setting)
        if form.is_valid():
            form.save()
            return redirect('bot_setting_list')
    else:
        form = BotSettingForm(instance=bot_setting)
    return render(request, 'news_manager/edit_bot_setting.html', {'form': form})

@login_required
def manage_subscription(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=request.user.subscription)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = request.user
            subscription.save()
            return redirect('subscription_success')
    else:
        form = SubscriptionForm(instance=request.user.subscription)
    return render(request, 'news_manager/manage_subscription.html', {'form': form})

@login_required
def subscription_success(request):
    return render(request, 'news_manager/subscription_success.html')

@login_required
def subscription_cancel(request):
    return render(request, 'news_manager/subscription_cancel.html')

def pricing(request):
    return render(request, 'news_manager/pricing.html')

@csrf_exempt
def subscribe(request):
    if request.method == 'POST':
        try:
            # Get PayPal access token
            auth_response = requests.post(
                f'{settings.PAYPAL_API_BASE}/v1/oauth2/token',
                headers={
                    'Accept': 'application/json',
                    'Accept-Language': 'en_US',
                },
                auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
                data={'grant_type': 'client_credentials'},
            )
            auth_response.raise_for_status()
            access_token = auth_response.json()['access_token']

            # Create PayPal order
            order_response = requests.post(
                f'{settings.PAYPAL_API_BASE}/v2/checkout/orders',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {access_token}',
                },
                json={
                    "intent": "CAPTURE",
                    "purchase_units": [{
                        "amount": {
                            "currency_code": "USD",
                            "value": "5.00"  # Changed to $5.00
                        }
                    }]
                }
            )
            order_response.raise_for_status()
            order = order_response.json()

            # Redirect to PayPal approval URL
            for link in order['links']:
                if link['rel'] == 'approve':
                    approval_url = link['href']
                    return redirect(approval_url)
        except requests.exceptions.RequestException as e:
            print(f"Error during PayPal transaction: {e}")
            return redirect('pricing')

def subscription_success(request):
    payment_id = request.GET.get('token')
    payer_id = request.GET.get('PayerID')

    try:
        # Get PayPal access token
        auth_response = requests.post(
            f'{settings.PAYPAL_API_BASE}/v1/oauth2/token',
            headers={
                'Accept': 'application/json',
                'Accept-Language': 'en_US',
            },
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
            data={'grant_type': 'client_credentials'},
        )
        auth_response.raise_for_status()
        access_token = auth_response.json()['access_token']

        # Capture PayPal order
        capture_response = requests.post(
            f'{settings.PAYPAL_API_BASE}/v2/checkout/orders/{payment_id}/capture',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            }
        )
        capture_response.raise_for_status()
        capture = capture_response.json()

        if capture['status'] == 'COMPLETED':
            request.user.subscription.is_premium = True
            request.user.subscription.premium_expiry = datetime.datetime.now() + datetime.timedelta(days=30)
            request.user.subscription.save()
            return render(request, 'news_manager/subscription_success.html')
    except requests.exceptions.RequestException as e:
        print(f"Error during PayPal transaction: {e}")
    return redirect('pricing')
