import os
import sys

import django

controller_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(controller_dir)

sys.path.append(src_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from api.models.user import ApiUser  #

user_id = 2
try:
    user = ApiUser.objects.get(id=user_id)
    user.delete()
    print(f"User with ID {user_id} has been deleted.")
except User.DoesNotExist:
    print(f"User with ID {user_id} does not exist.")