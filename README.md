PiLight
=======

Flexible LED controller designed to run on a Raspberry Pi, and drive WS2801 LED strings. Has a Django web-based interface for access anywhere.

Although it is more work to set up (and completely optional), PiLight is designed to be run in a server/client configuration - with a powerful server driving the configuration interface, and computing color data to send to the LEDs; and a lightweight client script running on the Raspberry Pi. See the Client/Server section below for more details.

For more information, check out the following sources:

* [Blog post](http://tom.net.nz/2013/10/pilight/) detailing hardware and installation of PiLight
* [Demo video](http://www.youtube.com/watch?v=ohJMUAsssQw) showing the PiLight interface and lights running


Client/Server
-------------

The instructions below describe the configuration of a "standalone" installation of PiLight, such as onto a Raspberry Pi. While the Raspberry Pi is perfectly capable of running the PiLight configuration interface, and producing color data for the LEDs, its processor can sometimes struggle with the workload, reducing "framerate" to <10 updates per second.

For high-performance installations running complex animations, it's recommended to run PiLight on a more powerful server computer, and use the lightweight [PiLight Client](https://bitbucket.org/tomnz/pilight-client) as the only software running on the Raspberry Pi. If you intend to use this configuration, then pay attention to the following differences in installation:

* Install PiLight (as per the instructions below) onto your intended server computer
* Install [PiLight Client](https://bitbucket.org/tomnz/pilight-client) onto the Raspberry Pi, according to the instructions on that page
* Do NOT install the full PiLight software onto your Raspberry Pi
* In the PiLight `settings.py` file, set `LIGHTS_DRIVER_MODE` to `'server'`
* Make sure to open your RabbitMQ port (usually 5672) on your server computer, so that the Raspberry Pi can access it
* You still need to run the `lightdriver` command on your server computer - this will now output to the RabbitMQ queue for the client to pick up, instead of directly to the LEDs


Installation
------------

Install all prerequisites first:

* [Python](http://www.python.org/download/) - 2.7 recommended
* Database software - [PostgreSQL](http://www.postgresql.org/download/) recommended
* [RabbitMQ](http://www.rabbitmq.com/download.html) (requires [Erlang](http://www.erlang.org/download.html))
* [pip](https://pypi.python.org/pypi/pip/) strongly recommended to install extra Python dependencies

> Note: These instructions assume you're using a Raspberry Pi with Occidentalis for the most part - omit sudo if your flavor doesn't use it, for example. This is all tested working with a 512MB Raspberry Pi device, and Occidentalis v0.2.

Download the source to a desired location:

    hg clone https://bitbucket.org/tomnz/pilight

Install the Python dependencies:

    cd pilight
    sudo pip install -r requirements.txt

> Note: If you get an error message about available space on the device, it's likely your /tmp folder is too small. Run `sudo nano /etc/default/tmpfs`, change TMP_SIZE to 200M, then try `pip install -r requirements.txt` again. You may run into this when installing on a Raspberry Pi device.

> Note: If setting up a server installation on Windows, with PostgreSQL, you may find it easier to install the `psycopg2` package from a binary installer instead of with pip. [Download the binary](http://www.stickpeople.com/projects/python/win-psycopg/) corresponding to your Python/PostgreSQL version.

Create a new database in your DBMS (e.g. PostgreSQL) to use for PiLight.

Copy the settings file and make required changes (particularly set up your light parameters, and database instance):

    cd pilight
    cp pilight/settings.py.default pilight/settings.py

> Note: Be sure to edit your new `settings.py` file!

Setup the database:

    python manage.py syncdb
    python manage.py migrate
    python manage.py loaddata fixtures/initial_data.json
    python manage.py createcachetable pilight_cache


Launch PiLight
--------------

Once you've gone through all the installation steps, you're ready to run PiLight!

First, ensure that RabbitMQ and your DBMS are running. Then, run the following commands in separate console windows (or use `screen`):

    sudo python manage.py lightdriver

And

    python manage.py runserver 0.0.0.0:8000

> Note: `lightdriver` and `runserver` are both blocking commands that run until stopped, which is why they must be in separate console windows. We bind `runserver` to 0.0.0.0:8000 so that it can be accessed from other devices on the network, not just localhost. This is useful for controlling PiLight from your phone or computer.

That's it! You should now be able to access the interface to control the lights by accessing [http://localhost:8000/](http://localhost:8000/).


Guide
-----

### Introduction

PiLight is designed around a simple "Colors" + "Transformations" system. You specify both parts in the configuration interface.

* Colors define the "initial" or "base" states for each individual LED. Using the PiLight interface, you can "paint" colors onto the LEDs. Specify a tool (solid/smooth), tool radius and opacity, and a color. Then, click individual lights to start painting. The lights will refresh after each click.
* Transformations get applied in real time when the light driver is running. They modify the base colors based on a variety of input parameters, and usually a "time" component. Typically they will produce an animation effect, such as flashing or scrolling. Transformations can be added to the "active" stack. Each transformation is applied in sequence, for each "frame" that gets sent to the LEDs. Multiple transformations of the same type can be stacked; for example, to have a slow flash, with faster small fluctuations.

> Note: Currently parameters for transforms are not editable via nice controls. However, when adding a transform, sensible defaults will be applied, and you can edit the parameter string by hand. This should be fairly self-explanatory.

You can view a 10-second preview of what the lights will look like after animations are applied (animated in-browser) by hitting the Preview button.

### Running the light driver

Changes in the configuration interface are instantly sent to the light driver if it's currently running. You can also use the buttons at the top right to control the driver:

* Refresh will force the light driver to reload its configuration (if it's started), as well as refresh the configuration page for any changes
* Start will start the light driver so that it powers the lights and runs transforms
* Stop will stop the light driver and power off the lights - then await a new Start command

> Note: These buttons all have no effect if the driver is not running. Remember to start it with `python manage.py lightdriver`.

### Loading and saving

You can save the current configuration by typing a name in the text box at top right, and hitting Save. You can also load past configurations with the Load button.

> Note: If you load a configuration, changes you make are NOT automatically saved back to that configuration. Make sure you hit Save again when you're done. This will overwrite previous settings, if a configuration already exists with the same name.


Updating
--------

Periodically you may want to update PiLight to get the latest features and bug fixes. Just run the following commands from the `pilight/pilight` directory:

    hg pull
    hg update
    python manage.py syncdb
    python manage.py migrate
    python manage.py loaddata fixtures/initial_data.json