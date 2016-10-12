from django import forms
from rango.models import Page, Category, UserProfile
from django.contrib.auth.models import User


class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text='Please enter the category name')
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Category
        fields = ('name', )


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text='Please enter the title of the page')
    url = forms.URLField(max_length=200, help_text='Please enter the URL of the page.')
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    # Does not work for some reason, ask later
    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url

            return cleaned_data

    class Meta:
        model = Page
        # Provide an association between the ModelForm and a model
        # What fields do we want?
        # Some fields allow for NULL values so we might not want them
        # Here we hide the foreign key
        # we can exclude fields from the form
        exclude = ('category', )
        # or specify the fields to include.


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    website = forms.URLField(required=False)
    picture = forms.ImageField(required=False)

    class Meta:
        model = UserProfile
        exclude = ('user',)
