# Lab device base classes

This repository supplies some abstract base classes for various device families
that are used as basis for specific implementations. Those base classes provide
the frontend used by experimental scripts - the implementations are then
done in a device specific way by other packages.

This package emerged from re-implementing different interfaces for different
devices from time to time to provide some kind of common base structure for
different devices.

The base classes just implement basic parameter validation and provide a calling
convention. Changes should never break existing libraries.

Currently implemented base classes:

* Power supplies
   * [KA3005PSerial](https://github.com/tspspi/pyka3005p) for Korad KA3005P power supplies via serial interface
   * [pydp832](https://github.com/tspspi/pydp832) for Rigol DP832 power supplies via Ethernet
   * [pykd3300](https://github.com/tspspi/pykd3300) for Korad KD3305P and KD3305P+ power supply (ethernet, usb, serial)
   * [pyka3005p](https://github.com/tspspi/pyka3005p) for Korad KA3005P
* Oscilloscopes
   * [Rigol MSO5000](https://github.com/tspspi/pymso5000) for Rigol MSO5000 oscilloscopes
   * [Rigol DHOxxx](https://github.com/MasterJubei/pydho800) for Rigol DHOxxx oscilloscopes (by [MasterJubei](https://github.com/MasterJubei))
* Function generators / Arbitrary waveform generators
   * [FY6900](https://github.com/tspspi/pyfy6900) for FE FY6900
   * Rigol DG832 (work in progress)
   * [Siglent SSG3021X](https://github.com/tspspi/pyssg3021x/) sinewave 9 kHz - 2.1 GHz generator (work in progress)
   * [Rigol DG1000Z](https://github.com/PMSchueler/pydg100z) by [PMSchueler](https://github.com/PMSchueler)
* Pressure gauges
   * [PYBPG400](https://github.com/tspspi/pybpg400) for the RS232C interface of the INFICON BPG400 pressure gauge
* Vector network analyzers
   * [NanoVNA v2](https://github.com/tspspi/pynanovnav2) (work in progress)
* Scanning Electron Microscopes
   * [XL30 ESEM](https://github.com/tspspi/pyxl30) (work in progress)
* General purpose I/O devices
   * [Rasbperry PI GPIO under FreeBSD](https://github.com/tspspi/fbsdgpio/)
* SPI bus
   * [FreeBSD spigen interface](https://github.com/tspspi/fbsdspiwrapper)

## TEM architecture

The TEM abstraction is intentionally split into two layers:

* `TransmissionElectronMicroscope` is the frontend entry point used by client code
* `TEMStack` stores the ordered composition of the microscope
* Individual subsystems are represented by classes derived from `TEMComponent`
* Optical modes such as `TEM` and `STEM` are separate from runtime modes that store semantic parameter sets for intermediate operating points

This keeps client code independent of hardware specific details such as registers,
message IDs or TCP commands. A backend implementation can later translate semantic
operations onto a concrete microscope while still exposing the same class structure.

Example:

```python
from labdevices.tem import TransmissionElectronMicroscope
from labdevices.tem import TEMStack, TEMOpticalMode, TEMDetectorMode, TEMColumnRegion
from labdevices.tem import ElectronSource, Monochromator, Lens, Stigmator
from labdevices.tem import ScanGenerator, SampleStage, AberrationCorrector, Detector

stack = TEMStack([
    ElectronSource("x_feg", emission_type = "cold_field_emission"),
    Monochromator("monochromator"),
    Lens("c1", lens_family = "condenser", region = TEMColumnRegion.ILLUMINATION),
    Lens("c2", lens_family = "condenser", region = TEMColumnRegion.ILLUMINATION),
    Stigmator("condenser_stig", region = TEMColumnRegion.ILLUMINATION),
    ScanGenerator("scan_generator", supported_modes = [TEMOpticalMode.STEM]),
    SampleStage("eucentric_stage"),
    AberrationCorrector("probe_corrector", region = TEMColumnRegion.POST_SPECIMEN),
    Detector(
        "haadf",
        detector_modes = [TEMDetectorMode.HIGH_ANGLE_ANNULAR_DARK_FIELD],
        supported_modes = [TEMOpticalMode.STEM]
    )
])

tem = TransmissionElectronMicroscope(
    stack = stack,
    supported_modes = [TEMOpticalMode.TEM, TEMOpticalMode.STEM]
)

detectors = tem.get_detectors(TEMDetectorMode.HIGH_ANGLE_ANNULAR_DARK_FIELD)
```

Runtime adjustments and intermediate operating points are supported without
exposing registers to client code:

```python
from labdevices.tem import TEMRuntimeMode

tem.set_optical_mode(TEMOpticalMode.STEM)
tem.stack["c2"].set_current(0.83)
tem.stack["c2"].set_focal_length(1.2e-3)
tem.stack["condenser_stig"].set_x(-0.02)
tem.stack["condenser_stig"].set_y(0.01)

tem.add_runtime_mode(TEMRuntimeMode(
    "probe_search",
    optical_mode = TEMOpticalMode.STEM,
    component_parameters = {
        "c2": {
            "current": 0.78,
            "focal_length": 1.4e-3
        },
        "condenser_stig": {
            "x": -0.03,
            "y": 0.015
        }
    }
))

tem.activate_runtime_mode("probe_search")
```
