import os
from time import sleep
import subprocess

from abaqus import *
from abaqusConstants import *
import numpy as np
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

from log import log

class Model:
    _path = 'C:/temp/model-test-34'

    _model_database = None

    _model_name = 'Hollow-Concrete-{}'
    _steel_material_name = 'Steel'
    _concrete_material_name = 'Concrete'
    _young_reinforcement = 209e9
    _young_concrete = 30e9
    _cube_part_name = 'Concrete-Cube'
    _reinforcement_part_name = 'Steel-Rod'

    _cube_part_name_assembly = 'Concrete-Cube-1'
    _reinforcement_part_name_assembly = 'Steel-Rod-{}'

    __mesh_size = None

    _POISSON_REINFORCEMENT = 0.3
    _POISSON_CONCRETE = 0.2

    _a = None
    _h = None
    _as = None
    _a1 = None
    _r = None
    _l = None
    _c_nom = None

    _as_r = 5

    i = 0

    def __init__(self):
        os.chdir(r"C:\temp")

    def _save_model(self):
        self._model_database.save()

    def __r_calculate(self):
        """r calculate method
        =====================

        Responsible for calculating the radius of the rod in model.
        Takes /as/ value from class, calculate radius and divide it on two rods
        """
        self._as_r = (self._as / np.pi) ** 0.5 / 2

    def _materials(self):
        """materials function
        =====================

        Function creating elastic materials with the parameters passed to the class.

        Parameters:
            1. Young module concrete
            2. Young module steel
            3. Poisson ratio concrete
            4. Poisson ratio steel
        """

        self._model_database.models[self._model_name.format(self.i)].Material(name=self._steel_material_name)
        self._model_database.models[self._model_name.format(self.i)].materials[self._steel_material_name].Elastic(
            table=((self._young_reinforcement, self._POISSON_REINFORCEMENT),))

        self._model_database.models[self._model_name.format(self.i)].Material(name=self._concrete_material_name)
        self._model_database.models[self._model_name.format(self.i)].materials[self._concrete_material_name].Elastic(
            table=((self._young_concrete, self._POISSON_CONCRETE),))

    def _profile_create(self):
        """profile create function
        ===========================

        Create rod profile for 2D steel rod.

        Parameters:
            1. Radius
        """

        self.__r_calculate()
        self._model_database.models[self._model_name.format(self.i)].CircularProfile(name='Rod', r=self._as_r)

    def _section_create(self):
        """section create function
        ==========================

        Function responsible for creating section for the models from existing materials
        """

        self._model_database.models[self._model_name.format(self.i)].HomogeneousSolidSection(name='Section-concrete',
                                                                                             material=self._concrete_material_name,
                                                                                             thickness=None)

        self._model_database.models[self._model_name.format(self.i)].BeamSection(name='Section-reinforcement',
                                                                                 integration=DURING_ANALYSIS,
                                                                                 poissonRatio=0.0, profile='Rod',
                                                                                 material=self._steel_material_name,
                                                                                 temperatureVar=LINEAR,
                                                                                 consistentMassMatrix=False)

    def _step_create(self):
        """step create function
        =======================

        Creating step for calculations
        """

        self._model_database.models[self._model_name.format(self.i)].StaticStep(name='Step-1', previous='Initial',
                                                                                maxNumInc=10000, initialInc=1,
                                                                                minInc=1e-10,
                                                                                nlgeom=ON)

    #
    #
    # TODO Refactor what lies below, function to another files (divide on creating and editing), check if database exist
    # Simplify editing model (for faster calculation), Edit parameters of step, documentation!!!
    #
    #

    def _model_assembly(self):
        a1 = self._model_database.models[self._model_name.format(self.i)].rootAssembly
        p = self._model_database.models[self._model_name.format(self.i)].parts[
            self._reinforcement_part_name.format('1')]

        a1.Instance(name='SteelRod-1', part=p, dependent=ON)
        a1 = self._model_database.models[self._model_name.format(self.i)].rootAssembly
        a1.rotate(instanceList=('SteelRod-1',), axisPoint=(0.0, 1.0, 0.0), axisDirection=(0.0, -1.0, 0.0), angle=90.0)

        a1 = self._model_database.models[self._model_name.format(self.i)].rootAssembly
        p = self._model_database.models[self._model_name.format(self.i)].parts[
            self._reinforcement_part_name.format('1')]

        a1.Instance(name='SteelRod-2', part=p, dependent=ON)
        a1 = self._model_database.models[self._model_name.format(self.i)].rootAssembly
        a1.rotate(instanceList=('SteelRod-2',), axisPoint=(0.0, 1.0, 0.0), axisDirection=(0.0, -1.0, 0.0), angle=90.0)

        a1 = self._model_database.models[self._model_name.format(self.i)].rootAssembly
        p = self._model_database.models[self._model_name.format(self.i)].parts[self._cube_part_name]

        a1.Instance(name='ConcreteCube-1', part=p, dependent=ON)
        a1 = self._model_database.models[self._model_name.format(self.i)].rootAssembly
        a1.translate(instanceList=('SteelRod-1',), vector=(self._a - self._a1, self._a1, 0.0))
        a1.translate(instanceList=('SteelRod-2',), vector=(self._a1, self._a1, 0.0))

        self._save_model()

    def _constraints_set(self):
        a = self._model_database.models[self._model_name.format(self.i)].rootAssembly
        e1 = a.instances['SteelRod-1'].edges
        edges1 = e1.getSequenceFromMask(mask=('[#1 ]',), )
        e2 = a.instances['SteelRod-2'].edges
        edges2 = e2.getSequenceFromMask(mask=('[#1 ]',), )
        region1 = regionToolset.Region(edges=edges1 + edges2)
        c1 = a.instances['ConcreteCube-1'].cells
        cells1 = c1.getSequenceFromMask(mask=('[#1 ]',), )
        region2 = regionToolset.Region(cells=cells1)
        self._model_database.models[self._model_name.format(self.i)].EmbeddedRegion(name='Constraint-1',
                                                                                    embeddedRegion=region1,
                                                                                    hostRegion=region2,
                                                                                    weightFactorTolerance=1e-06,
                                                                                    absoluteTolerance=0.0,
                                                                                    fractionalTolerance=0.05,
                                                                                    toleranceMethod=BOTH)

        a = self._model_database.models[self._model_name.format(self.i)].rootAssembly
        e11 = a.instances['ConcreteCube-1'].edges
        a.DatumPointByMidPoint(point1=a.instances['ConcreteCube-1'].InterestingPoint(edge=e11[0], rule=MIDDLE),
                               point2=a.instances['ConcreteCube-1'].InterestingPoint(edge=e11[7], rule=MIDDLE))

        d21 = a.datums

        self._save_model()

        a.ReferencePoint(point=d21[9])

        a = self._model_database.models[self._model_name.format(self.i)].rootAssembly
        r1 = a.referencePoints
        refPoints1 = (r1[10],)
        region1 = regionToolset.Region(referencePoints=refPoints1)
        a = self._model_database.models[self._model_name.format(self.i)].rootAssembly
        s1 = a.instances['ConcreteCube-1'].faces
        side1Faces1 = s1.getSequenceFromMask(mask=('[#20 ]',), )
        region2 = regionToolset.Region(side1Faces=side1Faces1)
        self._model_database.models[self._model_name.format(self.i)].Coupling(name='Constraint-2', controlPoint=region1,
                                                                              surface=region2,
                                                                              influenceRadius=WHOLE_SURFACE,
                                                                              couplingType=KINEMATIC,
                                                                              localCsys=None, u1=ON, u2=ON, u3=ON,
                                                                              ur1=ON, ur2=ON,
                                                                              ur3=ON)

    def _boundary_conditions(self):
        a = self._model_database.models[self._model_name.format(self.i)].rootAssembly
        f1 = a.instances['ConcreteCube-1'].faces
        faces1 = f1.getSequenceFromMask(mask=('[#40 ]',), )
        region = regionToolset.Region(faces=faces1)
        self._model_database.models[self._model_name.format(self.i)].DisplacementBC(name='BC-1',
                                                                                    createStepName='Step-1',
                                                                                    region=region,
                                                                                    u1=0.0, u2=0.0, u3=0.0, ur1=0.0,
                                                                                    ur2=0.0, ur3=0.0,
                                                                                    amplitude=UNSET, fixed=OFF,
                                                                                    distributionType=UNIFORM,
                                                                                    fieldName='', localCsys=None)

        a = self._model_database.models[self._model_name.format(self.i)].rootAssembly
        r1 = a.referencePoints
        refPoints1 = (r1[10],)
        region = regionToolset.Region(referencePoints=refPoints1)
        self._model_database.models[self._model_name.format(self.i)].DisplacementBC(name='BC-2',
                                                                                    createStepName='Step-1',
                                                                                    region=region,
                                                                                    u1=UNSET, u2=-0.1, u3=UNSET,
                                                                                    ur1=UNSET,
                                                                                    ur2=UNSET,
                                                                                    ur3=UNSET, amplitude=UNSET,
                                                                                    fixed=OFF,
                                                                                    distributionType=UNIFORM,
                                                                                    fieldName='',
                                                                                    localCsys=None)
        self._model_database.models[self._model_name.format(self.i)].boundaryConditions['BC-2'].setValues(u1=-0.1,
                                                                                                          u2=UNSET)
        self._model_database.models[self._model_name.format(self.i)].boundaryConditions['BC-2'].setValues(u1=UNSET,
                                                                                                          u3=-0.1)

    def _mesh_calculation(self):
        self.__mesh_size = (self._a + self._h) / 2 / 15

    def _mesh_set(self):
        p = self._model_database.models[self._model_name.format(self.i)].parts[
            self._reinforcement_part_name.format('1')]
        p.seedPart(size=self.__mesh_size, deviationFactor=0.1, minSizeFactor=0.1)
        p = self._model_database.models[self._model_name.format(self.i)].parts[
            self._reinforcement_part_name.format('1')]
        p.generateMesh()

        p = self._model_database.models[self._model_name.format(self.i)].parts[self._cube_part_name]
        p.seedPart(size=self.__mesh_size, deviationFactor=0.1, minSizeFactor=0.1)
        p = self._model_database.models[self._model_name.format(self.i)].parts[self._cube_part_name]
        p.generateMesh()

    def _section_assigment(self):
        p = self._model_database.models[self._model_name.format(self.i)].parts[self._reinforcement_part_name]
        e = p.edges
        edges = e.getSequenceFromMask(mask=('[#1 ]',), )
        region = regionToolset.Region(edges=edges)
        p.SectionAssignment(region=region, sectionName='Section-reinforcement', offset=0.0, offsetType=MIDDLE_SURFACE,
                            offsetField='', thicknessAssignment=FROM_SECTION)

        p = self._model_database.models[self._model_name.format(self.i)].parts[self._cube_part_name]
        c = p.cells
        cells = c.getSequenceFromMask(mask=('[#1 ]',), )
        region = regionToolset.Region(cells=cells)
        p.SectionAssignment(region=region, sectionName='Section-concrete', offset=0.0, offsetType=MIDDLE_SURFACE,
                            offsetField='', thicknessAssignment=FROM_SECTION)

    def _job_create(self):
        a = self._model_database.models[self._model_name.format(self.i)].rootAssembly
        a.regenerate()

        self._model_database.Job(name='HC-Slab-Job-{}'.format(self.i), model=self._model_name.format(self.i),
                                 description='', type=ANALYSIS,
                                 atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
                                 memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
                                 explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
                                 modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
                                 scratch='C:/temp/', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1,
                                 numGPUs=0)
        self._save_model()

    def _job_calculate(self):
        self._model_database.jobs['HC-Slab-Job-{}'.format(self.i)].submit(consistencyChecking=OFF)
        self._model_database.jobs['HC-Slab-Job-{}'.format(self.i)].waitForCompletion()

        self.i += 1

    def _model_delete(self):
        self._model_database.Model(name='Model-1', modelType=STANDARD_EXPLICIT)
        del self._model_database.models[self._model_name.format(self.i)]
        del self._model_database.jobs['HC-Slab-Job-{}'.format(self.i)]

    def _check_radius(self):
        equation = 2 * self._r + 2 * self._a1

        if equation > self._a:
            self._r = (self._a - (2 * self._a1)) / 2

    def _check_lagging(self):
        '''
        if self._a1 < self._as_r:
            self._a1 = self._as_r + self._c_nom
        '''

        if self._a1 * 2 + self._r * 2 + self._l >= self._h:
            self._l = self._h - (self._a1 * 2 + self._r * 2)
            log(self._l)
            if self._l < 0:
                self._l = 0

    def save_dimensions(self):
        dimensions = [self._a, self._h, self._r, self._as, self._a1, self._l, self._c_nom]
        return dimensions
