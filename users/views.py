import os

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import User, RoleList, Documents
from django.core.files.storage import default_storage


def home(request):
    if request.method == 'GET':
        docs = Documents.objects.filter(assigned_user=request.user)
        return render(request, 'users/dashboard.html', {'docs': docs})


@login_required()
def serve_protected_document(request, owner_id, file_name):
    try:
        document = Documents.objects.filter(url__contains=request.path)
        name, extension = os.path.splitext(file_name)
        if extension.lower() in ['.jpg', '.jpeg']:
            content_type = 'image/jpeg'
        elif extension.lower() in ['.png']:
            content_type = 'image/png'
        elif extension.lower() in ['.pdf']:
            content_type = 'application/pdf'
        else:
            content_type = f'image/{extension.strip(".").lower()}'
        response = FileResponse(open(f'temp/{owner_id}/' + file_name, 'rb'), content_type=content_type)
        if document and request.user.is_superuser:
            return response
        if document.filter(owner__id=owner_id) and request.user.role == RoleList.ADMIN:
            return response
        if document.filter(owner__id=owner_id, assigned_user=request.user) and request.user.role == RoleList.USER:
            return response
        elif request.user.role == RoleList.ADMIN:
            messages.error(request, "Document does not exist.")
            return redirect("/admin/users/Documents/")
        elif request.user.role == RoleList.USER:
            messages.error(request, "Document does not exist.")
            return redirect(reverse('Dashboard'))
    except Exception as e:
        raise Http404


def upload_doc(request):
    try:
        if request.method == 'POST' and 'doc_file' in request.FILES:
            file = request.FILES.get('doc_file')
            fs = default_storage
            # date_time = datetime.now().strftime('%y_%m_%d_%H_%M_%S')
            filename = f"temp/{request.user.id}/{file.name}"
            fs_obj = fs.save(filename.replace(" ", "_"), file)
            filepath = fs.url(fs_obj)
            file_url = f"{request.scheme}://{request.get_host()}{filepath}"

            document_obj = Documents()
            document_obj.name = request.POST.get('document_name')
            document_obj.url = file_url
            document_obj.owner = request.user
            document_obj.save()
            user_from_request = request.POST.get('assigned_users')
            users = [user for user in user_from_request] if user_from_request else []
            document_obj.assigned_user.add(*users)
            document_obj.save()
            messages.success(request, 'Document uploaded successfully')
            return redirect('/admin/users/documents/')
    except Exception as e:
        messages.error(request, "Error in Document Upload: " + str(e))
        return redirect('/admin/users/documents/add/')


def user_login(request):
    if request.method == 'GET':
        return render(request, 'users/index.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not (username and password):
            messages.add_message(request, messages.ERROR, "Enter username and password")
        user = authenticate(username=username, password=password)
        message = None
        if not user:
            try:
                user_obj = User.objects.get(username=username)
                if user_obj:
                    if not user_obj.is_active:
                        message = "User is disabled, please contact cfs support"
            except Exception as e:
                message = "Invalid username or password"
                pass
            messages.add_message(request, messages.ERROR, message)
            return redirect(reverse('login'))

        elif not user.is_active:
            messages.add_message(request, messages.ERROR, "User is inactive, please contact admin")
            return redirect(reverse('login'))
        elif user.is_superuser or user.role == RoleList.ADMIN:
            login(request, user)
            return redirect('/admin/')
        elif user.role == RoleList.USER:
            login(request, user)
            return redirect(reverse('Dashboard'))
    else:
        messages.add_message(request, messages.ERROR, "Invalid method")
        return redirect(reverse('login'))


def forgot_password(request):
    if request.method == "GET":
        return render(request, 'forget_password.html')
    elif request.method == "POST":
        return render(request, 'forget_password.html')


def check_authentication(request):
    if not request.user.is_authenticated:
        messages.add_message(request, messages.ERROR, "LogIn Required")
        return False
    else:
        return True


def user_logout(request):
    res = check_authentication(request)
    if not res:
        return redirect('login')
    logout(request)
    request.session.flush()
    return redirect('login')
