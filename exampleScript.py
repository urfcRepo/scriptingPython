  # Código 9. Script de  generación de slices y cálculo de variables de interés
  # flujoMasico.py
  #se crean cortes sobre eje Y para encontrar valores promedio
  #los datos calculados son almacenados en archivo .csv
from paraview.simple import *
import numpy as np
path = '/media/urfc/27ee57f4-3055-49c0-99fd-2c01ecaeb241/doctorado/'
case = 'fluido5MMnormal/fluido5MMnormal.OpenFOAM'
areaI = []
flujoVol =  []
avgVelocidad =  []
avgPresion = []
avgPresionTotal = []
openFOAMReader1= OpenFOAMReader(FileName= path + case)
# Properties modified on openFOAMReader1
openFOAMReader1.MeshRegions = ['internalMesh']
openFOAMReader1.CellArrays = ['U', 'p']
SetActiveSource(openFOAMReader1)
# get active view
renderView1 = FindViewOrCreate('RenderView1', 'RenderView')
# show data in view
openFOAMReader1Display = Show(openFOAMReader1, renderView1)
# get animation scene
animationScene1 = GetAnimationScene()
# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()
# Check the current view time
renderView1.ViewTime
#  set the last timestep case
tsteps = openFOAMReader1.TimestepValues
renderView1.ViewTime = tsteps[len(tsteps)-1]
# set scalar coloring
ColorBy(openFOAMReader1Display, ('POINTS', 'U', 'Magnitude'))
Render()
#Set active source
SetActiveSource(openFOAMReader1)
SliceFile = GetActiveSource()
#get data from slice to analyze
#DataSliceFile = paraview.servermanager.Fetch(SliceFile) 
#generate coord Y values of slice in GDL zone
originY = np.arange(11e-5,-7e-5, -.5e-5 )
normal = [0.0, 1.0, 0.0]
for sliceId in range (len(originY)):
    origin = [0.0022499999176943675, originY[sliceId], 0.0024600000760983676]
    #apply slice filter to get selected surface of cell 
    salidaGDL = Slice(Input=openFOAMReader1)
    salidaGDL.SliceType.Origin = origin
    salidaGDL.SliceType.Normal = normal
    salidaGDL.SliceType = 'Plane'
    salidaGDL.SliceOffsetValues = [0.0]
    #Display slice on renderView
    salidaGDLDisplay = Show(salidaGDL, renderView1)
    ColorBy(salidaGDLDisplay , ('POINTS', 'U', 'Magnitude'))
    renderView1 = GetActiveViewOrCreate('RenderView')
    Hide(openFOAMReader1, renderView1)
    # create a  velocity magnitude Calculator for each cell in GDL
    calculator1 = Calculator(Input=salidaGDL)
    calculator1.AttributeType = 'Cell Data'
    calculator1.ResultArrayName = 'magnitud'
    calculator1.Function = 'mag(U)' 
    # Integrate Variables to calculate volumetric flow
    integrateVariables1 = IntegrateVariables(Input=calculator1)
    # create an average pressure Calculator
    calculator2 = Calculator(Input=integrateVariables1)
    calculator2.AttributeType = 'Cell Data'
    calculator2.ResultArrayName = 'avgPresion'
    calculator2.Function = 'p/Area'
    # create an average velocity Calculator
    calculator3 = Calculator(Input=calculator2)
    calculator3.AttributeType = 'Cell Data'
    calculator3.ResultArrayName = 'avgVelocidad'
    calculator3.Function = 'magnitud/Area'
    # create a total pressure Calculator (cinematic pressure*rho)
    calculator4 = Calculator(Input=calculator3)
    calculator4.AttributeType = 'Cell Data'
    calculator4.ResultArrayName = 'avgPresionTotal'
    calculator4.Function = 'avgPresion*1.2999'
    #get data from calculators
    SetActiveSource(calculator4)
    CalculatorFile = GetActiveSource()
    DataCalculator = paraview.servermanager.Fetch(CalculatorFile)
    areaI.append( DataCalculator.GetCellData().GetArray('Area').GetTuple(0))
    flujoVol.append( DataCalculator.GetCellData().GetArray('magnitud').GetTuple(0) )
    avgVelocidad.append( DataCalculator.GetCellData().GetArray('avgVelocidad').GetTuple(0) )    
    avgPresionTotal.append(  DataCalculator.GetCellData().GetArray('avgPresionTotal').GetTuple(0) )            
#write calculated data  in file             
outputFile ='myFile.csv'
fw = open(path + outputFile, 'w')
fw.write(',sliceId')
fw.write(',area[m2]')
fw.write(',flujoVol[m3/s]')
fw.write(',avgPresion[m2/s2]')
fw.write(',avgVelocidad[m/s]')
fw.write(',avgPresionTotal[kg/ms2]')
fw.write('\n')
tamArreglo = len(originY)
for sliceId in range (tamArreglo):
    fw.write(',' + str(sliceId))
    fw.write(',' + str(areaI[sliceId][0]))
    fw.write(',' + str(flujoVol[sliceId][0]))
    fw.write(',' + str(avgVelocidad[sliceId][0]))
    fw.write(',' + str(avgPresionTotal[sliceId][0]))
    fw.write('\n')
#close file
fw.close()