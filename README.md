# Django Project Setup Guide on Windows 11
## 1. Install Python
Check if Python is installed:
    ```bash python --version

If not, download and install it from https://www.python.org/downloads/windows/
Ensure you check 'Add Python to PATH' during installation.
## 2. Create a Virtual Environment
In your project directory:
    ```bash python -m venv venv

This will create a virtual environment in a folder named 'venv'.
## 3. Activate the Virtual Environment
In Command Prompt:
    ```bash venv\Scripts\activate

Your terminal should now show (venv) prefix.
## 4. Install Django and Dependencies
If you have a requirements.txt:
    ```bash pip install -r requirements.txt

Otherwise install manually:
    ```bash pip install django psycopg2
## 5. Configure PostgreSQL
1. Install PostgreSQL from https://www.postgresql.org/download/windows/
2. Create a database and user using pgAdmin or CLI.
3. Update your settings.py DATABASES config:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
## 6. Run Migrations
Run the following commands:
    ```bash python manage.py makemigrations
    ```bash python manage.py migrate
## 7. Create Superuser
Run:
    ```bash python manage.py createsuperuser
Follow the prompts to create an admin user.
## 8. Run the Development Server
Start the server:
    ```bash python manage.py runserver
Then visit http://127.0.0.1:8000/ in your browser.
## 9. Access Admin
Visit http://127.0.0.1:8000/admin/ and login with your superuser credentials.
## 10. Notes
- Reactivate venv every terminal session
- Use a .env file for sensitive settings (optional)
- Use 'collectstatic' for static files in production
