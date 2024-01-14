# Application Global Variables
# This module serves as a way to share variables across different
# modules (global variables).

import os

# Flag that indicates to run in Debug mode or not. When running in Debug mode
# more information is written to the Text Command window. Generally, it's useful
# to set this to True while developing an add-in and set it to False when you
# are ready to distribute it.
DEBUG = True

# Gets the name of the add-in from the name of the folder the py file is in.
# This is used when defining unique internal names for various UI elements 
# that need a unique name. It's also recommended to use a company name as 
# part of the ID to better ensure the ID is unique.
ADDIN_NAME = os.path.basename(os.path.dirname(__file__))
COMPANY_NAME = 'TManiac'

ICON_GLOBAL_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources\icons', '')
FUSION_UI_RESOURCES_FOLDER = os.getenv('LOCALAPPDATA') + '/Autodesk/webdeploy/production/b0c303e70bd97cfdc195adab65922cfeffcb363a/Fusion/UI/FusionUI/Resources'

# custom feature naming
aluProfileFeature_id = f'{COMPANY_NAME}_{ADDIN_NAME}_FeatureId'
aluProfileFeature_name = 'Alu Profile Feature'

# FIXME add good comments
design_workspace = 'FusionSolidEnvironment'

# Tabs
design_tab_id = f'{ADDIN_NAME}_design_tab'
design_tab_name = "Alu Profiles"

tools_tab_id = "ToolsTab"
my_tab_name = "Alu Profiles"  # Only used if creating a custom Tab

# use any other name to build a new Tab
create_panel_name = 'Alu Profile' #ADDIN_NAME
create_panel_id = f'{ADDIN_NAME}_profil_panel'
create_panel_after = ''

# the edit uses the same panel like the create
edit_panel_name = create_panel_name
edit_panel_id = create_panel_id
edit_panel_after = create_panel_after

edit_CMD_ID = f'{COMPANY_NAME}_{ADDIN_NAME}_editDialog'
edit_CMD_NAME = 'Command Dialog Sample'
edit_CMD_Description = 'A Fusion 360 Add-in Command with a dialog'

addins_panel_name = 'ADD-INS'
addins_panel_id = f'{ADDIN_NAME}_addins_panel'
addins_panel_after = edit_panel_id

help_panel_name = 'HELP'
help_panel_id = f'{ADDIN_NAME}_help_panel'
help_panel_after = addins_panel_id


