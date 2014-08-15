"""
Calculations for satellite positions and various associated angles. This module needs some reqorking. It has
evolved through several refactorings and has become difficult to follow. Some of the function signatures are
out of date (i.e. they receive arguments that are either unused or could be simplified for the sake of clarity).
The docstrings are also out of date and consequently the documentation is currently incomplete or misleading.

:todo:
    Cleanup, rework, document and write tests for this module.
"""
import math, os, re, logging, ephem
import xml.dom.minidom
from datetime import timedelta
from EOtools.utils import unicode_to_ascii, log_multiline

logger = logging.getLogger('root.' + __name__)

class earth(object):

    # Mean radius
    RADIUS = 6371009.0  # (metres)

    # WGS-84
    #RADIUS = 6378135.0  # equatorial (metres)
    #RADIUS = 6356752.0  # polar (metres)

    # Length of Earth ellipsoid semi-major axis (metres)
    SEMI_MAJOR_AXIS = 6378137.0

    # WGS-84
    A = 6378137.0           # equatorial radius (metres)
    B = 6356752.3142        # polar radius (metres)
    F = (A - B) / A         # flattening
    ECC2 = 1.0 - B**2/A**2  # squared eccentricity

    MEAN_RADIUS = (A*2 + B) / 3

    # Earth ellipsoid eccentricity (dimensionless)
    #ECCENTRICITY = 0.00669438
    #ECC2 = math.pow(ECCENTRICITY, 2)

    # Earth rotational angular velocity (radians/sec)
    OMEGA = 0.000072722052





def N(lat, sm_axis=earth.SEMI_MAJOR_AXIS, ecc2=earth.ECC2):
    lat_s = math.sin(lat)
    return sm_axis / math.sqrt(1.0 - ecc2 * lat_s * lat_s)





def geocentric_lat(lat_gd, sm_axis=earth.A, ecc2=earth.ECC2):
    """Convert geodetic latitude to geocentric latitude.

    Arguments:
        lat_gd: geodetic latitude (radians)
        sm_axis: Earth semi-major axis (metres)
        ecc2: Earth squared eccentricity (dimensionless)

    Returns:
        Geocentric latitude (radians)
    """

    #return math.atan((1.0 - ecc2) * math.tan(lat_gd))
    return math.atan2(math.tan(lat_gd), 1.0/(1.0 - ecc2))


def geodetic_lat(lat_gc, sm_axis=earth.A, ecc2=earth.ECC2):
    """Calculate geocentric latitude to geodetic latitude.

    Arguments:
        lat_gc: geocentric latitude (radians)
        sm_axis: Earth semi-major axis (metres)
        ecc2: Earth squared eccentricity (dimensionless)

    Returns:
        Geodetic latitude (radians)
    """

    return math.atan2(math.tan(lat_gc), (1.0 - ecc2))




# These were found in 'earth.py', but appeared not be used
# def geocentric_lat(lat, sm_axis=SEMI_MAJOR_AXIS, ecc2=ECC2):
#     """Calculate geocentric latitude on the earth ellipsoid surface.
#
#     Arguments:
#         lat: geodetic latitude (radians)
#         sm_axis: length of earth ellipsoid semi-major axis (metres)
#         ecc2: squared eccentricity (dimensionless)
#
#     Returns:
#         Geocentric latitude value (radians).
#     """
#
#     lat_c = math.cos(lat)
#     lat_s = math.sin(lat)
#     N = sm_axis / math.sqrt(1.0 - ecc2 * lat_s * lat_s)
#     return lat - math.asin(N * ecc2 * lat_s * lat_c / sm_axis)
#
# def lat_geocentric(gdlat, sm_axis=SEMI_MAJOR_AXIS, ecc2=ECC2):
#     return math.atan((1.0 - ecc2) * math.tan(gdlat))
#
#
# def lat_geodetic(gclat, sm_axis=SEMI_MAJOR_AXIS, ecc2=ECC2):
#     return math.atan(math.tan(gclat) / (1.0 - ecc2))






class Satellite(object):
    """
    Manages data such as orbital parameters or sensor configuration for a satellite. Information on
    individual sensor bands and their respective wavelength ranges is read in for the specified
    sensor so that wavelength-dependent operations such as the acquisition of BRDF ancillary data can be
    performed dynamically rather than having to be hard-coded for specific band numbers.
    """
    _dom_tree = None

    def __init__(self, sat_name, sensor):
        """
        Constructor. Reads information on individual sensor bands and their respective wavelength ranges for
        the specified sensor from satellite.xml.

        :param sat_name:
            The namve of the satellite.

        :param sensor:
            The name of the sensor.

        """
        def parse_list(list_string, element_type=str):
            """Parses a string representation of a flat list into a list
            """
            return [element_type(element.strip()) for element in re.search('\s*(?<=\[)(.*)(?=\])\s*', list_string).group(0).split(',')]

        def get_sat_attributes(sat_node):
            """sets satellite attributes from XML file
            """
            self.NAME = unicode_to_ascii(sat_node.getAttribute('NAME'))
            self.TAG = unicode_to_ascii(sat_node.getAttribute('TAG'))
            assert self.TAG in ['LS5', 'LS7', 'LS8'], 'Unhandled satellite tag: ' + repr(self.TAG)

            # Orbital semi-major axis (metres)
            self.SEMI_MAJOR_AXIS = float(unicode_to_ascii(sat_node.getAttribute('SEMI_MAJOR_AXIS')))

            # Orbital radius (metres)
            self.RADIUS = float(unicode_to_ascii(sat_node.getAttribute('RADIUS')))

            # Orbital altitude (metres)
            self.ALTITUDE = float(unicode_to_ascii(sat_node.getAttribute('ALTITUDE')))

            # Orbital inclination (radians)
            self.INCLINATION = float(unicode_to_ascii(sat_node.getAttribute('INCLINATION')))
            self.INCL_SIN = math.sin(self.INCLINATION)
            self.INCL_COS = math.cos(self.INCLINATION)
            self.INCL_TAN = math.tan(self.INCLINATION)

            # Orbital angular velocity (radians/sec)
            self.OMEGA = float(unicode_to_ascii(sat_node.getAttribute('OMEGA')))

            # Sensor sweep period (sec)
            self.SWEEP_PERIOD = float(unicode_to_ascii(sat_node.getAttribute('SWEEP_PERIOD')))

            # TLE Format
            self.TLE_FORMAT = unicode_to_ascii(sat_node.getAttribute('TLE_FORMAT'))

            # Solar irradiance file
            self.SOLAR_IRRAD_FILE = unicode_to_ascii(sat_node.getAttribute('SOLAR_IRRAD_FILE'))

            # Spectral filter file
            self.SPECTRAL_FILTER_FILE = unicode_to_ascii(sat_node.getAttribute('SPECTRAL_FILTER_FILE'))

            # POOMA number - approximation only
            self.NOMINAL_PIXEL_DEGREES = float(unicode_to_ascii(sat_node.getAttribute('NOMINAL_PIXEL_DEGREES')))

            # Satellite number
            self.NUMBER = unicode_to_ascii(sat_node.getAttribute('NUMBER'))

            # Satellite classification
            self.CLASSIFICATION = unicode_to_ascii(sat_node.getAttribute('CLASSIFICATION'))

            # International designator
            # TLE compatible format: <last two digits of launch year><launch number of the year><piece of the launch>
            self.INTL_DESIGNATOR = unicode_to_ascii(sat_node.getAttribute('INTL_DESIGNATOR'))


        def get_sensor(sat_node, sensor):

            def get_bands(sensor_node):

                for band_node in sensor_node.getElementsByTagName('BAND'):
                    band_dict = {}
                    band_number = int(unicode_to_ascii(band_node.getAttribute('NUMBER')))
                    band_dict['NUMBER'] = band_number
                    self.BAND_TYPES['ALL'].append(band_number)

                    band_dict['NAME'] = unicode_to_ascii(band_node.getAttribute('NAME'))

                    # Store wavelength range as a two-element list
                    band_dict['WAVELENGTH'] = [float(wavelength) for wavelength in unicode_to_ascii(band_node.getAttribute('WAVELENGTH')).split('-')]

                    band_type = unicode_to_ascii(band_node.getAttribute('TYPE')).upper()
                    band_dict['TYPE'] = band_type
                    logger.debug('Band %d is of type %s', band_number, band_type)
                    # Store band in appropriate list according to type (Default to reflective)
                    band_list = self.BAND_TYPES.get(band_type)
                    if band_list is None:
                        band_list = self.BAND_TYPES['REFLECTIVE']
                    band_list.append(band_number)

                    band_dict['RESOLUTION'] = float(unicode_to_ascii(band_node.getAttribute('RESOLUTION')))

                    self.BAND_LIST.append(band_dict)

            self.sensor = None
            for sensor_node in sat_node.getElementsByTagName('SENSOR'):
                sensor_name = unicode_to_ascii(sensor_node.getAttribute('NAME'))
                #if sensor_name.lower() == sensor.lower():
                #if re.sub('\W+', '', sensor_name.lower()) == re.sub('\W+', '', sensor.lower()):
                if re.sub('[+,_,-]', '', sensor_name.lower()) == re.sub('[+,_,-]', '', sensor.lower()):
                    self.sensor = sensor_name

                    self.k = (float(unicode_to_ascii(sensor_node.getAttribute('K1'))),
                              float(unicode_to_ascii(sensor_node.getAttribute('K2'))))
                    break

            assert self.sensor, 'Sensor %s not found in configuration' % sensor

            self.sensor_description = unicode_to_ascii(sensor_node.getAttribute('DESCRIPTION'))
            self.root_band = int(unicode_to_ascii(sensor_node.getAttribute('ROOT_BAND')))
            self.rgb_bands = [int(bandstring) for bandstring in unicode_to_ascii(sensor_node.getAttribute('RGB_BANDS')).split(',')]
            self.acquistion_seconds = timedelta(seconds=float(unicode_to_ascii(sensor_node.getAttribute('ACQUISITION_SECONDS'))))

            get_bands(sensor_node)

        self.sensor = None
        self.sensor_description = None

        self.BAND_LIST = []

        # Define dict to contain all band groups
        self.BAND_TYPES = {}
        self.BAND_TYPES['ALL'] = []
        self.BAND_TYPES['REFLECTIVE'] = []
        self.BAND_TYPES['THERMAL'] = []
        self.BAND_TYPES['PANCHROMATIC'] = []
        self.BAND_TYPES['ATMOSPHERE'] = []
        self.rgb_bands = []

        self._tle_path_dict = {} # Dict to hold any TLE paths looked up by date

        if not Satellite._dom_tree: # If the satellite.xml file hasn't already been opened
            self.config_file = os.path.join(os.path.dirname(__file__), 'satellite.xml')

            logger.debug('Parsing XML file %s', self.config_file)

            # Open XML document using minidom parser
            Satellite._dom_tree = xml.dom.minidom.parse(self.config_file)

        self.NAME_PATTERN = None
        for sat_node in Satellite._dom_tree.getElementsByTagName('SATELLITE'):
            name_pattern = unicode_to_ascii(sat_node.getAttribute('NAME_PATTERN'))
            if re.match(re.compile(name_pattern, re.IGNORECASE), sat_name):
                self.NAME_PATTERN = name_pattern
                break

        assert self.NAME_PATTERN, 'Configuration for ' + sat_name + ' does not exist in ' + self.config_file

        get_sat_attributes(sat_node)
        get_sensor(sat_node, sensor)

#        log_multiline(logger.info, self.__dict__, 'Satellite object for ' + sat_name, '\t')


    def load_tle(self, centre_datetime, data_root, date_radius=45):
        """
        Loads satellite TLE (two-line element) for the given date and time.

        Arguments:
            centre_datetime: datetime.datetime instance
            data_root: root directory for TLE archive files
            date_radius: date radius for TLE search (days)

        Returns:
            ephem EarthSatellite instance

        """

        return (self._load_tle_from_archive(centre_datetime, data_root, date_radius) or
                self._load_tle_from_file_sequence(centre_datetime, data_root, date_radius))


    def _load_tle_from_archive(self, centre_datetime, data_root=None, date_radius=45):
        """Loads TLE (two-line element) for the satellite, date and time from
        an archive file.

        Arguments:
            centre_datetime: datetime.datetime instance
            data_root: directory containing TLE archive files
            date_radius: date radius for TLE search (days)

        Returns:
            ephem EarthSatellite instance

        """

        if data_root is None:
            logger.warning('load_tle_from_archive: data_root=None')
            return None

        TLE_ENTRY_PATTERN_FORMAT = (
            r'^([1])(\s+)'
            r'([%(NUMBER)s%(CLASSIFICATION)s]+)(\s+)([%(INTL_DESIGNATOR)s]+)(\s+)%(YYDDD)s'  # dict subst keys
            r'(\.)(\d+)(\s+)([\s\-]+)(\.)(\d+)(\s+)(\d+)([\-\+])(\d+)(\s+)(\d+)([\-\+])(\d+)(\s+)(\d+)(\s+)(\d+)(\s)'
            r'^([2])(.+)$'
        )

        def _cmp(x, y): return abs(x) - abs(y)  # For sorting date offsets.

        date_deltas = [timedelta(days=d) for d in sorted(range(-date_radius, date_radius), cmp=_cmp)]
        yyddd_list = [x.strftime('%02y%03j') for x in [(centre_datetime + d) for d in date_deltas]]

        tle_archive_path = os.path.join(
                               data_root,
                               self.NAME.replace('-', '').upper(),
                               'TLE', '%s_ARCHIVE.txt' % self.TAG
                           )

        tle_archive_text = ''

        with open(tle_archive_path, 'r') as fd:
            tle_archive_text = fd.read()

        logger.info('loaded TLE archive file: %s' % tle_archive_path)

        _smap = {
            'NUMBER': self.NUMBER,
            'CLASSIFICATION': self.CLASSIFICATION,
            'INTL_DESIGNATOR': self.INTL_DESIGNATOR,
        }

        tle_entry = None
        for yyddd in yyddd_list:
            _smap['YYDDD'] = yyddd
            m = re.search(TLE_ENTRY_PATTERN_FORMAT % _smap, tle_archive_text, re.MULTILINE)
            if m:
                logger.info('loaded TLE archive entry: %s' % centre_datetime)
                # Reconstitute TLE entry from regex match groups.
                tle_text = ''.join(m.groups()[0:6]) + yyddd + ''.join(m.groups()[6:])
                logger.info('TLE TEXT:\n%s' % tle_text)
                tle_lines = tle_text.split('\n')
                return ephem.readtle(self.NAME, tle_lines[0], tle_lines[1])

        logger.error('No TLE found for %s in archive file %s' % (centre_datetime, tle_archive_path))
        return None


    def _load_tle_from_file_sequence(self, centre_datetime, data_root=None, tle_search_range=45):
        """Load a TLE file for the specified datetime.

        Arguments:
            centre_datetime: scene centre datetime (datetime instance)
            data_root: ephemeris data root directory

        Returns:
            ephem EarthSatellite instance
        """

        if data_root is None:
            logger.warning('load_tle_from_sequence: data_root=None')
            return None

        def open_tle(tle_path, centre_datetime):
            """Function to open specified TLE file
            """
            try:
                fd = open(tle_path, 'r')
                tle_text = fd.readlines()
                logger.info('TLE file %s opened', tle_path)

                log_multiline(logger.debug, tle_text, 'TLE FILE CONTENTS', '\t')

                if self.TAG == 'LS5':
                    tle1, tle2 = tle_text[7:9]
                elif self.TAG == 'LS7':
                    tle1, tle2 = tle_text[1:3]

                sat_obj = ephem.readtle(self.NAME, tle1, tle2)

                # Cache TLE filename for specified date
                self._tle_path_dict[centre_datetime.date()] = tle_path

                return sat_obj
            finally:
                fd.close()

        # Check whether TLE path has been opened previously for this date
        tle_path = self._tle_path_dict.get(centre_datetime.date())
        if tle_path:
            return open_tle(tle_path, centre_datetime)

        data_subdir = re.sub('\W', '', self.NAME).upper()

        # Primary TLE: matches scene date.
        scene_doy = centre_datetime.strftime('%j')  # Note format: '%03d'

        tle_dir = os.path.join(
            data_root,
            data_subdir,  # 'LANDSAT5' or 'LANDSAT7'
            'TLE',
            '%s_YEAR' % self.TAG,
            '%4d' % centre_datetime.year
            )

        tle_file = self.TLE_FORMAT % (centre_datetime.year, scene_doy)
        tle_path = os.path.join(tle_dir, tle_file)

        if os.path.exists(tle_path):
            try:
                logger.debug('Opening primary TLE file %s', tle_path)
                return open_tle(tle_path, centre_datetime)
            except (Exception), e: #TODO: Tighten up this except clause - too general
                logger.warning('Unable to open primary TLE file %s: %s', tle_path, e.message)

        # Secondary TLE: closest TLE within specified number of days from scene date.
        for d in xrange(1, tle_search_range):
            ddelta = timedelta(days=d)
            for s in (-1, 1):
                dt = centre_datetime + (ddelta * s)
                tle_dir = os.path.join(data_root, data_subdir,
                    'TLE',
                    '%s_YEAR' % self.TAG,
                    '%4d' % dt.year)
                tle_file = self.TLE_FORMAT % (dt.year, dt.strftime('%j'))
                tle_path = os.path.join(tle_dir, tle_file)
                if os.path.exists(tle_path):
                    try:
                        logger.debug('Opening secondary TLE file %s', tle_path)
                        return open_tle(tle_path, centre_datetime)
                    except (Exception), e: #TODO: Tighten up this except clause - too general
                        logger.warning('Unable to open Secondary TLE file %s: %s', tle_path, e.message)

        logger.error('No valid TLE file found for %s in %s', dt.strftime('%Y-%m-%d'), tle_dir)
        return None

