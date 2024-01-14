# Assuming you have not changed the general structure of the template no modification is needed in this file.
from . import commands
from .lib import fusion360utils as futil

from . import config
import adsk.core, adsk.fusion, traceback

_app: adsk.core.Application = None
_ui: adsk.core.UserInterface = None
_customFeatureDef: adsk.fusion.CustomFeature = None

_handlers = []

def run(context):
    try:
        # This will run the start function in each of your commands as defined in commands/__init__.py
        commands.start()

        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        # Create the custom feature definition.
        global _customFeatureDef
        _customFeatureDef = adsk.fusion.CustomFeatureDefinition.create(config.aluProfileFeature_id, 
                                                                       config.aluProfileFeature_name, 
                                                                        'resources/CustomPocket')
        # connect the existing edit command to the custom feature edit
        _customFeatureDef.editCommandId = config.edit_CMD_ID
        
        # Connect to the compute event for the custom feature.
        computeCustomFeature = ComputeCustomFeature()
        _customFeatureDef.customFeatureCompute.add(computeCustomFeature)
        _handlers.append(computeCustomFeature)

    except:
        futil.handle_error('run')


def stop(context):
    try:
        # Remove all of the event handlers your app has created
        futil.clear_handlers()

        # This will run the start function in each of your commands as defined in commands/__init__.py
        commands.stop()

    except:
        futil.handle_error('stop')


# Event handler to handle the compute of the custom feature.
class ComputeCustomFeature(adsk.fusion.CustomFeatureEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:        
            _app.log('Compute Custom Feature ')
        except:
            showMessage('CustomFeatureCompute: {}\n'.format(traceback.format_exc()))
            
def showMessage(message, error = False):
    textPalette: adsk.core.TextCommandPalette = _ui.palettes.itemById('TextCommands')
    textPalette.writeText(message)

    if error:
        _ui.messageBox(message)