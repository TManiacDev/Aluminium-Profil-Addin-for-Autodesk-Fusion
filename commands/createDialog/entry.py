import adsk.core, adsk.fusion 
import os, math, traceback
from ...lib import fusion360utils as futil
from . import dialog_IDs as dialogID
from ... import config
app = adsk.core.Application.get()
ui = app.userInterface


# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_createDialog'
CMD_NAME = 'Create a new Alu Profile'
CMD_Description = 'Dialog to create a Alu Profile on a path'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the 
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = config.design_workspace
TAB_ID = config.design_tab_id
TAB_NAME = config.design_tab_name

PANEL_ID = config.create_panel_id
PANEL_NAME = config.create_panel_name
PANEL_AFTER = config.create_panel_after

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')
PROFILE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/profiles', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []


# Executed when add-in is run.
def start():
    # check for existing command and kill it befor create new
    existingDef = ui.commandDefinitions.itemById(CMD_ID)
    if existingDef:
        existingDef.deleteMe()
        
    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get target toolbar tab for the command and create the tab if necessary.
    toolbar_tab = workspace.toolbarTabs.itemById(TAB_ID)
    if toolbar_tab is None:
        toolbar_tab = workspace.toolbarTabs.add(TAB_ID, TAB_NAME)
        
    # Get the panel the button will be created in.
    #panel = workspace.toolbarPanels.itemById(PANEL_ID)
    # Get target panel for the command and and create the panel if necessary.
    panel = toolbar_tab.toolbarPanels.itemById(PANEL_ID)
    if panel is None:
        panel = toolbar_tab.toolbarPanels.add(PANEL_ID, PANEL_NAME, PANEL_AFTER, False)

    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def)

    # Specify if the command is promoted to the main toolbar. 
    control.isPromoted = IS_PROMOTED


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    toolbar_tab = workspace.toolbarTabs.itemById(TAB_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

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
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    # TODO Define the dialog for your command by adding different inputs to the command.

    # Create the selector for the plane.
    planeInput = inputs.addSelectionInput(dialogID.planeSelect, 'Select Plane', 'Select Plane')
    planeInput.addSelectionFilter('PlanarFaces')
    planeInput.addSelectionFilter('ConstructionPlanes')
    planeInput.setSelectionLimits(1,1)

    # Create the selector for the points.
    pointInput = inputs.addSelectionInput(dialogID.pointSelect, 'Select Points', 'Select Points')
    pointInput.addSelectionFilter('Vertices')
    pointInput.addSelectionFilter('ConstructionPoints')
    pointInput.addSelectionFilter('SketchPoints')
    pointInput.setSelectionLimits(1,1)
    pointInput.isEnabled = False

    # Create the list for types of shapes.
    shapeList = inputs.addDropDownCommandInput(dialogID.shapeList, 'Slot Type', adsk.core.DropDownStyles.LabeledIconDropDownStyle)
    shapeList.listItems.add('I-Type 8', True, ICON_FOLDER + '/Square', -1)
    shapeList.listItems.add('None', True, ICON_FOLDER + '/None', -1)
    shapeList.listItems.add('Pentagon', False, ICON_FOLDER + '/Pentagon', -1)

    sizeSpinner = inputs.addIntegerSpinnerCommandInput(dialogID.sizeSpinner, 'Profile Size' , 10, 100, 5, 40)
    slotSizeSpinner = inputs.addIntegerSpinnerCommandInput(dialogID.slotSizeSpinner, 'Slot Size' , 4, 10, 2, 8)

    initValue = adsk.core.ValueInput.createByString('10.0 cm')
    distanceInput = inputs.addDistanceValueCommandInput(dialogID.distanceInput, 'Distance', initValue)
    distanceInput.isEnabled = False
    distanceInput.isVisible = False

    # Create the list for dircetion type.
    app.log('Icon Folder: ' + config.FUSION_UI_RESOURCES_FOLDER)
    dircetTypeList = inputs.addDropDownCommandInput(dialogID.directionTypeList, 'Direction', adsk.core.DropDownStyles.LabeledIconDropDownStyle)
    dircetTypeList.listItems.add('One Side', True, config.FUSION_UI_RESOURCES_FOLDER + '/Modeling/LeftSide', -1)
    dircetTypeList.listItems.add('Both Side', False, config.FUSION_UI_RESOURCES_FOLDER + '/Modeling/BothSide', -1)
    dircetTypeList.listItems.add('Symetric', False, config.FUSION_UI_RESOURCES_FOLDER + '/Modeling/Symmetric', -1)

    # TODO Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    #futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    # TODO ******************************** Your code here ********************************

    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs
    text_box: adsk.core.TextBoxCommandInput = inputs.itemById('text_box')
    value_input: adsk.core.ValueCommandInput = inputs.itemById('value_input')

    # Do something interesting
    text = text_box.text
    expression = value_input.expression
    msg = f'Your text: {text}<br>Your value: {expression}'
    ui.messageBox(msg)


# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
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
                pointEnts = adsk.core.ObjectCollection.create()
                for i in range(0, input.selectionCount):
                    pointEnts.add(input.selection(i).entity)
            elif input.id == dialogID.sizeSpinner:
                size = input.value
            elif input.id == dialogID.distanceInput:
                length = input.value
            elif input.id == dialogID.shapeList:
                shape = input.selectedItem.name
            elif input.id == dialogID.directionTypeList:
                direction = input.selectedItem.name
        
        # Draw the preview geometry.
        drawGeometry(planeEnt , pointEnts, shape, size, length, direction)
        
        # Set this property indicating that the preview is a good
        # result and can be used as the final result when the command
        # is executed.
        cmdArgs.isValidResult = True            
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
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')
    
    planeSelect: adsk.core.SelectionCommandInput = inputs.itemById(dialogID.planeSelect)
    distanceInput: adsk.core.DistanceValueCommandInput = inputs.itemById(dialogID.distanceInput)
    
    # Show and update the distance input when a plane is selected
    if changed_input.id == planeSelect.id:
        if planeSelect.selectionCount > 0:
            selection = planeSelect.selection(0)
            selection_point = selection.point
            selected_entity = selection.entity
            plane = selected_entity.geometry

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
    futil.log(f'{CMD_NAME} Validate Input Event')

    inputs = args.inputs
    
    # Verify the validity of the input values. This controls if the OK button is enabled or not.
    valueInput = inputs.itemById('value_input')
    if valueInput.value >= 0:
        args.areInputsValid = True
    else:
        args.areInputsValid = False
        

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []
 
# Draws the shapes based on the input argument.     
def drawGeometry(planeEnt, pointEnts, shape, size, length, direction):
    try:
        # Get the design.
        app = adsk.core.Application.get()
        des = adsk.fusion.Design.cast(app.activeProduct)

        defaultSize = 40 / 10 # Angabe in mm in cm
        
        # Create a new sketch plane.
        sk = des.rootComponent.sketches.add(planeEnt)    
        
        for pntEnt in pointEnts:
            # Project the point onto the sketch.
            skPnt = sk.project(pntEnt).item(0)
            
            if shape == 'Square':
                # Draw four lines to define a square.
                skLines = sk.sketchCurves.sketchLines
                line1 = skLines.addByTwoPoints(adsk.core.Point3D.create(skPnt.geometry.x - size/2, skPnt.geometry.y - size/2, 0), adsk.core.Point3D.create(skPnt.geometry.x + size/2, skPnt.geometry.y - size/2, 0))
                line2 = skLines.addByTwoPoints(line1.endSketchPoint, adsk.core.Point3D.create(skPnt.geometry.x + size/2, skPnt.geometry.y + size/2, 0))
                line3 = skLines.addByTwoPoints(line2.endSketchPoint, adsk.core.Point3D.create(skPnt.geometry.x - size/2, skPnt.geometry.y + size/2, 0))
                line4 = skLines.addByTwoPoints(line3.endSketchPoint, line1.startSketchPoint)
            elif shape == 'Pentagon':
                # Draw file lines to define a pentagon.
                skLines = sk.sketchCurves.sketchLines
                angle = math.pi/2
                halfSize = size/2
                x1 = halfSize * math.cos(angle)
                y1 = halfSize * math.sin(angle)

                angle += math.pi/2.5
                x2 = halfSize * math.cos(angle)
                y2 = halfSize * math.sin(angle)
                line1 = skLines.addByTwoPoints(adsk.core.Point3D.create(x1 + skPnt.geometry.x, y1 + skPnt.geometry.y, 0), adsk.core.Point3D.create(x2 + skPnt.geometry.x, y2 + skPnt.geometry.y, 0))

                angle += math.pi/2.5
                x = halfSize * math.cos(angle)
                y = halfSize * math.sin(angle)
                line2 = skLines.addByTwoPoints(line1.endSketchPoint, adsk.core.Point3D.create(x + skPnt.geometry.x, y + skPnt.geometry.y, 0))

                angle += math.pi/2.5
                x = halfSize * math.cos(angle)
                y = halfSize * math.sin(angle)
                line3 = skLines.addByTwoPoints(line2.endSketchPoint, adsk.core.Point3D.create(x + skPnt.geometry.x, y + skPnt.geometry.y, 0))

                angle += math.pi/2.5
                x = halfSize * math.cos(angle)
                y = halfSize * math.sin(angle)
                line4 = skLines.addByTwoPoints(line3.endSketchPoint, adsk.core.Point3D.create(x + skPnt.geometry.x, y + skPnt.geometry.y, 0))
                
                line5 = skLines.addByTwoPoints(line4.endSketchPoint, line1.startSketchPoint)
    
            else: 
                # in any other case we create a profile without a slice
                skLines = sk.sketchCurves.sketchLines
                sketchArcs = sk.sketchCurves.sketchArcs 
                arcRadius = size / 10            

                point_1 = adsk.core.Point3D.create(skPnt.geometry.x - size/2 + arcRadius, skPnt.geometry.y + size/2, 0)

                arcCenter = adsk.core.Point3D.create(skPnt.geometry.x - size/2 + arcRadius, skPnt.geometry.y + size/2 - arcRadius , 0)
                arc1 = sketchArcs.addByCenterStartSweep(arcCenter,point_1,math.radians(90))

                point_2 = adsk.core.Point3D.create(skPnt.geometry.x - size/2, skPnt.geometry.y - size/2 + arcRadius, 0)
                line1 = skLines.addByTwoPoints(arc1.endSketchPoint,point_2)

                arcCenter = adsk.core.Point3D.create(skPnt.geometry.x - size/2 + arcRadius, skPnt.geometry.y - size/2 + arcRadius , 0)
                arc2 = sketchArcs.addByCenterStartSweep(arcCenter,line1.endSketchPoint,math.radians(90))
                
                point_3 = adsk.core.Point3D.create(skPnt.geometry.x + size/2 - arcRadius, skPnt.geometry.y - size/2, 0)
                line2 = skLines.addByTwoPoints(arc2.endSketchPoint, point_3)

                arcCenter = adsk.core.Point3D.create(skPnt.geometry.x + size/2 - arcRadius, skPnt.geometry.y - size/2 + arcRadius , 0)
                arc3 = sketchArcs.addByCenterStartSweep(arcCenter,line2.endSketchPoint,math.radians(90))

                point_4 = adsk.core.Point3D.create(skPnt.geometry.x + size/2, skPnt.geometry.y + size/2 - arcRadius, 0)
                line3 = skLines.addByTwoPoints(arc3.endSketchPoint, point_4)

                arcCenter = adsk.core.Point3D.create(skPnt.geometry.x + size/2 - arcRadius, skPnt.geometry.y + size/2 - arcRadius , 0)
                arc4 = sketchArcs.addByCenterStartSweep(arcCenter,line3.endSketchPoint,math.radians(90))

                line4 = skLines.addByTwoPoints(arc4.endSketchPoint, arc1.startSketchPoint)

                
                #thirdPoint = adsk.core.Point3D.create(skPnt.geometry.x + size/2, skPnt.geometry.y + size/2, 0)

        # Find the inner profiles (only those with one loop).
        profiles = adsk.core.ObjectCollection.create()
        for prof in sk.profiles:
            if prof.profileLoops.count == 1:
                profiles.add(prof)

        # Create the extrude feature.            
        input = des.rootComponent.features.extrudeFeatures.createInput(profiles, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extrudes = des.rootComponent.features.extrudeFeatures
        distanceValue = adsk.core.ValueInput.createByReal(length)
        
        # Extrude Sample 2: Create an extrusion that goes from the profile plane with one side distance extent
        extrudeInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        # Create a distance extent definition       
        extent_distance = adsk.fusion.DistanceExtentDefinition.create(distanceValue) 
        if direction == 'One Side':
            extrudeInput.setOneSideExtent(extent_distance, adsk.fusion.ExtentDirections.PositiveExtentDirection)
            # Create the extrusion
            extrude2 = extrudes.add(extrudeInput)
        elif direction == 'Symetric':
            extrudeInput.setSymmetricExtent(distanceValue, True)
            # Create the extrusion
            extrude2 = extrudes.add(extrudeInput)

    except:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))    
     