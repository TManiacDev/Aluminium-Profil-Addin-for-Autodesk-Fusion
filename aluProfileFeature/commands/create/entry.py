import adsk.core, adsk.fusion 
import os, math, traceback
from ....lib import fusion360utils as futil

app = adsk.core.Application.get()
ui = app.userInterface

def start():
    app.log('Start the feature create command')