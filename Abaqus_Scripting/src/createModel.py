from abaqus import *
from abaqusConstants import *
import __main__

import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior


class CreateModel:
    __path = 'C:/temp/model-test-3'
    __name = None
    __model_name = 'ReinforcedConcrete'

    __concrete_part_name = 'ConcreteCube'
    __concrete_part_name_2 = 'SteelRod'

    __a = 20
    __h = 25
    __r = 7.5

    def __init__(self):
        Mdb()
        model_data_base = mdb
        model_data_base.saveAs(pathName=self.__path)

        model_data_base.Model(name=self.__model_name, modelType=STANDARD_EXPLICIT)
        s = model_data_base.models[self.__model_name].ConstrainedSketch(name='__profile__', sheetSize=200.0)

        s.setPrimaryObject(option=STANDALONE)

        # prostokat
        s.rectangle(point1=(0.0, 0.0), point2=(self.__a, self.__h))

        # wyciecie
        s.CircleByCenterPerimeter(center=(self.__a / 2, self.__h / 2), point1=(self.__a / 2, self.__h / 2 - self.__r))

        model_data_base.models[self.__model_name].Part(name=self.__concrete_part_name, dimensionality=THREE_D,
                                                       type=DEFORMABLE_BODY)

        p = model_data_base.models[self.__model_name].parts[self.__concrete_part_name]
        p.BaseSolidExtrude(sketch=s, depth=self.__a)

        del model_data_base.models[self.__model_name].sketches['__profile__']

        model_data_base.save()

        """ tworzenie kolejnej czesci"""

        s = model_data_base.models[self.__model_name].ConstrainedSketch(name='__profile__', sheetSize=200.0)
        g = s.geometry

        s.setPrimaryObject(option=STANDALONE)
        s.Line(point1=(0.0, 0.0), point2=(self.__a, 0.0))

        s.HorizontalConstraint(entity=g[2], addUndoState=False)

        model_data_base.models[self.__model_name].Part(name=self.__concrete_part_name_2, dimensionality=THREE_D,
                                                       type=DEFORMABLE_BODY)

        p = model_data_base.models[self.__model_name].parts[self.__concrete_part_name_2]
        p.BaseWire(sketch=s)

        del model_data_base.models[self.__model_name].sketches['__profile__']

        e = p.edges
        edges = e.getSequenceFromMask(mask=('[#1 ]',), )
        region = p.Set(edges=edges, name='Set-1')

        p.assignBeamSectionOrientation(region=region, method=N1_COSINES, n1=(0.0, 0.0, -1.0))

        """ tworzenie materialow """

        model_data_base.models[self.__model_name].Material(name='Steel')
        model_data_base.models[self.__model_name].materials['Steel'].Elastic(table=((209000000000.0, 0.2),))
        model_data_base.models[self.__model_name].Material(name='Concrete')
        model_data_base.models[self.__model_name].materials['Concrete'].Elastic(table=((30000000000.0, 0.3),))

        """przypisywanie sections"""
        model_data_base.models[self.__model_name].CircularProfile(name='Rod', r=5.0)

        model_data_base.models[self.__model_name].HomogeneousSolidSection(name='Section-concrete', material='Concrete',
                                                                          thickness=None)

        model_data_base.models[self.__model_name].BeamSection(name='Section-reinforcement', integration=DURING_ANALYSIS,
                                                              poissonRatio=0.0, profile='Rod', material='Steel',
                                                              temperatureVar=LINEAR, consistentMassMatrix=False)
        """create step"""

        model_data_base.models[self.__model_name].StaticStep(name='Step-1', previous='Initial',
                                                             maxNumInc=10000, initialInc=0.0001, minInc=1e-10,
                                                             nlgeom=ON)

        """ assembly """

        a1 = model_data_base.models[self.__model_name].rootAssembly
        p = model_data_base.models[self.__model_name].parts[self.__concrete_part_name_2]
        a1.Instance(name='SteelRod-1', part=p, dependent=ON)
        a1 = model_data_base.models[self.__model_name].rootAssembly
        a1.rotate(instanceList=('SteelRod-1',), axisPoint=(0.0, 0.0, 0.0), axisDirection=(10.0, 0.0, 0.0), angle=90.0)
        a1 = model_data_base.models[self.__model_name].rootAssembly
        a1.rotate(instanceList=('SteelRod-1',), axisPoint=(0.0, 1.0, 0.0), axisDirection=(0.0, -1.0, 0.0), angle=90.0)

        a1 = model_data_base.models[self.__model_name].rootAssembly
        p = model_data_base.models[self.__model_name].parts[self.__concrete_part_name]
        a1.Instance(name='ConcreteCube-1', part=p, dependent=ON)

        a1 = model_data_base.models[self.__model_name].rootAssembly
        a1.translate(instanceList=('SteelRod-1',), vector=(10.0, 0.0, 0.0))
        a1 = model_data_base.models[self.__model_name].rootAssembly
        a1.translate(instanceList=('SteelRod-1',), vector=(0.0, 2.5, 0.0))

        model_data_base.save()

        """constraints"""

        a = model_data_base.models[self.__model_name].rootAssembly
        e1 = a.instances['SteelRod-1'].edges
        edges1 = e1.getSequenceFromMask(mask=('[#1 ]',), )
        region1 = regionToolset.Region(edges=edges1)

        a = model_data_base.models[self.__model_name].rootAssembly
        c1 = a.instances['ConcreteCube-1'].cells
        cells1 = c1.getSequenceFromMask(mask=('[#1 ]',), )
        region2 = regionToolset.Region(cells=cells1)

        model_data_base.models[self.__model_name].EmbeddedRegion(name='Constraint-1', embeddedRegion=region1,
                                                                 hostRegion=region2, weightFactorTolerance=1e-06,
                                                                 absoluteTolerance=0.0, fractionalTolerance=0.05,
                                                                 toleranceMethod=BOTH)
        model_data_base.save()

        a = model_data_base.models[self.__model_name].rootAssembly
        e11 = a.instances['ConcreteCube-1'].edges
        a.DatumPointByMidPoint(point1=a.instances['ConcreteCube-1'].InterestingPoint(edge=e11[0], rule=MIDDLE),
                               point2=a.instances['ConcreteCube-1'].InterestingPoint(edge=e11[7], rule=MIDDLE))

        # a = model_data_base.models[self.__model_name].rootAssembly
        d21 = a.datums

        a.ReferencePoint(point=d21[7])

        a = model_data_base.models[self.__model_name].rootAssembly
        r1 = a.referencePoints
        refPoints1 = (r1[8],)
        region1 = regionToolset.Region(referencePoints=refPoints1)
        a = model_data_base.models[self.__model_name].rootAssembly
        s1 = a.instances['ConcreteCube-1'].faces
        side1Faces1 = s1.getSequenceFromMask(mask=('[#20 ]',), )
        region2 = regionToolset.Region(side1Faces=side1Faces1)
        model_data_base.models[self.__model_name].Coupling(name='Constraint-2', controlPoint=region1, surface=region2,
                                                           influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC,
                                                           localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)
        model_data_base.save()

        """boundary conditions"""

        a = model_data_base.models[self.__model_name].rootAssembly
        f1 = a.instances['ConcreteCube-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#40 ]',), )
        region = regionToolset.Region(faces=faces1)
        model_data_base.models[self.__model_name].DisplacementBC(name='BC-1', createStepName='Step-1', region=region,
                                                                 u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, ur3=0.0,
                                                                 amplitude=UNSET, fixed=OFF, distributionType=UNIFORM,
                                                                 fieldName='', localCsys=None)

        a = model_data_base.models[self.__model_name].rootAssembly
        r1 = a.referencePoints
        refPoints1 = (r1[8],)
        region = regionToolset.Region(referencePoints=refPoints1)
        model_data_base.models[self.__model_name].DisplacementBC(name='BC-2', createStepName='Step-1', region=region,
                                                                 u1=UNSET, u2=-1.0, u3=UNSET, ur1=UNSET, ur2=UNSET,
                                                                 ur3=UNSET, amplitude=UNSET, fixed=OFF,
                                                                 distributionType=UNIFORM, fieldName='', localCsys=None)
        model_data_base.models[self.__model_name].boundaryConditions['BC-2'].setValues(u1=-1.0, u2=UNSET)
        model_data_base.models[self.__model_name].boundaryConditions['BC-2'].setValues(u1=UNSET, u3=-1.0)

        """Mesh"""

        p = model_data_base.models[self.__model_name].parts[self.__concrete_part_name_2]
        p.seedPart(size=2.5, deviationFactor=0.1, minSizeFactor=0.1)
        p = model_data_base.models[self.__model_name].parts[self.__concrete_part_name_2]
        p.generateMesh()

        p = model_data_base.models[self.__model_name].parts[self.__concrete_part_name]
        p.seedPart(size=2.5, deviationFactor=0.1, minSizeFactor=0.1)
        p = model_data_base.models[self.__model_name].parts[self.__concrete_part_name]
        p.generateMesh()



        """section assignment"""

        p = model_data_base.models[self.__model_name].parts[self.__concrete_part_name_2]
        e = p.edges
        edges = e.getSequenceFromMask(mask=('[#1 ]',), )
        region = regionToolset.Region(edges=edges)
        p = model_data_base.models[self.__model_name].parts[self.__concrete_part_name_2]
        p.SectionAssignment(region=region, sectionName='Section-reinforcement', offset=0.0, offsetType=MIDDLE_SURFACE,
                            offsetField='', thicknessAssignment=FROM_SECTION)

        p = model_data_base.models[self.__model_name].parts[self.__concrete_part_name]
        c = p.cells
        cells = c.getSequenceFromMask(mask=('[#1 ]',), )
        region = regionToolset.Region(cells=cells)
        p = model_data_base.models[self.__model_name].parts[self.__concrete_part_name]
        p.SectionAssignment(region=region, sectionName='Section-concrete', offset=0.0, offsetType=MIDDLE_SURFACE,
                            offsetField='', thicknessAssignment=FROM_SECTION)


        """jobs"""
        a = model_data_base.models[self.__model_name].rootAssembly
        a.regenerate()

        model_data_base.Job(name='Job-1', model=self.__model_name, description='', type=ANALYSIS,
                atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
                memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
                explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
                modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
                scratch='', resultsFormat=ODB)
        model_data_base.jobs['Job-1'].submit(consistencyChecking=OFF)

        model_data_base.save()

CreateModel()
