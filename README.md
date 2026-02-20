# Crop Prediction using Machine Learning

## Project Installation:
### Setting the system environment variables:
1) Using a Google Account create an App Password as: "Manage your Google Account" -> Search "App passwords" in the search bar -> Enter a name for you app and click "Create" and note down the password by removing the in between spaces. This password is confidential and should not be shared with anyone.
2) Rename the "set_sys_env_vars.cmd.example" file to "set_sys_env_vars.cmd" and fill the values inside. Open Command Prompt (cmd) in root folder where the file is placed and run "set_sys_env_vars.cmd"
Other operating systems might have a different procedure to store environment variables.

### Dependencies Configuration
1) Install Python 3.14.2. Then pull the remote repository to your local machine.
2) Open a command prompt (cmd) in root folder and make a new python virtual environment using command "python -m venv venv".
3) Use command "venv\Scripts\activate" to activate the virtual environment. Use the command "venv\Scripts\deactivate" to deactivate the virtual environment.
4) Run "pip install -r requirements.txt" to install dependencies.

### Nginx Server Configuration:
1) Install nginx zip file from https://nginx.org/en/download.html.
2) Extract the folder, place in root folder and name the nginx folder as "Server".
3) Replace the placeholder values in the nginx.conf.example file and rename to nginx.conf.
4) Now, replace the Server -> conf -> nginx.conf file with the new file.
5) Tip: Ensure that the paths use the "/" and not "\". Also ensure "/" at the end of the paths. Example: "C:/PATH/TO/Crop Prediction/Django App/static_root/"

### PostgreSQL Configuration:
1) Install PostgreSQL from https://www.postgresql.org/download/.
2) In the init.sql.example file in root folder, replace placeholder values with your values.
3) Run the sql queries in pgAdmin or alternative approches as available in PostgresSQL to create a user and database. Ensure the environment variables are set accordingly.

## Project Run:
1) In the Django app folder, open cmd with virtual env, run "python manage.py makemigrations", "python manage.py migrate" and "python manage.py collectstatic" consecutively. Create a superuser (administrator) using the commands "python manage.py createsuperuser" and enter the prompted values of your choice. Now run "python manage.py runserver". These commands are only required for first time run. From next time onwards just run "python manage.py runserver". For any change in static files, run "python manage.py collectstatic".
2) In the Server folder open a cmd with virtual environment and change path to the nginx folder (named as "Server"). Run "start nginx" to start the server.
3) Visit the url "127.0.0.1" to view the web app.

To close the project, close the Ctrl + C the python cmd and in the nginx cmd run "nginx -s stop". Use "nginx -s reload" if any code changes have been implemented.


# Render Deployment Instructions:
### Pre-Git commit:
1) Required libraries: gunicorn, whitenoise. For PostgreSQL Database: psycopg2-binary
2) Add "whitenoise.middleware.WhiteNoiseMiddleware" to the list of middlewares in settings.py
3) Add "your-app-name.onrender.com" to the list of allowed hosts only if you know the full domain name. Else add "*" for temporary basis. Then replace with your full render domain name in the next code commit.
4) Add -> STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' in settings.py
5) Test your local project using "gunicorn yourprojectname.wsgi:application" (Remember to replace yourprojectname) before commit and deployment. 
6) If using PostgresSQL, create a PostgresSQL DB instance on Render.
7) Ensure the project has code set to use environment variables to retrieve sensitive data like Database credentials, etc.
8) Make a new git commit and push to remote repository.

### Post-Git commit:
1) Create PostgreSQL DB Instance.
2) Create New Web Service in the same region as your DB instance. Connect your GitHub repository. Select the branch to deploy (main).
3) Select Language: Python 3. Set Root Directory appropriately. Root Directory is the folder which contains manage.py file. Enter Build Command as follows:
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
4) Set the Start Command as follows (Remember to replace yourprojectname):
gunicorn yourprojectname.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 2
5) Set the required Environment Variables.
6) Save/Submit and monitor the Logs. Upon successfull deployment, a link will be available for accessing the deployed project.
Any errors encountered need to be fixed in the code and new commits new to be pushed to remote repo for Render to auto-detect and auto-redeploy the new commits. Also monitor environment varibles or Build/Start commands if relevant to the error encountered (if any).