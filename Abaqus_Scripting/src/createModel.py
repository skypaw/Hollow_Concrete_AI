from abaqus import *
from abaqusConstants import *
from Model import Model
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


class CreateModel(Model):
    _a = 25
    _h = 20
    _as = 29
    _a1 = 5
    _r = 7

    def __init__(self):
        Model.__init__(self)

        self._create_model_database()

    def _create_model_database(self):
        self.__part_concrete_cube()
        self.__part_steel_rod()
        self._model_assembly()
        self._constraints_set()
        self._boundary_conditions()
        self._mesh_calculation()
        self._mesh_set()
        self._section_assigment()
        self.__create_history()
        self._save_model()
        self._job_calculate()

    def __part_concrete_cube(self):
        """part concrete cube function
        ==============================

        Function creating 3D cuboid with the dimensions /a/ and /h/ and with the cylindrical hole with dimension /a/
        and /r/
        """

        s = self._model_database.models[self._model_name].ConstrainedSketch(name='__profile__', sheetSize=self._a)
        s.setPrimaryObject(option=STANDALONE)

        s.rectangle(point1=(0.0, 0.0), point2=(self._a, self._h))
        s.CircleByCenterPerimeter(center=(self._a / 2, self._h / 2),
                                  point1=(self._a / 2, self._h / 2 - self._r))

        self._model_database.models[self._model_name].Part(name=self._cube_part_name, dimensionality=THREE_D,
                                                           type=DEFORMABLE_BODY)

        p = self._model_database.models[self._model_name].parts[self._cube_part_name]
        p.BaseSolidExtrude(sketch=s, depth=self._a)

        del self._model_database.models[self._model_name].sketches['__profile__']

    def __part_steel_rod(self):
        """part steel rod function
        ==============================

        Function creating 2D wire with the dimension /a/
        """

        s = self._model_database.models[self._model_name].ConstrainedSketch(name='__profile__', sheetSize=200.0)
        g = s.geometry

        s.setPrimaryObject(option=STANDALONE)
        s.Line(point1=(0.0, 0.0), point2=(self._a, 0.0))

        s.HorizontalConstraint(entity=g[2], addUndoState=False)

        self._model_database.models[self._model_name].Part(name=self._reinforcement_part_name,
                                                           dimensionality=THREE_D,
                                                           type=DEFORMABLE_BODY)

        p = self._model_database.models[self._model_name].parts[self._reinforcement_part_name]
        p.BaseWire(sketch=s)

        del self._model_database.models[self._model_name].sketches['__profile__']

        e = p.edges
        edges = e.getSequenceFromMask(mask=('[#1 ]',), )
        region = regionToolset.Region(edges=edges)

        p.assignBeamSectionOrientation(region=region, method=N1_COSINES, n1=(0.0, 0.0, -1.0))

    def __create_history(self):
        a = self._model_database.models[self._model_name].rootAssembly
        r1 = a.referencePoints
        refPoints1 = (r1[10],)
        a.Set(referencePoints=refPoints1, name='Set-1')
        regionDef = self._model_database.models[self._model_name].rootAssembly.sets['Set-1']
        self._model_database.models[self._model_name].HistoryOutputRequest(name='H-Output-2', createStepName='Step-1',
                                                                           variables=('RF3',), frequency=LAST_INCREMENT,
                                                                           region=regionDef, sectionPoints=DEFAULT,
                                                                           rebar=EXCLUDE)


CreateModel()
