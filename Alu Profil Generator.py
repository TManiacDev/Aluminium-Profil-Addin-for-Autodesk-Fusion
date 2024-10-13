"""
Project to handle some nice functions around Alu Profiles used on 3D Printers and so an.

@file: this is the entry used from Fusion 360

"""

# Assuming you have not changed the general structure of the template no modification is needed in this file.
from . import commands
from . import customFeatures
from .lib import fusion360utils as futil

from . import config
import adsk.core, adsk.fusion, traceback

#from . import aluProfileFeature

def run(context):
    """This function is called from Fusion360 to start the Add-In"""
    try:
        # This will run the start function in each of your commands as defined in commands/__init__.py
        commands.start()
        customFeatures.start()
        # we want to start the custom features
        # the features have there own commands
        #aluProfileFeature.start()


    except:
        futil.handle_error('run')


def stop(context):
    """This function is called from Fusion360 if you shut down the Add-In"""
    try:
        # Remove all of the event handlers your app has created
        futil.clear_handlers()

        #aluProfileFeature.stop()

        # This will run the start function in each of your commands as defined in commands/__init__.py
        customFeatures.stop()
        commands.stop()

    except:
        futil.handle_error('stop')
