from django import forms
from .models import complaint



class ComplaintForm(forms.ModelForm):
    class Meta:
        model = complaint
        fields = ['description']

class ComplaintReplyForm(forms.ModelForm):
    class Meta:
        model = complaint
        fields = ['reply']
        

from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['sender_id', 'feedback_desc']
        widgets = {
            
            'sender_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'feedback_desc': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Review', 'rows': 4}),
        }
        



