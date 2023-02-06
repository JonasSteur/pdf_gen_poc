from django_auth_ldap.config import LDAPGroupQuery, LDAPSearch, NestedGroupOfNamesType
from environ import Env
from ldap import SCOPE_SUBTREE

env = Env(
    DEBUG=(bool, False),
)

# The order of these backends is important. `ModelBackend` should come before `OAuthBackend`
# otherwise a custom oauthlib.Request is passed twice through the OAuth2Backend causing errors
# since a recent fix in oauth2_provider.oauth2_validators.OAuth2Validator.validate_user commit: d5e6645184
AUTHENTICATION_BACKENDS = env.tuple(
    'AUTHENTICATION_BACKENDS',
    default=(
        'django.contrib.auth.backends.ModelBackend',
        'oauth2_provider.backends.OAuth2Backend',
        'django_auth_ldap.backend.LDAPBackend',  # admin users: Unleashed staff
    ),
)

AUTH_LDAP_SERVER_URI = 'ldap://ldap.internal.unleashed.be'
AUTH_LDAP_BIND_DN = ''
AUTH_LDAP_BIND_PASSWORD = ''

AUTH_LDAP_USER_SEARCH = LDAPSearch(
    'ou=Users,dc=unleashed,dc=loc',
    SCOPE_SUBTREE,
    '(uid=%(user)s)',
)

AUTH_LDAP_GROUP_SEARCH = LDAPSearch('ou=Groups,dc=unleashed,dc=loc', SCOPE_SUBTREE, '(objectClass=groupOfNames)')

AUTH_LDAP_GROUP_TYPE = NestedGroupOfNamesType(name_attr='cn')
AUTH_LDAP_DENY_GROUP = None

AUTH_LDAP_USER_ATTR_MAP = {
    'username': 'uid',
    'external_id': 'uid',
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mail',
}

AUTH_LDAP_FIND_GROUP_PERMS = False
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

if env('DJANGO_CONFIG_CONTEXT', default='dev') == 'production':
    AUTH_LDAP_USER_FLAGS_BY_GROUP = {
        'is_active': (
            LDAPGroupQuery('cn=allow_pdf_gen_poc_admin,ou=Groups,dc=unleashed,dc=loc')
            | LDAPGroupQuery('cn=allow_django_superuser,ou=Groups,dc=unleashed,dc=loc')
        ),
        'is_staff': (
            LDAPGroupQuery('cn=allow_pdf_gen_poc_admin,ou=Groups,dc=unleashed,dc=loc')
            | LDAPGroupQuery('cn=allow_django_superuser,ou=Groups,dc=unleashed,dc=loc')
        ),
        'is_superuser': LDAPGroupQuery('cn=allow_django_superuser,ou=Groups,dc=unleashed,dc=loc'),
    }
else:
    AUTH_LDAP_USER_FLAGS_BY_GROUP = {
        'is_active': (
            LDAPGroupQuery('cn=allow_pdf_gen_poc_admin,ou=Groups,dc=unleashed,dc=loc')
            | LDAPGroupQuery('cn=allow_testing_django_admin,ou=Groups,dc=unleashed,dc=loc')
        ),
        'is_staff': (
            LDAPGroupQuery('cn=allow_pdf_gen_poc_admin,ou=Groups,dc=unleashed,dc=loc')
            | LDAPGroupQuery('cn=allow_testing_django_admin,ou=Groups,dc=unleashed,dc=loc')
        ),
        'is_superuser': (
            LDAPGroupQuery('cn=allow_pdf_gen_poc_admin,ou=Groups,dc=unleashed,dc=loc')
            | LDAPGroupQuery('cn=allow_testing_django_admin,ou=Groups,dc=unleashed,dc=loc')
        ),
    }

AUTH_LDAP_MIRROR_GROUPS = True
