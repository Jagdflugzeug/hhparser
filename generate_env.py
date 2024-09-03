import os


try:
    from django.core.management.utils import get_random_secret_key
    secret_key = get_random_secret_key()
except ImportError:
    secret_key = 'CHANGE_ME_PLEASE_TO_A_REAL_SECRET_KEY'

pg_db = 'your_database_name'       
pg_username = 'your_database_user'  
pg_password = 'your_database_password' 


env_file_path = '.env'


if not os.path.exists(env_file_path):

    with open(env_file_path, 'w') as env_file:
        env_file.write(f'PG_DB={pg_db}\n')
        env_file.write(f'PG_USERNAME={pg_username}\n')
        env_file.write(f'PG_PASSWORD={pg_password}\n')
        env_file.write(f"DJANGO_SECRET_KEY='{secret_key}'\n")
    print(f'{env_file_path} created')
else:
    print(f'{env_file_path} already exists.')