import os
import ldap
from django_auth_ldap.config import LDAPSearch
from prod2app.settings.base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'dev'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'USER': os.environ.get('POSTGRES_USER', 'root'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'test')
    }
}

AUTHENTICATION_BACKENDS = [
    # Uncomment the line below to enable LDAP authentication
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend"]

AUTH_LDAP_SERVER_URI = os.environ.get('PROD2LAB_LDAP_SERVER_URI', None)
AUTH_LDAP_BIND_DN = os.environ.get('PROD2LAB_LDAP_SERVER_USERNAME', None)
AUTH_LDAP_BIND_PASSWORD = os.environ.get('PROD2LAB_LDAP_SERVER_PASSWORD', None)
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    os.environ.get('PROD2LAB_LDAP_SERVER_SEARCH', None),
    ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
)
