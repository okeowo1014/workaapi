from functools import wraps

from django.shortcuts import redirect

from api.models import Staff


# https://chat.whatsapp.com/JIcHfXrpo014x08yTMhRTC
def has_role(role, request):
    staff = Staff.objects.get(user=request.user)
    if role in staff.roles.split(','):
        return True
    else:
        return redirect('administrator:access_denied')


# def user_is_entry_author(function):
#     def wrap(request, *args, **kwargs):
#         entry = Entry.objects.get(pk=kwargs['entry_id'])
#         if entry.created_by == request.user:
#             return function(request, *args, **kwargs)
#         else:
#             raise PermissionDenied
#
#     wrap.__doc__ = function.__doc__
#     wrap.__name__ = function.__name__
#     return wrap


def can_view(role):
    def inner_render(fn):
        @wraps(fn)  # Ensure the wrapped function keeps the same name as the view
        def wrapped(request, *args, **kwargs):
            staff = Staff.objects.get(user=request.user)
            if role in staff.roles.split(','):
                return fn(request, *args, **kwargs)
            else:
                return redirect('administrator:access_denied')

        return wrapped

    return inner_render
