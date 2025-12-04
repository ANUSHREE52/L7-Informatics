# Create a new Django project
django-admin startproject expense_tracker .

# Create the expenses app
python manage.py startapp expenses

# Create necessary directories
New-Item -ItemType Directory -Force -Path "expenses/templates/expenses"
New-Item -ItemType Directory -Force -Path "expenses/static/expenses"
New-Item -ItemType Directory -Force -Path "expenses/static/expenses/css"
New-Item -ItemType Directory -Force -Path "expenses/static/expenses/js"

Write-Host "Project setup complete. Next steps:"
Write-Host "1. Run 'python manage.py migrate' to create the database"
Write-Host "2. Run 'python manage.py createsuperuser' to create an admin user"
Write-Host "3. Run 'python manage.py runserver' to start the development server"
