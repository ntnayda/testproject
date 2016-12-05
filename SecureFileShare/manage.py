#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SecureFileShare.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

DATABASES = {
    'default': {
       	'ENGINE': 'django.db.backends.sqlite3', #but we are no longer using sqlite
       	'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
 		}
}

if os.environ.get('DATABASE_URL'):
	import dj_database_url
	db_from_env = dj_database_url.config(conn_max_age=500)
	DATABASES['default'].update(db_from_env)