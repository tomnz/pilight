PiLight
=======

Flexible LED controller designed to run on a Raspberry Pi, and drive LED strings. Has a Django + React web-based interface for access anywhere and easy configuration. For more information, check out the following sources:

* [Blog post](http://tom.net.nz/2013/10/pilight/) detailing hardware and installation of PiLight
* [Demo video](http://www.youtube.com/watch?v=ohJMUAsssQw) showing the PiLight interface and lights running

The software is tested compatible with most versions of the Raspberry Pi (A/B/2/3) - but this is a rich application that will take full use of available hardware - so a Pi 3 is recommended!


Client/Server
-------------

The instructions below describe the configuration of a "standalone" installation of PiLight, such as onto a Raspberry Pi. While the Raspberry Pi is perfectly capable of running the PiLight configuration interface, and producing color data for the LEDs, its processor can sometimes struggle with the workload, reducing "framerate" to <10 updates per second.

For high-performance installations running complex animations, it's recommended to run PiLight on a more powerful server computer, and use the lightweight [PiLight Client](https://bitbucket.org/tomnz/pilight-client) as the only software running on the Raspberry Pi. Note that this is more work to set up, and completely optional.

If you intend to use this configuration, then pay attention to the following differences in installation:

* Install PiLight (as per the instructions below) onto your intended server computer
* Install [PiLight Client](https://bitbucket.org/tomnz/pilight-client) onto the Raspberry Pi, according to the instructions on that page
* Do NOT install the full PiLight software onto your Raspberry Pi
* In the PiLight `settings.py` file, set `LIGHTS_DEVICE` to `'client'`
* Make sure to open your RabbitMQ port (usually 5672) on your server computer, so that the Raspberry Pi can access it
* You still need to run the `lightdriver` command on your server computer - this will now output to the RabbitMQ queue for the client to pick up, instead of directly to the LEDs


Installation
------------

Install all prerequisites first:

* [Python](http://www.python.org/download/) - 2.7 recommended
* Database software - [PostgreSQL](http://www.postgresql.org/download/) recommended
* [RabbitMQ](http://www.rabbitmq.com/download.html) (requires [Erlang](http://www.erlang.org/download.html))
* [pip](https://pypi.python.org/pypi/pip/) strongly recommended to install extra Python dependencies

Install deps:

    sudo apt-get install python python-pip python-dev git \
            postgresql rabbitmq-server python-pyaudio \
            python-numpy alsa-utils

> Note: These instructions assume you're using a Raspberry Pi with Raspbian for the most part - omit sudo if your flavor doesn't use it, for example.

You'll also need to install `postgresql-server-dev-9.x`, with the specific version corresponding to your PostgreSQL install (use `psql -v`).

Download the source to a desired location:

    git clone https://github.com/TomNZ/pilight.git

Install the Python dependencies:

    cd pilight
    sudo pip install -r requirements.txt

> Note: If you get an error message about available space on the device, it's likely that your /tmp folder is too small. Run `sudo nano /etc/default/tmpfs`, change TMP_SIZE to 200M, then try `pip install -r requirements.txt` again. You may run into this when installing on an older Raspberry Pi device.

> Note: If setting up a server installation on Windows, with PostgreSQL, you may find it easier to install the `psycopg2` package from a binary installer instead of with pip. [Download the binary](http://www.stickpeople.com/projects/python/win-psycopg/) corresponding to your Python/PostgreSQL version.

Create a new database in your DBMS (e.g. PostgreSQL) to use for PiLight. These commands will give you a basic functional setup:

    # Create a new user/password - you'll need to enter it in settings later
    sudo -u postgres createuser pilight --pwprompt
    sudo -u postgres createdb pilight --owner pilight

Copy the settings file and make required changes.

    cd pilight
    cp pilight/settings.py.default pilight/settings.py

> Note: Be sure to edit your new `settings.py` file!

* Configure your output device, light parameters, and database instance.
* Turn on audio var or ADC support if you need it.
* Django has a [security feature](https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts) where you must pre-specify all hosts that a given server expects to be accessed as. You should populate the `ALLOWED_HOSTS` setting according to the hostname that you gave your Pi. For example: `ALLOWED_HOSTS = ['raspberrypi.local']`.

Follow the sections below to set up corresponding prerequisites for your selected inputs and LED strip type.

Setup the database:

    python manage.py migrate
    python manage.py createcachetable pilight_cache

Now you're ready to run! Head to the Launch section below.


Lights
------

Depending on the type of LED you are trying to drive, you will need to install a helper library so that PiLight is able to talk to your lights. Follow the directions for your given driver type:

### WS2801

Driving this chip requires a SPI device. The SPI driver is disabled by default on Raspbian, so you'll need to [enable it](https://www.raspberrypi.org/documentation/hardware/raspberrypi/spi/README.md).

Install Adafruit's library:

    pip install adafruit-ws2801

Install Adafruit's GPIO driver (for SPI support) using [their instructions](https://github.com/adafruit/Adafruit_Python_GPIO).

In `settings.py`, change `LIGHTS_MICROCONTROLLER` to `ws2801`. Configure any other related settings for WS2801.


### WS281x (NeoPixel)

Follow [Adafruit's instructions](https://learn.adafruit.com/neopixels-on-raspberry-pi/software) to build and install the Python library.

In `settings.py`, change `LIGHTS_MICROCONTROLLER` to `ws281x`. Configure any other related settings for WS281x.


Launch PiLight
--------------

Once you've gone through all the installation steps, you're ready to run PiLight!

First, ensure that RabbitMQ and your DBMS are running. Then, run the following commands in separate console windows (or use `screen`):

    sudo python manage.py lightdriver

And

    python manage.py runserver --noreload 0.0.0.0:8000

> Note: `lightdriver` and `runserver` are both blocking commands that run until stopped, which is why they must be in separate console windows. We bind `runserver` to 0.0.0.0:8000 so that it can be accessed from other devices on the network, not just localhost. This is useful for controlling PiLight from your phone or computer. `--noreload` reduces CPU usage by the web service significantly when idle. This is especially important when running in standalone mode.

That's it! You should now be able to access the interface to control the lights by accessing [http://localhost:8000/](http://localhost:8000/).


Starting Automatically
----------------------

If running PiLight from a Raspberry Pi, it may be beneficial to have the server and light driver start automatically when the device boots. This saves having to connect a keyboard or SSH to your Pi whenever the power cycles. It's suggested that you do this by using `screen`.

    sudo apt-get install screen

Then, open your screen config:

    nano ~/.screenrc

Suggested config to use (important piece commented):

    startup_message off
    vbell off
    escape /
    defscrollback 5000
    hardstatus alwayslastline
    hardstatus string '%{= kG}%-Lw%{= kW}%50> %n*%f %t%{= kG}%+Lw%< %{= kG}%-=%D %m/%d/%y | %C:%s %A'

    chdir $HOME
    screen -t shell 0 bash
    screen -t shell 1 bash

    # Crucial tabs:
    chdir $HOME/pilight/pilight
    # --insecure is important if Django's DEBUG is set to False - allows serving static files
    screen -t pl 2 bash -c 'python manage.py runserver --noreload --insecure 0.0.0.0:8000; exec bash'
    screen -t pl-driver 3 bash -c 'sudo python manage.py lightdriver; exec bash'

    chdir $HOME
    select 0

This will open two extra tabs (2+3) for PiLight on startup - one for the web interface, and one for the light driver. The final step is to have screen run at startup. There are a few ways to do this, but crontab is likely the simplest. Run `crontab -e`, then enter a line like the following:

    @reboot sleep 15 && screen -d -m -A

This will open screen in a detached mode on startup. The delay is necessary due to other services starting up (you may need to increase it). If you SSH into the Pi later, you can view the opened processes by running `screen -R`. Navigate screens by Ctrl+A then the screen id (0 through 3 in the above example). To detach screen again, use Ctrl+A then Ctrl+D.


Usage Guide
-----------

### Introduction

PiLight is designed around a simple "Colors" + "Transforms" system. You specify both parts in the configuration interface.

* Colors define the "initial" or "base" states for each individual LED. Using the PiLight interface, you can "paint" colors onto the LEDs. Specify a tool (solid/smooth), tool radius and opacity, and a color. Then, click individual lights to start painting. The lights will refresh after each click.
* Transforms get applied in real time when the light driver is running. They modify the base colors based on a variety of input parameters, and usually a "time" component. Typically they will produce an animation effect, such as flashing or scrolling. Transforms can be added to the "active" stack. Each transform is applied in sequence, for each "frame" that gets sent to the LEDs. Multiple transforms of the same type can be stacked; for example, to have a slow flash, with faster small fluctuations. The order that transforms are applied in is important, so try moving them up and down to achieve different effects.
* Some transforms operate as "layers", and can be used to insert colors that are different to the "base" colors. Use blend mode and opacity to combine these layers with other effects.

You can view a 10-second preview of what the lights will look like after animations are applied (animated in-browser) by hitting the Preview button.

### Variables

In order to make the behavior more dynamic, you can introduce "Variables". These are designed to take external inputs and allow them to affect transforms. For example, you can hook up a microphone, and get a variable that tracks bass levels in a song. Or hook up an ADC and use a potentiometer to physically manipulate a value. Or use an API call to modify a color parameter dynamically.

To use a variable, you first need to add it. Then adjust its parameters as you see fit. Then, you have the ability to select the checkbox beside any compatible transform parameter, and select your new variable from the dropdown. If you have multiple variables of the same type (e.g. two ADC inputs), you can give them meaningful names.

See below for more details on configuring the Audio variable and ADC.

### Running the light driver

Changes in the configuration interface are instantly sent to the light driver if it's currently running. You can also use the buttons at the top right to control the driver:

* Start will start the light driver so that it powers the lights and runs transforms
* Stop will stop the light driver and power off the lights - then await a new Start command

> Note: These buttons all have no effect if the driver is not running. Remember to start it with `python manage.py lightdriver`.

> Note: There may be a slight delay between hitting Stop and the lights actually turning off. This is normal. The light driver polls for commands infrequently (this can be changed in the settings).

### Loading and saving

You can save the current configuration by typing a name in the text box at top right, and hitting Save. You can also load past configurations with the Load button.

> Note: If you load a configuration, changes you make are NOT automatically saved back to that configuration. Make sure you hit Save again when you're done. This will overwrite previous settings, if a configuration already exists with the same name.


Updating
--------

Periodically you may want to update PiLight to get the latest features and bug fixes. Just run the following commands from the `pilight/pilight` directory:

    git pull
    python manage.py migrate


Audio
-----

PiLight has builtin support for audio reactivity based on a microphone input. This is designed to pick up bass frequencies from music. It will adapt to volume changes over time, so shouldn't require any specific tweaking. To enable it:

* Set `ENABLE_AUDIO_VAR` to `True` in your settings.
* Use the interface to connect the Audio variable to transform parameters. Recommended examples are brightness, or the strength component of a Crush Color transform.

> Note: You may experience some difficulties getting the microphone to be picked up correctly. Ensure you have set the given microphone as the default input source in both alsa and PulseAudio. For WS281X strips, you may also need to disable the onboard audio as per [the instructions](https://github.com/jgarff/rpi_ws281x#limitations). Finally, you may want to enable PulseAudio to run on startup - check out [this article](http://serendipity.ruwenzori.net/index.php/2015/06/01/sending-an-audio-stream-across-the-network-to-a-remote-raspberry-pi-with-pulseaudio-the-easy-way).

> Note: There is some performance impact to using the audio variable, since it needs to continually recompute FFTs. This is partially mitigated by running the processing on a separate CPU core, but for very high frame rates it may become a limiting factor. Ensure you're using a Pi 2/3, which have 4 cores available.


ADC
---

Similar to the Audio variable, you can configure an Analog-to-Digital Converter (ADC) to use as an analog input device. The suggested IC is an MPC3008 (available from [Adafruit](https://www.adafruit.com/product/856)).

Install Adafruit's MCP3008 library:

    sudo pip install adafruit-mcp3008

Enable the MPC3008 variable in your `settings.py`.


Development
-----------

PiLight uses Django for the driver backend and API, and Webpack/React for the frontend. When running the server in standalone mode, you do not need to install any Node/Webpack/React deps, since the precompiled app bundle is checked in, and can be served independently by Django.

However, if you wish to develop the PiLight frontend, you'll need to set those dependencies up.

* Install Node as appropriate for your system.
* It's recommended to use `yarn` instead of `npm` (although this is really up to personal preference).
* From the `pilight` directory, run:
* `yarn install` to install all of the relevant Node packages.
* `yarn run` to run the development server. This will automatically forward API calls to `localhost:8000`, so ensure Django is also running.
* When you're ready to check in changes, make sure to re-generate the frontend bundle for Django: `yarn build`
