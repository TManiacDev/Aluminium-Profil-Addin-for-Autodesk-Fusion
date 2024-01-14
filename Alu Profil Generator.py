# Assuming you have not changed the general structure of the template no modification is needed in this file.
from . import commands
from .lib import fusion360utils as futil

from . import config
import adsk.core, adsk.fusion, traceback

from . import aluProfileFeature

def run(context):
    try:
        # This will run the start function in each of your commands as defined in commands/__init__.py
        commands.start()

        # we want to start the custom features
        # the features have there own commands
        aluProfileFeature.start()


    except:
        futil.handle_error('run')


def stop(context):
    try:
        # Remove all of the event handlers your app has created
        futil.clear_handlers()

        aluProfileFeature.stop()

        # This will run the start function in each of your commands as defined in commands/__init__.py
        commands.stop()

    except:
        futil.handle_error('stop')
