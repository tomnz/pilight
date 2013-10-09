PiLight
=======

Flexible LED controller designed to run on a Raspberry Pi, and drive WS2801 LED strings. Has a Django web-based interface for access anywhere.


Installation
------------

Install all prerequisites first:

* [Python](http://www.python.org/download/) - 2.7 recommended
* Database software - [PostgreSQL](http://www.postgresql.org/download/) recommended
* [RabbitMQ](http://www.rabbitmq.com/download.html) (requires [Erlang](http://www.erlang.org/download.html))
* [pip](https://pypi.python.org/pypi/pip/) strongly recommended to install extra Python dependencies

Download the source to a desired location:

    hg pull https://bitbucket.org/tomnz/pilight

Install the Python dependencies:

    pip install -r requirements.txt

Create a new database in your DBMS (e.g. PostgreSQL) to use for PiLight.

Copy the settings file and make required changes (particularly set up your light parameters, and database instance):

    cp pilight/pilight/settings.py.default pilight/pilight/settings.py

(Be sure to edit your new settings.py file).

Setup the database:

    python manage.py syncdb
    python manage.py migrate
    python manage.py loaddata fixtures\initial_data.json


Launch PiLight
--------------

Once you've gone through all the installation steps, you're ready to run PiLight!

First, ensure that RabbitMQ and your DBMS are running. Then, run the following commands in separate console windows (or use screen):

    python manage.py lightdriver

And

    python manage.py runserver

> Note:
> 
> `lightdriver` and `runserver` are both blocking commands that run until stopped.

That's it! You should now be able to access the interface to control the lights by accessing http://localhost:8000/