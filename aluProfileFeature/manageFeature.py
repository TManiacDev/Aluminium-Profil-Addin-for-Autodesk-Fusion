"""
custom feature to work with alu extrudes profiles
"""
import adsk.core, adsk.fusion
import math, traceback 

from ..lib import fusion360utils as futil

from . import config
from .commands import dialog_IDs as dialogID

_app: adsk.core.Application = None
_ui: adsk.core.UserInterface = None

_myFeatureDef: adsk.fusion.CustomFeatureDefinition = None

def create(_app : adsk.core.Application, editCmdDef : adsk.core.CommandDefinition):
    """Creates the internal behavior of the feature and connects the edit function to the feature

        :param _app: the application where in we are
        :param editCmdDef: The definition for the "Edit" command.
    """

    # Create the custom feature definition.
    global _myFeatureDef
    _myFeatureDef = adsk.fusion.CustomFeatureDefinition.create(config.FEATURE_ID, 
                                                               config.FEATURE_NAME, 
                                                                'aluProfileFeature/resources')
    _myFeatureDef.editCommandId = editCmdDef.id

def createFromInput( planeInput: adsk.core.SelectionCommandInput,
                     pointInput: adsk.core.SelectionCommandInput,
                     distanceInput: adsk.core.DistanceValueCommandInput,
                     sizeInput: adsk.core.IntegerSpinnerCommandInput,
                     slotTypeInput: adsk.core.IntegerSpinnerCommandInput,
                     shapeInput: adsk.core.DropDownCommandInput,
                     directInput: adsk.core.DropDownCommandInput,
                     featureTypeInput: adsk.core.DropDownCommandInput ):
    """Create an element of the feature

    The constructed element will become a feature element
    """

    try:
        futil.log('create alu profile feature from input(s)')
        plane = planeInput.selection(0).entity
        skPoint: adsk.fusion.SketchPoint = pointInput.selection(0).entity

        if featureTypeInput.selectedItem.name == dialogID.newCustomFeature_Name:
            sk, extr = drawGeometry('CustomFeature', plane, skPoint, shapeInput.selectedItem.name, sizeInput.value, distanceInput.value, directInput.selectedItem.name)
            # Create the custom feature input.
            _app = adsk.core.Application.get()
            comp: adsk.fusion.Component = skPoint.parentSketch.parentComponent
            des: adsk.fusion.Design = _app.activeProduct
            defLengthUnits = des.unitsManager.defaultLengthUnits
            custFeatureInput = comp.features.customFeatures.createInput(_myFeatureDef)
            custFeatureInput.addDependency('point', skPoint)
            custFeatureInput.addCustomParameter('length', 'Length', adsk.core.ValueInput.createByString(distanceInput.expression), des.unitsManager.defaultLengthUnits, True)
            custFeatureInput.addCustomParameter('size', 'Size', adsk.core.ValueInput.createByReal(sizeInput.value), des.unitsManager.defaultLengthUnits, True)
            custFeatureInput.setStartAndEndFeatures(sk, extr)
            custFeature = comp.features.customFeatures.add(custFeatureInput)
        elif featureTypeInput.selectedItem.name == dialogID.newBody_Name:
            sk, extr = drawGeometry(dialogID.newBody_Name, plane, skPoint, shapeInput.selectedItem.name, sizeInput.value, distanceInput.value, directInput.selectedItem.name)


    except:
        futil.log('Failed:\n{}'.format(traceback.format_exc()))
        
# Draws the shapes based on the input argument.     
def drawGeometry(geoType, planeEnt, pointEnt, shape, size_cm, length, direction) -> (adsk.fusion.Sketch, adsk.fusion.ExtrudeFeature):
    """Draw the element
    
    The function will call the steps to create the visual element
    """

    try:
        sk: adsk.fusion.Sketch = None
        body = None
        if geoType == dialogID.newBody_Name:
            # the new body type uses a full sketch type because the circular pattern in sketch is more comfort then the circular pattern on body
            # TODO: we need the real sketch type, today giving the shape is the wrong way
            sk, startPoint = drawSketch(planeEnt, pointEnt, config.attr_fullSketch, size_cm)
            drawSlotToSketch(sk, startPoint, shape)
            body = drawBody(sk, length, direction)
        return sk, body
    except:
        futil.log('Failed:\n{}'.format(traceback.format_exc()))

# Draw the sketch
def drawSketch(planeEnt, pointEnt, sketchType, size_cm) -> (adsk.fusion.Sketch, adsk.fusion.SketchPoint):
    """Draw an element sketch
    
    We draw an element to visualize it
    """

    try:
        # Get the design.
        app = adsk.core.Application.get()
        des = adsk.fusion.Design.cast(app.activeProduct)
        
        # Create a new sketch plane.
        sk = des.rootComponent.sketches.add(planeEnt)    
        
        # Project the point onto the sketch.
        skPnt = sk.project(pointEnt).item(0)
        
        if sketchType == 'Custom':
            # ######################################
            # the custom sketch is drawn by the user
            # we do nothing
            # maybe we handle a circular pattern later
            # ######################################
            pass
        elif sketchType == config.attr_fullSketch:
            # ######################################
            # this sketch holds the full profile
            # ######################################

            # ######################################
            # TODO this costs many of time
            # so we need a preview without constraints and dimension fixing
            # ######################################
            size = size_cm / 10
            # in any other case we create a profile without a slice
            skLines = sk.sketchCurves.sketchLines
            sketchArcs = sk.sketchCurves.sketchArcs 
            sketchDimensions = sk.sketchDimensions
            sketchConstraints = sk.geometricConstraints
            arcRadius = size / 10           
            sk.name = 'Profile Full Sketch'
            sk.attributes.add(config.attr_SketchStyleGroup, config.attr_SketchStyle, config.attr_fullSketch)
            sk.attributes.add(config.attr_SketchStyleGroup, config.attr_CustomSketch, 'False')

            # starting with the projected point and goes to x positiv => horizontal 
            pointProfilCenter = adsk.core.Point3D.create(skPnt.geometry.x, skPnt.geometry.y, 0)

            # draw the starting arc at top right corner
            arcCenter = adsk.core.Point3D.create(pointProfilCenter.x + size/2 - arcRadius, pointProfilCenter.y - size/2 + arcRadius , 0)  
            arcStartpoint = adsk.core.Point3D.create(pointProfilCenter.x + size/2 - arcRadius, pointProfilCenter.y - size/2 , 0)
            startingArc = sketchArcs.addByCenterStartSweep(arcCenter,arcStartpoint,math.radians(90))

            # draw the right vertical outer line with constraint
            point_v2 = adsk.core.Point3D.create(pointProfilCenter.x + size/2, pointProfilCenter.y + size/2 - arcRadius, 0)
            outerVerticalLine1 = skLines.addByTwoPoints(startingArc.endSketchPoint,point_v2)
            sketchConstraints.addVertical(outerVerticalLine1)
            sketchConstraints.addTangent(startingArc, outerVerticalLine1)

            # draw the arc at lower right corner
            arcCenter = adsk.core.Point3D.create(pointProfilCenter.x + size/2 - arcRadius, pointProfilCenter.y + size/2 - arcRadius , 0)            
            arc = sketchArcs.addByCenterStartSweep(arcCenter,outerVerticalLine1.endSketchPoint,math.radians(90))            
            # create the arc tangent constraint to the previos line
            sketchConstraints.addTangent(outerVerticalLine1, arc)
            sketchConstraints.addEqual(arc, startingArc)

            # draw the lower line horizontal
            point_h1 = adsk.core.Point3D.create(pointProfilCenter.x - size/2 + arcRadius, pointProfilCenter.y - size/2, 0)
            outerHorizontalLine1 = skLines.addByTwoPoints(arc.endSketchPoint,point_h1)
            sketchConstraints.addHorizontal(outerHorizontalLine1)
            sketchConstraints.addTangent(arc, outerHorizontalLine1)

            # draw the arc at lower left corner and create constraint to the previous line
            arcCenter = adsk.core.Point3D.create(pointProfilCenter.x - size/2 + arcRadius, pointProfilCenter.y + size/2 - arcRadius , 0)            
            arc = sketchArcs.addByCenterStartSweep(arcCenter,outerHorizontalLine1.endSketchPoint,math.radians(90))
            sketchConstraints.addTangent(outerHorizontalLine1, arc)
            sketchConstraints.addEqual(arc, startingArc)

            centerLine = skLines.addByTwoPoints(startingArc.centerSketchPoint, arc.centerSketchPoint)
            centerLine.isCenterLine = True
            sketchConstraints.addMidPoint(skPnt, centerLine)
            
            # draw the left side
            point_v3 = adsk.core.Point3D.create(pointProfilCenter.x - size/2, pointProfilCenter.y - size/2 + arcRadius, 0)
            outerVerticalLine2 = skLines.addByTwoPoints(arc.endSketchPoint,point_v3)
            sketchConstraints.addTangent(arc, outerVerticalLine2)
            
            # draw the arc 
            arcCenter = adsk.core.Point3D.create(pointProfilCenter.x - size/2 + arcRadius, pointProfilCenter.y - size/2 + arcRadius , 0)            
            arc = sketchArcs.addByCenterStartSweep(arcCenter,outerVerticalLine2.endSketchPoint,math.radians(90))
            sketchConstraints.addTangent(outerVerticalLine2, arc)
            sketchConstraints.addEqual(arc, startingArc)

            # close with last line back to starting arc
            outerHorizontalLine2 = skLines.addByTwoPoints(arc.endSketchPoint,startingArc.startSketchPoint)
            sketchConstraints.addTangent(arc, outerHorizontalLine2)


            # fix the dimensions
            textPoint = adsk.core.Point3D.create(pointProfilCenter.x - 0.5, pointProfilCenter.y + 0.5, 0) 
            dimSize = sketchDimensions.addOffsetDimension(outerHorizontalLine1, outerHorizontalLine2, textPoint)
            textPoint = adsk.core.Point3D.create(pointProfilCenter.x + 0.5, pointProfilCenter.y - 0.5, 0) 
            dimSize = sketchDimensions.addOffsetDimension(outerVerticalLine1, outerVerticalLine2, textPoint)
            textPoint = adsk.core.Point3D.create(startingArc.centerSketchPoint.geometry.x + 0.5,startingArc.centerSketchPoint.geometry.y - 0.5, 0)
            dimArc = sketchDimensions.addRadialDimension(startingArc,textPoint)
        elif sketchType == 'Half of Quarter':
            # ######################################
            # the Half of a Quarter is enough
            # ######################################
            pass
        else: 
            # ######################################
            # standard is to hold the quarter sketch
            # ######################################
            size = size_cm / 10 + 2
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
            point_center_h = adsk.core.Point3D.create(pointProfilCenter.x + size/2, pointProfilCenter.y, 0)
            point_center_v = adsk.core.Point3D.create(pointProfilCenter.x, pointProfilCenter.y + size/2, 0)
            
            # draw the horizontal line with the horizontal constraint
            # make it as center line
            horizontalCenterLine = skLines.addByTwoPoints(skPnt,point_center_h)
            sketchConstraints.addHorizontal(horizontalCenterLine)
            horizontalCenterLine.isCenterLine = True

            # draw the vertical center line with the vertical constraint
            # we start at the "end of the line" and goes to the sketch center
            # so we will come back at the end of this line later
            verticalCenterLine = skLines.addByTwoPoints(point_center_v,horizontalCenterLine.startSketchPoint)
            sketchConstraints.addVertical(verticalCenterLine)
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

# add the slot to sketch
def drawSlotToSketch(sketch: adsk.fusion.Sketch, startPoint: adsk.fusion.SketchPoint, slotType, planeEnt = None):
    """Draw the slot sketch"""

    try:
        # Get the design.
        app = adsk.core.Application.get()
        des = adsk.fusion.Design.cast(app.activeProduct)

        sketchType = sketch.attributes.itemByName(config.attr_SketchStyleGroup, config.attr_SketchStyle)
        if sketchType == config.attr_quarterSketch:
            # using quarter sketch it is best way to use a second scetch for the slot
        
            # Create a new sketch plane.
            slotsketch = des.rootComponent.sketches.add(planeEnt)   

    except:
        futil.log('Failed:\n{}'.format(traceback.format_exc()))   
     
def drawBody (sketch: adsk.fusion.Sketch, length, direction):
    """Draw an element
    
    We draw an element to visualize it
    """

    try:
        # Get the design.
        app = adsk.core.Application.get()
        des = adsk.fusion.Design.cast(app.activeProduct)

        # Find the inner profiles (only those with one loop).
        profiles = adsk.core.ObjectCollection.create()
        for prof in sketch.profiles:
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

        """
        # Create input entities for circular pattern
        inputEntites = adsk.core.ObjectCollection.create()
        inputEntites.add(extrude2.bodies.item(0))
        axis = extrude2.faces.item(0).edges.item(0)
        circularFeats = des.rootComponent.features.circularPatternFeatures
        circularInput = circularFeats.createInput(inputEntites, axis)
        circularInput.quantity = adsk.core.ValueInput.createByReal(3)
        # Create the circular pattern
        circularFeat = circularFeats.add(circularInput)
        """

        return extrude2
    except:
        futil.log('Failed:\n{}'.format(traceback.format_exc()))  