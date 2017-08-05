"""
* Address create update
* Work experience create update
* 400/500 handler
* LDAP with login
* Privacy level
* Account creation source
"""

from uuid import uuid4
from functools import wraps

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import HttpResponse
from django.forms.models import model_to_dict
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate

from .forms import User_BasicInfoForm, User_MiscInfoForm, User_SocialLinksForm
from .forms import AddressForm, QualificationForm, WorkExperienceForm
from .models import User, Address, Qualification, WorkExperience

# Create your views here.
def index(request):
    return HttpResponse("Hello from the server side!")


def handler400(request):
    render(request, '400.html', status=400)


def handler403(request):
    render(request, '403.html', status=403)


def handler404(request):
    render(request, '404.html', status=404)


def handler500(request):
    render(request, '500.html', status=500)


from .forms import LoginForm
from .models import UserSession


def get_session(request):
    try:
        sessionid = request.session.get('sessionid')
        userid = request.session.get('userid')
        if (not sessionid) or (not userid):
            return None
        return UserSession.objects.get(pk=sessionid)
    except UserSession.DoesNotExist:
        return None


def register_new_session(userid):
    if not userid:
        return None
    try:
        userobj = User.objects.get(roll_no=userid)
        print(userobj)
        session = UserSession(sessionid=uuid4().hex, user=userobj)
        session.save()
        return session
    except User.DoesNotExist:
        print('User does not exist to register new session')
        return None


def authenticate(request):
    if request.method == 'POST':
        userid = request.POST.get('username')
        password = request.POST.get('password')
        print(userid, password)
        # some random validation
        session = register_new_session(userid)
        if session:
            request.session['userid'] = session.user.roll_no
            request.session['sessionid'] = session.sessionid
            return HttpResponse('authenticated')
        else:
            return HttpResponse('Invalid user')
    else:
        return HttpResponse('Method not allowed.')


def login(request):
    session = get_session(request)
    if session is None:
        return render(request, 'login.html',
                      {'form': LoginForm, 'submit_url': reverse(authenticate)})
    else:
        return redirect(reverse(GetInfo.basic, args=[request.session.get('userid')]))



def logout(request):
    session = get_session(request)
    if session is not None:
        request.session.pop('sessionid')
        request.session.pop('userid')
        session.delete()
    return HttpResponse('logout done')



def login_required(f):
    @wraps(f)
    def decorated_fn(request, *args, **kwargs):
        session = get_session(request)
        if session is None:
            return redirect(reverse(login))
        return f(request, *args, **kwargs)
    return decorated_fn


def authorized(f):
    @wraps(f)
    def decorated_fn(request, roll_no, *args, **kwargs):
        if request.session.get('userid') == roll_no:
            return f(request, roll_no, *args, **kwargs)
        return HttpResponse('Unauthorized')
    return decorated_fn


class GetInfo(object):

    @staticmethod
    def basic(request, roll_no):
        user = get_object_or_404(User, roll_no=roll_no)
        context = {
            key: getattr(user, key, None)
            for key in User_BasicInfoForm.Meta.fields
        }
        return render(request, 'user_basic.html', context)

    @staticmethod
    def social(request, roll_no):
        user = User.objects.get(roll_no=roll_no)
        context = {
            key: getattr(user, key, None)
            for key in User_SocialLinksForm.Meta.fields
        }
        return render(request, 'user_social.html', context)

    @staticmethod
    def misc(request, roll_no):
        user = User.objects.get(roll_no=roll_no)
        context = {
            key: getattr(user, key, None)
            for key in User_MiscInfoForm.Meta.fields
        }
        return render(request, 'user_misc.html', context)


class PostInfo(object):

    @staticmethod
    @login_required
    @authorized
    def basic(request, roll_no):
        context = {
            'roll_no': roll_no,
            'form': None,
            'submit_url': reverse(PostInfo.basic, args=[roll_no])
        }
        user = get_object_or_404(User, roll_no=roll_no)
        if request.method == 'POST':
            form = User_BasicInfoForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                return redirect(GetInfo.basic, roll_no=roll_no)
            else:
                context['form'] = form
                return render(request, 'user_edit.html', context)
        else:
            context['form'] = User_BasicInfoForm(initial=model_to_dict(user))
            return render(request, 'user_edit.html', context)

    @staticmethod
    @login_required
    @authorized
    def social(request, roll_no):
        context = {
            'roll_no': roll_no,
            'form': None,
            'submit_url': reverse(PostInfo.social, args=[roll_no])
        }
        user = get_object_or_404(User, roll_no=roll_no)
        if request.method == 'POST':
            form = User_SocialLinksForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                return redirect(GetInfo.social, roll_no=roll_no)
            else:
                context['form'] = form
                return render(request, 'user_edit.html', context)
        else:
            context['form'] = User_SocialLinksForm(initial=model_to_dict(user))
            return render(request, 'user_edit.html', context)

    @staticmethod
    @login_required
    @authorized
    def misc(request, roll_no):
        context = {
            'roll_no': roll_no,
            'form': None,
            'submit_url': reverse(PostInfo.misc, args=[roll_no])
        }
        user = get_object_or_404(User, roll_no=roll_no)
        if request.method == 'POST':
            form = User_MiscInfoForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                return redirect(GetInfo.misc, roll_no=roll_no)
            else:
                context['form'] = form
                return render(request, 'user_edit.html', context)
        else:
            context['form'] = User_MiscInfoForm(initial=model_to_dict(user))
            return render(request, 'user_edit.html', context)
