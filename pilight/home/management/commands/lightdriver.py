from django.conf import settings
from pilight.driver import LightDriver
from django.core.management.base import BaseCommand
from django.core.cache import cache
from optparse import make_option
import traceback
import sys


# How long to wait to expire an old lock
# Set to a day by default
LOCK_EXPIRE = 60 * 60 * 24


# Boilerplate to launch the light driver as a Django command
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--force-run',
            action='store_true',
            dest='force_run',
            default=False,
            help="Forces the light driver to run, even if there appears to be another instance. Useful if " +
                 "the last driver exited unexpectedly and didn't clear the running flag",
        ),
        make_option(
            '--clear-lock',
            action='store_true',
            dest='clear_lock',
            default=False,
            help="Forces clearing of the flag indicating that another driver is running. Only use if you are " +
                 "sure that another instance of the driver is not running. This should never be necessary. Does " +
                 "not actually run the driver.",
        ),
    )

    help = 'Starts the light driver to await commands'

    def handle(self, *args, **options):
        lock_id = 'light-driver-running'

        if options['clear_lock']:
            # This is a "last ditch" utility function to clear the running flag
            # Return immediately afterwards
            cache.delete(lock_id)
            return

        # Perform locking - can we even run right now?
        acquire_lock = lambda: cache.add(lock_id, 'true', LOCK_EXPIRE)
        release_lock = lambda: cache.delete(lock_id)

        got_lock = acquire_lock()
        if got_lock or options['force_run']:
            # Setup the output device
            spidev = None
            if not settings.LIGHTS_NOOP:
                try:
                    spidev = file(settings.LIGHTS_DEV_NAME, 'wb')
                except:
                    # Ugly catch-all...
                    print 'Exception opening SPI device!'
                    traceback.print_exc(file=sys.stdout)
                    return

            driver = LightDriver()
            try:
                # Run the actual driver loop
                driver.wait(spidev)
            except KeyboardInterrupt:
                # The user has interrupted execution - close our resources
                print '* Cleaning up...'
                pass
            except:
                # The catch-all here is bad, but manage.py commands usually don't print
                # a stack trace, which is not very helpful for finding bugs
                print 'Exception while running light driver!'
                traceback.print_exc(file=sys.stdout)
            finally:
                # Clean up resources
                if not settings.LIGHTS_NOOP and spidev:
                    driver.clear_lights(spidev)
                    spidev.close()

                # Only release lock if it was ours to begin with (i.e. don't release if
                # someone else already had it and we were forced to run)
                if got_lock:
                    release_lock()
        else:
            print 'Another light driver appears to already be running'
            print 'Force light driver to run with --force-run'
            print 'Note that you WILL encounter issues if more than one driver runs at once'
