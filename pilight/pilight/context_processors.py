from django.conf import settings


def extra_settings(request):
    # Return settings we want to access in our pages
    return {
        'INSTALLATION_NAME': settings.LIGHTS_INSTALLATION_NAME,
        'MICROCONTROLLER': settings.LIGHTS_MICROCONTROLLER,
        'DEV_NAME': settings.LIGHTS_DEV_NAME,
        'NUM_LEDS': settings.LIGHTS_NUM_LEDS,
    }