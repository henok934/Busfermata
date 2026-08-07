from django.apps import AppConfig
from django.db.utils import OperationalError
from django.db.models.signals import post_migrate

class YourAppConfig(AppConfig):
    name = 'users'

    def ready(self):
        # We connect the signal to run after migrations are done
        post_migrate.connect(create_default_user, sender=self)




def create_default_user(sender, **kwargs):
    from .models import CustomUser
    try:
        if not CustomUser.objects.filter(username='henok').exists():
            # We use first_name and last_name (Django defaults)
            # instead of fname and lname
            CustomUser.objects.create_superuser(
                username='henok',
                email='henok@example.com',
                password='Super_admin@934',
                phone='0934567890',
                first_name='Henok',
                last_name='Mossie',
                city='Addis Ababa',

                # ---- ነባሪ የክፍያ አካውንት መረጃዎች ----
                cbe_account='1000123456789',        # የኢትዮጵያ ንግድ ባንክ አካውንት ቁጥር
                telebirr_account='0934567890',      # የቴሌብር ቁጥር (ብዙውን ጊዜ ከስልክ ቁጥር ጋር አንድ ነው)
                boa_account='45678912',             # የአቢሲኒያ ባንክ አካውንት ቁጥር
            )
            print("--- Default Superuser 'henok' with Payment Accounts created successfully ---")
    except Exception as e:
        print(f"--- Note: Admin auto-creation skipped: {e} ---")


