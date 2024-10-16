"""
custom feature to work with alu extrudes profiles
"""
import adsk.core, adsk.fusion
import math, traceback, os

from ....lib import fusion360utils as futil

from .. import config
from ..commands import dialog_IDs as dialogID

_app: adsk.core.Application = None
_ui: adsk.core.UserInterface = None

_myFeatureDef: adsk.fusion.CustomFeatureDefinition = None

# Get the active component.
app = adsk.core.Application.get()
des = adsk.fusion.Design.cast(app.activeProduct)

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '') 

def create(_app : adsk.core.Application, editCmdDef : adsk.core.CommandDefinition):
    """
    Creates the internal behavior of the feature and connects the edit function to the feature

        :param _app: the application where in we are
        :param editCmdDef: The definition for the "Edit" command.
    """

    # Create the custom feature definition.
    global _myFeatureDef
    _myFeatureDef = adsk.fusion.CustomFeatureDefinition.create(config.FEATURE_ID, 
                                                               config.FEATURE_NAME, 
                                                               ICON_FOLDER)
    _myFeatureDef.editCommandId = editCmdDef.id

def createFromInput( planeInput: adsk.core.SelectionCommandInput,
                     pointInput: adsk.core.SelectionCommandInput,
                     distanceInput: adsk.core.DistanceValueCommandInput,
                     sizeInput: adsk.core.FloatSpinnerCommandInput,
                     slotSizeInput: adsk.core.IntegerSpinnerCommandInput,
                     directInput: adsk.core.DropDownCommandInput ):
    """
    Create an element of the feature

    The constructed element will become a feature element
    This implementation was the first shot. It needs much more work
    """
    
    activeComponent = des.activeComponent

    #try:
    if(True):
        futil.log(f'create alu profile feature from input(s) ')
        plane = planeInput.selection(0).entity
        skPoint: adsk.fusion.SketchPoint = pointInput.selection(0).entity
        startFeature = activeComponent.features.baseFeatures.add()
        mat = adsk.core.Matrix3D.create() 
        newOcc = activeComponent.occurrences.addNewComponent(mat)
        newComponent =  adsk.fusion.Component.cast(newOcc.component) 

        sk, extr = drawGeometryGeneric( newComponent, 
                                        plane, 
                                        skPoint, 
                                        sizeInput.value, 
                                        slotSizeInput.value, 
                                        distanceInput.value, 
                                        directInput.selectedItem.index)
        futil.log(f'We created the Geo')
        defLengthUnits = des.unitsManager.defaultLengthUnits
        custFeatureInput = activeComponent.features.customFeatures.createInput(_myFeatureDef)
        custFeatureInput.addDependency('plane', plane)
        custFeatureInput.addDependency('point', skPoint)
        custFeatureInput.addCustomParameter('length', 'Length', adsk.core.ValueInput.createByString(distanceInput.expression), des.unitsManager.defaultLengthUnits, True)
        custFeatureInput.addCustomParameter('size', 'Size', adsk.core.ValueInput.createByString(sizeInput.expression), des.unitsManager.defaultLengthUnits, True)
        custFeatureInput.setStartAndEndFeatures(startFeature, extr)
        custFeature = activeComponent.features.customFeatures.add(custFeatureInput)


    #except:
    else:
        futil.log('Failed:\n{}'.format(traceback.format_exc()))
        
def createFeatFromDxf(parent:adsk.fusion.Component,
                      planeEnt,
                      dxfFile: str,
                      length, 
                      direction ):
        """
        Create a feature element from dxf data
        """
        futil.log(f'create alu profile feature from input(s) ')
        startFeature = parent.features.baseFeatures.add()
        mat = adsk.core.Matrix3D.create() 
        newOcc = parent.occurrences.addNewComponent(mat)
        newComponent =  adsk.fusion.Component.cast(newOcc.component) 

        sk = dxfToSketch(newComponent, planeEnt, dxfFile)
        body = drawBody(newComponent,sk, length, direction)
        
        custFeatureInput = parent.features.customFeatures.createInput(_myFeatureDef)
        custFeatureInput.addDependency('plane', planeEnt)
        custFeatureInput.addCustomParameter('length', 'Length', adsk.core.ValueInput.createByReal(length), des.unitsManager.defaultLengthUnits, True)
        custFeatureInput.setStartAndEndFeatures(startFeature, body)
        custFeature = parent.features.customFeatures.add(custFeatureInput)
        
def createBodyFromDxf(parent:adsk.fusion.Component,
                      planeEnt,
                      dxfFile: str,
                      length, 
                      direction ):
    """
    we will create the profiles from file
    """
    futil.log(f'create alu profile feature from dxf file')

    sk = dxfToSketch(parent, planeEnt, dxfFile)
    body = drawBody(parent,sk, length, direction)


# Draws the shapes based on the input argument.     
def drawGeometryGeneric( parent:adsk.fusion.Component, 
                        planeEnt, 
                        pointEnt,  
                        size, 
                        slotSize_cm,
                        length, 
                        direction, 
                        isPreview: bool = False
                        ) -> tuple[adsk.fusion.Sketch, adsk.fusion.ExtrudeFeature]:
    """
    Draw the element
    
    The function will call the steps to create the visual element. It will be used to preview and to create it
    """
    try:
        sk: adsk.fusion.Sketch = None
        body = None
        if isPreview:
            # the new body type uses a full sketch type because the circular pattern in sketch is more comfort then the circular pattern on body
            # the preview creates a scetch without constrains to reduce calculation overhead
            sk, startPoint = drawGenericSketch(parent, 
                                               planeEnt, 
                                               pointEnt, 
                                               config.attr_previewSketch, 
                                               size,
                                               slotSize_cm)
            body = drawBody(parent,sk, length, direction)
        else:
            # the new body type uses a full sketch type because the circular pattern in sketch is more comfort then the circular pattern on body
            sk, startPoint = drawGenericSketch(parent, 
                                               planeEnt, 
                                               pointEnt, 
                                               config.attr_fullSketch, 
                                               size,
                                               slotSize_cm)
            body = drawBody(parent, sk, length, direction)       
        return sk, body
    except:
        futil.log('Failed:\n{}'.format(traceback.format_exc()))

# Draw the sketch
def drawGenericSketch(parent:adsk.fusion.Component, 
                      planeEnt:adsk.core.Base, 
                      pointEnt:adsk.core.Base, 
                      sketchType, 
                      size,
                      slotSize_cm
                    ) -> tuple[adsk.fusion.Sketch, adsk.fusion.SketchPoint]:
    """
    Draw an element sketch
    
    We draw the generic sketch
    """

    try:
        
        # Create a new sketch plane.
        
        sk = parent.sketches.add(planeEnt)    
        
        # Project the point onto the sketch.
        skPnt = sk.project(pointEnt).item(0)
        
        if sketchType == 'Custom':
            # ######################################
            # the custom sketch is drawn by the user
            # we do nothing
            # maybe we handle a circular pattern later
            # ######################################
            pass
        elif ((sketchType == config.attr_fullSketch) | (sketchType == config.attr_previewSketch)):
            # ######################################
            # this sketch holds the full profile
            # ######################################
            sk.attributes.add(config.attr_SketchStyleGroup, config.attr_SketchStyle, config.attr_previewSketch)
            sk.attributes.add(config.attr_SketchStyleGroup, config.attr_CustomSketch, 'False')
            
            # in any other case we create a profile without a slice
            skLines = sk.sketchCurves.sketchLines
            sketchArcs = sk.sketchCurves.sketchArcs 
            sketchDimensions = sk.sketchDimensions
            sketchConstraints = sk.geometricConstraints
            arcRadius = size / 10          

            # starting with the projected point and goes to x positiv => horizontal 
            pointProfilCenter = adsk.core.Point3D.create(skPnt.geometry.x, skPnt.geometry.y, 0)           
            
            # draw the horizontal line with the horizontal constraint
            # make it as construction line
            point_center_h1 = adsk.core.Point3D.create(pointProfilCenter.x - size/2, pointProfilCenter.y, 0)
            point_center_h2 = adsk.core.Point3D.create(pointProfilCenter.x + size/2, pointProfilCenter.y, 0)
            horizontalCenterLine = skLines.addByTwoPoints(point_center_h1,point_center_h2)
            sketchConstraints.addHorizontal(horizontalCenterLine)
            sketchConstraints.addMidPoint(skPnt, horizontalCenterLine)
            horizontalCenterLine.isConstruction = True

            # draw the vertical construction line with the vertical constraint
            # we start at the "end of the line" and goes to the sketch center
            # so we will come back at the end of this line later
            point_center_v1 = adsk.core.Point3D.create(pointProfilCenter.x, pointProfilCenter.y - size/2, 0) 
            point_center_v2 = adsk.core.Point3D.create(pointProfilCenter.x, pointProfilCenter.y + size/2, 0) 
            verticalCenterLine = skLines.addByTwoPoints(point_center_v1,point_center_v2)
            sketchConstraints.addVertical(verticalCenterLine)
            sketchConstraints.addMidPoint(skPnt, verticalCenterLine)
            verticalCenterLine.isConstruction = True 

            # we uses the points inside the config sketch class to build the slot
            # later we will do a selection depending on the profil type
            sketchPoints = config.quarterSketchPoints
            sketchSize = sketchPoints.size()
            startPoint = adsk.core.Point3D.create(size/2 - sketchPoints.point_x[0], sketchPoints.point_y[0], 0 )
            line = None
            for i in sketchPoints.pointPos:
                #startPoint = adsk.core.Point3D.create(size/2 - point_x[i], point_y[i], 0 )
                endPoint = adsk.core.Point3D.create(size/2 - sketchPoints.point_x[i+1], sketchPoints.point_y[i+1], 0 )
                if line:
                    line = skLines.addByTwoPoints(line.endSketchPoint, endPoint)
                else:
                    line = skLines.addByTwoPoints(startPoint, endPoint)
            # the last line defines the slot 
            slotLine = line

            # outer line to the corner arc                    
            point_v1 = adsk.core.Point3D.create(pointProfilCenter.x + size/2, pointProfilCenter.y + size/2 - arcRadius, 0) 
            outerVerticalLine = skLines.addByTwoPoints(line.endSketchPoint, point_v1)
            
            # draw the starting arc at top right corner
            arcCenter = adsk.core.Point3D.create(pointProfilCenter.x + size/2 - arcRadius, pointProfilCenter.y + size/2 - arcRadius , 0)  
            arc_1 = sketchArcs.addByCenterStartSweep(arcCenter,outerVerticalLine.endSketchPoint,math.radians(90))

            line = None
            for i in sketchPoints.pointPos:
                # we use switched x and y to build up the second half of the quarter
                endPoint = adsk.core.Point3D.create(sketchPoints.point_y[sketchSize -i],size/2 -  sketchPoints.point_x[sketchSize - i], 0 )
                if line:
                    line = skLines.addByTwoPoints(line.endSketchPoint, endPoint)
                else:
                    line = outerHorizontalLine = skLines.addByTwoPoints(arc_1.endSketchPoint, endPoint)
                    
            endPoint = adsk.core.Point3D.create( sketchPoints.point_y[0], size/2 - sketchPoints.point_x[0], 0 )
            line = skLines.addByTwoPoints(line.endSketchPoint, endPoint)

            # circular pattern in sketch to create full sketch
            curves = sk.findConnectedCurves(line)
            curveList = []
            for curve in curves:
                curveList.append(curve)
            circularInp = sk.geometricConstraints.createCircularPatternInput(curveList,skPnt)
            circularInp.quantity = adsk.core.ValueInput.createByReal(4)
            sk.geometricConstraints.addCircularPattern(circularInp)

            # ######################################
            # TODO this costs many of time
            # so we need a preview without constraints and dimension fixing
            # ######################################
            # adding constrains to the full sketch
            # the preview doesn't need them
            if sketchType == config.attr_fullSketch :        
                sk.name = 'Profile Full Sketch'
                sk.attributes.add(config.attr_SketchStyleGroup, config.attr_SketchStyle, config.attr_fullSketch)
                sk.attributes.add(config.attr_SketchStyleGroup, config.attr_CustomSketch, 'False')

                # fix the dimensions
                textPoint = adsk.core.Point3D.create(pointProfilCenter.x - 0.5, size/2 + 0.5, 0) 
                dimSize = sketchDimensions.addDistanceDimension( horizontalCenterLine.startSketchPoint, 
                                                                 horizontalCenterLine.endSketchPoint, 
                                                                 adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, 
                                                                 textPoint)
                textPoint = adsk.core.Point3D.create(size/2 + 0.5, pointProfilCenter.y - 0.5, 0) 
                dimSize = sketchDimensions.addDistanceDimension( verticalCenterLine.startSketchPoint, 
                                                                 verticalCenterLine.endSketchPoint, 
                                                                 adsk.fusion.DimensionOrientations.VerticalDimensionOrientation,
                                                                 textPoint)
                textPoint = adsk.core.Point3D.create(arc_1.centerSketchPoint.geometry.x + 0.5,arc_1.centerSketchPoint.geometry.y + 0.5, 0)
                dimArc = sketchDimensions.addRadialDimension(arc_1,textPoint)

                textPoint = adsk.core.Point3D.create(size/2 - 0.2, pointProfilCenter.y, 0)  
                dimSize = sketchDimensions.addOffsetDimension(horizontalCenterLine, slotLine, textPoint) 
                
                # we fix the sketch to the selected point
                sketchConstraints.addParallel(outerVerticalLine, verticalCenterLine)
                sketchConstraints.addCoincident(horizontalCenterLine.endSketchPoint, outerVerticalLine)
                sketchConstraints.addTangent(arc_1, outerVerticalLine) 
                sketchConstraints.addTangent(outerHorizontalLine, arc_1) 
                sketchConstraints.addParallel(outerHorizontalLine, horizontalCenterLine)
                sketchConstraints.addCoincident(verticalCenterLine.endSketchPoint, outerHorizontalLine)
                sketchConstraints.addEqual(outerVerticalLine, outerHorizontalLine)
                """
                sketchConstraints.addVertical(outerVerticalLine1)
                sketchConstraints.addHorizontal(outerHorizontalLine1)
                sketchConstraints.addTangent(arc_1, outerVerticalLine1)  
                sketchConstraints.addTangent(outerVerticalLine1, arc_2)
                sketchConstraints.addTangent(arc_2, outerHorizontalLine1)
                sketchConstraints.addTangent(outerHorizontalLine1, arc_3)
                sketchConstraints.addTangent(arc_3, outerVerticalLine2)
                sketchConstraints.addTangent(outerVerticalLine2, arc_4)
                sketchConstraints.addTangent(arc_4, outerHorizontalLine2)
                sketchConstraints.addEqual(arc_2, arc_1)
                sketchConstraints.addEqual(arc_3, arc_1)
                sketchConstraints.addEqual(arc_4, arc_1)
                """
        elif sketchType == 'Half of Quarter':
            # ######################################
            # the Half of a Quarter is enough
            # ######################################
            pass
        else: 
            # ######################################
            # standard is to hold the quarter sketch
            # ######################################

            # in any other case we create a profile without a slice
            skLines = sk.sketchCurves.sketchLines
            sketchArcs = sk.sketchCurves.sketchArcs 
            sketchDimensions = sk.sketchDimensions
            sketchConstraints = sk.geometricConstraints
            arcRadius = size / 10           
            sk.name = 'Profile Sketch'
            sk.attributes.add(config.attr_SketchStyleGroup, config.attr_SketchStyle, config.attr_quarterSketch)
            sk.attributes.add(config.attr_SketchStyleGroup, config.attr_CustomSketch, 'False')
            # we use quarter as sketch
            # starting with the projected point and goes to x positiv => horizontal 
            pointProfilCenter = adsk.core.Point3D.create(skPnt.geometry.x, skPnt.geometry.y, 0)           
            
            # draw the horizontal line with the horizontal constraint
            # make it as center line
            point_center_h1 = adsk.core.Point3D.create(pointProfilCenter.x - size/2, pointProfilCenter.y, 0)
            point_center_h2 = adsk.core.Point3D.create(pointProfilCenter.x + size/2, pointProfilCenter.y, 0)
            horizontalCenterLine = skLines.addByTwoPoints(point_center_h1,point_center_h2)
            sketchConstraints.addHorizontal(horizontalCenterLine)
            sketchConstraints.addMidPoint(skPnt, horizontalCenterLine)
            horizontalCenterLine.isCenterLine = True

            # draw the vertical center line with the vertical constraint
            # we start at the "end of the line" and goes to the sketch center
            # so we will come back at the end of this line later
            point_center_v1 = adsk.core.Point3D.create(pointProfilCenter.x, pointProfilCenter.y - size/2, 0) 
            point_center_v2 = adsk.core.Point3D.create(pointProfilCenter.x, pointProfilCenter.y + size/2, 0) 
            verticalCenterLine = skLines.addByTwoPoints(point_center_v1,point_center_v2)
            sketchConstraints.addVertical(verticalCenterLine)
            sketchConstraints.addMidPoint(skPnt, verticalCenterLine)
            verticalCenterLine.isCenterLine = True
            
            # draw the vertical outer line with constraint
            point_out_v = adsk.core.Point3D.create(pointProfilCenter.x + size/2, pointProfilCenter.y + size/2 - arcRadius, 0)
            outerVerticalLine = skLines.addByTwoPoints(horizontalCenterLine.endSketchPoint,point_out_v)

            # draw the arc 
            arcCenter = adsk.core.Point3D.create(pointProfilCenter.x + size/2 - arcRadius, pointProfilCenter.y + size/2 - arcRadius , 0)            
            arc = sketchArcs.addByCenterStartSweep(arcCenter,outerVerticalLine.endSketchPoint,math.radians(90))
            
            # draw the last line horizontal back to the vertical center line
            outerHorizontalLine = skLines.addByTwoPoints(arc.endSketchPoint,verticalCenterLine.startSketchPoint)

            # create the arc tangent constraints
            sketchConstraints.addTangent(outerVerticalLine, arc)
            sketchConstraints.addTangent(arc, outerHorizontalLine)

            # fix the dimensions
            textPoint = adsk.core.Point3D.create(pointProfilCenter.x - 0.5, pointProfilCenter.y + 0.5, 0) 
            dimSize = sketchDimensions.addOffsetDimension(horizontalCenterLine, outerHorizontalLine, textPoint)
            textPoint = adsk.core.Point3D.create(pointProfilCenter.x + 0.5, pointProfilCenter.y - 0.5, 0) 
            dimSize = sketchDimensions.addOffsetDimension(outerVerticalLine, verticalCenterLine, textPoint)
            textPoint = adsk.core.Point3D.create(horizontalCenterLine.endSketchPoint.geometry.x + 0.5,verticalCenterLine.startSketchPoint.geometry.y + 0.5,0)
            dimArc = sketchDimensions.addRadialDimension(arc,textPoint)
                        

        return sk, skPnt

    except:
        futil.log('Failed:\n{}'.format(traceback.format_exc()))    
 
def dxfToSketch(parent:adsk.fusion.Component, 
                planeEnt,  
                dxfFile) -> adsk.fusion.Sketch:
    """
    create a sketch witch the data from dxf file
    """
    # Create a new sketch plane.
    
    #sk = parent.sketches.add(planeEnt)    

    app = adsk.core.Application.get()
    ui  = app.userInterface
    importManager = app.importManager
    # Get dxf import options
    ### Variante 1
    dxfOptions = importManager.createDXF2DImportOptions(dxfFile, planeEnt)
    dxfOptions.isViewFit = False
    dxfOptions.isSingleSketchResult = True

    # Import dxf file to root component
    importManager.importToTarget(dxfOptions, parent)

    sketchResult: adsk.fusion.Sketch = dxfOptions.results.item(0) 
    # for prof in sketchResult.profiles:
    #     if prof.profileLoops.count == 1:
    #         profileLoop = prof.profileLoops.item(0)
    #         for curve in profileLoop.profileCurves:
    #             # we should fix the sketch curves


    return sketchResult
     
def drawBody (parent: adsk.fusion.Component, sketch: adsk.fusion.Sketch, length, direction):
    """Draw an element
    
    We draw an element to visualize it
    """

    try:
        # Get the design.
        app = adsk.core.Application.get()
        des = adsk.fusion.Design.cast(app.activeProduct)
        extrudes = parent.features.extrudeFeatures
        distanceValue = adsk.core.ValueInput.createByReal(length)

        # Find the inner profiles (only those with one loop).
        profCounter = 0
        futil.log(f'drawBody from sketch {str(sketch.profiles.count)} with profiles ')

        # use all profiles or only one / the first ???
        # for prof in sketch.profiles:
        prof = sketch.profiles.item(0)
        if prof != None:
            profCounter += 1
            profileName = "Profile " + sketch.name # + str(profCounter)
            # if prof.profileLoops.count == 1:
            profileLoop = prof.profileLoops.item(0)
            singleProfiles = adsk.core.ObjectCollection.create()
            if profileLoop.isOuter:
                singleProfiles.add(prof)
               
            # Create the extrude feature.
            if profCounter != 0 :
                extrudeInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                futil.log(f'Create Extrude (new body operation) with {profileName} with {str(prof.profileLoops.count)} loops')
            else:
                extrudeInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
                futil.log(f'Create Extrude (Cut Operation) with {profileName} with {str(prof.profileLoops.count)} loops')
            # Create a distance extent definition       
            extent_distance = adsk.fusion.DistanceExtentDefinition.create(distanceValue) 
            if direction == 0 : # 'One Side'
                extrudeInput.setOneSideExtent(extent_distance, adsk.fusion.ExtentDirections.PositiveExtentDirection)
                # Create the extrusion
                extrude2 = extrudes.add(extrudeInput)
            elif direction == 2 : # 'Symetric'
                extrudeInput.setSymmetricExtent(distanceValue, True)
                # Create the extrusion
                extrude2 = extrudes.add(extrudeInput)

                extrude2.name = profileName

        return extrude2
    except:
        futil.log('Failed:\n{}'.format(traceback.format_exc()))  