from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class SignUpForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password and confirm and password != confirm:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))



class EditProfileForm(forms.ModelForm):
    display_name = forms.CharField(max_length=150, required=True)
    avatar = forms.ChoiceField(
        choices=[('iconA', 'Icon A'), ('iconB', 'Icon B'), ('iconC', 'Icon C')],
        widget=forms.RadioSelect
    )

    class Meta:
        model = User
        fields = ['display_name', 'email']
