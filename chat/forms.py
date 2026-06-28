from django import forms
from .models import Message, Thread
from shared.models import CustomUser

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Type your message...'
            }),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class NewThreadForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=True
    )
    
    class Meta:
        model = Thread
        fields = ['name', 'participants']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Group name (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Exclude current user and only include valid chat partners
            self.fields['participants'].queryset = CustomUser.objects.exclude(id=user.id).filter(
                is_active=True
            )