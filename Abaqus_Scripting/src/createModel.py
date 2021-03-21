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

import numpy as np


class CreateModel:
    __path = 'C:/temp/model-test-34'

    __model_name = 'ReinforcedConcrete'
    __concrete_part_name = 'ConcreteCube'
    __steel_part_name_2 = 'SteelRod'
    __concrete_material_name = 'Concrete'
    __steel_material_name = 'Steel'
    __concrete_instance_name = None
    __steel_instance_name = None
    __job_name = None

    __young_steel = 209e9
    __young_concrete = 30e9

    __mesh_size = None
    __as_r = None

    __POISSON_STEEL = 0.3
    __POISSON_CONCRETE = 0.2

    def __init__(self, a, h, r, as_value, a1):
        self.__a = a
        self.__h = h
        self.__r = r
        self.__as = as_value
        self.__a1 = a1

        self.__check_model()

    def __r_calculate(self):
        """r calculate method
        =====================

        Responsible for calculating the radius of the rod in model.
        Takes /as/ value from class, calculate radius and divide it on two rods
        """
        self.__as_r = (self.__as / np.pi) ** 0.5 / 2

    def setter_model_data(self, a, h, r, as_value, a1):
        self.__a = a
        self.__h = h
        self.__r = r
        self.__as = as_value
        self.__a1 = a1

    def __create_model_database(self):
        Mdb()
        self.__model_database = mdb
        self.__model_database.saveAs(pathName=self.__path)
        self.__model_database.Model(name=self.__model_name, modelType=STANDARD_EXPLICIT)

        self.__part_concrete_cube()
        self.__part_steel_rod()
        self.__materials()
        self.__profile_create()
        self.__section_create()
        self.__step_create()
        self.__model_assembly()
        self.__constraints_set()
        self.__boundary_conditions()
        self.__mesh_calculation()
        self.__mesh_set()
        self.__section_assigment()
        self.__job_create()
        self.__save_model()
        self.__job_calculate()

    def edit_model_database(self):
        """Edit model database function
        =============================

        function responsible for calling for another functions, when model is already created. function exists to save time.
        Instead of creating new model it is editing parameters of the existing model.
        """

        self.__part_concrete_cube()
        self.__part_steel_rod()
        self.__profile_create()
        self.__model_assembly()
        self.__constraints_set()
        self.__boundary_conditions()
        self.__mesh_calculation()
        self.__mesh_set()
        self.__section_assigment()
        self.__save_model()
        self.__job_calculate()

    def __check_model(self):
        if self.__path is file:

            pass
        else:
            self.__create_model_database()

    def __save_model(self):
        self.__model_database.save()

    def __part_concrete_cube(self):
        """part concrete cube function
        ==============================

        Function creating 3D cuboid with the dimensions /a/ and /h/ and with the cylindrical hole with dimension /a/
        and /r/
        """

        s = self.__model_database.models[self.__model_name].ConstrainedSketch(name='__profile__', sheetSize=200.0)
        s.setPrimaryObject(option=STANDALONE)

        s.rectangle(point1=(0.0, 0.0), point2=(self.__a, self.__h))
        s.CircleByCenterPerimeter(center=(self.__a / 2, self.__h / 2), point1=(self.__a / 2, self.__h / 2 - self.__r))

        self.__model_database.models[self.__model_name].Part(name=self.__concrete_part_name, dimensionality=THREE_D,
                                                             type=DEFORMABLE_BODY)

        p = self.__model_database.models[self.__model_name].parts[self.__concrete_part_name]
        p.BaseSolidExtrude(sketch=s, depth=self.__a)

        del self.__model_database.models[self.__model_name].sketches['__profile__']

    def __part_steel_rod(self):
        """part steel rod function
        ==============================

        Function creating 2D wire with the dimension /a/
        """

        s = self.__model_database.models[self.__model_name].ConstrainedSketch(name='__profile__', sheetSize=200.0)
        g = s.geometry

        s.setPrimaryObject(option=STANDALONE)
        s.Line(point1=(0.0, 0.0), point2=(self.__a, 0.0))

        s.HorizontalConstraint(entity=g[2], addUndoState=False)

        self.__model_database.models[self.__model_name].Part(name=self.__steel_part_name_2, dimensionality=THREE_D,
                                                             type=DEFORMABLE_BODY)

        p = self.__model_database.models[self.__model_name].parts[self.__steel_part_name_2]
        p.BaseWire(sketch=s)

        del self.__model_database.models[self.__model_name].sketches['__profile__']

        #
        # TODO -> Delete unnecessary 'set'
        #

        e = p.edges
        edges = e.getSequenceFromMask(mask=('[#1 ]',), )
        region = p.Set(edges=edges, name='Set-1')

        p.assignBeamSectionOrientation(region=region, method=N1_COSINES, n1=(0.0, 0.0, -1.0))

    def __materials(self):
        """materials function
        =====================

        Function creating elastic materials with the parameters passed to the class.

        Parameters:
            1. Young module concrete
            2. Young module steel
            3. Poisson ratio concrete
            4. Poisson ratio steel
        """

        self.__model_database.models[self.__model_name].Material(name=self.__steel_material_name)
        self.__model_database.models[self.__model_name].materials[self.__steel_material_name].Elastic(
            table=((self.__young_steel, self.__young_steel),))

        self.__model_database.models[self.__model_name].Material(name=self.__concrete_material_name)
        self.__model_database.models[self.__model_name].materials[self.__concrete_material_name].Elastic(
            table=((self.__young_concrete, self.__young_concrete),))

    def __profile_create(self):
        """profile create function
        ===========================

        Create rod profile for 2D steel rod.

        Parameters:
            1. Radius
        """

        self.__model_database.models[self.__model_name].CircularProfile(name='Rod', r=self.__as_r)

    def __section_create(self):
        """section create function
        ==========================

        Function responsible for creating section for the models from existing materials
        """

        self.__model_database.models[self.__model_name].HomogeneousSolidSection(name='Section-concrete',
                                                                                material=self.__concrete_material_name,
                                                                                thickness=None)

        self.__model_database.models[self.__model_name].BeamSection(name='Section-reinforcement',
                                                                    integration=DURING_ANALYSIS,
                                                                    poissonRatio=0.0, profile='Rod',
                                                                    material=self.__steel_material_name,
                                                                    temperatureVar=LINEAR, consistentMassMatrix=False)

    def __step_create(self):
        """step create function
        =======================

        Creating step for calculations
        """

        self.__model_database.models[self.__model_name].StaticStep(name='Step-1', previous='Initial',
                                                                   maxNumInc=10000, initialInc=0.0001, minInc=1e-10,
                                                                   nlgeom=ON)

    #
    #
    # TODO Refactor what lies below, function to another files (divide on creating and editing), check if database exist
    # Simplify editing model (for faster calculation), Edit parameters of step, documentation!!!
    # PATH, CONFIG, DEBUG,
    #
    #

    def __model_assembly(self):
        a1 = self.__model_database.models[self.__model_name].rootAssembly
        p = self.__model_database.models[self.__model_name].parts[self.__steel_part_name_2]
        a1.Instance(name='SteelRod-1', part=p, dependent=ON)
        a1 = self.__model_database.models[self.__model_name].rootAssembly
        a1.rotate(instanceList=('SteelRod-1',), axisPoint=(0.0, 0.0, 0.0), axisDirection=(10.0, 0.0, 0.0), angle=90.0)
        a1 = self.__model_database.models[self.__model_name].rootAssembly
        a1.rotate(instanceList=('SteelRod-1',), axisPoint=(0.0, 1.0, 0.0), axisDirection=(0.0, -1.0, 0.0), angle=90.0)

        a1 = self.__model_database.models[self.__model_name].rootAssembly
        p = self.__model_database.models[self.__model_name].parts[self.__concrete_part_name]
        a1.Instance(name='ConcreteCube-1', part=p, dependent=ON)

        a1 = self.__model_database.models[self.__model_name].rootAssembly
        a1.translate(instanceList=('SteelRod-1',), vector=(10.0, 0.0, 0.0))
        a1 = self.__model_database.models[self.__model_name].rootAssembly
        a1.translate(instanceList=('SteelRod-1',), vector=(0.0, 2.5, 0.0))

        self.__model_database.save()

    def __constraints_set(self):
        a = self.__model_database.models[self.__model_name].rootAssembly
        e1 = a.instances['SteelRod-1'].edges
        edges1 = e1.getSequenceFromMask(mask=('[#1 ]',), )
        region1 = regionToolset.Region(edges=edges1)

        a = self.__model_database.models[self.__model_name].rootAssembly
        c1 = a.instances['ConcreteCube-1'].cells
        cells1 = c1.getSequenceFromMask(mask=('[#1 ]',), )
        region2 = regionToolset.Region(cells=cells1)

        self.__model_database.models[self.__model_name].EmbeddedRegion(name='Constraint-1', embeddedRegion=region1,
                                                                       hostRegion=region2, weightFactorTolerance=1e-06,
                                                                       absoluteTolerance=0.0, fractionalTolerance=0.05,
                                                                       toleranceMethod=BOTH)
        self.__model_database.save()

        a = self.__model_database.models[self.__model_name].rootAssembly
        e11 = a.instances['ConcreteCube-1'].edges
        a.DatumPointByMidPoint(point1=a.instances['ConcreteCube-1'].InterestingPoint(edge=e11[0], rule=MIDDLE),
                               point2=a.instances['ConcreteCube-1'].InterestingPoint(edge=e11[7], rule=MIDDLE))

        d21 = a.datums

        a.ReferencePoint(point=d21[7])

        a = self.__model_database.models[self.__model_name].rootAssembly
        r1 = a.referencePoints
        refPoints1 = (r1[8],)
        region1 = regionToolset.Region(referencePoints=refPoints1)
        a = self.__model_database.models[self.__model_name].rootAssembly
        s1 = a.instances['ConcreteCube-1'].faces
        side1Faces1 = s1.getSequenceFromMask(mask=('[#20 ]',), )
        region2 = regionToolset.Region(side1Faces=side1Faces1)
        self.__model_database.models[self.__model_name].Coupling(name='Constraint-2', controlPoint=region1,
                                                                 surface=region2,
                                                                 influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC,
                                                                 localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON,
                                                                 ur3=ON)
        self.__model_database.save()

    def __boundary_conditions(self):
        a = self.__model_database.models[self.__model_name].rootAssembly
        f1 = a.instances['ConcreteCube-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#40 ]',), )
        region = regionToolset.Region(faces=faces1)
        self.__model_database.models[self.__model_name].DisplacementBC(name='BC-1', createStepName='Step-1',
                                                                       region=region,
                                                                       u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=0.0,
                                                                       ur3=0.0,
                                                                       amplitude=UNSET, fixed=OFF,
                                                                       distributionType=UNIFORM,
                                                                       fieldName='', localCsys=None)

        a = self.__model_database.models[self.__model_name].rootAssembly
        r1 = a.referencePoints
        refPoints1 = (r1[8],)
        region = regionToolset.Region(referencePoints=refPoints1)
        self.__model_database.models[self.__model_name].DisplacementBC(name='BC-2', createStepName='Step-1',
                                                                       region=region,
                                                                       u1=UNSET, u2=-1.0, u3=UNSET, ur1=UNSET,
                                                                       ur2=UNSET,
                                                                       ur3=UNSET, amplitude=UNSET, fixed=OFF,
                                                                       distributionType=UNIFORM, fieldName='',
                                                                       localCsys=None)
        self.__model_database.models[self.__model_name].boundaryConditions['BC-2'].setValues(u1=-1.0, u2=UNSET)
        self.__model_database.models[self.__model_name].boundaryConditions['BC-2'].setValues(u1=UNSET, u3=-1.0)

    def __mesh_calculation(self):

        pass

    def __mesh_set(self):

        p = self.__model_database.models[self.__model_name].parts[self.__steel_part_name_2]
        p.seedPart(size=2.5, deviationFactor=0.1, minSizeFactor=0.1)
        p = self.__model_database.models[self.__model_name].parts[self.__steel_part_name_2]
        p.generateMesh()

        p = self.__model_database.models[self.__model_name].parts[self.__concrete_part_name]
        p.seedPart(size=2.5, deviationFactor=0.1, minSizeFactor=0.1)
        p = self.__model_database.models[self.__model_name].parts[self.__concrete_part_name]
        p.generateMesh()

    def __section_assigment(self):

        p = self.__model_database.models[self.__model_name].parts[self.__steel_part_name_2]
        e = p.edges
        edges = e.getSequenceFromMask(mask=('[#1 ]',), )
        region = regionToolset.Region(edges=edges)
        p = self.__model_database.models[self.__model_name].parts[self.__steel_part_name_2]
        p.SectionAssignment(region=region, sectionName='Section-reinforcement', offset=0.0, offsetType=MIDDLE_SURFACE,
                            offsetField='', thicknessAssignment=FROM_SECTION)

        p = self.__model_database.models[self.__model_name].parts[self.__concrete_part_name]
        c = p.cells
        cells = c.getSequenceFromMask(mask=('[#1 ]',), )
        region = regionToolset.Region(cells=cells)
        p = self.__model_database.models[self.__model_name].parts[self.__concrete_part_name]
        p.SectionAssignment(region=region, sectionName='Section-concrete', offset=0.0, offsetType=MIDDLE_SURFACE,
                            offsetField='', thicknessAssignment=FROM_SECTION)

    def __job_create(self):

        a = self.__model_database.models[self.__model_name].rootAssembly
        a.regenerate()

        self.__model_database.Job(name='Job-1', model=self.__model_name, description='', type=ANALYSIS,
                                  atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
                                  memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
                                  explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
                                  modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
                                  scratch='', resultsFormat=ODB)

    def __job_calculate(self):
        self.__model_database.jobs['Job-1'].submit(consistencyChecking=OFF)


CreateModel()
