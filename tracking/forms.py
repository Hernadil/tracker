from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import CustomUser, Project, Log, VideoTitle


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Felhasználónév', 'autocomplete': 'off'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Jelszó'}))


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Régi jelszó'}))
    new_password1 = forms.CharField(label='Új jelszó', widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Új jelszó'}))
    new_password2 = forms.CharField(label='Új jelszó újra', widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Új jelszó újra'}))


class NewEmployeeForm(forms.ModelForm):
    password = forms.CharField(label='Jelszó', widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Jelszó'}))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'job_role', 'is_boss']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Keresztnév'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Vezetéknév'}),
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Felhasználónév'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Telefonszám'}),
            'job_role': forms.Select(attrs={'class': 'form-input'}),
            'is_boss': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        labels = {
            'first_name': 'Keresztnév', 'last_name': 'Vezetéknév',
            'username': 'Felhasználónév', 'email': 'Email',
            'phone_number': 'Telefonszám', 'job_role': 'Munkakör', 'is_boss': 'Boss jogosultság',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class CreateProjectForm(forms.ModelForm):
    both_types = forms.BooleanField(required=False, label='Mindkét típus (videó + fotó)')

    class Meta:
        model = Project
        fields = [
            'title', 'company', 'revenue', 'project_type', 'location', 'description',
            'required_video_count', 'writer_deadline', 'editor_deadline', 'videographer_date',
            'photo_onsite_date', 'photo_editing_deadline', 'onsite_hours', 'total_hours_expected',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Projekt cím'}),
            'company': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Cég neve'}),
            'revenue': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0'}),
            'project_type': forms.Select(attrs={'class': 'form-input', 'id': 'project_type_select'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Helyszín'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Rövid leírás'}),
            'required_video_count': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0'}),
            'writer_deadline': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'editor_deadline': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'videographer_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'photo_onsite_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'photo_editing_deadline': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'onsite_hours': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0'}),
            'total_hours_expected': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0'}),
        }
        labels = {
            'title': 'Projekt cím', 'company': 'Cég', 'revenue': 'Teljes bevétel (Ft)',
            'project_type': 'Projekt típusa', 'location': 'Helyszín', 'description': 'Leírás',
            'required_video_count': 'Szükséges videók száma',
            'writer_deadline': 'Forgatókönyv határidő', 'editor_deadline': 'Vágó határidő',
            'videographer_date': 'Forgatás dátuma', 'photo_onsite_date': 'Fotózás dátuma',
            'photo_editing_deadline': 'Fotó szerkesztési határidő',
            'onsite_hours': 'Helyszíni órák', 'total_hours_expected': 'Összes elvárható óra',
        }


class NewLogForm(forms.ModelForm):
    class Meta:
        model = Log
        fields = ['hours', 'comment']
        widgets = {
            'hours': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0', 'step': '0.5', 'min': '0'}),
            'comment': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Megjegyzés (opcionális)'}),
        }
        labels = {'hours': 'Ledolgozott órák', 'comment': 'Megjegyzés'}
