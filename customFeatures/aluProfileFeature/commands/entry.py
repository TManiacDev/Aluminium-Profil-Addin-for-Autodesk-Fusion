import adsk.core, adsk.fusion
import os, math, traceback 
from ....lib import fusion360utils as futil 

from ....multiLanguage import languages as translation

from .. import config as featureConfig
from .... import config as addinConfig

from . import dialog_IDs as dialogID
from ..feature import manageFeature as myFeature

from ....profileLibrary import entry as profileLibrary
import xml.etree.ElementTree as xmlElementTree

# Resource location for command icons, here we assume a sub folder in this directory named "resources". 
RES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '') 
PROFILE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/profiles', '') 

# Local list of event handlers used to maintain a reference so 
# they are not released and garbage collected. 
local_handlers = [] 

_uiForEdit: adsk.core.UserInterface = None
_editedCustomFeature: adsk.fusion.CustomFeature = None
_restoreTimelineObject: adsk.fusion.TimelineObject = None
_isRolledForEdit = False

_dict = None
#_dict = translation.Language( adsk.core.UserLanguages.EnglishLanguage, RES_FOLDER)
#_dict = translation.Language( adsk.core.UserLanguages.GermanLanguage, RES_FOLDER)
_profileLib = profileLibrary.AluProfileLibrary()

def startCreateCommand(ui: adsk.core.UserInterface) -> adsk.core.CommandDefinition:
    """ create the entry for the create command """
    
    futil.log(f'Add the create Profile Command to the user interface') 
    # check for existing command and kill it befor create new
    existingDef = ui.commandDefinitions.itemById(featureConfig.CREATE_CMD_ID)
    if existingDef:
        existingDef.deleteMe()
    
    app = adsk.core.Application.get()
    appLanguage = app.preferences.generalPreferences.userLanguage
    global _dict 
    _dict = translation.Language( appLanguage, RES_FOLDER)

    # create the command view for the "Create Profile"
    createCmdDef = ui.commandDefinitions.addButtonDefinition(featureConfig.CREATE_CMD_ID, 
                                                             _dict.getTranslation('Create Aluminium Profile'), 
                                                             _dict.getTranslation('createProfileCommand_Desc'), 
                                                             RES_FOLDER)

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

    # create the command view for the "Edit Profile Feature"
    editCmdDef = ui.commandDefinitions.addButtonDefinition(featureConfig.EDIT_CMD_ID, 
                                                           _dict.getTranslation('Edit Aluminium Profile'), "")
    global _uiForEdit
    _uiForEdit = ui
    # Define an event handler for the command created event. It will be called when the button is clicked. 
    futil.add_handler(editCmdDef.commandCreated, editCommand_created) 
    return editCmdDef

def stopEditCommand(ui: adsk.core.UserInterface):
    """ Stopping the edit command """
     # Get the various UI elements for this command 
    command_definition = ui.commandDefinitions.itemById(featureConfig.EDIT_CMD_ID)  
 
    # Delete the command definition 
    if command_definition: 
        command_definition.deleteMe() 
        
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
        
# Function that is called when a user clicks edit feature.
# This defines the contents of the command dialog and connects to the command related events.
def editCommand_created(args: adsk.core.CommandCreatedEventArgs):
    """ handling the create event for the edit command """
    # General logging for debug.
    futil.log(f'{featureConfig.EDIT_CMD_NAME} Command Edit Event')
    
    # Get the currently selected custom feature.
    # we must use the global namespace to hold the feature under edit to the other event functions :-/
    global _editedCustomFeature
    _editedCustomFeature = _uiForEdit.activeSelections.item(0).entity
    if _editedCustomFeature is None:
        return
    # Get the collection of custom parameters for this custom feature.
    params = _editedCustomFeature.parameters # _editedCustomFeature.parameters
    createCommandView(args, params)

    # we need some event handlers
    # ExecutePreviewHandler
    # EditExecuteHandler
    # PreSelectHandler
    # EditActivateHandler
    # ValidateInputsHandler
    futil.add_handler(args.command.activate, editCommand_activate, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.execute, createCommand_execute, local_handlers=local_handlers)

def createCommandView(args: adsk.core.CommandCreatedEventArgs, featureParams: adsk.fusion.CustomFeatureParameters = None):
    """ create the visible command dialog 
        This is the same for create and edit command """
    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs 
    inputs = args.command.commandInputs 

    # prepare initial values
    lengthValue = None
    sizeValue = None
    if featureParams != None:
        featureLength = featureParams.itemById('length')
        try:
            featureSize = featureParams.itemById('size')
        except:
            featureSize = None
        if featureLength:
            lengthValue = adsk.core.ValueInput.createByString(featureLength.expression)
        if featureSize:
            realSplit = featureSize.expression.split(" ")
            realSize = adsk.core.ValueInput.createByString(featureSize.expression)
            futil.log(f'Prepare Initial Value for Size : {featureSize.expression} | {float(realSplit[0])} | the SpinnerInput works on float')
            sizeValue =  float(realSplit[0])
            sizeUnit = realSplit[1]
 
    # try to look for existing command inputs
    
    planeSelect: adsk.core.SelectionCommandInput = inputs.itemById(dialogID.planeSelect)
    pointSelect: adsk.core.SelectionCommandInput = inputs.itemById(dialogID.pointSelect)
    distanceInput: adsk.core.DistanceValueCommandInput = inputs.itemById(dialogID.distanceInput)
 
    # Create the selector for the plane. 
    if planeSelect == None:
        inputName =  _dict.getTranslation('Select Plane')
        planeSelect = inputs.addSelectionInput(dialogID.planeSelect, inputName, inputName) 
        planeSelect.addSelectionFilter('PlanarFaces') 
        planeSelect.addSelectionFilter('ConstructionPlanes') 
        planeSelect.setSelectionLimits(1,1) 
        planeSelect.tooltip =  _dict.getTranslation('selectPlane_Desc')
 
    # Create the selector for the points. 
    if pointSelect == None:
        inputName =  _dict.getTranslation('Select Point')
        pointSelect = inputs.addSelectionInput(dialogID.pointSelect, inputName, inputName) 
        pointSelect.addSelectionFilter('Vertices') 
        pointSelect.addSelectionFilter('ConstructionPoints') 
        pointSelect.addSelectionFilter('SketchPoints') 
        pointSelect.setSelectionLimits(1,1) 
        pointSelect.isEnabled = False 
        pointSelect.tooltip =  _dict.getTranslation('selectPoint_Desc')

    # Create the list for types of shapes.
    inputName =  _dict.getTranslation('Select Manufacture')
    slotTypeList = inputs.addDropDownCommandInput(dialogID.manufactureList, inputName, adsk.core.DropDownStyles.LabeledIconDropDownStyle)
    slotTypeList.tooltip = _dict.getTranslation('selectManufacture_Desc')
    createProfileList(slotTypeList)

    genericGroupInputs = inputs.addGroupCommandInput(dialogID.genericTypeGroup, 'Generic Value Input')

    # keep in mind the spinner command works on int only
    inputName =  _dict.getTranslation('Size')
    if sizeValue == None:
        sizeValue = 40
        sizeUnit = 'mm' #_des.unitsManager.defaultLengthUnits
    sizeSpinner = genericGroupInputs.children.addFloatSpinnerCommandInput(dialogID.sizeSpinner, inputName , sizeUnit, 10, 100, 5, sizeValue)
    sizeSpinner.value
    inputName =  _dict.getTranslation('Slot Size')
    slotSizeSpinner = genericGroupInputs.children.addIntegerSpinnerCommandInput(dialogID.slotSizeSpinner, inputName , 4, 10, 2, 8)

    libGroupInputs = inputs.addGroupCommandInput(dialogID.libTypeGroup, 'Select from Library')
    createLibInput(libGroupInputs)
    libGroupInputs.isVisible = False

    if distanceInput == None:
        inputName =  _dict.getTranslation('Distance')
        if lengthValue == None:
            lengthValue = adsk.core.ValueInput.createByString('10.0 cm')
        distanceInput = inputs.addDistanceValueCommandInput(dialogID.distanceInput, inputName, lengthValue)
        distanceInput.isEnabled = False

    # Create the list for dircetion type.
    directTypeList = inputs.addDropDownCommandInput(dialogID.directionTypeList, 
                                                    _dict.getTranslation('Direction'), 
                                                    adsk.core.DropDownStyles.LabeledIconDropDownStyle)
    # The Order of this list items is important because the manageFeature doesn't know the translated names
    directTypeList.listItems.add(_dict.getTranslation('One Side'), True, addinConfig.FUSION_UI_RESOURCES_FOLDER + '/Modeling/LeftSide', -1)
    directTypeList.listItems.add(_dict.getTranslation('Two Sides'), False, addinConfig.FUSION_UI_RESOURCES_FOLDER + '/Modeling/BothSide', -1)
    directTypeList.listItems.add(_dict.getTranslation('Symetric'), False, addinConfig.FUSION_UI_RESOURCES_FOLDER + '/Modeling/Symmetric', -1)

    
    # Create the list for dircetion type.
    featureTypeList = inputs.addDropDownCommandInput(dialogID.featureTypeList, _dict.getTranslation('Operation'), adsk.core.DropDownStyles.LabeledIconDropDownStyle)
    # The Order of this list items is important because the manageFeature doesn't know the translated names
    featureTypeList.listItems.add(_dict.getTranslation('New Body'), True) #, addinConfig.FUSION_UI_RESOURCES_FOLDER + '/Modeling/LeftSide', -1)
    featureTypeList.listItems.add(_dict.getTranslation('New Component'), False) #, addinConfig.FUSION_UI_RESOURCES_FOLDER + '/NewComponent', -1)
    featureTypeList.listItems.add(_dict.getTranslation('New Feature'), True)#, addinConfig.FUSION_UI_RESOURCES_FOLDER + '/Modeling/Symmetric', -1)
    featureTypeList.tooltip = _dict.getTranslation('operation_Desc')

def createProfileList(list: adsk.core.DropDownCommandInput):
    """
    The list must be created depending on the profile library
    """
    allProfiles = _profileLib.getLibNameList()
    for profile in allProfiles:
        text = str(profile)
        FolderName = os.path.join(_profileLib.getFolder(), text, '')
        #os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '') 
        list.listItems.add(text, True, FolderName)
    # we add this at last so it will shown on creation
    list.listItems.add('None (simple block)', True, RES_FOLDER + '/None', 0)
    list.listItems.add('Generic', True, RES_FOLDER + '/profiles' , 1)

def createLibInput(groupInput: adsk.core.GroupCommandInput):
    """
    to add selections depending from the library
    """
    # give some informations for direction of axis 
    copyrightText = _dict.getTranslation('Profile Copyright1') + "<br>"
    copyrightText += _dict.getTranslation('Profile Copyright2') + "<br>"
    copyrightText += "<br><b>" + _dict.getTranslation('Profile Copyright3') + "</b>"
    text_box_input = groupInput.children.addTextBoxCommandInput(dialogID.copyrightText, 'Copyright Info', 
                                                   copyrightText, 
                                                   6, 
                                                   True) 
    # Create the list for dircetion type.
    directTypeList = groupInput.children.addDropDownCommandInput(dialogID.profileTypeList, 
                                                                 _dict.getTranslation('Select Profile Type'), 
                                                                 adsk.core.DropDownStyles.TextListDropDownStyle)

# This event handler is called when the edit dialog comes active
# We is this to set the selection to the plane and point.
def editCommand_activate(args: adsk.core.CommandEventArgs):
    """ 
    handling the activate event for the edit command 
    """
    # General logging for debug.
    futil.log(f'{featureConfig.FEATURE_NAME} Command Edit Activate Event ' )
    
    eventArgs = adsk.core.CommandEventArgs.cast(args)
    app = adsk.core.Application.get()
    des: adsk.fusion.Design = app.activeProduct
    # Save the current position of the timeline.
    timeline = des.timeline
    markerPosition = timeline.markerPosition
    global _restoreTimelineObject, _isRolledForEdit
    _restoreTimelineObject = timeline.item(markerPosition - 1)
    # Roll the timeline to just before the custom feature being edited.
    _editedCustomFeature.timelineObject.rollTo(rollBefore = True)
    _isRolledForEdit = True
    # Define a transaction marker so the the roll is not aborted with each change.
    eventArgs.command.beginStep()

    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs
    planeSelect: adsk.core.SelectionCommandInput = inputs.itemById(dialogID.planeSelect)
    pointSelect: adsk.core.SelectionCommandInput = inputs.itemById(dialogID.pointSelect)
    distanceInput: adsk.core.DistanceValueCommandInput = inputs.itemById(dialogID.distanceInput)

    plane = _editedCustomFeature.dependencies.itemById('plane')
    if (plane != None):
        planeSelect.addSelection(plane.entity)
    skPoint = _editedCustomFeature.dependencies.itemById('point')
    if (skPoint != None):
        pointSelect.addSelection(skPoint.entity)    
   
    manufactureInput: adsk.core.DropDownCommandInput = inputs.itemById(dialogID.manufactureList)
    # we must preselect the manufacture and following data
    if (_editedCustomFeature.attributes.count == 2 ):
        for attr in _editedCustomFeature.attributes:
            if attr.name == 'Manufacture':
                profileManufacture =  attr.value
            if attr.name == 'Profile':
                profileType =  attr.value

        for item in manufactureInput.listItems:
            if item.name == profileManufacture:
                item.isSelected = True
    # this doesn't work yet, because the profile list isn't loaded at this moment
    # we must do this on change input event
    # typeList: adsk.core.DropDownCommandInput = inputs.itemById(dialogID.profileTypeList)
    # for item in typeList.typeList:
    #     if item.name == profileType:
    #         item.isSelected = True


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def createCommand_execute(args: adsk.core.CommandEventArgs):
    """ handling the execute event for the create command 
        Remark: this event would not fired if the preview sets the isValidResult to True """
    # General logging for debug.
    futil.log(f'{featureConfig.FEATURE_NAME} Command Execute Event')

    global _editedCustomFeature
    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs
    # Get the active component.
    app = adsk.core.Application.get()
    des = adsk.fusion.Design.cast(app.activeProduct)
    activeComponent = des.activeComponent
    
    planeSelect: adsk.core.SelectionCommandInput = inputs.itemById(dialogID.planeSelect)
    pointSelect: adsk.core.SelectionCommandInput = inputs.itemById(dialogID.pointSelect)
    distanceInput: adsk.core.DistanceValueCommandInput = inputs.itemById(dialogID.distanceInput)
    directInput: adsk.core.DropDownCommandInput = inputs.itemById(dialogID.directionTypeList)
    manufactureInput: adsk.core.DropDownCommandInput = inputs.itemById(dialogID.manufactureList)
    sizeInput: adsk.core.IntegerSpinnerCommandInput = inputs.itemById(dialogID.sizeSpinner)
    featureTypeInput: adsk.core.DropDownCommandInput = inputs.itemById(dialogID.featureTypeList)

    planeEnt = planeSelect.selection(0).entity
    pointEnt = pointSelect.selection(0).entity

    if (manufactureInput.selectedItem.index == 0) | (manufactureInput.selectedItem.index == 1):
        # create a box or a generic profile
        # they two manufacturing types are the both first
        futil.log(f' execute create command: Create the aluminium profile as {manufactureInput.selectedItem.name} | Index: {manufactureInput.selectedItem.index}')
        slotSizeInput: adsk.core.IntegerSpinnerCommandInput = inputs.itemById(dialogID.slotSizeSpinner)

        if featureTypeInput.selectedItem.name == _dict.getTranslation('New Feature'):
            myFeature.createFromInput(planeSelect, 
                                      pointSelect, 
                                      distanceInput, 
                                      sizeInput, 
                                      slotSizeInput, 
                                      directInput)
        else:
            if featureTypeInput.selectedItem.name == _dict.getTranslation('New Component'):
                # create a new component
                mat = adsk.core.Matrix3D.create() 
                newOcc = activeComponent.occurrences.addNewComponent(mat)
                newComponent = newOcc.component
                newComponent.name = manufactureInput.selectedItem.name + str(f' {sizeInput.value}')
            else:
                # use the allready active component
                newComponent = activeComponent

            myFeature.drawGeometryGeneric(newComponent, 
                                            planeEnt,
                                            pointEnt, 
                                            sizeInput.value, 
                                            slotSizeInput.value,
                                            distanceInput.value,
                                            directInput.selectedItem.index)
    else:
        # create a profile with manufacture data
        # today we have only dxf data
        # the xml library should give the information of data types later
        futil.log(f' execute create command: Create the aluminium profile as {manufactureInput.selectedItem.name} | Index: {manufactureInput.selectedItem.index} ')

        manufactureInput: adsk.core.DropDownCommandInput = inputs.itemById(dialogID.manufactureList)
        profileInput: adsk.core.DropDownCommandInput = inputs.itemById(dialogID.profileTypeList)
        manufactureName = manufactureInput.selectedItem.name
        profileName = profileInput.selectedItem.name
        pathName = _profileLib.getProfileFilePath(manufactureName, profileName)

        if featureTypeInput.selectedItem.name == _dict.getTranslation('New Feature'):
            
            nameIt = manufactureName + " " + profileName
            myFeature.createFeatFromDxf(activeComponent,
                                        nameIt,
                                        planeEnt,
                                        pointEnt,
                                        pathName, 
                                        distanceInput.value,
                                        directInput.selectedItem.index)
            futil.log(f'just to do something')
        else:
            if featureTypeInput.selectedItem.name == _dict.getTranslation('New Component'):
                # create a new component
                mat = adsk.core.Matrix3D.create() 
                newOcc = activeComponent.occurrences.addNewComponent(mat)
                newComponent = newOcc.component
                newComponent.name = manufactureName + " " + profileName
            else:
                newComponent = activeComponent

            futil.log(f'Execute {manufactureName} {profileName} path: {pathName}')
            myFeature.createBodyFromDxf(newComponent,planeEnt,pathName, distanceInput.value,
                                                    directInput.selectedItem.index)
            
    # myFeature.updateProfile()

    # Roll the timeline to its previous position.
    global _isRolledForEdit
    if _isRolledForEdit:
        _restoreTimelineObject.rollTo(False)
        _isRolledForEdit = False
    _editedCustomFeature = None
            
# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def editCommand_execute(args: adsk.core.CommandEventArgs):
    """ handling the execute event for the edit command 
        Remark: this event would not fired if the preview sets the isValidResult to True """
    # General logging for debug.
    futil.log(f'{featureConfig.FEATURE_NAME} Command Execute Event')

    global _editedCustomFeature

    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs

    # myFeature.updateProfile()

    # Roll the timeline to its previous position.
    global _isRolledForEdit
    if _isRolledForEdit:
        _restoreTimelineObject.rollTo(False)
        _isRolledForEdit = False
    _editedCustomFeature = None

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
        # Get the active component.
        app = adsk.core.Application.get()
        des = adsk.fusion.Design.cast(app.activeProduct)
        activeComponent = des.activeComponent

        #  getInput
        
        for input in inputs:        
            if input.id == dialogID.planeSelect:
                planeEnt = input.selection(0).entity
            elif input.id == dialogID.pointSelect:
                pointEnt = input.selection(0).entity
            elif input.id == dialogID.manufactureList:
                manufactureIndex = input.selectedItem.index
            elif input.id == dialogID.directionTypeList:
                direction = input.selectedItem.index
            elif input.id == dialogID.distanceInput:
                length = input.value
                
        # do the generic preview
        if (manufactureIndex == 0) | (manufactureIndex == 1):
            for input in inputs: 
                if input.id == dialogID.sizeSpinner:
                    size = input.value
                elif input.id == dialogID.slotSizeSpinner:
                    slotSize = input.value
            

            # Draw the preview geometry.
            myFeature.drawGeometryGeneric(activeComponent, 
                                          planeEnt , 
                                          pointEnt, 
                                          size, 
                                          slotSize, 
                                          length, 
                                          direction, 
                                          True)
        else:
            manufactureInput: adsk.core.DropDownCommandInput = inputs.itemById(dialogID.manufactureList)
            profileInput: adsk.core.DropDownCommandInput = inputs.itemById(dialogID.profileTypeList)
            manufactureName = manufactureInput.selectedItem.name
            profileName = profileInput.selectedItem.name
            pathName = _profileLib.getProfileFilePath(manufactureName, profileName)
            futil.log(f'Preview {manufactureName} {profileName} path: {pathName}')
            myFeature.createBodyFromDxf(activeComponent,planeEnt,pathName, length, direction)

        
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
    futil.log(f'{featureConfig.FEATURE_NAME} Input Changed Event fired from a change to {changed_input.id} {changed_input.objectType}')
    
    planeSelect: adsk.core.SelectionCommandInput = inputs.itemById(dialogID.planeSelect)
    pointSelect: adsk.core.SelectionCommandInput = inputs.itemById(dialogID.pointSelect)
    distanceInput: adsk.core.DistanceValueCommandInput = inputs.itemById(dialogID.distanceInput)
    manufactureInput: adsk.core.DropDownCommandInput = inputs.itemById(dialogID.manufactureList)
    
    if changed_input.objectType == adsk.core.SelectionCommandInput.classType():
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
                #distanceInput.expression = "10mm"
                distanceInput.isEnabled = True
            else:
                distanceInput.isEnabled = False

    genericInputGroup: adsk.core.GroupCommandInput = inputs.itemById(dialogID.genericTypeGroup)
    libGroupInputs: adsk.core.GroupCommandInput = inputs.itemById(dialogID.libTypeGroup)
    typeList: adsk.core.DropDownCommandInput = inputs.itemById(dialogID.profileTypeList)
    
    # we must preselect the manufacture and following data
    if _editedCustomFeature != None:
        if (_editedCustomFeature.attributes.count == 2 ):
            for attr in _editedCustomFeature.attributes:
                if attr.name == 'Manufacture':
                    profileManufacture =  attr.value
                if attr.name == 'Profile':
                    profileType =  attr.value
    else:
        profileManufacture =  None
        profileType =  None

    if changed_input.objectType == adsk.core.DropDownCommandInput.classType():
        if changed_input.id == dialogID.manufactureList:
            if manufactureInput.selectedItem.index == 0:
                genericInputGroup.isVisible = False
                libGroupInputs.isVisible = False
                # the first item is allways the simple block
                # we show the generic group
            elif manufactureInput.selectedItem.index == 1:
                #the second item is the generic type
                genericInputGroup.isVisible = True
                libGroupInputs.isVisible = False
            else: # in all other cases we have library elements
                genericInputGroup.isVisible = False
                # update the list before show it
                profilList = _profileLib.getProfilListByManufacture(manufactureInput.selectedItem.name)
                typeList.listItems.clear()
                if profileType == None:
                    profileType = profilList[0].get("name")
                for profil in profilList:
                    # add list item
                    if profil.get("name") == profileType:
                        # select the first element
                        # on change during edit feature we should select the allready created profil
                        typeList.listItems.add(profil.get("name"), True)
                    else:
                        typeList.listItems.add(profil.get("name"), False)
                
                libGroupInputs.isVisible = True





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
 