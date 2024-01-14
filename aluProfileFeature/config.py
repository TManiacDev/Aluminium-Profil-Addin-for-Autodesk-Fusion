from ..config import COMPANY_NAME
from ..config import ADDIN_NAME

# custom feature naming
FEATURE_NAME = 'Alu Profile Feature'
FEATURE_ID = f'{COMPANY_NAME}_{FEATURE_NAME}_FeatureId'

# Specify the command identity information.
CREATE_CMD_ID = f'{COMPANY_NAME}_{FEATURE_NAME}_createDialog'
CREATE_CMD_NAME = FEATURE_NAME 
CREATE_CMD_Description = 'Dialog to create a Alu Profile on a path' 

# Specify that the command will be promoted to the panel. 
CREATE_CMD_IS_PROMOTED = True 

# Specify the command identity information.
EDIT_CMD_ID = f'{COMPANY_NAME}_{FEATURE_NAME}_editDialog'
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