import numpy as np
import uvdata.parameter as uvp
import uvdata.utils as utils


class Telescope(object):

    def __init__(self):
        # add the UVParameters to the class
        # use the same names as in UVData so they can be automatically set
        self._telescope_name = uvp.UVParameter('telescope_name', description='name of telescope '
                                               '(string)', form='str')
        desc = ('coordinate frame for antenna positions '
                '(eg "ITRF" -also google ECEF). NB: ECEF has x running '
                'through long=0 and z through the north pole')
        self._xyz_telescope_frame = uvp.UVParameter('xyz_telescope_frame', description=desc,
                                                    form='str')

        self._x_telescope = uvp.UVParameter('x_telescope',
                                            description='x coordinates of array '
                                                        'center in meters in coordinate frame',
                                            tols=1e-3)  # 1 mm
        self._y_telescope = uvp.UVParameter('y_telescope',
                                            description='y coordinates of array '
                                                        'center in meters in coordinate frame',
                                            tols=1e-3)  # 1 mm
        self._z_telescope = uvp.UVParameter('z_telescope',
                                            description='z coordinates of array '
                                                        'center in meters in coordinate frame',
                                            tols=1e-3)  # 1 mm

        self._latitude = uvp.AngleParameter('latitude',
                                            description='latitude of telescope, units radians',
                                            expected_type=np.float,
                                            tols=2 * np.pi * 1e-3 / (60.0 * 60.0 * 24.0))  # 1 mas in radians
        self._longitude = uvp.AngleParameter('longitude',
                                             description='longitude of telescope, units radians',
                                             expected_type=np.float,
                                             tols=2 * np.pi * 1e-3 / (60.0 * 60.0 * 24.0))  # 1 mas in radians
        self._altitude = uvp.UVParameter('altitude',
                                         description='altitude of telescope, units meters',
                                         expected_type=np.float,
                                         tols=1e-3)  # 1 mm

        # possibly add in future versions:
        # Antenna positions (but what about reconfigurable/growing telescopes?)

        # setup parameters as properties
        for p in self.parameter_iter():
            this_param = getattr(self, p)
            attr_name = this_param.name
            setattr(self.__class__, attr_name, property(self.prop_fget(p), self.prop_fset(p)))

    def prop_fget(self, param_name):
        def fget(self):
            this_param = getattr(self, param_name)
            return this_param.value
        return fget

    def prop_fset(self, param_name):
        def fset(self, value):
            this_param = getattr(self, param_name)
            this_param.value = value
            setattr(self, param_name, this_param)
        return fset

    def parameter_iter(self):
        attribute_list = [a for a in dir(self) if not a.startswith('__') and
                          not callable(getattr(self, a))]
        param_list = []
        for a in attribute_list:
            attr = getattr(self, a)
            if isinstance(attr, uvp.UVParameter):
                param_list.append(a)
        for a in param_list:
            yield a

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            isequal = True
            for p in self.parameter_iter():
                self_param = getattr(self, p)
                other_param = getattr(other, p)
                if self_param != other_param:
                    # print('parameter {pname} does not match. Left is {lval} '
                    #       'and right is {rval}'.
                    #       format(pname=p, lval=str(self_param.value),
                    #              rval=str(other_param.value)))
                    isequal = False
            return isequal
        else:
            print('Classes do not match')
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


def telescopes():
    paper_sa = {name: 'PAPER_SA', frame: 'ITRF', center_xyz: [],
                latitude: , longitude: , altitude: }

    hera = {name: 'HERA', frame: 'ITRF', center_xyz: [],
            latitude: , longitude: , altitude: }

    mwa = {name: 'MWA', frame: 'ITRF', center_xyz: [],
           latitude: , longitude: , altitude: }

    dict_list = [paper_sa, hera, mwa]

    telescopes = {}
    for telescope in dict_list:
        obj = Telescope()
        obj.telescope_name = telescope.name
        if ('center_xyz' in telescope.keys() and 'frame' in telescope.keys()):
            obj.xyz_telescope_frame = telescope.frame
            obj.x_telescope = telescope.center_xyz[0]
            obj.y_telescope = telescope.center_xyz[1]
            obj.z_telescope = telescope.center_xyz[2]

            if ('latitude' in telescope.keys() and 'longitude' in telescope.keys() and 'altitude' in telescope.keys()):
                obj.latitude = telescope.latitude
                obj.longitude = telescope.longitude
                obj.altitude = telescope.altitude
            else:
                if telescope.frame == 'ITRF':
                    latitude, longitude, altitude = utils.LatLonAlt_from_XYZ(telescope.center_xyz)
                    obj.latitude = latitude
                    obj.longitude = longitude
                    obj.altitude = altitude
                else:
                    raise ValueError('latitude, longitude or altitude not
                                     'specified and frame is not "ITRF"')
        else:
            if not ('latitude' in telescope.keys() and 'longitude' in telescope.keys() and 'altitude' in telescope.keys()):
                raise ValueError('either the center_xyz and frame or the '
                                 'latitude, longitude and altitude of the '
                                 'telescope must be specified')
            obj.latitude = telescope.latitude
            obj.longitude = telescope.longitude
            obj.latitude = telescope.latitude

            xyz = utils.XYZ_from_LatLonAlt(telescope.latitude, telescope.longitude,
                                           telescope.altitude)
            obj.xyz_telescope_frame = 'ITRF'
            obj.x_telescope = xyz[0]
            obj.y_telescope = xyz[1]
            obj.z_telescope = xyz[2]

        telescopes[telescope.name] = obj
