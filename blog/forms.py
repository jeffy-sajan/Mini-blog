from django import forms
from .models import Comment, Profile

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Write your comment here...'
        }),
        label='Comment'
    )

    class Meta:
        model = Comment
        fields = ['content']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture', 'social_link']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'social_link': forms.URLInput(attrs={'placeholder': 'https://your-social-profile.com'})
        }
