import gettext
import os

# Working directory is already the project directory
try:
    t = gettext.translation('django', localedir='locale', languages=['ru'])
    print('Cabinet:', t.gettext('Cabinet'))
    print('Learning:', t.gettext('Learning'))
    print('Sign In:', t.gettext('Sign In'))
    print('Welcome Back:', t.gettext('Welcome Back'))
    print('About RTK:', t.gettext('About RTK'))
    print('Settings:', t.gettext('Settings'))
    print('Dashboard:', t.gettext('Dashboard'))
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
