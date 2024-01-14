"""
custom feature to work with alu extrudes profiles
"""
import adsk.core, adsk.fusion, traceback
from ..lib import fusion360utils as futil

from . import config

from .commands import entry as command

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

        createCmdDef =  command.startCreate(_ui)
        editCmdDef = command.startEdit(_ui)
        
        # Create the custom feature definition.
        global _customFeatureDef
        _customFeatureDef = adsk.fusion.CustomFeatureDefinition.create('adskCustomPocket', 
                                                                        'Custom Pocket', 
                                                                        'Resources/CustomPocket')
        _customFeatureDef.editCommandId = editCmdDef.id
    except:
        futil.handle_error('start feature')

        

def stop():
    """
    Stop the custom feature
    """
    try:
        # Remove all of the event handlers your app has created
        futil.clear_handlers()

        command.stopEdit(_ui)
        command.stopCreate(_ui)


    except:
        futil.handle_error('stop feature')