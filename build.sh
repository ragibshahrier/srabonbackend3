# #!/usr/bin/env bash
# # exit on error
# set -o errexit

# pip install -r requirements.txt

# python manage.py collectstatic --no-input
# python manage.py migrate
# if [[ $CREATE_SUPERUSER ]];
# then
#   python manage.py createsuperuser --no-input --email "$DJANGO_SUPERUSER_EMAIL"
# fi



#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py makemigrations --no-input
python manage.py migrate --no-input

# Create superuser only if required variables are set
if [[ $CREATE_SUPERUSER == "true" ]]; then
  echo "Creating superuser..."
  python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email="${DJANGO_SUPERUSER_EMAIL}").exists():
    User.objects.create_superuser(
        username="${DJANGO_SUPERUSER_USERNAME}",
        email="${DJANGO_SUPERUSER_EMAIL}",
        password="${DJANGO_SUPERUSER_PASSWORD}"
    )
EOF
fi
