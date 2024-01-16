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
    """ to create the feature """
    # Create the custom feature definition.
    global _myFeatureDef
    _myFeatureDef = adsk.fusion.CustomFeatureDefinition.create(config.FEATURE_ID, 
                                                               config.FEATURE_NAME, 
                                                                'resources')
    _myFeatureDef.editCommandId = editCmdDef.id

def myFunction():
    pass

def createFromInput( planeInput: adsk.core.SelectionCommandInput,
                     pointInput: adsk.core.SelectionCommandInput,
                     distanceInput: adsk.core.DistanceValueCommandInput,
                     sizeInput: adsk.core.IntegerSpinnerCommandInput,
                     slotSizeInput: adsk.core.IntegerSpinnerCommandInput,
                     shapeInput: adsk.core.DropDownCommandInput,
                     directInput: adsk.core.DropDownCommandInput,
                     featureTypeInput: adsk.core.DropDownCommandInput ):
    try:
        futil.log('create alu profile feature from input(s)')
        plane = planeInput.selection(0).entity
        skPoint: adsk.fusion.SketchPoint = pointInput.selection(0).entity

        sk, extr = drawGeometry(plane, skPoint, shapeInput.selectedItem.name, sizeInput.value, distanceInput.value, directInput.selectedItem.name)
        if featureTypeInput.selectedItem.name == dialogID.newCustomFeature_Name:
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

    except:
        futil.log('Failed:\n{}'.format(traceback.format_exc()))
        
# Draws the shapes based on the input argument.     
def drawGeometry(planeEnt, pointEnt, shape, size, length, direction) -> (adsk.fusion.Sketch, adsk.fusion.ExtrudeFeature):
    try:
        # Get the design.
        app = adsk.core.Application.get()
        des = adsk.fusion.Design.cast(app.activeProduct)

        defaultSize = 40 / 10 # Angabe in mm in cm
        
        # Create a new sketch plane.
        sk = des.rootComponent.sketches.add(planeEnt)    
        
        # Project the point onto the sketch.
        skPnt = sk.project(pointEnt).item(0)
        
        if shape == 'Square':
            pass
        elif shape == 'Pentagon':
            pass

        else: 
            # in any other case we create a profile without a slice
            skLines = sk.sketchCurves.sketchLines
            sketchArcs = sk.sketchCurves.sketchArcs 
            sketchDimensions = sk.sketchDimensions
            sketchConstraints = sk.geometricConstraints
            arcRadius = size / 10           
            sk.name = 'Profile Sketch'
            sk.attributes.add('sketchStyle', 'quarterSketch', 'True')
            # we use quarte as sketch

            point_center_h = adsk.core.Point3D.create(skPnt.geometry.x + size/2, 0, 0)
            horizontalCenterLine = skLines.addByTwoPoints(skPnt,point_center_h)
            horizontalCenterLine.isCenterLine = True
            sketchConstraints.addHorizontal(horizontalCenterLine)

            point_out_v = adsk.core.Point3D.create(skPnt.geometry.x + size/2, skPnt.geometry.x + size/2 - arcRadius, 0)
            outerVerticalLine = skLines.addByTwoPoints(horizontalCenterLine.endSketchPoint,point_out_v)
            arcCenter = adsk.core.Point3D.create(skPnt.geometry.x + size/2 - arcRadius, skPnt.geometry.y + size/2 - arcRadius , 0)
            arc = sketchArcs.addByCenterStartSweep(arcCenter,outerVerticalLine.endSketchPoint,math.radians(90))
            point_out_h = adsk.core.Point3D.create(0, skPnt.geometry.x + size/2, 0)
            outerHorizontalLine = skLines.addByTwoPoints(arc.endSketchPoint,point_out_h)
            verticalCenterLine = skLines.addByTwoPoints(outerHorizontalLine.endSketchPoint,skPnt)
            verticalCenterLine.isCenterLine = True
            sketchConstraints.addVertical(verticalCenterLine)

            sketchConstraints.addTangent(outerVerticalLine, arc)
            sketchConstraints.addTangent(arc, outerHorizontalLine)

            textPoint = adsk.core.Point3D.create(-5,5,0) 
            dimSize = sketchDimensions.addOffsetDimension(horizontalCenterLine, outerHorizontalLine, textPoint)
            textPoint = adsk.core.Point3D.create(5,-5,0)
            dimSize = sketchDimensions.addOffsetDimension(outerVerticalLine, verticalCenterLine, textPoint)
            textPoint = adsk.core.Point3D.create(horizontalCenterLine.endSketchPoint.geometry.x,verticalCenterLine.startSketchPoint.geometry.y,0)
            dimArc = sketchDimensions.addRadialDimension(arc,textPoint)

            
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

        return sk, extrude2

    except:
        futil.log('Failed:\n{}'.format(traceback.format_exc()))    
     