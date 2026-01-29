from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.exceptions import PermissionDenied

from .forms import SignUpForm, LoginForm, EditProfileForm
from bookings.models import Booking

# -------------------- HELPER DECORATORS --------------------
def admin_required(view_func):
    """Decorator to ensure the user is staff/admin."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

# -------------------- HOME --------------------
def home_view(request):
    return render(request, "accounts/home.html")

# -------------------- ABOUT --------------------
def about_view(request):
    return render(request, "about.html")

# -------------------- SIGNUP --------------------
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import SignUpForm

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # secure password
            user.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

# -------------------- LOGIN --------------------
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('admin_dashboard')
                next_url = request.GET.get('next')
                return redirect(next_url if next_url else 'dashboard')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
        if 'next' in request.GET:
            messages.warning(request, 'You need to login first before booking.')

    return render(request, 'accounts/login.html', {'form': form})

# -------------------- LOGOUT --------------------
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('home')

# -------------------- USER DASHBOARD --------------------
@login_required
def dashboard_view(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')

    user = request.user
    next_booking = Booking.objects.filter(user=user, session_datetime__gte=now()).order_by('session_datetime').first()
    total_booked = Booking.objects.filter(user=user).count()
    pending_sessions = Booking.objects.filter(user=user, status__iexact="pending").count()
    completed_sessions = Booking.objects.filter(user=user, status__iexact="approved").count()

    context = {
        'next_booking': next_booking,
        'total_booked': total_booked,
        'pending_sessions': pending_sessions,
        'completed_sessions': completed_sessions,
    }

    return render(request, 'accounts/dashboard.html', context)

# -------------------- BOOK NOW --------------------
@login_required
def book_now(request):
    return redirect('create_booking')

# -------------------- USER PROFILE --------------------
@login_required
def user_profile(request):
    return render(request, "accounts/user_profile.html")

# -------------------- EDIT PROFILE --------------------
@login_required
def edit_profile(request):
    if request.method == "POST":
        user = request.user
        display_name = request.POST.get('display_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        avatar = request.POST.get('avatar')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if User.objects.filter(username=username).exclude(pk=user.pk).exists():
            messages.error(request, "Username is already taken!")
            return redirect('edit_profile')

        user.first_name = display_name
        user.username = username
        user.email = email

        if password1 or password2:
            if password1 != password2:
                messages.error(request, "Passwords do not match!")
                return redirect('edit_profile')
            user.set_password(password1)

        user.save()

        profile = getattr(user, 'profile', None)
        if profile:
            profile.avatar = avatar
            profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('edit_profile')

    return render(request, 'accounts/edit_profile.html')

# -------------------- ADMIN DASHBOARD --------------------
@login_required
@admin_required
def admin_dashboard(request):

    # -------- BOOKINGS --------
    all_bookings = Booking.objects.all().order_by('-session_datetime')
    total_bookings = all_bookings.count()
    approved_bookings = all_bookings.filter(status='approved').count()
    pending_bookings = all_bookings.filter(status='pending')
    cancelled_bookings = all_bookings.filter(status='cancelled').count()

    # -------- USERS --------
    user_list = User.objects.all().order_by('-date_joined')
    total_users = user_list.count()

    # -------- DELETED USERS --------
    from accounts.models import DeletedUser
    deleted_users = DeletedUser.objects.all().order_by('-timestamp')

    # -------- NOTIFICATIONS --------
    notifications = []

    for b in pending_bookings[:5]:
        notifications.append(
            {'message': f"{b.user.username} requested a {b.get_service_type_display()} session."}
        )

    cancelled_recent = all_bookings.filter(status='cancelled').order_by('-created_at')[:5]
    for b in cancelled_recent:
        notifications.append(
            {'message': f"{b.user.username} cancelled their {b.get_service_type_display()} booking."}
        )

    # -------- ACTIVITY LOGS --------
    activity_logs = [
        {'timestamp': b.created_at, 'action': f"{b.user.username} booked {b.get_service_type_display()}"}
        for b in all_bookings.order_by('-created_at')[:5]
    ]

    context = {
        'all_bookings': all_bookings,
        'total_bookings': total_bookings,
        'approved_bookings': approved_bookings,
        'pending_bookings': pending_bookings,
        'cancelled_bookings': cancelled_bookings,

        # FIXED — ADDED
        'user_list': user_list,
        'total_users': total_users,
        'deleted_users': deleted_users,

        'notifications': notifications,
        'activity_logs': activity_logs,
    }

    return render(request, 'accounts/dashboard_admin.html', context)






@login_required
@admin_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if booking.status != 'cancelled':
        booking.status = 'cancelled'
        booking.save()
        messages.info(request, f"{booking.user.username}'s booking has been cancelled.")  # purple/pink info
    return redirect('admin_dashboard')


from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import DeletedUser
from .views import admin_required  # your custom decorator

@login_required
@admin_required
def admin_delete_user(request, user_id):
    # Prevent admin from deleting themselves
    if request.user.id == user_id:
        messages.error(request, "You cannot delete your own account.")
        return redirect('admin_dashboard')

    user_to_delete = get_object_or_404(User, id=user_id)

    # Log deleted user
    DeletedUser.objects.create(
        user=user_to_delete,
        username=user_to_delete.username,
        deleted_by=request.user.username
    )

    # Delete the user
    user_to_delete.delete()

    messages.success(request, f"User '{user_to_delete.username}' deleted successfully.")
    return redirect('admin_dashboard')






# -------------------- ADMIN – DELETE USER --------------------
@login_required
@admin_required
def admin_delete_user(request, user_id):

    if request.user.id == user_id:
        messages.error(request, "You cannot delete your own account.")
        return redirect('admin_dashboard')

    user_to_delete = get_object_or_404(User, id=user_id)

    # record deletion history (safe fix)
    DeletedUser.objects.create(
        username=user_to_delete.username,
        deleted_by=request.user.username
    )

    user_to_delete.delete()

    messages.success(request, "User deleted successfully.")
    return redirect('admin_dashboard')
