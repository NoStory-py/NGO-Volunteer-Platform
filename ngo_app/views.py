from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

from .forms import UserForm, NGOForm, VolunteerForm, LoginForm, TaskForm, ApplicationForm, UserProfileForm, UserEditForm
from .models import NGO, Volunteer, Task, Application, TASK_CHOICES, STATE_CHOICES, STATUS_CHOICES, UserProfile

from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import render_to_string

from django.http import FileResponse
from django.conf import settings
import os

def home(request):
    return render(request, 'index.html')

def user_register(request):
    user_form = UserForm()
    volunteer_form = VolunteerForm()
    ngo_form = NGOForm()
    profile_form = UserProfileForm(request.POST, request.FILES)

    if request.method == 'POST':
        user_type = request.POST.get('user_type')

        user_form = UserForm(request.POST)
        if user_type == 'volunteer':
            volunteer_form = VolunteerForm(request.POST)

            if user_form.is_valid() and volunteer_form.is_valid() and profile_form.is_valid():
                user = user_form.save(commit=False)
                user.set_password(user_form.cleaned_data['password']) 
                user.save()  

                volunteer = volunteer_form.save(commit=False) 
                volunteer.user = user 
                volunteer.save()  

                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()

                messages.success(request, "Registration successful! You can now log in.")
                return redirect('user_login')
            else:
                print(user_form.errors)  
                print(volunteer_form.errors)
                print(profile_form.errors)

        elif user_type == 'ngo':
            ngo_form = NGOForm(request.POST, request.FILES)

            if user_form.is_valid() and ngo_form.is_valid() and profile_form.is_valid():
                user = user_form.save(commit=False)
                user.set_password(user_form.cleaned_data['password'])
                user.save()  

                ngo = ngo_form.save(commit=False) 
                ngo.user = user  
                ngo.save()  

                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()

                messages.success(request, "Registration successful! You can now log in.")
                return redirect('user_login')  
            else:
                print(user_form.errors)
                print(ngo_form.errors)  
                print(profile_form.errors)  
    
    return render(request, 'register.html', {
        'user_form': user_form,
        'volunteer_form': volunteer_form,
        'ngo_form': ngo_form,
        'profile_form': profile_form,
        'show_register_button': False,
    })



def user_login(request):
    form = LoginForm()

    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        
        if user_type == 'volunteer':
            form = LoginForm(data=request.POST)
         
            if form.is_valid():
             
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
         
                if user is not None:
                    try:
                        Volunteer.objects.get(user=user)
                        login(request, user)
                        return redirect('volunteer_dashboard')

                    except Volunteer.DoesNotExist:
                        messages.error(request, "User does not have a Volunteer account.")
                        return redirect('user_login')  
                        
                else:
                    messages.error(request, "Please enter a correct username and password.")
                    return redirect('user_login') 
    
        elif user_type == 'ngo':
            form = LoginForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                
                if user is not None:
                    try:
                        NGO.objects.get(user=user)
                        login(request, user)
                        return redirect('ngo_dashboard')
                    except NGO.DoesNotExist:
                        messages.error(request, "User does not have a NGO account.")
                        return redirect('user_login')
                        
                else:
                    messages.error(request, "Please enter a correct username and password.")
                    return redirect('user_login')  


    return render(request, 'login.html', {
        'login_form': form, 
        'show_register_button': True,
    })

@login_required
def user_logout(request):
    auth_logout(request)
    messages.success(request, "User Logged out")
    return redirect('user_login')

@login_required
def volunteer_dashboard(request):
    try:
        volunteer = Volunteer.objects.get(user=request.user)

        selected_state = request.GET.get('state')  
        selected_job_type = request.GET.get('job_type')  
        max_start_date = request.GET.get('max_start_date')
        payment_type = request.GET.get('payment')  

        tasks = Task.objects.exclude(status='completed').exclude(application__volunteer=request.user)

        if selected_state:
            tasks = tasks.filter(state=selected_state)

        if selected_job_type:
            tasks = tasks.filter(job_type=selected_job_type)

        if max_start_date:
            tasks = tasks.filter(start_date__lte=max_start_date)

        if payment_type:
            if payment_type == 'free':
                tasks = tasks.filter(payment = 0)
            elif payment_type == 'paid':
                tasks = tasks.exclude(payment = 0)
        
        user = request.user
        applications = Application.objects.filter(volunteer=user)

        context = {
            'volunteer': volunteer,
            'tasks': tasks,
            'filter_state': STATE_CHOICES,
            'filter_task': TASK_CHOICES,
            'applications': applications
        }
        
        return render(request, 'volunteer_dashboard.html', context)

    except Volunteer.DoesNotExist:

        messages.error(request, "Access denied: You do not have permission to view this page.")
        return redirect('user_login')

@login_required
def ngo_dashboard(request):
    try:
        ngo = NGO.objects.get(user=request.user)

        if request.method == 'POST':
            task_form = TaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False) 
                task.ngo = ngo  
                task.save()  
                messages.success(request, 'Task created successfully!')
                return redirect('ngo_dashboard')
        else:
            task_form = TaskForm()
        
        tasks = Task.objects.filter(ngo=ngo)
        applications = Application.objects.filter(task__in=tasks).exclude(application_status__in=['approved', 'rejected'])
        complete_requests = Application.objects.filter(task__in=tasks, completion_requested=True, completed_task=False)
        print("Complete Requests:", complete_requests)

        total_tasks = Task.objects.filter(ngo=ngo).count() 
        active_tasks = Task.objects.filter(ngo=ngo, status='active').count() 
        completed_tasks = Task.objects.filter(ngo=ngo, status='completed').count() 
        tasks = Task.objects.filter(ngo=ngo)

        return render(request, 'ngo_dashboard.html', {
            'ngo': ngo,
            'name': ngo.user.username, 
            'objective': ngo.objective,  
            'task_form': task_form,
            'total_tasks': total_tasks, 
            'active_tasks': active_tasks,
            'completed_tasks': completed_tasks,
            'tasks' : tasks,
            'applications': applications,
            'complete_requests': complete_requests
        })

    except NGO.DoesNotExist:
        messages.error(request, "Access denied: You do not have permission to view this page.")
        return redirect('user_login')

# profile

@login_required
def view_profile(request):
  
    user = request.user  

    try:
        volunteer = Volunteer.objects.get(user=user)
        profile_pic = user.userprofile.profile_pic.url
        return render(request, 'view_profile.html', {'profile': volunteer, 'user': user, 'profile_type': 'volunteer', 'profile_pic': profile_pic})
    except Volunteer.DoesNotExist:
        volunteer = None


    try:
        ngo = NGO.objects.get(user=user)
        profile_pic = user.userprofile.profile_pic.url
        return render(request, 'view_profile.html', {'profile': ngo, 'user': user, 'profile_type': 'ngo', 'profile_pic': profile_pic,})
    except NGO.DoesNotExist:
        ngo = None

    return render(request, 'login.html', {'error': 'Profile not found.'})

@login_required
def create_task(request):
    if request.method == 'POST':
     
        task_form = TaskForm(request.POST)
        
        if task_form.is_valid():
          
            task = task_form.save(commit=False)
            task.ngo = request.user.ngo  
            task.save()  
            
            messages.success(request, 'Task created successfully!')
            return redirect('ngo_dashboard')
        else:
          
            print(task_form.errors)

    else:
        
        task_form = TaskForm()

    context = {
        'task_form': task_form,
    }
    return render(request, 'create_task.html', context)

@login_required
def portfolio(request):

    volunteer = Volunteer.objects.get(user=request.user)
    
    completed_applications = Application.objects.filter(
        volunteer=request.user,
        application_status='completed'
    )

    completed_tasks = Application.objects.filter(completed_task= True)

    skills = volunteer.skills
    interests = volunteer.interests
    profession = volunteer.profession

    portfolio_directory = 'media/portfolios' 
    portfolio_filename = f"{volunteer.user.username}_portfolio.pdf"
    portfolio_path = os.path.join(portfolio_directory, portfolio_filename)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{portfolio_filename}"'

    html = render_to_string('portfolio.html', {
        'volunteer': volunteer,
        'completed_tasks': completed_tasks,
        'skills': skills,
        'interests': interests,
        'profession': profession,
    })

    pisa_status = pisa.CreatePDF(html, dest=response)

    if not os.path.exists(portfolio_directory):
        os.makedirs(portfolio_directory)  

    with open(portfolio_path, 'wb') as pdf_file:
        pdf_file.write(response.content)  

    return response


@login_required
def apply_task(request, task_id):
    
    if request.method == "POST":
        
        task = get_object_or_404(Task, id=task_id)
        if Application.objects.filter(volunteer=request.user, task=task).exists():
            messages.warning(request, "You have already applied for this task.")
            return redirect('volunteer_dashboard')

        application = Application(
            volunteer=request.user, 
            task=task,
        )
        application.save()
        save_portfolio(request)
        return redirect('volunteer_dashboard')

    return redirect('volunteer_dashboard')

@login_required
def update_status(request, application_id):
    try:
        application = get_object_or_404(Application, id=application_id)

        if request.method == 'POST':
            new_status = request.POST.get('status')
            application.application_status = new_status
            if new_status == 'approved':
            
                task = application.task
                task.position = -1 
                task.save() 
            
            application.save()
            messages.success(request, 'Application status updated successfully!')
        else:
            messages.error(request, 'Invalid request method.')

    except Exception as e:
        messages.error(request, f'Error updating application: {str(e)}')

    return redirect('ngo_dashboard')

# views.py

from .forms import UserEditForm  # Make sure to import the new form

@login_required
def edit_profile(request):
    user = request.user
    user_profile = user.userprofile

    user_form = UserEditForm(instance=user)  # Use the new form here
    profile_form = UserProfileForm(instance=user_profile)

    if hasattr(user, 'volunteer'):
        profile_type = 'volunteer'
        volunteer_form = VolunteerForm(instance=user.volunteer)
        ngo_form = None
    elif hasattr(user, 'ngo'):
        profile_type = 'ngo'
        ngo_form = NGOForm(instance=user.ngo)
        volunteer_form = None
    else:
        profile_type = None
        volunteer_form = None
        ngo_form = None

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if profile_type == 'volunteer':
            volunteer_form = VolunteerForm(request.POST, instance=user.volunteer)
        elif profile_type == 'ngo':
            ngo_form = NGOForm(request.POST, request.FILES, instance=user.ngo)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            if profile_type == 'volunteer' and volunteer_form.is_valid():
                volunteer_form.save()
            elif profile_type == 'ngo' and ngo_form.is_valid():
                ngo_form.save()

            messages.success(request, "Profile updated successfully!")
            return redirect('view_profile')
        else:
            messages.error(request, "There was an error updating your profile.")

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'volunteer_form': volunteer_form,
        'ngo_form': ngo_form,
        'profile_type': profile_type,
    }
    return render(request, 'edit_profile.html', context)

def edit_task(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        task = get_object_or_404(Task, id=task_id)

        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'task_id': task.id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'DELETE':
        task.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def download_portfolio(request, application_id):

    application = get_object_or_404(Application, id=application_id)
    volunteer = application.volunteer
    print(volunteer.username)
    portfolio_filename = f"{volunteer.username}_portfolio.pdf"
    

    portfolio_path = os.path.join(settings.MEDIA_ROOT, f'portfolios/{portfolio_filename}')

    if os.path.exists(portfolio_path):
        return FileResponse(open(portfolio_path, 'rb'), content_type='application/pdf')
    else:
        return HttpResponse("Portfolio not found", status=404)

def save_portfolio(request):
    volunteer = Volunteer.objects.get(user=request.user)
    completed_tasks = None
    
    completed_applications = Application.objects.filter(
        volunteer=request.user,
        application_status='completed'
    )

    completed_tasks = Application.objects.filter(completed_task= True)

    skills = volunteer.skills
    interests = volunteer.interests
    profession = volunteer.profession

    portfolio_directory = 'media/portfolios' 
    portfolio_filename = f"{volunteer.user.username}_portfolio.pdf"
    portfolio_path = os.path.join(portfolio_directory, portfolio_filename)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{portfolio_filename}"'

    html = render_to_string('portfolio.html', {
        'volunteer': volunteer,
        'completed_tasks': completed_tasks,
        'skills': skills,
        'interests': interests,
        'profession': profession,
    })

    if not os.path.exists(portfolio_directory):
        os.makedirs(portfolio_directory)  

    with open(portfolio_path, 'wb') as pdf_file:
        pisa_status = pisa.CreatePDF(html, dest=pdf_file)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return redirect('volunteer_dashboard')

def task_completion(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    print(application.completion_requested)
    application.completion_requested = True
    print(application.completion_requested)
    application.save()

    return redirect('volunteer_dashboard')

def update_completion(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        
        if status == "approved":
            application.completed_task = True
        
        application.save()
    return redirect('ngo_dashboard')
