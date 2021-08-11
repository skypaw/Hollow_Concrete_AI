import os
from abaqus import *
from abaqusConstants import *
import numpy as np
import constant_values as const
import change_input as c_input
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

import model_functions as m_functions
from log import log


class Model:
    _path = const.MODEL_DATABASE_NAME

    _model_name = const.MODEL_NAME
    _steel_material_name = const.REINFORCEMENT_MATERIAL_NAME
    _concrete_material_name = const.SOLID_MATERIAL_NAME
    _young_reinforcement = const.YOUNG_REINFORCEMENT
    _young_concrete = const.YOUNG_CONCRETE
    _cube_part_name = const.SOLID_PART_NAME
    _reinforcement_part_name = const.REINFORCEMENT_PART_NAME
    _POISSON_REINFORCEMENT = const.POISSON_REINFORCEMENT
    _POISSON_CONCRETE = const.POISSON_CONCRETE
    _cube_part_name_assembly = const.SOLID_ASSEMBLY_NAME
    _reinforcement_part_name_assembly = const.REINFORCEMENT_ASSEMBLY_NAME
    _job_name = const.JOB_NAME

    _model_database = None  # CEA database
    _model_parameters = None  # database with model name

    _i = None
    _a = None
    _h = None
    _as = None
    _a1 = None
    _r = None
    _l = None

    def __init__(self):
        os.chdir(r"C:\temp")

    def set_dimensions(self, i, a, h, a_s, a1, r, l):
        self._i = int(i)
        self._a = a
        self._h = h
        self._as = a_s
        self._a1 = a1
        self._r = r
        self._l = l

    def get_dimensions(self):
        return [self._i, self._a, self._h, self._as, self._a1, self._r, self._l]

    def check_dimensions(self):
        m_functions.r_calculate(self._as)
        m_functions.mesh_calculation(self._a, self._h)
        self._r, self._l, self._a1 = m_functions.check_dimensions(self._r, self._l, self._a, self._a1, self._h)

    def create_database(self):
        self._create_model_database()

    def _save_model(self):
        self._model_database.save()

    def _materials(self):
        """materials function
        =====================

        Function creating elastic materials with the parameters passed to the class. For two materials - main and
        reinforcement

        Parameters:
            1. Young module concrete
            2. Young module steel
            3. Poisson ratio concrete
            4. Poisson ratio steel
        """

        self._model_parameters.Material(name=self._steel_material_name)
        self._model_parameters.materials[self._steel_material_name].Elastic(table=((self._young_reinforcement,
                                                                                    self._POISSON_REINFORCEMENT),))

        self._model_parameters.Material(name=self._concrete_material_name)
        self._model_parameters.materials[self._concrete_material_name].Elastic(table=((self._young_concrete,
                                                                                       self._POISSON_CONCRETE),))

    def _section_create(self):
        """section create function
        ==========================

        Function responsible for creating section for the models from existing materials.
        """
        as_area = m_functions.r_calculate(self._as)

        self._model_parameters.HomogeneousSolidSection(name='Section-concrete',
                                                       material=self._concrete_material_name,
                                                       thickness=None)

        self._model_parameters.TrussSection(name='Section-reinforcement',
                                            material=self._steel_material_name,
                                            area=as_area)

    def _step_create(self):
        """step create function
        =======================

        Creating basic step for calculations, in order to simplify replacement in input file in later steps.
        Later is replaced by @changeInput
        """

        self._model_parameters.StaticStep(name='Step-1', previous='Initial', maxNumInc=10000, initialInc=1,
                                          minInc=1e-10, nlgeom=ON)

    def _model_assembly(self):
        """model_assembly
        =================

        Function responsible for placing reinforcement rods in the model, and assembly it for calculations
        """

        a = self._model_parameters.rootAssembly
        a.DatumCsysByDefault(CARTESIAN)

        a1 = self._model_parameters.rootAssembly
        p = self._model_parameters.parts[
            self._reinforcement_part_name.format('1')]

        a1.Instance(name='SteelRod-1', part=p, dependent=ON)
        a1 = self._model_parameters.rootAssembly
        a1.rotate(instanceList=('SteelRod-1',), axisPoint=(0.0, 1.0, 0.0), axisDirection=(0.0, -1.0, 0.0), angle=90.0)

        a1 = self._model_parameters.rootAssembly
        p = self._model_parameters.parts[
            self._reinforcement_part_name.format('2')]

        a1.Instance(name='SteelRod-2', part=p, dependent=ON)
        a1 = self._model_parameters.rootAssembly
        a1.rotate(instanceList=('SteelRod-2',), axisPoint=(0.0, 1.0, 0.0), axisDirection=(0.0, -1.0, 0.0), angle=90.0)

        a1 = self._model_parameters.rootAssembly
        p = self._model_parameters.parts[self._cube_part_name]

        a1.Instance(name='ConcreteCube-1', part=p, dependent=ON)
        a1 = self._model_parameters.rootAssembly
        a1.translate(instanceList=('SteelRod-1',), vector=(self._a - self._a1, self._a1, 0.0))
        a1.translate(instanceList=('SteelRod-2',), vector=(self._a1, self._a1, 0.0))

        a1 = self._model_parameters.rootAssembly
        a1.rotate(instanceList=('SteelRod-1', 'SteelRod-2', 'ConcreteCube-1'),
                  axisPoint=(0.0, 0.0, 0.0), axisDirection=(10.0, 0.0, 0.0), angle=90.0)
        a1 = self._model_parameters.rootAssembly

        a1.translate(instanceList=('SteelRod-1', 'SteelRod-2', 'ConcreteCube-1'),
                     vector=(0.0, self._a, 0.0))

        self._save_model()

    def _constraint_set(self):
        """constrain_set
        =================

        Set constraint in order to take into account impact of the reinforcement in model
        """

        a = self._model_parameters.rootAssembly
        e1 = a.instances['SteelRod-1'].edges
        edges1 = e1.getSequenceFromMask(mask=('[#1 ]',), )
        e2 = a.instances['SteelRod-2'].edges
        edges2 = e2.getSequenceFromMask(mask=('[#1 ]',), )
        region1 = regionToolset.Region(edges=edges1 + edges2)
        c1 = a.instances['ConcreteCube-1'].cells
        cells1 = c1.getSequenceFromMask(mask=('[#1 ]',), )
        region2 = regionToolset.Region(cells=cells1)
        self._model_parameters.EmbeddedRegion(name='Constraint-1', embeddedRegion=region1, hostRegion=region2,
                                              weightFactorTolerance=1e-06, absoluteTolerance=0.0,
                                              fractionalTolerance=0.05, toleranceMethod=BOTH)

        self._save_model()

    def _mesh_set(self):
        """mesh_set
        =================

        Creating mesh for parts. Truss element for reinforcement, solid element for concrete
        """

        mesh_size = m_functions.mesh_calculation(self._a, self._h)

        p = self._model_parameters.parts[self._cube_part_name]
        p.seedPart(size=mesh_size, deviationFactor=0.1, minSizeFactor=0.1)
        p.generateMesh()

        elemType1 = mesh.ElemType(elemCode=T3D2, elemLibrary=STANDARD)
        p = self._model_parameters.parts[
            self._reinforcement_part_name.format('1')]
        e = p.edges
        edges = e.getSequenceFromMask(mask=('[#1 ]',), )
        pickedRegions = (edges,)
        p.setElementType(regions=pickedRegions, elemTypes=(elemType1,))
        p.seedPart(size=mesh_size, deviationFactor=0.1, minSizeFactor=0.1)
        p.generateMesh()

        self._save_model()

    def _section_assigment(self):
        """section_assigment
        ====================

        Assigning section for parts with materials data.
        """

        p = self._model_parameters.parts[self._reinforcement_part_name]
        e = p.edges
        edges = e.getSequenceFromMask(mask=('[#1 ]',), )
        region = regionToolset.Region(edges=edges)
        p.SectionAssignment(region=region, sectionName='Section-reinforcement', offset=0.0, offsetType=MIDDLE_SURFACE,
                            offsetField='', thicknessAssignment=FROM_SECTION)

        p = self._model_parameters.parts[self._cube_part_name]
        c = p.cells
        cells = c.getSequenceFromMask(mask=('[#1 ]',), )
        region = regionToolset.Region(cells=cells)
        p.SectionAssignment(region=region, sectionName='Section-concrete', offset=0.0, offsetType=MIDDLE_SURFACE,
                            offsetField='', thicknessAssignment=FROM_SECTION)

        self._save_model()

    def _job_create(self):
        """job_create
        =============

        Creating a job in order to write input of the model and later stiffness matrix calculation.
        """

        a = self._model_parameters.rootAssembly
        a.regenerate()

        self._model_database.Job(name=self._job_name.format(self._i), model=self._model_name,
                                 description='', type=ANALYSIS,
                                 atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
                                 memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
                                 explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
                                 modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
                                 scratch='C:/temp/', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1,
                                 numGPUs=0)
        self._save_model()

    def _job_write_and_change_input_calculation(self):
        """job write and change input calculation
        =========================================

        Writing input of the file, change step parameters, creating job after input changes and calculating stiffness
        matrix
        """

        job_name_changed = const.JOB_NAME_CHANGED

        self._model_database.jobs[self._job_name.format(self._i)].writeInput(consistencyChecking=OFF)
        self._model_database.jobs[self._job_name.format(self._i)].waitForCompletion()

        c_input.change_input(self._job_name.format(self._i), job_name_changed.format(self._i))

        del self._model_database.jobs[self._job_name.format(self._i)]
        self._model_database.JobFromInputFile(name=job_name_changed.format(self._i),
                                              inputFileName='C:\\temp\\{}.inp'.format(job_name_changed.format(self._i)),
                                              type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None,
                                              memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
                                              explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE,
                                              userSubroutine='', scratch='', resultsFormat=ODB,
                                              multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)

        self._model_database.jobs[job_name_changed.format(self._i)].submit(consistencyChecking=OFF)
        self._model_database.jobs[job_name_changed.format(self._i)].waitForCompletion()

        self._save_model()

    def model_delete(self):
        """model delete
        ===============

        Deleting model to make possible overwriting old database with new values
        """

        self._model_database.Model(name='Model-1', modelType=STANDARD_EXPLICIT)
        del self._model_parameters
        del self._model_database.jobs[self._job_name.format(self._i)]

    def _part_concrete_cube(self):
        """part concrete cube function
        ==============================

        Function creating 3D cuboid with the dimensions /a/ and /h/ and with the cylindrical hole with dimension /a/
        and /r/
        """

        if self._l == 0:
            s = self._model_parameters.ConstrainedSketch(name='__profile__',
                                                         sheetSize=self._a)
            s.setPrimaryObject(option=STANDALONE)

            s.rectangle(point1=(0.0, 0.0), point2=(self._a, self._h))
            s.CircleByCenterPerimeter(center=(self._a / 2, self._h / 2),
                                      point1=(self._a / 2, self._h / 2 - self._r))

            self._model_parameters.Part(name=self._cube_part_name,
                                        dimensionality=THREE_D,
                                        type=DEFORMABLE_BODY)

            p = self._model_parameters.parts[self._cube_part_name]
            p.BaseSolidExtrude(sketch=s, depth=self._a)

            del self._model_parameters.sketches['__profile__']

        else:
            s = self._model_parameters.ConstrainedSketch(name='__profile__',
                                                         sheetSize=self._a)
            s.setPrimaryObject(option=STANDALONE)

            s.rectangle(point1=(0.0, 0.0), point2=(self._a, self._h))

            down_point_line = self._h / 2 - self._l / 2
            up_point_line = self._h / 2 + self._l / 2
            left_point_line = self._a / 2 - self._r
            right_point_line = self._a / 2 + self._r

            s.Line(point1=(left_point_line, down_point_line), point2=(left_point_line, up_point_line))
            s.Line(point1=(right_point_line, down_point_line), point2=(right_point_line, up_point_line))

            s.ArcByCenterEnds(center=(self._a / 2, up_point_line), point1=(left_point_line, up_point_line),
                              point2=(right_point_line, up_point_line), direction=CLOCKWISE)
            s.ArcByCenterEnds(center=(self._a / 2, down_point_line), point1=(right_point_line, down_point_line),
                              point2=(left_point_line, down_point_line), direction=CLOCKWISE)

            self._model_parameters.Part(name=self._cube_part_name,
                                        dimensionality=THREE_D,
                                        type=DEFORMABLE_BODY)

            p = self._model_parameters.parts[self._cube_part_name]
            p.BaseSolidExtrude(sketch=s, depth=self._a)

            del self._model_parameters.sketches['__profile__']

    def _part_steel_rod(self):
        """part steel rod function
        ==============================

        Function creating 2D wire with the dimension /a/
        """

        s = self._model_parameters.ConstrainedSketch(name='__profile__',
                                                     sheetSize=200.0)
        g = s.geometry

        s.setPrimaryObject(option=STANDALONE)
        s.Line(point1=(0.0, 0.0), point2=(self._a, 0.0))

        s.HorizontalConstraint(entity=g[2], addUndoState=False)

        self._model_parameters.Part(name=self._reinforcement_part_name,
                                    dimensionality=THREE_D,
                                    type=DEFORMABLE_BODY)

        p = self._model_parameters.parts[self._reinforcement_part_name]
        p.BaseWire(sketch=s)

        del self._model_parameters.sketches['__profile__']

        e = p.edges
        edges = e.getSequenceFromMask(mask=('[#1 ]',), )
        region = regionToolset.Region(edges=edges)

        p.assignBeamSectionOrientation(region=region, method=N1_COSINES, n1=(0.0, 0.0, -1.0))

    def _create_model_database(self):
        # Creating database and assigning correct name and path
        Mdb()
        self._model_database = mdb
        self._model_database.saveAs(pathName=self._path)
        self._model_database.models.changeKey(fromName='Model-1', toName=self._model_name)
        self._model_parameters = self._model_database.models[self._model_name.format(self._i)]

        # Creating model
        self._materials()
        self._section_create()
        self._step_create()
        self._job_create()
        self._part_concrete_cube()
        self._part_steel_rod()

        self._model_assembly()
        self._mesh_set()
        self._section_assigment()
        self._constraint_set()

        self._job_write_and_change_input_calculation()
        self._save_model()
