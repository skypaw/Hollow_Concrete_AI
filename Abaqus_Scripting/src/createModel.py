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
from log import log

import numpy as np


class CreateModel(Model):
    _a = None
    _h = None
    _as = None
    _a1 = None
    _r = None
    _l = None
    _c_nom = None
    i = None

    def __init__(self):
        Model.__init__(self)
        self.i = 0

    def dimensions_setter(self, a, h, a_s, a1, r, l, c_nom):
        self._a = a
        self._h = h
        self._as = a_s
        self._a1 = a1
        self._r = r
        self._l = l
        self._c_nom = c_nom

    def create_database(self):
        self._create_model_database()

    def _create_model_database(self):
        # from model -> todo delete datum

        Mdb()
        self._model_database = mdb
        self._model_database.saveAs(pathName=self._path)
        self._model_database.models.changeKey(fromName='Model-1', toName=self._model_name.format(self.i))
        self._materials()
        self._profile_create()
        self._section_create()
        self._step_create()
        self._job_create()

        # from create model

        self._check_lagging()
        self._check_radius()

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

        if self._l == 0:
            s = self._model_database.models[self._model_name.format(self.i)].ConstrainedSketch(name='__profile__',
                                                                                               sheetSize=self._a)
            s.setPrimaryObject(option=STANDALONE)

            s.rectangle(point1=(0.0, 0.0), point2=(self._a, self._h))
            s.CircleByCenterPerimeter(center=(self._a / 2, self._h / 2),
                                      point1=(self._a / 2, self._h / 2 - self._r))

            self._model_database.models[self._model_name.format(self.i)].Part(name=self._cube_part_name,
                                                                              dimensionality=THREE_D,
                                                                              type=DEFORMABLE_BODY)

            p = self._model_database.models[self._model_name.format(self.i)].parts[self._cube_part_name]
            p.BaseSolidExtrude(sketch=s, depth=self._a)

            del self._model_database.models[self._model_name.format(self.i)].sketches['__profile__']

        else:
            s = self._model_database.models[self._model_name.format(self.i)].ConstrainedSketch(name='__profile__',
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

            self._model_database.models[self._model_name.format(self.i)].Part(name=self._cube_part_name,
                                                                              dimensionality=THREE_D,
                                                                              type=DEFORMABLE_BODY)

            p = self._model_database.models[self._model_name.format(self.i)].parts[self._cube_part_name]
            p.BaseSolidExtrude(sketch=s, depth=self._a)

            del self._model_database.models[self._model_name.format(self.i)].sketches['__profile__']

    def __part_steel_rod(self):
        """part steel rod function
        ==============================

        Function creating 2D wire with the dimension /a/
        """

        s = self._model_database.models[self._model_name.format(self.i)].ConstrainedSketch(name='__profile__',
                                                                                           sheetSize=200.0)
        g = s.geometry

        s.setPrimaryObject(option=STANDALONE)
        s.Line(point1=(0.0, 0.0), point2=(self._a, 0.0))

        s.HorizontalConstraint(entity=g[2], addUndoState=False)

        self._model_database.models[self._model_name.format(self.i)].Part(name=self._reinforcement_part_name,
                                                                          dimensionality=THREE_D,
                                                                          type=DEFORMABLE_BODY)

        p = self._model_database.models[self._model_name.format(self.i)].parts[self._reinforcement_part_name]
        p.BaseWire(sketch=s)

        del self._model_database.models[self._model_name.format(self.i)].sketches['__profile__']

        e = p.edges
        edges = e.getSequenceFromMask(mask=('[#1 ]',), )
        region = regionToolset.Region(edges=edges)

        p.assignBeamSectionOrientation(region=region, method=N1_COSINES, n1=(0.0, 0.0, -1.0))

