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
* Oscilloscopes
   * [Rigol MSO5000](https://github.com/tspspi/pymso5000) for Rigol MSO5000 oscilloscopes
* Function generators / Arbitrary waveform generators
   * [FY6900](https://github.com/tspspi/pyfy6900) for FE FY6900
   * Rigol DG832 (work in progress)
   * [Siglent SSG3021X](https://github.com/tspspi/pyssg3021x/) sinewave 9 kHz - 2.1 GHz generator (work in progress)
* Pressure gauges
   * [PYBPG400](https://github.com/tspspi/pybpg400) for the RS232C interface of the INFICON BPG400 pressure gauge
* Vector network analyzers
   * NanoVNA v2 (work in progress)
* Scanning Electron Microscopes
   * XL30 ESEM (work in progress)
