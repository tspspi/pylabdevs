from enum import Enum

class SIUNIT(Enum):
    ONE     = 0
    DECA    = 1
    HECTO   = 2
    KILO    = 3
    MEGA    = 4
    GIGA    = 5
    TERA    = 6
    PETA    = 7
    EXA     = 8
    ZETTA   = 9
    YOTTA   = 10
    RONNA   = 11
    QUETTA  = 12
    DECI    = 13
    CENTI   = 14
    MILLI   = 15
    MICRO   = 16
    NANO    = 17
    PICO    = 18
    FEMTO   = 19
    ATTO    = 20
    ZEPTO   = 21
    YOCTO   = 22
    RONTO   = 23
    QUECTO  = 24

class SiUtils:
    def __init__(self):
        self._tbl = {
                SIUNIT.ONE    : { 'factor' : 1    , 'symbol' : ''  , 'name' : 'one'    },

                SIUNIT.DECA   : { 'factor' : 1e1  , 'symbol' : 'da', 'name' : 'deca'   },
                SIUNIT.HECTO  : { 'factor' : 1e2  , 'symbol' : 'h' , 'name' : 'hecto'  },
                SIUNIT.KILO   : { 'factor' : 1e3  , 'symbol' : 'k' , 'name' : 'kilo'   },
                SIUNIT.MEGA   : { 'factor' : 1e6  , 'symbol' : 'M' , 'name' : 'mega'   },
                SIUNIT.GIGA   : { 'factor' : 1e9  , 'symbol' : 'G' , 'name' : 'giga'   },
                SIUNIT.TERA   : { 'factor' : 1e12 , 'symbol' : 'T' , 'name' : 'tera'   },
                SIUNIT.PETA   : { 'factor' : 1e15 , 'symbol' : 'P' , 'name' : 'peta'   },
                SIUNIT.EXA    : { 'factor' : 1e18 , 'symbol' : 'E' , 'name' : 'exa'    },
                SIUNIT.ZETTA  : { 'factor' : 1e21 , 'symbol' : 'Z' , 'name' : 'zetta'  },
                SIUNIT.YOTTA  : { 'factor' : 1e24 , 'symbol' : 'Y' , 'name' : 'yotta'  },
                SIUNIT.RONNA  : { 'factor' : 1e27 , 'symbol' : 'R' , 'name' : 'ronna'  },
                SIUNIT.QUETTA : { 'factor' : 1e30 , 'symbol' : 'Q' , 'name' : 'quetta' },

                SIUNIT.DECI   : { 'factor' : 1e-1 , 'symbol' : 'd' , 'name' : 'deci'   },
                SIUNIT.CENTI  : { 'factor' : 1e-2 , 'symbol' : 'c' , 'name' : 'centi'  },
                SIUNIT.MILLI  : { 'factor' : 1e-3 , 'symbol' : 'm' , 'name' : 'milli'  },
                SIUNIT.MICRO  : { 'factor' : 1e-6 , 'symbol' : 'u' , 'name' : 'micro'  },
                SIUNIT.NANO   : { 'factor' : 1e-9 , 'symbol' : 'n' , 'name' : 'nano'   },
                SIUNIT.PICO   : { 'factor' : 1e-12, 'symbol' : 'p' , 'name' : 'pico'   },
                SIUNIT.FEMTO  : { 'factor' : 1e-15, 'symbol' : 'f' , 'name' : 'femto'  },
                SIUNIT.ATTO   : { 'factor' : 1e-18, 'symbol' : 'a' , 'name' : 'atto'   },
                SIUNIT.ZEPTO  : { 'factor' : 1e-21, 'symbol' : 'z' , 'name' : 'zepto'  },
                SIUNIT.YOCTO  : { 'factor' : 1e-24, 'symbol' : 'y' , 'name' : 'yocto'  },
                SIUNIT.RONTO  : { 'factor' : 1e-27, 'symbol' : 'r' , 'name' : 'ronto'  },
                SIUNIT.QUECTO : { 'factor' : 1e-30, 'symbol' : 'q' , 'name' : 'quecto' }
        }

    def get_unit(self, unitname):
        if unitname is None:
            return SIUNIT.ONE

        if isinstance(unitname, SIUNIT):
            return unitname
        try:
            raise ValueError("Getting via numeric value is currently not supported")
        except:
            # Search by name
            strname = str(unitname).lower().strip()
            for unit in self._tbl:
                if self._tbl[unit]['name'] == strname:
                    return unit
            return None

    def get_factor(self, unit):
        un = self.get_unit(unit)
        if un is None:
            return 1
        return self._tbl[un]['factor']

    def get_symbol(self, unit):
        un = self.get_unit(unit)
        if un is None:
            return ""
        return self._tbl[un]['symbol']

    def get_name(self, unit):
        un = self.get_unit(unit)
        if un is None:
            return ""
        return self._tbl[un]['name']

    def get_closest(self, value):
        absval = value
        if absval < 0:
            absval = absval * -1.0

        prevunit = SIUNIT.ONE

        for un in self._tbl:
            if (absval < 1) and (self._tbl[un]['factor'] >= 1):
                continue

            if absval < 1:
                if absval > self._tbl[un]['factor']:
                    return un
            else:
                if absval < self._tbl[un]['factor']:
                    return prevunit
                prevunit = un

        if absval < 1:
            return SIUNIT.QUECTO
        else:
            return SIUNIT.QUETTA

    def get_str(self, value, unit = ""):
        unt = self.get_closest(value)
        factor, symb = self.get_factor(unt), self.get_symbol(unt)

        s = f"{value / factor:.2f} {symb}{unit}".strip()
        return s
