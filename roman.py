"""Convert to and from Roman numerals

This program is part of "Dive Into Python", a free Python book for
experienced programmers.  Visit http://diveintopython.org/ for the
latest version.

Mildly modified by Brennan Vincent (cases and removing fromRoman)
"""

#Define exceptions
class RomanError(Exception): pass
class OutOfRangeError(RomanError): pass
class NotIntegerError(RomanError): pass
class InvalidRomanNumeralError(RomanError): pass

#Define digit mapping
capRomanNumeralMap = (('M',  1000),
				   ('CM', 900),
				   ('D',  500),
				   ('CD', 400),
				   ('C',  100),
				   ('XC', 90),
				   ('L',  50),
				   ('XL', 40),
				   ('X',  10),
				   ('IX', 9),
				   ('V',  5),
				   ('IV', 4),
				   ('I',  1))

lowerRomanNumeralMap = (('m',  1000),
				   ('cm', 900),
				   ('d',  500),
				   ('cd', 400),
				   ('c',  100),
				   ('xc', 90),
				   ('l',  50),
				   ('xl', 40),
				   ('x',  10),
				   ('ix', 9),
				   ('v',  5),
				   ('iv', 4),
				   ('i',  1))
def toRoman(n, uppercase):
    """convert integer to Roman numeral"""
    if not (0 < n < 5000):
        raise OutOfRangeError, "number out of range (must be 1..4999)"
    if int(n) <> n:
        raise NotIntegerError, "non-integers can not be converted"

    result = ""
    romanNumeralMap = capRomanNumeralMap if uppercase else lowerRomanNumeralMap
    for numeral, integer in romanNumeralMap:
        while n >= integer:
            result += numeral
            n -= integer
    return result
