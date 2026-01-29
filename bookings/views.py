from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .forms import BookingForm
from .models import Booking


# --------------------
# USER — CREATE BOOKING
# --------------------
@login_required
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.notified = False
            booking.save()
            return redirect('my_bookings')
    else:
        form = BookingForm()

    return render(request, 'bookings/create_booking.html', {'form': form})


# --------------------
# USER — VIEW BOOKINGS
# --------------------
@login_required
def my_bookings(request):
    # Show the logged-in user's bookings
    bookings = Booking.objects.filter(user=request.user).order_by('-session_datetime')

    # Notifications only for the user (admins get same notifications if they create bookings)
    for booking in bookings.filter(status='approved', notified=False):
        messages.info(
            request,
            f"Your booking for {booking.get_service_type_display()} on "
            f"{booking.session_datetime.strftime('%Y-%m-%d %H:%M')} is now APPROVED."
        )
        booking.notified = True
        booking.save()

    for booking in bookings.filter(status='disapproved', notified=False):
        booking.notified = True
        booking.save()

    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})



# --------------------
# USER — UPDATE BOOKING
# --------------------
@login_required
def update_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.info(request, 'Booking updated successfully.')
            return redirect('my_bookings')
    else:
        form = BookingForm(instance=booking)

    return render(request, 'bookings/update_booking.html', {'form': form})


# --------------------
# USER — CANCEL BOOKING (Not Delete)
# --------------------
@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)

    # User can always cancel any booking except already cancelled
    if booking.status != 'cancelled':
        booking.status = 'cancelled'
        booking.notified = False
        booking.save()
        messages.info(request, "Your booking has been cancelled.")

    return redirect('my_bookings')


# --------------------
# USER — DELETE BOOKING (Permanent Remove)
# --------------------
@login_required
def delete_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.user.is_staff:  # Admin delete
        booking.delete()
        messages.info(request, "Booking deleted successfully.")
        return redirect('admin_dashboard')

    if booking.user == request.user:  # User delete
        booking.delete()
        messages.info(request, "Booking removed successfully.")
        return redirect('my_bookings')

    return redirect('my_bookings')


# --------------------
# DETAILS VIEW
# --------------------
@login_required
def booking_details(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'bookings/booking_details.html', {'booking': booking})


# --------------------
# ADMIN — UPDATE
# --------------------
@staff_member_required
def admin_update_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.info(request, f"{booking.user.username}'s booking updated.")
            return redirect('admin_dashboard')
    else:
        form = BookingForm(instance=booking)

    return render(
        request,
        'bookings/admin_update_booking.html',
        {'form': form, 'booking': booking}
    )


# --------------------
# ADMIN — APPROVE
# --------------------
@staff_member_required
def approve_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    booking.status = 'approved'
    booking.notified = False
    booking.save()
    return redirect('admin_dashboard')


# --------------------
# ADMIN — DISAPPROVE
# --------------------
@staff_member_required
def disapprove_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    booking.status = 'disapproved'
    booking.notified = True
    booking.save()
    return redirect('admin_dashboard')


# --------------------
# ADMIN — RESCHEDULE
# --------------------
@staff_member_required
def reschedule_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.status = 'pending'
            updated.notified = False
            updated.save()
            messages.info(request, f"{booking.user.username}'s booking rescheduled.")
            return redirect('admin_dashboard')
    else:
        form = BookingForm(instance=booking)

    return render(
        request,
        'bookings/reschedule_booking.html',
        {'form': form, 'booking': booking}
    )


# --------------------
# ADMIN — DELETE (From Dashboard Delete Button)
# --------------------
@staff_member_required
def admin_delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    messages.success(request, "Booking deleted.")  # ← changed from info → success
    return redirect('admin_dashboard')

