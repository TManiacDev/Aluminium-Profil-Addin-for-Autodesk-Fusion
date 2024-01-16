"""
custom feature to work with alu extrudes profiles
"""
import adsk.core, adsk.fusion, traceback
from ..lib import fusion360utils as futil

from . import config

from .commands import entry as command

from . import manageFeature as myFeature

_app: adsk.core.Application = None
_ui: adsk.core.UserInterface = None
_handlers = []

def start():
    """
    Start the custom feature
    """
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        createCmdDef =  command.startCreateCommand(_ui)
        editCmdDef = command.startEditCommand(_ui)
        
        myFeature.create(_app, editCmdDef)
    except:
        futil.handle_error('start feature')

        

def stop():
    """
    Stop the custom feature
    """
    try:
        # Remove all of the event handlers your app has created
        futil.clear_handlers()

        command.stopEditCommand(_ui)
        command.stopCreateCommand(_ui)


    except:
        futil.handle_error('stop feature')