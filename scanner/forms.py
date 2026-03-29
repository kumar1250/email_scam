from django import forms


class EmailScanForm(forms.Form):
    subject = forms.CharField(
        max_length=500, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email subject (optional)'})
    )
    sender = forms.CharField(
        max_length=300, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sender email (optional)'})
    )
    content = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 'rows': 10,
            'placeholder': 'Paste email content here...'
        })
    )
    email_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.txt,.eml'})
    )
