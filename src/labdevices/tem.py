from abc import ABC
from collections import defaultdict
from enum import Enum


class TEMOpticalMode(Enum):
    TEM = "tem"
    STEM = "stem"
    DIFFRACTION = "diffraction"
    SCANNING_DIFFRACTION = "scanning_diffraction"
    SPECTROSCOPY = "spectroscopy"


class TEMSubsystemKind(Enum):
    ELECTRON_SOURCE = "electron_source"
    MONOCHROMATOR = "monochromator"
    APERTURE = "aperture"
    LENS = "lens"
    DEFLECTOR = "deflector"
    STIGMATOR = "stigmator"
    ABERRATION_CORRECTOR = "aberration_corrector"
    SCAN_GENERATOR = "scan_generator"
    SAMPLE_STAGE = "sample_stage"
    ENERGY_FILTER = "energy_filter"
    SPECTROMETER = "spectrometer"
    DETECTOR = "detector"
    VACUUM = "vacuum"
    CONTROL = "control"
    OTHER = "other"


class TEMColumnRegion(Enum):
    EMISSION = "emission"
    ILLUMINATION = "illumination"
    PRE_SPECIMEN = "pre_specimen"
    SPECIMEN = "specimen"
    POST_SPECIMEN = "post_specimen"
    DETECTION = "detection"
    AUXILIARY = "auxiliary"


class TEMDetectorMode(Enum):
    BRIGHT_FIELD = "bright_field"
    DARK_FIELD = "dark_field"
    ANNULAR_BRIGHT_FIELD = "annular_bright_field"
    ANNULAR_DARK_FIELD = "annular_dark_field"
    HIGH_ANGLE_ANNULAR_DARK_FIELD = "high_angle_annular_dark_field"
    BACKSCATTER = "backscatter"
    SECONDARY = "secondary"
    X_RAY = "x_ray"
    EELS = "eels"
    CAMERA = "camera"
    PIXELATED = "pixelated"
    OTHER = "other"


class TEMParameter:
    def __init__(
        self,
        name,
        default=None,
        unit=None,
        description=None,
        readonly=False,
        metadata=None
    ):
        if not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("Parameter name has to be a non empty string")
        if unit is not None and not isinstance(unit, str):
            raise ValueError("Unit has to be a string or None")
        if description is not None and not isinstance(description, str):
            raise ValueError("Description has to be a string or None")
        if not isinstance(readonly, bool):
            raise ValueError("Readonly flag has to be boolean")
        if metadata is None:
            metadata = {}
        if not isinstance(metadata, dict):
            raise ValueError("Metadata has to be a dictionary")

        self._name = name
        self._default = default
        self._unit = unit
        self._description = description
        self._readonly = readonly
        self._metadata = dict(metadata)

    @property
    def name(self):
        return self._name

    @property
    def default(self):
        return self._default

    @property
    def unit(self):
        return self._unit

    @property
    def description(self):
        return self._description

    @property
    def readonly(self):
        return self._readonly

    @property
    def metadata(self):
        return dict(self._metadata)


class TEMRuntimeMode:
    def __init__(
        self,
        name,
        optical_mode=None,
        component_parameters=None,
        metadata=None
    ):
        if not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("Runtime mode name has to be a non empty string")
        if optical_mode is not None and not isinstance(optical_mode, TEMOpticalMode):
            raise ValueError("Optical mode has to be TEMOpticalMode or None")
        if component_parameters is None:
            component_parameters = {}
        if metadata is None:
            metadata = {}
        if not isinstance(component_parameters, dict):
            raise ValueError("Component parameters have to be a dictionary")
        if not isinstance(metadata, dict):
            raise ValueError("Metadata has to be a dictionary")

        self._name = name
        self._optical_mode = optical_mode
        self._component_parameters = {}
        self._metadata = dict(metadata)

        for component_name, parameter_values in component_parameters.items():
            self.set_component_parameters(component_name, parameter_values)

    @property
    def name(self):
        return self._name

    @property
    def optical_mode(self):
        return self._optical_mode

    @property
    def metadata(self):
        return dict(self._metadata)

    def set_component_parameters(self, component_name, parameter_values):
        if not isinstance(component_name, str) or len(component_name.strip()) == 0:
            raise ValueError("Component name has to be a non empty string")
        if not isinstance(parameter_values, dict):
            raise ValueError("Parameter values have to be a dictionary")

        self._component_parameters[component_name] = dict(parameter_values)

    def get_component_parameters(self, component_name):
        if not isinstance(component_name, str) or len(component_name.strip()) == 0:
            raise ValueError("Component name has to be a non empty string")
        return dict(self._component_parameters.get(component_name, {}))

    def component_names(self):
        return tuple(self._component_parameters.keys())

    def describe(self):
        return {
            "name": self._name,
            "optical_mode": None if self._optical_mode is None else self._optical_mode.value,
            "component_parameters": {
                component_name: dict(parameter_values)
                for component_name, parameter_values in self._component_parameters.items()
            },
            "metadata": dict(self._metadata)
        }


class TEMComponent(ABC):
    def __init__(
        self,
        name,
        kind,
        region,
        tags=None,
        supported_modes=None,
        metadata=None,
        supported_parameters=None
    ):
        if not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("Component name has to be a non empty string")
        if not isinstance(kind, TEMSubsystemKind):
            raise ValueError("Component kind has to be a TEMSubsystemKind")
        if not isinstance(region, TEMColumnRegion):
            raise ValueError("Component region has to be a TEMColumnRegion")
        if tags is None:
            tags = []
        if supported_modes is None:
            supported_modes = []
        if metadata is None:
            metadata = {}
        if supported_parameters is None:
            supported_parameters = []
        if not isinstance(tags, (list, tuple)):
            raise ValueError("Tags have to be a list or tuple")
        if not isinstance(supported_modes, (list, tuple)):
            raise ValueError("Supported modes have to be a list or tuple")
        if not isinstance(metadata, dict):
            raise ValueError("Metadata has to be a dictionary")
        if not isinstance(supported_parameters, (list, tuple)):
            raise ValueError("Supported parameters have to be a list or tuple")

        for mode in supported_modes:
            if not isinstance(mode, TEMOpticalMode):
                raise ValueError("All supported modes have to be TEMOpticalMode entries")
        for parameter in supported_parameters:
            if not isinstance(parameter, TEMParameter):
                raise ValueError("All supported parameters have to be TEMParameter entries")

        self._name = name
        self._kind = kind
        self._region = region
        self._tags = tuple(tags)
        self._supported_modes = tuple(supported_modes)
        self._metadata = dict(metadata)
        self._supported_parameters = {}
        self._parameter_values = {}

        for parameter in supported_parameters:
            self._supported_parameters[parameter.name] = parameter
            self._parameter_values[parameter.name] = parameter.default

    @property
    def name(self):
        return self._name

    @property
    def kind(self):
        return self._kind

    @property
    def region(self):
        return self._region

    @property
    def tags(self):
        return self._tags

    @property
    def supported_modes(self):
        return self._supported_modes

    @property
    def metadata(self):
        return dict(self._metadata)

    @property
    def supported_parameters(self):
        return tuple(self._supported_parameters.values())

    def supports_mode(self, mode):
        if not isinstance(mode, TEMOpticalMode):
            raise ValueError("Mode has to be a TEMOpticalMode")
        return mode in self._supported_modes

    def supports_parameter(self, parameter_name):
        if not isinstance(parameter_name, str) or len(parameter_name.strip()) == 0:
            raise ValueError("Parameter name has to be a non empty string")
        return parameter_name in self._supported_parameters

    def list_parameter_names(self):
        return tuple(self._supported_parameters.keys())

    def get_parameter_names(self):
        return tuple(
            (parameter.name, parameter.description)
            for parameter in self._supported_parameters.values()
        )

    def get_parameter_definition(self, parameter_name):
        if not isinstance(parameter_name, str) or len(parameter_name.strip()) == 0:
            raise ValueError("Parameter name has to be a non empty string")
        if parameter_name not in self._supported_parameters:
            raise ValueError(f"Component {self._name} does not support parameter {parameter_name}")
        return self._supported_parameters[parameter_name]

    def set_parameter(self, parameter_name, value):
        parameter = self.get_parameter_definition(parameter_name)
        if parameter.readonly:
            raise ValueError(f"Parameter {parameter_name} is read only")
        self._parameter_values[parameter_name] = value

    def get_parameter(self, parameter_name):
        self.get_parameter_definition(parameter_name)
        return self._parameter_values[parameter_name]

    def get_parameter_values(self):
        return dict(self._parameter_values)

    def get_parameters(self):
        return dict(self._parameter_values)

    def set_parameters(self, parameters):
        if not isinstance(parameters, dict):
            raise ValueError("Parameters have to be a dictionary")
        for parameter_name, value in parameters.items():
            self.set_parameter(parameter_name, value)

    def describe(self):
        return {
            "name": self._name,
            "class": self.__class__.__name__,
            "kind": self._kind.value,
            "region": self._region.value,
            "tags": self._tags,
            "supported_modes": tuple(mode.value for mode in self._supported_modes),
            "metadata": dict(self._metadata),
            "parameters": tuple(
                {
                    "name": parameter.name,
                    "unit": parameter.unit,
                    "description": parameter.description,
                    "readonly": parameter.readonly,
                    "default": parameter.default,
                    "value": self._parameter_values[parameter.name],
                    "metadata": parameter.metadata
                }
                for parameter in self._supported_parameters.values()
            )
        }


class ElectronSource(TEMComponent):
    def __init__(self, name, emission_type=None, **kwargs):
        if "supported_parameters" not in kwargs:
            kwargs["supported_parameters"] = [
                TEMParameter("acceleration_voltage", unit="V", description="Electron acceleration voltage"),
                TEMParameter("emission_current", unit="A", description="Electron emission current"),
                TEMParameter("extractor_voltage", unit="V", description="Extractor electrode voltage"),
                TEMParameter("gun_lens_current", unit="A", description="Gun lens current")
            ]
        super().__init__(
            name=name,
            kind=TEMSubsystemKind.ELECTRON_SOURCE,
            region=TEMColumnRegion.EMISSION,
            **kwargs
        )
        self._emission_type = emission_type

    @property
    def emission_type(self):
        return self._emission_type

    def set_emission_current(self, current):
        self.set_parameter("emission_current", current)

    def get_emission_current(self):
        return self.get_parameter("emission_current")

    def set_acceleration_voltage(self, voltage):
        self.set_parameter("acceleration_voltage", voltage)

    def get_acceleration_voltage(self):
        return self.get_parameter("acceleration_voltage")

    def set_extractor_voltage(self, voltage):
        self.set_parameter("extractor_voltage", voltage)

    def get_extractor_voltage(self):
        return self.get_parameter("extractor_voltage")

    def set_gun_lens_current(self, current):
        self.set_parameter("gun_lens_current", current)

    def get_gun_lens_current(self):
        return self.get_parameter("gun_lens_current")


class Monochromator(TEMComponent):
    def __init__(self, name, **kwargs):
        if "supported_parameters" not in kwargs:
            kwargs["supported_parameters"] = [
                TEMParameter("energy_spread", unit="eV", description="Target energy spread"),
                TEMParameter("slit_width", unit="eV", description="Monochromator slit width")
            ]
        super().__init__(
            name=name,
            kind=TEMSubsystemKind.MONOCHROMATOR,
            region=TEMColumnRegion.ILLUMINATION,
            **kwargs
        )

    def set_energy_spread(self, value):
        self.set_parameter("energy_spread", value)

    def get_energy_spread(self):
        return self.get_parameter("energy_spread")

    def set_slit_width(self, value):
        self.set_parameter("slit_width", value)

    def get_slit_width(self):
        return self.get_parameter("slit_width")


class Aperture(TEMComponent):
    def __init__(self, name, aperture_family=None, **kwargs):
        super().__init__(
            name=name,
            kind=TEMSubsystemKind.APERTURE,
            **kwargs
        )
        self._aperture_family = aperture_family

    @property
    def aperture_family(self):
        return self._aperture_family


class Lens(TEMComponent):
    def __init__(self, name, lens_family=None, **kwargs):
        if "supported_parameters" not in kwargs:
            kwargs["supported_parameters"] = [
                TEMParameter("current", unit="A", description="Lens current"),
                TEMParameter("excitation", unit="1", description="Normalized lens excitation"),
                TEMParameter("focal_length", unit="m", description="Effective focal length")
            ]
        super().__init__(
            name=name,
            kind=TEMSubsystemKind.LENS,
            **kwargs
        )
        self._lens_family = lens_family

    @property
    def lens_family(self):
        return self._lens_family

    def set_current(self, current):
        self.set_parameter("current", current)

    def get_current(self):
        return self.get_parameter("current")

    def set_excitation(self, excitation):
        self.set_parameter("excitation", excitation)

    def get_excitation(self):
        return self.get_parameter("excitation")

    def set_focal_length(self, focal_length):
        self.set_parameter("focal_length", focal_length)

    def get_focal_length(self):
        return self.get_parameter("focal_length")


class Deflector(TEMComponent):
    def __init__(self, name, axis_count=2, **kwargs):
        if "supported_parameters" not in kwargs:
            kwargs["supported_parameters"] = [
                TEMParameter("x", description="Deflection along x axis"),
                TEMParameter("y", description="Deflection along y axis")
            ]
        super().__init__(
            name=name,
            kind=TEMSubsystemKind.DEFLECTOR,
            **kwargs
        )
        if not isinstance(axis_count, int) or axis_count < 1:
            raise ValueError("Axis count has to be a positive integer")
        self._axis_count = axis_count

    @property
    def axis_count(self):
        return self._axis_count

    def set_x(self, value):
        self.set_parameter("x", value)

    def get_x(self):
        return self.get_parameter("x")

    def set_y(self, value):
        self.set_parameter("y", value)

    def get_y(self):
        return self.get_parameter("y")


class Stigmator(TEMComponent):
    def __init__(self, name, axis_count=2, **kwargs):
        if "supported_parameters" not in kwargs:
            kwargs["supported_parameters"] = [
                TEMParameter("x", description="Stigmation along x axis"),
                TEMParameter("y", description="Stigmation along y axis")
            ]
        super().__init__(
            name=name,
            kind=TEMSubsystemKind.STIGMATOR,
            **kwargs
        )
        if not isinstance(axis_count, int) or axis_count < 1:
            raise ValueError("Axis count has to be a positive integer")
        self._axis_count = axis_count

    @property
    def axis_count(self):
        return self._axis_count

    def set_x(self, value):
        self.set_parameter("x", value)

    def get_x(self):
        return self.get_parameter("x")

    def set_y(self, value):
        self.set_parameter("y", value)

    def get_y(self):
        return self.get_parameter("y")


class AberrationCorrector(TEMComponent):
    def __init__(self, name, correction_order=None, **kwargs):
        if "supported_parameters" not in kwargs:
            kwargs["supported_parameters"] = [
                TEMParameter("c1", description="First order correction term"),
                TEMParameter("c3", description="Third order correction term"),
                TEMParameter("c5", description="Fifth order correction term"),
                TEMParameter("coma_x", description="Coma correction along x axis"),
                TEMParameter("coma_y", description="Coma correction along y axis")
            ]
        super().__init__(
            name=name,
            kind=TEMSubsystemKind.ABERRATION_CORRECTOR,
            **kwargs
        )
        self._correction_order = correction_order

    @property
    def correction_order(self):
        return self._correction_order

    def set_c1(self, value):
        self.set_parameter("c1", value)

    def get_c1(self):
        return self.get_parameter("c1")

    def set_c3(self, value):
        self.set_parameter("c3", value)

    def get_c3(self):
        return self.get_parameter("c3")

    def set_c5(self, value):
        self.set_parameter("c5", value)

    def get_c5(self):
        return self.get_parameter("c5")

    def set_coma_x(self, value):
        self.set_parameter("coma_x", value)

    def get_coma_x(self):
        return self.get_parameter("coma_x")

    def set_coma_y(self, value):
        self.set_parameter("coma_y", value)

    def get_coma_y(self):
        return self.get_parameter("coma_y")


class ScanGenerator(TEMComponent):
    def __init__(self, name, **kwargs):
        if "supported_parameters" not in kwargs:
            kwargs["supported_parameters"] = [
                TEMParameter("field_of_view", unit="m", description="Scan field of view"),
                TEMParameter("rotation", unit="deg", description="Scan rotation angle"),
                TEMParameter("pixel_time", unit="s", description="Pixel dwell time"),
                TEMParameter("scan_offset_x", description="Scan offset along x axis"),
                TEMParameter("scan_offset_y", description="Scan offset along y axis")
            ]
        super().__init__(
            name=name,
            kind=TEMSubsystemKind.SCAN_GENERATOR,
            region=TEMColumnRegion.PRE_SPECIMEN,
            **kwargs
        )

    def set_field_of_view(self, value):
        self.set_parameter("field_of_view", value)

    def get_field_of_view(self):
        return self.get_parameter("field_of_view")

    def set_rotation(self, value):
        self.set_parameter("rotation", value)

    def get_rotation(self):
        return self.get_parameter("rotation")

    def set_pixel_time(self, value):
        self.set_parameter("pixel_time", value)

    def get_pixel_time(self):
        return self.get_parameter("pixel_time")

    def set_scan_offset_x(self, value):
        self.set_parameter("scan_offset_x", value)

    def get_scan_offset_x(self):
        return self.get_parameter("scan_offset_x")

    def set_scan_offset_y(self, value):
        self.set_parameter("scan_offset_y", value)

    def get_scan_offset_y(self):
        return self.get_parameter("scan_offset_y")


class SampleStage(TEMComponent):
    def __init__(self, name, axes=None, **kwargs):
        if "supported_parameters" not in kwargs:
            kwargs["supported_parameters"] = [
                TEMParameter("x", unit="m", description="Stage x position"),
                TEMParameter("y", unit="m", description="Stage y position"),
                TEMParameter("z", unit="m", description="Stage z position"),
                TEMParameter("alpha", unit="deg", description="Stage alpha tilt"),
                TEMParameter("beta", unit="deg", description="Stage beta tilt")
            ]
        super().__init__(
            name=name,
            kind=TEMSubsystemKind.SAMPLE_STAGE,
            region=TEMColumnRegion.SPECIMEN,
            **kwargs
        )
        if axes is None:
            axes = ("x", "y", "z", "alpha", "beta")
        if not isinstance(axes, (list, tuple)):
            raise ValueError("Axes have to be a list or tuple")
        self._axes = tuple(axes)

    @property
    def axes(self):
        return self._axes

    def set_x(self, value):
        self.set_parameter("x", value)

    def get_x(self):
        return self.get_parameter("x")

    def set_y(self, value):
        self.set_parameter("y", value)

    def get_y(self):
        return self.get_parameter("y")

    def set_z(self, value):
        self.set_parameter("z", value)

    def get_z(self):
        return self.get_parameter("z")

    def set_alpha(self, value):
        self.set_parameter("alpha", value)

    def get_alpha(self):
        return self.get_parameter("alpha")

    def set_beta(self, value):
        self.set_parameter("beta", value)

    def get_beta(self):
        return self.get_parameter("beta")


class EnergyFilter(TEMComponent):
    def __init__(self, name, **kwargs):
        if "supported_parameters" not in kwargs:
            kwargs["supported_parameters"] = [
                TEMParameter("energy_window_center", unit="eV", description="Energy window center"),
                TEMParameter("energy_window_width", unit="eV", description="Energy window width")
            ]
        super().__init__(
            name=name,
            kind=TEMSubsystemKind.ENERGY_FILTER,
            region=TEMColumnRegion.POST_SPECIMEN,
            **kwargs
        )

    def set_energy_window_center(self, value):
        self.set_parameter("energy_window_center", value)

    def get_energy_window_center(self):
        return self.get_parameter("energy_window_center")

    def set_energy_window_width(self, value):
        self.set_parameter("energy_window_width", value)

    def get_energy_window_width(self):
        return self.get_parameter("energy_window_width")


class Spectrometer(TEMComponent):
    def __init__(self, name, **kwargs):
        if "supported_parameters" not in kwargs:
            kwargs["supported_parameters"] = [
                TEMParameter("dispersion", description="Spectrometer dispersion"),
                TEMParameter("collection_angle", unit="rad", description="Collection angle")
            ]
        super().__init__(
            name=name,
            kind=TEMSubsystemKind.SPECTROMETER,
            region=TEMColumnRegion.DETECTION,
            **kwargs
        )

    def set_dispersion(self, value):
        self.set_parameter("dispersion", value)

    def get_dispersion(self):
        return self.get_parameter("dispersion")

    def set_collection_angle(self, value):
        self.set_parameter("collection_angle", value)

    def get_collection_angle(self):
        return self.get_parameter("collection_angle")


class Detector(TEMComponent):
    def __init__(self, name, detector_modes=None, **kwargs):
        if "supported_parameters" not in kwargs:
            kwargs["supported_parameters"] = [
                TEMParameter("exposure_time", unit="s", description="Detector exposure time"),
                TEMParameter("gain", description="Detector gain"),
                TEMParameter("binning", description="Detector binning")
            ]
        super().__init__(
            name=name,
            kind=TEMSubsystemKind.DETECTOR,
            region=TEMColumnRegion.DETECTION,
            **kwargs
        )
        if detector_modes is None:
            detector_modes = []
        if not isinstance(detector_modes, (list, tuple)):
            raise ValueError("Detector modes have to be a list or tuple")
        for mode in detector_modes:
            if not isinstance(mode, TEMDetectorMode):
                raise ValueError("All detector modes have to be TEMDetectorMode entries")
        self._detector_modes = tuple(detector_modes)

    @property
    def detector_modes(self):
        return self._detector_modes

    def supports_detector_mode(self, mode):
        if not isinstance(mode, TEMDetectorMode):
            raise ValueError("Mode has to be a TEMDetectorMode")
        return mode in self._detector_modes

    def set_exposure_time(self, value):
        self.set_parameter("exposure_time", value)

    def get_exposure_time(self):
        return self.get_parameter("exposure_time")

    def set_gain(self, value):
        self.set_parameter("gain", value)

    def get_gain(self):
        return self.get_parameter("gain")

    def set_binning(self, value):
        self.set_parameter("binning", value)

    def get_binning(self):
        return self.get_parameter("binning")


class TEMStack:
    def __init__(
        self,
        components=None
    ):
        if components is None:
            components = []
        if not isinstance(components, (list, tuple)):
            raise ValueError("Components have to be provided as list or tuple")

        self._stack = []
        self._components_by_name = {}
        self._components_by_kind = defaultdict(list)
        self._components_by_region = defaultdict(list)

        for component in components:
            self.add_component(component)

    def __iter__(self):
        return iter(self._stack)

    def __len__(self):
        return len(self._stack)

    def __getitem__(self, key):
        if isinstance(key, int) or isinstance(key, slice):
            return self._stack[key]
        if isinstance(key, str):
            return self.require_component(key)
        raise TypeError("TEMStack indices have to be integers, slices or component names")

    def __contains__(self, item):
        if isinstance(item, str):
            return item in self._components_by_name
        return item in self._stack

    def add_component(self, component):
        if not isinstance(component, TEMComponent):
            raise ValueError("Component has to be derived from TEMComponent")
        if component.name in self._components_by_name:
            raise ValueError(f"Duplicate component name {component.name}")

        self._stack.append(component)
        self._components_by_name[component.name] = component
        self._components_by_kind[component.kind].append(component)
        self._components_by_region[component.region].append(component)

    def find_component(
        self,
        name=None,
        kind=None,
        region=None,
        component_class=None,
        tag=None,
        mode=None,
        index=0
    ):
        components = self.find_components(
            name=name,
            kind=kind,
            region=region,
            component_class=component_class,
            tag=tag,
            mode=mode
        )
        if not isinstance(index, int):
            raise ValueError("Index has to be an integer")
        if (index < 0) or (index >= len(components)):
            return None
        return components[index]

    def list_components(self):
        return tuple(self._stack)

    def keys(self):
        return tuple(self._components_by_name.keys())

    def values(self):
        return tuple(self._stack)

    def items(self):
        return tuple((component.name, component) for component in self._stack)

    def get_parameter_names(self):
        parameter_names = []
        for component in self._stack:
            for parameter_name, description in component.get_parameter_names():
                parameter_names.append(
                    (f"{component.name}.{parameter_name}", description)
                )
        return tuple(parameter_names)

    def get_parameters(self):
        parameters = {}
        for component in self._stack:
            for parameter_name, value in component.get_parameters().items():
                parameters[f"{component.name}.{parameter_name}"] = value
        return parameters

    def set_parameters(self, parameters):
        if not isinstance(parameters, dict):
            raise ValueError("Parameters have to be a dictionary")

        for parameter_key, value in parameters.items():
            if not isinstance(parameter_key, str):
                raise ValueError("Parameter keys have to be strings")
            key_parts = parameter_key.split(".", 1)
            if len(key_parts) != 2:
                raise ValueError("Parameter keys have to use the form component.parameter")
            component_name, parameter_name = key_parts
            component = self.require_component(component_name)
            component.set_parameter(parameter_name, value)

    def get_component(self, name):
        if not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("Component name has to be a non empty string")
        return self._components_by_name.get(name)

    def require_component(self, name):
        component = self.get_component(name)
        if component is None:
            raise ValueError(f"Unknown component {name}")
        return component

    def get_components_by_kind(self, kind):
        if not isinstance(kind, TEMSubsystemKind):
            raise ValueError("Kind has to be a TEMSubsystemKind")
        return tuple(self._components_by_kind.get(kind, []))

    def get_components_by_region(self, region):
        if not isinstance(region, TEMColumnRegion):
            raise ValueError("Region has to be a TEMColumnRegion")
        return tuple(self._components_by_region.get(region, []))

    def find_components(
        self,
        name=None,
        kind=None,
        region=None,
        component_class=None,
        tag=None,
        mode=None
    ):
        components = self._stack

        if name is not None:
            if not isinstance(name, str):
                raise ValueError("Name has to be a string")
            components = [component for component in components if component.name == name]
        if kind is not None:
            if not isinstance(kind, TEMSubsystemKind):
                raise ValueError("Kind has to be a TEMSubsystemKind")
            components = [component for component in components if component.kind == kind]
        if region is not None:
            if not isinstance(region, TEMColumnRegion):
                raise ValueError("Region has to be a TEMColumnRegion")
            components = [component for component in components if component.region == region]
        if component_class is not None:
            if not isinstance(component_class, type):
                raise ValueError("Component class has to be a type")
            components = [component for component in components if isinstance(component, component_class)]
        if tag is not None:
            if not isinstance(tag, str):
                raise ValueError("Tag has to be a string")
            components = [component for component in components if tag in component.tags]
        if mode is not None:
            if not isinstance(mode, TEMOpticalMode):
                raise ValueError("Mode has to be a TEMOpticalMode")
            components = [component for component in components if component.supports_mode(mode)]

        return tuple(components)

    def get_source(self):
        sources = self.get_components_by_kind(TEMSubsystemKind.ELECTRON_SOURCE)
        if len(sources) == 0:
            return None
        return sources[0]

    def get_stage(self):
        stages = self.get_components_by_kind(TEMSubsystemKind.SAMPLE_STAGE)
        if len(stages) == 0:
            return None
        return stages[0]

    def get_detectors(self, detector_mode=None):
        detectors = list(self.get_components_by_kind(TEMSubsystemKind.DETECTOR))
        if detector_mode is None:
            return tuple(detectors)
        if not isinstance(detector_mode, TEMDetectorMode):
            raise ValueError("Detector mode has to be a TEMDetectorMode")
        return tuple(
            detector
            for detector in detectors
            if detector.supports_detector_mode(detector_mode)
        )

    def get_illumination_path(self):
        return tuple(
            component
            for component in self._stack
            if component.region in (
                TEMColumnRegion.EMISSION,
                TEMColumnRegion.ILLUMINATION,
                TEMColumnRegion.PRE_SPECIMEN
            )
        )

    def get_detection_path(self):
        return tuple(
            component
            for component in self._stack
            if component.region in (
                TEMColumnRegion.POST_SPECIMEN,
                TEMColumnRegion.DETECTION
            )
        )

    def get_components_between(self, start_name, end_name, inclusive=False):
        start_component = self.require_component(start_name)
        end_component = self.require_component(end_name)

        start_index = self._stack.index(start_component)
        end_index = self._stack.index(end_component)
        if start_index > end_index:
            raise ValueError("Start component has to be before end component in the stack")

        if inclusive:
            return tuple(self._stack[start_index:end_index + 1])
        return tuple(self._stack[start_index + 1:end_index])

    def describe_stack(self):
        return tuple(self.describe_components())

    def describe_components(self):
        return tuple(
            dict(
                {
                    "index": index
                },
                **component.describe()
            )
            for index, component in enumerate(self._stack)
        )


class TransmissionElectronMicroscope:
    def __init__(
        self,
        stack=None,
        supported_modes=None,
        metadata=None
    ):
        if stack is None:
            stack = TEMStack()
        if supported_modes is None:
            supported_modes = []
        if metadata is None:
            metadata = {}
        if not isinstance(stack, TEMStack):
            if isinstance(stack, (list, tuple)):
                stack = TEMStack(stack)
            else:
                raise ValueError("Stack has to be a TEMStack, list or tuple")
        if not isinstance(supported_modes, (list, tuple)):
            raise ValueError("Supported modes have to be a list or tuple")
        if not isinstance(metadata, dict):
            raise ValueError("Metadata has to be a dictionary")

        for mode in supported_modes:
            if not isinstance(mode, TEMOpticalMode):
                raise ValueError("All supported modes have to be TEMOpticalMode entries")

        self._stack = stack
        self._metadata = dict(metadata)
        self._supported_modes = tuple(supported_modes)
        self._optical_mode = None
        self._runtime_modes = {}

    @property
    def metadata(self):
        return dict(self._metadata)

    @property
    def supported_modes(self):
        return self._supported_modes

    @property
    def stack(self):
        return self._stack

    @property
    def optical_mode(self):
        return self._optical_mode

    def supports_mode(self, mode):
        if not isinstance(mode, TEMOpticalMode):
            raise ValueError("Mode has to be a TEMOpticalMode")
        return mode in self._supported_modes

    def set_optical_mode(self, mode):
        if not isinstance(mode, TEMOpticalMode):
            raise ValueError("Mode has to be a TEMOpticalMode")
        if not self.supports_mode(mode):
            raise ValueError(f"Optical mode {mode.value} is not supported by this TEM")
        self._optical_mode = mode

    def add_runtime_mode(self, runtime_mode):
        if not isinstance(runtime_mode, TEMRuntimeMode):
            raise ValueError("Runtime mode has to be a TEMRuntimeMode")
        if runtime_mode.name in self._runtime_modes:
            raise ValueError(f"Duplicate runtime mode {runtime_mode.name}")
        self._runtime_modes[runtime_mode.name] = runtime_mode

    def get_runtime_mode(self, name):
        if not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("Runtime mode name has to be a non empty string")
        return self._runtime_modes.get(name)

    def list_runtime_modes(self):
        return tuple(self._runtime_modes.values())

    def activate_runtime_mode(self, name):
        runtime_mode = self.get_runtime_mode(name)
        if runtime_mode is None:
            raise ValueError(f"Unknown runtime mode {name}")

        if runtime_mode.optical_mode is not None:
            self.set_optical_mode(runtime_mode.optical_mode)

        for component_name in runtime_mode.component_names():
            component = self.require_component(component_name)
            for parameter_name, value in runtime_mode.get_component_parameters(component_name).items():
                component.set_parameter(parameter_name, value)

        return runtime_mode

    def set_component_parameter(self, component_name, parameter_name, value):
        component = self.require_component(component_name)
        component.set_parameter(parameter_name, value)

    def get_component_parameter(self, component_name, parameter_name):
        component = self.require_component(component_name)
        return component.get_parameter(parameter_name)

    def add_component(self, component):
        return self._stack.add_component(component)

    def list_components(self):
        return self._stack.list_components()

    def get_component(self, name):
        return self._stack.get_component(name)

    def require_component(self, name):
        return self._stack.require_component(name)

    def get_parameter_names(self):
        return self._stack.get_parameter_names()

    def get_parameters(self):
        return self._stack.get_parameters()

    def set_parameters(self, parameters):
        return self._stack.set_parameters(parameters)

    def get_components_by_kind(self, kind):
        return self._stack.get_components_by_kind(kind)

    def get_components_by_region(self, region):
        return self._stack.get_components_by_region(region)

    def find_components(self, kind=None, region=None, tag=None, mode=None):
        return self._stack.find_components(
            name=None,
            kind=kind,
            region=region,
            component_class=None,
            tag=tag,
            mode=mode
        )

    def find_component(
        self,
        name=None,
        kind=None,
        region=None,
        component_class=None,
        tag=None,
        mode=None,
        index=0
    ):
        return self._stack.find_component(
            name=name,
            kind=kind,
            region=region,
            component_class=component_class,
            tag=tag,
            mode=mode,
            index=index
        )

    def get_source(self):
        return self._stack.get_source()

    def get_stage(self):
        return self._stack.get_stage()

    def get_detectors(self, detector_mode=None):
        return self._stack.get_detectors(detector_mode=detector_mode)

    def get_illumination_path(self):
        return self._stack.get_illumination_path()

    def get_detection_path(self):
        return self._stack.get_detection_path()

    def get_components_between(self, start_name, end_name, inclusive=False):
        return self._stack.get_components_between(
            start_name,
            end_name,
            inclusive=inclusive
        )

    def describe_stack(self):
        return self._stack.describe_stack()

    def describe_components(self):
        return self._stack.describe_components()

    def set_component_parameter_by_selector(
        self,
        parameter_name,
        value,
        name=None,
        kind=None,
        region=None,
        component_class=None,
        tag=None,
        mode=None,
        index=0
    ):
        component = self.find_component(
            name=name,
            kind=kind,
            region=region,
            component_class=component_class,
            tag=tag,
            mode=mode,
            index=index
        )
        if component is None:
            raise ValueError("No component matches the given selector")
        component.set_parameter(parameter_name, value)
        return component
