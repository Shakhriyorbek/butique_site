from .forms import LoginForm, RegistrationForm

def add_my_forms(request):
    return {
        'login_form': LoginForm(),
        'register_form': RegistrationForm()
    }