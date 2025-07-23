from django import forms
from .models import NGO, Volunteer, UserProfile, Task, Application
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
import re

class UserForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter at least one capital, one digit, and one symbol (@/./+/-/_)',
        }),
        min_length=8, 
    )
    class Meta():
        model = User
        fields = ('username','email','password')
        widgets={
            'username': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter your username', 'label':''}),
            'email': forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Enter your email ID' ,'required': 'True'}),
        }
    def clean_password(self):
        password = self.cleaned_data.get('password')

        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")

        if not re.search(r'[A-Z]', password): 
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[0-9]', password): 
            raise forms.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[@./+-_]', password):  
            raise forms.ValidationError("Password must contain at least one special character (@/./+/-/_).")

        return password

class NGOForm(forms.ModelForm):
    class Meta:
        model = NGO
        fields = ['objective', 'location', 'registration_number', 'verification_document']
        verification_document = forms.FileField(required=True)
        widgets= {
            'location': forms.TextInput(attrs={'class':'form-control', 'placeholder':"Enter NGO's Location"}),
            'registration_number': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Enter your registration number'}),
        }

class VolunteerForm(forms.ModelForm):
    gender= [
    ('', 'Select Gender'),
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other')
    ]
    state = [
    ('', 'Select State'),
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Delhi', 'Delhi'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jammu and Kashmir', 'Jammu and Kashmir'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'),
    ]
    profession = [
    ('', 'Select Profession'),
    ('doctor', 'Doctor'),
    ('engineer', 'Engineer'),
    ('teacher', 'Teacher'),
    ('nurse', 'Nurse'),
    ('volunteer', 'Volunteer'),
    ('artist', 'Artist'),
    ('social_worker', 'Social Worker'),
    ('programmer', 'Programmer'),
    ('marketing_specialist', 'Marketing Specialist'),
    ('researcher', 'Researcher'),
    ('photographer', 'Photographer'),
    ('other', 'Other'),
]

    gender = forms.ChoiceField(choices=gender, widget=forms.Select())
    state = forms.ChoiceField(choices=state, widget=forms.Select())
    profession = forms.ChoiceField(choices=profession, widget=forms.Select())
    class Meta():
        model = Volunteer
        fields = ('phone', 'gender','profession', 'skills', 'interests', 'state')
        widgets= {
            'phone': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Enter your 10-digit phone number'}),
            'gender': forms.Select(attrs={'class':'form-select'}),
            'profession': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter your profession'}),
            'skills': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter your skills, seperate skills with a "comma(,)"'}),
            'interests': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter your interests/hobbies'}),
            'state': forms.Select(attrs={'class':'form-select'}),
 
        }

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))

class TaskForm(forms.ModelForm):
    class Meta():
        model = Task
        fields = ['task_name', 'task_type', 'task_description', 'task_location', 'city', 'state', 'start_date', 'end_date', 'positions', 'payment', 'initial_meetup_location', 'initial_meetup_date', 'initial_meetup_time']
    start_date=forms.DateField(widget = forms.SelectDateWidget())
    end_date=forms.DateField(widget = forms.SelectDateWidget())
    initial_meetup_date = forms.DateField(widget=forms.SelectDateWidget(), required=False)  # Added field
    initial_meetup_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=False)  # Added field
    initial_meetup_location = forms.CharField(max_length=150, required=False)  # Added field
    
class ApplicationForm(forms.ModelForm):
    class Meta():
        fields = ['volunteer', 'task']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_pic']

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']