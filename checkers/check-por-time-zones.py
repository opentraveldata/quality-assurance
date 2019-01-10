#!/usr/bin/env python3

# You need to install the latest pytz, otherwise you might get false positives. Then run the tests with:
# OPTD_POR_FILE=./to_be_checked/optd_por_public.csv python check-por-time-zones.py

import pytz

def test_timezones(base):
    for por in base:
        tz = base.get(por, 'timezone')
        try:
            pytz.timezone(tz)
        except pytz.exceptions.UnknownTimeZoneError:
            print('Unknown timezone for {0} ({1})'.format(por, tz))


def test_geocodes(base):
    for por in base:
        if base.get_location(por) is None:
            print('Missing geocode for {0}'.format(por))


if __name__ == '__main__':
    from neobase import NeoBase
    test_timezones(NeoBase())
    test_geocodes(NeoBase())
