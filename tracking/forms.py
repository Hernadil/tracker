from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import CustomUser, Project, Log, VideoTitle, Expense


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
            'max_writer_count', 'max_videographer_count', 'max_editor_count', 'max_photographer_count',
            'pay_writer', 'pay_videographer', 'pay_editor', 'pay_photographer',
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
            'max_writer_count': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0', 'min': '0'}),
            'max_videographer_count': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0', 'min': '0'}),
            'max_editor_count': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0', 'min': '0'}),
            'max_photographer_count': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0', 'min': '0'}),
            'pay_writer': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0', 'min': '0'}),
            'pay_videographer': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0', 'min': '0'}),
            'pay_editor': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0', 'min': '0'}),
            'pay_photographer': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0', 'min': '0'}),
        }
        labels = {
            'title': 'Projekt cím', 'company': 'Cég', 'revenue': 'Teljes bevétel (Ft)',
            'project_type': 'Projekt típusa', 'location': 'Helyszín', 'description': 'Leírás',
            'required_video_count': 'Szükséges videók száma',
            'writer_deadline': 'Forgatókönyv határidő', 'editor_deadline': 'Vágó határidő',
            'videographer_date': 'Forgatás dátuma', 'photo_onsite_date': 'Fotózás dátuma',
            'photo_editing_deadline': 'Fotó szerkesztési határidő',
            'onsite_hours': 'Helyszíni órák', 'total_hours_expected': 'Összes elvárható óra',
            'max_writer_count': 'Forgatókönyv írók max. létszám',
            'max_videographer_count': 'Videósok max. létszám',
            'max_editor_count': 'Vágók max. létszám',
            'max_photographer_count': 'Fotósok max. létszám',
            'pay_writer': 'Forgatókönyv író díja / fő (Ft)',
            'pay_videographer': 'Videós díja / fő (Ft)',
            'pay_editor': 'Vágó díja / fő (Ft)',
            'pay_photographer': 'Fotós díja / fő (Ft)',
        }
        
    def clean(self):
        cleaned_data = super().clean()
        project_type = cleaned_data.get('project_type')
        both_types = cleaned_data.get('both_types')
        required_video_count = cleaned_data.get('required_video_count')
        
        # Ha fotó csak projektről van szó, a videók száma nem szükséges
        if project_type == 'photo' and not both_types:
            if required_video_count is None or required_video_count == 0:
                cleaned_data['required_video_count'] = 0

        revenue = cleaned_data.get('revenue') or 0
        max_writer_count = cleaned_data.get('max_writer_count') or 0
        max_videographer_count = cleaned_data.get('max_videographer_count') or 0
        max_editor_count = cleaned_data.get('max_editor_count') or 0
        max_photographer_count = cleaned_data.get('max_photographer_count') or 0
        pay_writer = cleaned_data.get('pay_writer') or 0
        pay_videographer = cleaned_data.get('pay_videographer') or 0
        pay_editor = cleaned_data.get('pay_editor') or 0
        pay_photographer = cleaned_data.get('pay_photographer') or 0

        total_allocated = (
            max_writer_count * pay_writer
            + max_videographer_count * pay_videographer
            + max_editor_count * pay_editor
            + max_photographer_count * pay_photographer
        )
        if total_allocated > revenue:
            raise forms.ValidationError(
                "A munkakörök összesített költsége nem lehet nagyobb a teljes bevételnél."
            )
        
        return cleaned_data


class EditProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['revenue', 'description']
        widgets = {
            'revenue': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Rövid leírás'}),
        }
        labels = {
            'revenue': 'Teljes bevétel (Ft)',
            'description': 'Leírás',
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


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0'}),
            'description': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Kiadás leírása'}),
        }
        labels = {
            'amount': 'Összeg (Ft)',
            'description': 'Leírás',
        }
