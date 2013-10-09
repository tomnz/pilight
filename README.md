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

> Note: Be sure to edit your new settings.py file!

Setup the database:

    python manage.py syncdb
    python manage.py migrate
    python manage.py loaddata fixtures/initial_data.json


Launch PiLight
--------------

Once you've gone through all the installation steps, you're ready to run PiLight!

First, ensure that RabbitMQ and your DBMS are running. Then, run the following commands in separate console windows (or use screen):

    python manage.py lightdriver

And

    python manage.py runserver

> Note: `lightdriver` and `runserver` are both blocking commands that run until stopped, which is why they must be in separate console windows. `lightdriver` performs the actual running of the lights, and `runserver` serves the configuration UI.

That's it! You should now be able to access the interface to control the lights by accessing [http://localhost:8000/](http://localhost:8000/).


Guide
-----

PiLight is designed around a simple "Colors" + "Transformations" system. You specify both parts in the configuration interface.

* Colors define the "initial" or "base" states for each individual LED. Using the PiLight interface, you can "paint" colors onto the LEDs. Specify a tool (solid/smooth), tool radius and opacity, and a color. Then, click individual lights to start painting. The lights will refresh after each click.
* Transformations get applied in real time when the light driver is running. They modify the base colors based on a variety of input parameters, and usually a "time" component. Typically they will produce an animation effect, such as flashing or scrolling. Transformations can be added to a "active" stack. Each transformation is applied in sequence, for each "frame" that gets sent to the LEDs. Multiple transformations of the same type can be stacked; for example, to have a slow flash, with faster small fluctuations.

Changes in the configuration interface are instantly sent to the light driver if it's running. You can also use the buttons at the top right to control the driver:

* Refresh will force the light driver to reload its configuration (if it's running), as well as refresh the configuration page for any changes
* Start will start the light driver
* Stop will stop the light driver