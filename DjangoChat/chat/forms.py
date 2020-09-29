from django import forms

from chat.models import Chat, Contact
from django_select2.forms import Select2MultipleWidget, ModelSelect2Widget


class ComposeForm(forms.Form):
    message = forms.CharField(
            widget=forms.TextInput(
                attrs={"class": "form-control"}
                )
            )


class CreateRoomForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ('title', 'participants')

    participants = forms.ModelMultipleChoiceField(label='Друзья', queryset=Contact.objects.all(), widget=Select2MultipleWidget, required=False)


class UpdateRoomForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ('participants',)

    participants = forms.ModelMultipleChoiceField(label='Учасники чата', queryset=Contact.objects.all(),
                                                  widget=Select2MultipleWidget, required=False)

    # def clean_participants(self):
    #     print(self.cleaned_data.get('participants', False))
