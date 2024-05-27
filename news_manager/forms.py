from django import forms
from .models import NewsSource, BotSetting, Subscription
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class NewsSourceForm(forms.ModelForm):
    class Meta:
        model = NewsSource
        fields = ['name', 'url', 'source_type']

class BotSettingForm(forms.ModelForm):
    class Meta:
        model = BotSetting
        fields = ['name', 'value']


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['is_premium', 'premium_expiry']
