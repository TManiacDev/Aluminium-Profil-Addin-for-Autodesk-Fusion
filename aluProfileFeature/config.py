from ..config import COMPANY_NAME
from ..config import ADDIN_NAME

# custom feature naming
FEATURE_NAME = 'Alu Profile Feature'
FEATURE_ID = f'{COMPANY_NAME}_AluProfile_FeatureId'

# Specify the command identity information.
CREATE_CMD_ID = f'{FEATURE_ID}_createDialog'
CREATE_CMD_NAME = FEATURE_NAME 
CREATE_CMD_Description = 'Dialog to create a Alu Profile on a path' 

# Specify that the command will be promoted to the panel. 
CREATE_CMD_IS_PROMOTED = True 

# Specify the command identity information.
EDIT_CMD_ID = f'{FEATURE_ID}_editDialog'
EDIT_CMD_NAME = FEATURE_NAME 
EDIT_CMD_Description = 'Dialog to edit a Alu Profile on a path' 

# use any other name to build a new Tab
create_panel_name = 'Alu Profile' #ADDIN_NAME
create_panel_id = f'{ADDIN_NAME}_create_panel'
create_panel_after = ''

# the edit uses the same panel like the create
edit_panel_name = create_panel_name
edit_panel_id = create_panel_id
edit_panel_after = create_panel_after

# attribute names
attr_SketchStyleGroup = f'{FEATURE_ID}_sketchStyleGroup'
""" this is the group name to hold the sketch style(s) """

attr_SketchStyle = 'sketchStyle'
""" this is the name for the attribute to hold the sketch style(s) """

attr_CustomSketch = 'customSketch'
""" the sketch is drawn and managed by the user """

attr_previewSketch = 'previewSketch'
""" this sketch is only for preview 

    it is for fast calculation and has no sketch constraints and no fixed dimensions """


attr_fullSketch = 'fullSketch'
""" the sketch shows the full profile """

attr_quarterSketch = 'quarterSketch'
""" the sketch is just a quarter of the profile """


# ######################################
# classes to hold the sketch points
# ######################################
class quarterSketchPoints:
    """ a simple class to hold the point definitions for the profile sketch """
    # TODO this is today just a idea

    point_x0 = 1.2
    """ the starting point has only a x value because we start at the hirzontal center line """
    pointPos = [ 0,    1,    2,     3, ]
    point_x = [  1.2,  1.2,  0.45,  0.45,  0.00 ]
    point_y = [  0.0,  0.4,  1.00,  0.40,  0.40 ]

    def size():
        """ returns the number of End Points """
        return 4