from django import forms
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm
from django.core.exceptions import ValidationError

from django_select2.forms import Select2MultipleWidget, ModelSelect2Widget

from chat.models import Contact
from .models import User, Interest


class UserRegisterForm(UserCreationForm):
    # email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''

    def save(self, commit=True, **kwargs):
        user = self.instance
        if not user.id:
            user.active = True
            user = super(UserRegisterForm, self).save()
            # Contact.objects.create(user=user)
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('interests', 'avatar')
    avatar = forms.ImageField(required=False)
    interests = forms.ModelMultipleChoiceField(label='Интересы', queryset=Interest.objects.all(),
                                          widget=Select2MultipleWidget, required=False)

    # def clean_avatar(self):
    #     image = self.cleaned_data.get('avatar', False)
    #     if image:
    #         if image._size > 4 * 1024 * 1024:
    #             raise ValidationError("Image file too large ( > 4mb )")
    #         return image
    #     else:
    #         raise ValidationError("Couldn't read uploaded image")


class SearchForm(forms.Form):
    method = 'GET'

    interests = forms.ModelMultipleChoiceField(label='Интересы', queryset=Interest.objects.all(), widget=Select2MultipleWidget, required=False)
