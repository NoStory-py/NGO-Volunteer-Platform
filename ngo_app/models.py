from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

#-------------------------------------------------

TASK_CHOICES = (('', '-----'), ('Marketing','Marketing'), ('Content Writing','Content Writing'),
('Fundraising','Fundraising'), ('Presentation','Presentation'), ('Photography','Photography'),
('Videography','Videography'),('Internet/Web','Internet/Web'), ('Teaching/Training/Coaching','Teaching/Training/Coaching'),
('Illustration/Design/Drawing','Illustration/Design/Drawing'),
('Event Planning/Management','Event Planning/Management'),('Social Volunteering','Social Volunteering'),
('Community Management','Community Management'), ('Data Entry','Data Entry'),('Caregivers','Caregivers'),
('Poster Creation','Poster Creation'), ('Other','Other'))

# Volunteer model

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other')
)

STATE_CHOICES = (
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
)

STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

PROFESSION_CHOICES = [
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

# NGO model

class NGO(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    objective = models.CharField(max_length=255)
    location = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50, unique=True)
    verification_document = models.FileField(upload_to='verification_docs/')
    verified = models.BooleanField(default=False)
   
    

    def __str__(self):
        return self.name


class Volunteer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    phone = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number.')])  
    gender = models.CharField(max_length=11, choices=GENDER_CHOICES)
    profession = models.CharField(max_length=50, choices=PROFESSION_CHOICES, default='volunteer')
    skills = models.CharField(max_length=255)
    interests = models.CharField(max_length=255)
    state = models.CharField(max_length=30, choices=STATE_CHOICES)
    

    def __str__(self):
        return self.user.username

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='default.jpg')

    def __str__(self):
        return self.user.username


class Task(models.Model):
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=255)
    task_type = models.CharField(max_length=50, choices=TASK_CHOICES) 
    task_description = models.TextField()
    task_location = models.CharField(max_length=150)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=30, choices=STATE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    positions = models.PositiveIntegerField()
    payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        default='active',
        choices=(
            ('active', 'Active'),
            ('completed', 'Completed')
        )
    )
    initial_meetup_location = models.CharField(max_length=150, blank=True, null=True)
    initial_meetup_date = models.DateField(blank=True, null=True)
    initial_meetup_time = models.TimeField(blank=True, null=True)

    def __str__(self):
        return self.task_name

class Application(models.Model):

    volunteer = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    application_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    completed_task = models.BooleanField(default=False)
    completion_requested = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.volunteer.username} - {self.task.task_name} ({self.application_status})"

