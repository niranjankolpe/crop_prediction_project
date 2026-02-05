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
