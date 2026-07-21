# TEM interface

This document describes the `TransmissionElectronMicroscope` abstraction that
is provided by this repository. It is intended for developers who implement
device specific TEM backends on top of the frontend classes in `labdevices.tem`.

The goal of the abstraction is:

* client code should work on semantic TEM concepts and not on registers,
  protocol message IDs, TCP commands or vendor specific naming
* the optical column should stay modular because different instruments expose
  different combinations of sources, monochromators, condenser systems,
  correctors, scanners, stages, filters, spectrometers and detectors
* a backend should be able to expose both standard operating points and
  intermediate runtime states where individual components are tuned directly

## Overview

The TEM abstraction has three main layers:

* `TransmissionElectronMicroscope`
  * frontend object used by client code
  * exposes optical mode selection, runtime modes, component lookup and
    flattened parameter access
* `TEMStack`
  * ordered list of the components that form one concrete microscope
  * keeps the physical order of the column and detector chain
* `TEMComponent`
  * base class of all component types
  * stores metadata, supported optical modes and supported parameters

The frontend class should be the main entry point for users. The stack and its
components are still accessible directly because for a TEM this is often useful.

## Optical mode and runtime mode

Two different concepts exist:

* `TEMOpticalMode`
  * describes the optical use case such as `TEM`, `STEM`, `DIFFRACTION`,
    `SCANNING_DIFFRACTION` or `SPECTROSCOPY`
* `TEMRuntimeMode`
  * describes a named set of semantic parameter values for multiple components
  * can optionally also specify the optical mode that should be active

This means:

* the optical mode selects the general beam path class
* the runtime mode selects one concrete operating point inside that class

Examples for runtime modes:

* `search`
* `low_dose_alignment`
* `high_resolution_probe`
* `eels_acquisition`
* `diffraction_setup`

## The stack

The `TEMStack` models the concrete microscope composition.

Example:

```python
from labdevices.tem import TEMColumnRegion, TEMDetectorMode, TEMOpticalMode
from labdevices.tem import TEMStack
from labdevices.tem import ElectronSource, Monochromator, Lens, Stigmator
from labdevices.tem import ScanGenerator, SampleStage, Detector

stack = TEMStack([
    ElectronSource("gun"),
    Monochromator("mono"),
    Lens("c1", lens_family = "condenser", region = TEMColumnRegion.ILLUMINATION),
    Lens("c2", lens_family = "condenser", region = TEMColumnRegion.ILLUMINATION),
    Stigmator("condenser_stig", region = TEMColumnRegion.ILLUMINATION),
    ScanGenerator("scan", supported_modes = [TEMOpticalMode.STEM]),
    SampleStage("stage"),
    Detector(
        "haadf",
        detector_modes = [TEMDetectorMode.HIGH_ANGLE_ANNULAR_DARK_FIELD],
        supported_modes = [TEMOpticalMode.STEM]
    )
])
```

The order is important. It should follow the physical order in the microscope
as seen by the electron beam path.

Typical order:

* source region
* illumination region
* pre specimen region
* specimen region
* post specimen region
* detection region

Not every microscope needs all component classes and not every vendor uses the
same subdivision. The stack is intentionally open ended.

## Stack access

`TEMStack` behaves both like an ordered sequence and like a name lookup table.

Sequence style:

```python
for component in tem.stack:
    print(component.name)

first = tem.stack[0]
subset = tem.stack[2:5]
count = len(tem.stack)
```

Name based access:

```python
gun = tem.stack["gun"]

if "haadf" in tem.stack:
    detector = tem.stack["haadf"]
```

Mapping helpers:

```python
names = tem.stack.keys()
components = tem.stack.values()
items = tem.stack.items()
```

These helpers return the components in stack order.

## Component model

Every concrete subsystem derives from `TEMComponent`.

Currently available component classes:

* `ElectronSource`
* `Monochromator`
* `Aperture`
* `Lens`
* `Deflector`
* `Stigmator`
* `AberrationCorrector`
* `ScanGenerator`
* `SampleStage`
* `EnergyFilter`
* `Spectrometer`
* `Detector`

Each component has:

* a unique `name`
* a `kind` from `TEMSubsystemKind`
* a `region` from `TEMColumnRegion`
* optional `tags`
* optional `supported_modes`
* optional `metadata`
* a set of `TEMParameter` definitions

Parameters are semantic and backend agnostic. For example:

* `acceleration_voltage`
* `emission_current`
* `current`
* `focal_length`
* `x`
* `y`
* `energy_window_width`
* `exposure_time`

A backend should prefer semantic names that are understandable without vendor
knowledge.

## Parameter access on components

Each component supports generic parameter access:

```python
component.set_parameter("current", 0.83)
value = component.get_parameter("current")
all_values = component.get_parameters()
component.set_parameters({
    "current": 0.81,
    "focal_length": 1.3e-3
})
```

Each component also exposes explicit getters and setters for its built in
parameters where applicable. For example:

```python
tem.stack["gun"].set_acceleration_voltage(200000)
tem.stack["mono"].set_slit_width(0.2)
tem.stack["c2"].set_focal_length(1.2e-3)
tem.stack["stage"].set_alpha(12.0)
tem.stack["camera"].set_exposure_time(0.1)
```

This is useful for direct coding and for discoverability in IDEs.

## Component introspection

For agent style access and generic tooling every component can describe itself.

```python
description = tem.stack["c2"].describe()
```

The returned structure includes:

* component name
* component class name
* kind
* region
* tags
* supported optical modes
* metadata
* parameter definitions and current parameter values

Every `TEMParameter` can provide:

* name
* default value
* unit
* human readable description
* readonly flag
* metadata

## Flattened stack view

For generic automation a TEM often needs a simple flat parameter view. This is
provided by `TEMStack.get_parameter_names()`, `TEMStack.get_parameters()` and
`TEMStack.set_parameters()`. The same methods are also available on
`TransmissionElectronMicroscope`.

The flat keys use the form:

```text
component_name.parameter_name
```

Examples:

* `gun.acceleration_voltage`
* `gun.emission_current`
* `mono.slit_width`
* `c2.current`
* `c2.focal_length`
* `stage.alpha`
* `camera.exposure_time`

### `get_parameter_names()`

Returns tuples in stable stack order:

```python
(
    ("gun.acceleration_voltage", "Electron acceleration voltage"),
    ("gun.emission_current", "Electron emission current"),
    ("mono.energy_spread", "Target energy spread"),
    ...
)
```

This is intended for enumeration and UI or agent prompt generation.

### `get_parameters()`

Returns a simple dictionary using the same stable key order:

```python
{
    "gun.acceleration_voltage": 200000,
    "gun.emission_current": 2.1e-6,
    "mono.energy_spread": 0.15,
    ...
}
```

The keys are always ordered by:

* component order in the stack
* parameter order in the component definition

### `set_parameters()`

Accepts a dictionary with the same keys. The dictionary may contain only a
subset of keys.

```python
tem.set_parameters({
    "gun.acceleration_voltage": 300000,
    "c2.current": 0.84,
    "stage.alpha": 10.0
})
```

The method applies the values to the corresponding components.

This flat view is especially useful for:

* agents
* configuration storage
* preset handling
* diffing operating points
* logging state snapshots

## Finding components

The stack supports semantic lookup:

```python
component = tem.find_component(
    name = "c2",
    kind = TEMSubsystemKind.LENS
)

all_lenses = tem.find_components(kind = TEMSubsystemKind.LENS)
illumination_components = tem.find_components(region = TEMColumnRegion.ILLUMINATION)
```

Supported selectors are:

* `name`
* `kind`
* `region`
* `component_class`
* `tag`
* `mode`
* `index`

This allows backend independent code to select components by meaning and not by
vendor register address.

## Paths inside the column

The stack provides helper accessors:

* `get_source()`
* `get_stage()`
* `get_detectors()`
* `get_illumination_path()`
* `get_detection_path()`
* `get_components_between(start_name, end_name, inclusive = False)`

These methods are convenience functions on top of the stack order and region
information.

## Backend implementation guidelines

This repository currently only defines frontend abstractions. A backend package
should derive from these classes and bind the semantic interface onto a real
microscope.

The important rules are:

* keep the public API semantic
  * do not expose register numbers or protocol specific names in the frontend
* use meaningful component names
  * `gun`, `mono`, `c1`, `c2`, `objective`, `scan`, `stage`, `haadf`, `eels`
  * avoid names that only make sense for one protocol dump
* keep a stable stack order
  * changing order changes the flat parameter order
* keep parameter meanings stable
  * `current` should still mean lens current across instruments
* add vendor specific details to `metadata`
  * for example hardware IDs, register mappings, protocol object IDs or limits
* if a hardware feature does not exist, do not model it
  * do not add fake components only to make one vendor match another

Recommended backend structure:

* subclass the relevant component classes if vendor specific behaviour is needed
* keep low level communication in private methods
* map semantic parameter names onto registers or messages internally
* if hardware values are quantized or limited, enforce that inside the backend
* if a readback exists, make `get_parameter()` return the semantic readback
* if no readback exists, document whether the backend returns a cached setpoint

## Runtime modes in backends

Backends can either:

* build runtime modes dynamically from application logic
* or predefine them and expose them through `add_runtime_mode()`

A runtime mode should contain only semantic values. For example:

```python
from labdevices.tem import TEMRuntimeMode, TEMOpticalMode

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
```

## What a backend should not do

A backend should not:

* leak raw registers into the public API
* assume client code knows vendor specific component numbering
* reorder stack entries depending on temporary state
* overload one parameter name with multiple meanings
* hide important semantic degrees of freedom only in backend private methods

## Minimal backend checklist

When implementing a TEM backend, verify the following:

* the microscope is represented by a `TransmissionElectronMicroscope`
* all physical subsystems are placed into a `TEMStack` in beam order
* all public parameters have semantic names
* every public parameter appears in the flattened view
* `describe_components()` returns enough information for generic tooling
* runtime modes can be expressed without vendor protocol knowledge
* client code can operate the microscope without knowing any register map
