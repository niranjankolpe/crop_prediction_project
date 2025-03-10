# crop_prediction_ml

Using Waitress and Nginx to start the prpject:
1) Open cmd with virtual env, run "python manage.py collect static"
2) Run "waitress-serve --port=8000 crop_prediction_ml.wsgi.application"
3) In another cmd run "start nginx" to start the server and visit the url "127.0.0.1" to view the web app.

To close the project, close the waitress cmd and in the nginx cmd run "nginx -s stop". Use "nginx -s reload" if any changes are done.