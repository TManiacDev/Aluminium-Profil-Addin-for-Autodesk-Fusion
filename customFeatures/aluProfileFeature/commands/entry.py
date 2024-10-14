import adsk.core, adsk.fusion
import os, math, traceback 
from ....lib import fusion360utils as futil 

from ....multiLanguage import languages as translation

from .. import config as featureConfig
from .... import config as addinConfig

from . import dialog_IDs as dialogID
from ..feature import manageFeature as myFeature

import xml.etree.ElementTree as xmlElementTree

# Resource location for command icons, here we assume a sub folder in this directory named "resources". 
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '') 
PROFILE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/profiles', '') 

# Local list of event handlers used to maintain a reference so 
# they are not released and garbage collected. 
local_handlers = [] 

_uiForEdit: adsk.core.UserInterface = None
_editedCustomFeature: adsk.fusion.CustomFeature = None
_restoreTimelineObject: adsk.fusion.TimelineObject = None
_isRolledForEdit = False

_dict = translation.Language( 'english', ICON_FOLDER) #os.path.dirname(os.path.abspath(__file__)) )# + "\\resources"

def startCreateCommand(ui: adsk.core.UserInterface) -> adsk.core.CommandDefinition:
    """ create the entry for the create command """
    
    futil.log(f'Add the create Profile Command') 
    # check for existing command and kill it befor create new
    existingDef = ui.commandDefinitions.itemById(featureConfig.CREATE_CMD_ID)
    if existingDef:
        existingDef.deleteMe()

    # createCmdDef = ui.commandDefinitions.addButtonDefinition(featureConfig.CREATE_CMD_ID, 
    #                                                          featureConfig.CREATE_CMD_NAME, 
    #                                                          featureConfig.CREATE_CMD_Description, 
    #                                                          ICON_FOLDER)    


    futil.log(f'new dictionary test: \n  -> {_dict.directory} \n  -> {_dict.xmlPaths[0]} \n  -> {_dict.xmlPaths[1]}') 
    myDict = _dict.getDictName(0)
    futil.log(f'#####\n {myDict.attrib}\n####')

    createCmdDef = ui.commandDefinitions.addButtonDefinition(featureConfig.CREATE_CMD_ID, 
                                                             _dict.getTranslation('createProfileCommand_Name'), 
                                                             _dict.getTranslation('createProfileCommand_Desc'), 
                                                             ICON_FOLDER)
    
    text = _dict.getTranslation('createProfileCommand_Name')

    #futil.log(f'Dictionary: {_dict.xmlDictionary}') 

    # Define an event handler for the command created event. It will be called when the button is clicked. 
    futil.add_handler(createCmdDef.commandCreated, createCommand_created) 
 
    # ******** Add a button into the UI so the user can run the command. ******** 
    # Get the target workspace the button will be created in. 
    workspace = ui.workspaces.itemById(addinConfig.design_workspace) 
 
    
    # Get target toolbar tab for the command and create the tab if necessary. 
    toolbar_tab = workspace.toolbarTabs.itemById(addinConfig.design_tab_id) 
    if toolbar_tab is None: 
        toolbar_tab = workspace.toolbarTabs.add(addinConfig.design_tab_id, addinConfig.design_tab_name) 
         
    # Get the panel the button will be created in. 
    #panel = workspace.toolbarPanels.itemById(PANEL_ID) 
    # Get target panel for the command and and create the panel if necessary. 
    panel = toolbar_tab.toolbarPanels.itemById(featureConfig.create_panel_id) 
    if panel is None: 
        panel = toolbar_tab.toolbarPanels.add(featureConfig.create_panel_id, featureConfig.create_panel_name, featureConfig.create_panel_after, False) 
 
    # Create the button command control in the UI after the specified existing command. 
    control = panel.controls.addCommand(createCmdDef) 
 
    # Specify if the command is promoted to the main toolbar.  
    control.isPromoted = featureConfig.CREATE_CMD_IS_PROMOTED 

    return createCmdDef

def stopCreateCommand(ui: adsk.core.UserInterface):
    """ Stopping the create command """
     # Get the various UI elements for this command 
    workspace = ui.workspaces.itemById(addinConfig.design_workspace) 
    panel = workspace.toolbarPanels.itemById(featureConfig.create_panel_id) 
    toolbar_tab = workspace.toolbarTabs.itemById(addinConfig.design_tab_id) 
    command_control = panel.controls.itemById(featureConfig.CREATE_CMD_ID) 
    command_definition = ui.commandDefinitions.itemById(featureConfig.CREATE_CMD_ID) 
 
    # Delete the button command control 
    if command_control: 
        command_control.deleteMe() 
 
    # Delete the command definition 
    if command_definition: 
        command_definition.deleteMe() 
 
    # Delete the panel if it is empty 
    if panel.controls.count == 0: 
        panel.deleteMe() 
 
    # Delete the tab if it is empty 
    if toolbar_tab.toolbarPanels.count == 0: 
        toolbar_tab.deleteMe() 

def startEditCommand(ui: adsk.core.UserInterface) -> adsk.core.CommandDefinition:
    """ create the entry for the edit command """
    
    # check for existing command and kill it befor create new
    existingDef = ui.commandDefinitions.itemById(featureConfig.EDIT_CMD_ID)
    if existingDef:
        existingDef.deleteMe()

    editCmdDef = ui.commandDefinitions.addButtonDefinition(featureConfig.EDIT_CMD_ID, featureConfig.EDIT_CMD_NAME, featureConfig.EDIT_CMD_Description)
    global _uiForEdit
    _uiForEdit = ui
    # Define an event handler for the command created event. It will be called when the button is clicked. 
    futil.add_handler(editCmdDef.commandCreated, editCommand_created) 
    return editCmdDef

def stopEditCommand(ui: adsk.core.UserInterface):
    """ Stopping the edit command """
     # Get the various UI elements for this command 
    workspace = ui.workspaces.itemById(addinConfig.design_workspace) 
    panel = workspace.toolbarPanels.itemById(featureConfig.edit_panel_id) 
    toolbar_tab = workspace.toolbarTabs.itemById(addinConfig.design_tab_id) 
    command_control = panel.controls.itemById(featureConfig.EDIT_CMD_ID) 
    command_definition = ui.commandDefinitions.itemById(featureConfig.EDIT_CMD_ID) 
 
    # Delete the button command control 
    if command_control: 
        command_control.deleteMe() 
 
    # Delete the command definition 
    if command_definition: 
        command_definition.deleteMe() 
 
    # Delete the panel if it is empty 
    if panel.controls.count == 0: 
        panel.deleteMe() 
 
    # Delete the tab if it is empty 
    if toolbar_tab.toolbarPanels.count == 0: 
        toolbar_tab.deleteMe() 
        
# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def createCommand_created(args: adsk.core.CommandCreatedEventArgs):
    """ handling the create event for the create command """
    # General logging for debug.
    futil.log(f'{featureConfig.CREATE_CMD_NAME} Command Create Event')
    createCommandView(args)

    # TODO Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, createCommand_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)
        
# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def editCommand_created(args: adsk.core.CommandCreatedEventArgs):
    """ handling the create event for the edit command """
    # General logging for debug.
    futil.log(f'{featureConfig.EDIT_CMD_NAME} Command Edit Event')
    
    # Get the currently selected custom feature.
    editedCustomFeature = _uiForEdit.activeSelections.item(0).entity
    if editedCustomFeature is None:
        return
    # Get the collection of custom parameters for this custom feature.
    params = _editedCustomFeature.parameters
    createCommandView(args, params)

def createCommandView(args: adsk.core.CommandCreatedEventArgs, featureParams: adsk.fusion.CustomFeatureParameters = None):
    """ create the visible command dialog 
        This is the same for create and edit command """
    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs 
    inputs = args.command.commandInputs 
 
    # try to look for existing command inputs
    
    planeSelect: adsk.core.SelectionCommandInput = inputs.itemById(dialogID.planeSelect)
    pointSelect: adsk.core.SelectionCommandInput = inputs.itemById(dialogID.pointSelect)
    distanceInput: adsk.core.DistanceValueCommandInput = inputs.itemById(dialogID.distanceInput)
 
    # Create the selector for the plane. 
    if planeSelect == None:
        planeSelect = inputs.addSelectionInput(dialogID.planeSelect, 'Select Plane', 'Select Plane') 
        planeSelect.addSelectionFilter('PlanarFaces') 
        planeSelect.addSelectionFilter('ConstructionPlanes') 
        planeSelect.setSelectionLimits(1,1) 
 
    # Create the selector for the points. 
    if pointSelect == None:
        pointSelect = inputs.addSelectionInput(dialogID.pointSelect, 'Select Points', 'Select Points') 
        pointSelect.addSelectionFilter('Vertices') 
        pointSelect.addSelectionFilter('ConstructionPoints') 
        pointSelect.addSelectionFilter('SketchPoints') 
        pointSelect.setSelectionLimits(1,1) 
        pointSelect.isEnabled = False 

    # Create the list for types of shapes.
    slotTypeList = inputs.addDropDownCommandInput(dialogID.slotTypeList, 'Slot Type', adsk.core.DropDownStyles.LabeledIconDropDownStyle)
    slotTypeList.listItems.add('I-Type 8', True, ICON_FOLDER + '/profiles', -1)
    slotTypeList.listItems.add('None', True, ICON_FOLDER + '/None', -1)

    sizeSpinner = inputs.addIntegerSpinnerCommandInput(dialogID.sizeSpinner, 'Profile Size' , 10, 100, 5, 40)
    slotSizeSpinner = inputs.addIntegerSpinnerCommandInput(dialogID.slotSizeSpinner, 'Slot Size' , 4, 10, 2, 8)

    if distanceInput == None:
        initValue = adsk.core.ValueInput.createByString('10.0 cm')
        distanceInput = inputs.addDistanceValueCommandInput(dialogID.distanceInput, 'Distance', initValue)
        distanceInput.isEnabled = False
        distanceInput.isVisible = False

    # Create the list for dircetion type.
    directTypeList = inputs.addDropDownCommandInput(dialogID.directionTypeList, 'Direction', adsk.core.DropDownStyles.LabeledIconDropDownStyle)
    directTypeList.listItems.add('One Side', True, addinConfig.FUSION_UI_RESOURCES_FOLDER + '/Modeling/LeftSide', -1)
    directTypeList.listItems.add('Both Side', False, addinConfig.FUSION_UI_RESOURCES_FOLDER + '/Modeling/BothSide', -1)
    directTypeList.listItems.add('Symetric', False, addinConfig.FUSION_UI_RESOURCES_FOLDER + '/Modeling/Symmetric', -1)

    
    # Create the list for dircetion type.
    featureTypeList = inputs.addDropDownCommandInput(dialogID.featureTypeList, 'Operation', adsk.core.DropDownStyles.LabeledIconDropDownStyle)
    featureTypeList.listItems.add(dialogID.newBody_Name, True) #, addinConfig.FUSION_UI_RESOURCES_FOLDER + '/Modeling/LeftSide', -1)
    featureTypeList.listItems.add(dialogID.newComponent_Name, False) #, addinConfig.FUSION_UI_RESOURCES_FOLDER + '/NewComponent', -1)
    featureTypeList.listItems.add(dialogID.newCustomFeature_Name, False)#, addinConfig.FUSION_UI_RESOURCES_FOLDER + '/Modeling/Symmetric', -1)

# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def createCommand_execute(args: adsk.core.CommandEventArgs):
    """ handling the execute event for the create command 
        Remark: this event would not fired if the preview sets the isValidResult to True """
    # General logging for debug.
    futil.log(f'{featureConfig.FEATURE_NAME} Command Execute Event')

    # TODO ******************************** Your code here ********************************

    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs
    
    planeSelect: adsk.core.SelectionCommandInput = inputs.itemById(dialogID.planeSelect)
    pointSelect: adsk.core.SelectionCommandInput = inputs.itemById(dialogID.pointSelect)
    distanceInput: adsk.core.DistanceValueCommandInput = inputs.itemById(dialogID.distanceInput)
    sizeInput: adsk.core.IntegerSpinnerCommandInput = inputs.itemById(dialogID.sizeSpinner)
    slotSizeInput: adsk.core.IntegerSpinnerCommandInput = inputs.itemById(dialogID.slotSizeSpinner)
    slotTypeInput: adsk.core.DropDownCommandInput = inputs.itemById(dialogID.slotTypeList)
    directInput: adsk.core.DropDownCommandInput = inputs.itemById(dialogID.directionTypeList)
    featureTypeInput: adsk.core.DropDownCommandInput = inputs.itemById(dialogID.featureTypeList)

    # Do something interesting
    futil.log(' execute create command: Create the custom feature')

    # call the preview event function to use the same result
    # this should move to a different function (calling from execute and preview)

    myFeature.createFromInput(planeSelect, pointSelect, distanceInput, sizeInput, slotSizeInput, slotTypeInput, directInput, featureTypeInput)


# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    """ handling the preview event for create and edit command """
    # General logging for debug.
    futil.log(f'{featureConfig.FEATURE_NAME} Command Preview Event')
    # Code to react to the event.
    try:
        cmdArgs = adsk.core.CommandEventArgs.cast(args)

        # Get the current value of inputs entered in the dialog.
        inputs = args.command.commandInputs

        #  getInput
        
        for input in inputs:        
            if input.id == dialogID.planeSelect:
                planeEnt = input.selection(0).entity
            elif input.id == dialogID.pointSelect:
                pointEnt = input.selection(0).entity
            elif input.id == dialogID.sizeSpinner:
                size = input.value
            elif input.id == dialogID.distanceInput:
                length = input.value
            elif input.id == dialogID.slotTypeList:
                slotType = input.selectedItem.name
            elif input.id == dialogID.directionTypeList:
                direction = input.selectedItem.name
        
        # Draw the preview geometry.
        myFeature.drawGeometry(dialogID.preview_Name, planeEnt , pointEnt, slotType, size, length, direction)
        
        # Set this property indicating that the preview is a good
        # result and can be used as the final result when the command
        # is executed.
        # this will skip the execute handler 
        #cmdArgs.isValidResult = True            
    except:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))   

# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs

    # General logging for debug.
    futil.log(f'{featureConfig.FEATURE_NAME} Input Changed Event fired from a change to {changed_input.id}')
    
    planeSelect: adsk.core.SelectionCommandInput = inputs.itemById(dialogID.planeSelect)
    pointSelect: adsk.core.SelectionCommandInput = inputs.itemById(dialogID.pointSelect)
    distanceInput: adsk.core.DistanceValueCommandInput = inputs.itemById(dialogID.distanceInput)
    
    # Show and update the distance input when a plane is selected
    if changed_input.id == planeSelect.id:
        if planeSelect.selectionCount > 0:
            selection = planeSelect.selection(0)
            selection_point = selection.point
            selected_entity = selection.entity
            pointSelect.hasFocus = True


    if changed_input.id == pointSelect.id:
        if pointSelect.selectionCount > 0:
            plane = planeSelect.selection(0).entity.geometry
            selection_point = pointSelect.selection(0).entity.geometry
            distanceInput.setManipulator(selection_point, plane.normal)
            distanceInput.expression = "10mm"
            distanceInput.isEnabled = True
            distanceInput.isVisible = True
        else:
            distanceInput.isEnabled = False
            distanceInput.isVisible = False



# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    #futil.log(f'{CMD_NAME} Validate Input Event')

    inputs = args.inputs
    
    # Verify the validity of the input values. This controls if the OK button is enabled or not.
    valueInput = inputs.itemById(dialogID.distanceInput)
    if valueInput.value >= 0:
        args.areInputsValid = True
        futil.log(f'{featureConfig.FEATURE_NAME} Validate Input Event is True')
    else:
        args.areInputsValid = False
        futil.log(f'{featureConfig.FEATURE_NAME} Validate Input Event is False')
        

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{featureConfig.FEATURE_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []
 