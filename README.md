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
