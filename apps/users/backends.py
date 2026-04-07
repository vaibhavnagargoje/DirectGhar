from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    This backend allows users to login using either their username OR their email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # The 'username' parameter might contain an email
        try:
            # Check if the user exists with this Username OR Email
            user = UserModel.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            # Edge Case: Extremely rare if constraints are set correctly,
            # but getting the first user prevents a 500 error.
            user = UserModel.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).order_by('id').first()

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
            
    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom custom logic prevents authentication.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None