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


# FIXME add good comments
design_workspace = 'FusionSolidEnvironment'

# Tabs
design_tab_id = f'{ADDIN_NAME}_design_tab'
design_tab_name = "Alu Profiles"

tools_tab_id = "ToolsTab"
my_tab_name = "Alu Profiles"  # Only used if creating a custom Tab

# use any other name to build a new Tab
create_panel_name = 'Alu Profile Generator' #ADDIN_NAME
create_panel_id = f'{ADDIN_NAME}_profil_panel'
create_panel_after = ''

addins_panel_name = 'ADD-INS'
addins_panel_id = f'{ADDIN_NAME}_addins_panel'
addins_panel_after = create_panel_id

help_panel_name = 'HELP'
help_panel_id = f'{ADDIN_NAME}_help_panel'
help_panel_after = addins_panel_id


