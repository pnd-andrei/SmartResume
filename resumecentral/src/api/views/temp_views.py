# temporary_urls/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import uuid

def generate_temporary_url(request, user_object):
    # Generate a unique token (for example, using UUID)
    token = str(uuid.uuid4())

    # Save the token in session or database for validation later
    request.session['temporary_token'] = {"token": token, "user_object": user_object}
    
    print(token)
    # Example: Redirect to a temporary URL endpoint with token
    #return redirect("temporary_url_process", token=token)

def process_temporary_url(request, token):
    # Retrieve the token from session or database
    stored_token = request.session.get('temporary_token')

    if token == stored_token:
        # Process the temporary URL action (e.g., reset password)
        # Remove the token from session or mark as used
        del request.session['temporary_token']
        return HttpResponse('Temporary URL is valid. Process your action here.')
    else:
        return HttpResponse('Invalid or expired temporary URL.')

