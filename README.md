# crop_prediction_ml

Setting the system environment variables:
1) Using a Google Account create an App Password as: "Manage your Google Account" -> Search "App passwords" in the search bar -> Enter a name for you app and click "Create" and note down the password by removing the in between spaces. This password is confidential and should not be shared with anyone.
2) On local computer taskbar, search "Edit the system environment variables". Click the "Environment Variables..." button and in he "System variables" section, click "New" and enter the following variable name and their respective values. Click "Ok" after filling a variable name and variable value pair. Similarly add the rest variable names and values.
Variable name: Variable value ->
[DJANGO_EMAIL_HOST: smtp.gmail.com,
DJANGO_EMAIL_PORT: 587,
DJANGO_EMAIL_HOST_USER: <YOUR_EMAIL_ADDRESS>,
EMAIL_HOST_PASSWORD, <YOUR_PASSWORD_SAVED_EARLIER>].
Other operating systems may have a different procedure to store environment variables.

Project Installation:
Requires pre-installed Python 3.14.2
1) Pull the remote repository to your local machine.
2) Open a command prompt (cmd) in root folder and make a new python virtual environment using command "python -m venv venv".
3) Use command "venv\Scripts\activate" to activate the virtual environment. Use the command "venv\Scripts\deactivate" to deactivate the virtual environment.
4) Run "pip install -r requirements.txt" to install dependencies.
5) Install nginx zip file from https://nginx.org/en/download.html. Extract the folder, place in root folder and name the nginx folder as "Server". In the Server -> conf -> nginx.conf file, modify the location-static and location-media paths with the absolute folder paths of the "static_root" and "media_root" folders present in project root folder. Ensure that the paths use the "/" and not "\". Also ensure "/" at the end of the paths. Example: "C:/My Files/Crop Prediction/Django App/static_root/"

Project Run:
1) In the Django app folder, open cmd with virtual env, run "python manage.py makemigrations", "python manage.py migrate" and "python manage.py collectstatic" consecutively. Create a superuser (administrator) using the commands "python manage.py createsuperuser" and enter the prompted values of your choice. Now run "python manage.py runserver". These commands are only required for first time run. From next time onwards just run "python manage.py runserver". For any change in static files, run "python manage.py collectstatic".
2) In the Server folder open a cmd with virtual environment and change path to the nginx folder (named as "Server"). Run "start nginx" to start the server.
3) Visit the url "127.0.0.1" to view the web app.

To close the project, close the Ctrl + C the python cmd and in the nginx cmd run "nginx -s stop". Use "nginx -s reload" if any code changes have been implemented.