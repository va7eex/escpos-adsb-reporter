#
# This is a python adaptation of https://github.com/adsbxchange/dump1090-fa/blob/master/public_html/registrations.js
# All credit to the original authors.
#

import math

class Hexid:

    limited_alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    full_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __init__(self):

        self.stride_mappings = [
            { 'start': 0x008011, 's1': 26*26, 's2': 26, 'prefix': "ZS-" },

            { 'start': 0x390000, 's1': 1024, 's2':  32, 'prefix': "F-G" },
            { 'start': 0x398000, 's1': 1024, 's2':  32, 'prefix': "F-H" },

            { 'start': 0x3C4421, 's1': 1024,  's2': 32, 'prefix': "D-A", 'first': 'AAA', 'last': 'OZZ' },
            { 'start': 0x3C0001, 's1': 26*26, 's2': 26, 'prefix': "D-A", 'first': 'PAA', 'last': 'ZZZ' },
            { 'start': 0x3C8421, 's1': 1024,  's2': 32, 'prefix': "D-B", 'first': 'AAA', 'last': 'OZZ' },
            { 'start': 0x3C2001, 's1': 26*26, 's2': 26, 'prefix': "D-B", 'first': 'PAA', 'last': 'ZZZ' },
            { 'start': 0x3CC000, 's1': 26*26, 's2': 26, 'prefix': "D-C" },
            { 'start': 0x3D04A8, 's1': 26*26, 's2': 26, 'prefix': "D-E" },
            { 'start': 0x3D4950, 's1': 26*26, 's2': 26, 'prefix': "D-F" },
            { 'start': 0x3D8DF8, 's1': 26*26, 's2': 26, 'prefix': "D-G" },
            { 'start': 0x3DD2A0, 's1': 26*26, 's2': 26, 'prefix': "D-H" },
            { 'start': 0x3E1748, 's1': 26*26, 's2': 26, 'prefix': "D-I" },

            { 'start': 0x448421, 's1': 1024,  's2': 32, 'prefix': "OO-" },
            { 'start': 0x458421, 's1': 1024,  's2': 32, 'prefix': "OY-" },
            { 'start': 0x460000, 's1': 26*26, 's2': 26, 'prefix': "OH-" },
            { 'start': 0x468421, 's1': 1024,  's2': 32, 'prefix': "SX-" },
            { 'start': 0x490421, 's1': 1024,  's2': 32, 'prefix': "CS-" },
            { 'start': 0x4A0421, 's1': 1024,  's2': 32, 'prefix': "YR-" },
            { 'start': 0x4B8421, 's1': 1024,  's2': 32, 'prefix': "TC-" },
            { 'start': 0x740421, 's1': 1024,  's2': 32, 'prefix': "JY-" },
            { 'start': 0x760421, 's1': 1024,  's2': 32, 'prefix': "AP-" },
            { 'start': 0x768421, 's1': 1024,  's2': 32, 'prefix': "9V-" },
            { 'start': 0x778421, 's1': 1024,  's2': 32, 'prefix': "YK-" },
            { 'start': 0xC00001, 's1': 26*26, 's2': 26, 'prefix': "C-F" },
            { 'start': 0xC044A9, 's1': 26*26, 's2': 26, 'prefix': "C-G" },
            { 'start': 0xE01041, 's1': 4096,  's2': 64, 'prefix': "LV-" }
        ]

        self.numeric_mappings = [
            { 'start': 0x140000, 'first': 0,    'count': 100000, 'template': "RA-00000" },
            { 'start': 0x0B03E8, 'first': 1000, 'count': 1000,   'template': "CU-T0000" }
        ]

        for mapping in self.stride_mappings:

            if not 'alphabet' in mapping:
                    mapping['alphabet'] = self.full_alphabet

            if 'first' in mapping:
                    c1 = mapping['alphabet'].index(mapping['first'][0])
                    c2 = mapping['alphabet'].index(mapping['first'][1])
                    c3 = mapping['alphabet'].index(mapping['first'][2])
                    mapping['offset'] = c1 * mapping['s1'] + c2 * mapping['s2'] + c3
            else:
                    mapping['offset'] = 0
        

            if 'last' in mapping:
                c1 = mapping['alphabet'].index(mapping['last'][0])
                c2 = mapping['alphabet'].index(mapping['last'][1])
                c3 = mapping['alphabet'].index(mapping['last'][2])
                mapping['end'] = (mapping['start'] - mapping['offset'] +
                        c1 * mapping['s1'] +
                        c2 * mapping['s2'] +
                        c3 - mapping['offset'])
            else:
                mapping['end'] = (mapping['start'] - mapping['offset'] +
                        (len(mapping['alphabet']) - 1) * mapping['s1'] +
                        (len(mapping['alphabet']) - 1) * mapping['s2'] +
                        (len(mapping['alphabet']) - 1))

        for mapping in self.numeric_mappings:
                mapping['end'] = mapping['start'] + mapping['count'] - 1

    def lookup(self, hexid):

        hexid = int(hexid,16)
        if math.isnan(hexid):
            return None

        reg = self.n_reg(hexid)
        if reg:
            return reg

        reg = self.ja_reg(hexid)
        if reg:
            return reg

        reg = self.hl_reg(hexid)
        if reg:
            return reg

        reg = self.numeric_reg(hexid)
        if reg:
            return reg

        reg = self.stride_reg(hexid)
        if reg:
            return reg

        return None

    def stride_reg(self, hexid):
        for mapping in self.stride_mappings:
            if hexid < mapping['start'] or hexid > mapping['end']:
                continue

            offset = hexid - mapping['start'] + mapping['offset']

            i1 = math.floor(offset / mapping['s1'])
            offset %= mapping['s1']
            i2 = math.floor(offset / mapping['s2'])
            offset %= mapping['s2']
            i3 = offset

            if (i1 < 0 or i1 >= len(mapping['alphabet'])
                or i2 < 0 or i2 >= len(mapping['alphabet'])
                or i3 < 0 or i3 >= len(mapping['alphabet'])):
                continue

            return mapping['prefix'] + mapping['alphabet'][i1]+ mapping['alphabet'][i2]+ mapping['alphabet'][i3]

        return None

    def numeric_reg(self, hexid):
        for mapping in self.numeric_mappings:
            if hexid < mapping['start'] or hexid > mapping['end']:
                continue
            reg = str(hexid - mapping['start'] + mapping['first'])

            return mapping['template'][0:len(mapping['template']-len(reg))] + reg

    #
    # US N-Numbers
    #

    def n_letters(self, rem):
        if rem == 0: return ''

        rem -= 1
        return self.limited_alphabet[math.floor(rem/25)] + self.n_letter(rem % 25)

    def n_letter(self, rem):
        if rem == 0: return ''

        rem -= 1
        return self.limited_alphabet[rem]

    def n_reg(self, hexid):
        offset = hexid - 0xA00001
        if offset < 0 or offset > 915399: return None

        digit1 = math.floor(offset / 101711)+1
        reg = f'N{digit1}'
        offset %= 101711
        if offset <= 600:
            return reg + self.n_letters(offset)

        offset -= 601
        digit2 = math.floor(offset / 10111)
        reg += f'{digit2}'
        offset %= 10111
        if offset <= 600:
            return reg + self.n_letters(offset)

        offset -= 601
        digit3 = math.floor(offset / 951)
        reg += f'{digit3}'
        offset %= 951
        if offset <= 600:
            return reg + self.n_letters(offset)

        offset -= 601
        digit4 = math.floor(offset / 35)
        reg += f'{round(digit4,0)}'
        offset %= 35
        if offset <= 24:
            return reg + f'{self.n_letters(offset)}'

        offset -= 25
        return reg + f'{round(offset,0)}'

    #
    # South Korea
    #

    def hl_reg(self, hexid):
        if hexid >= 0x71BA00 and hexid <= 0x71BF99:
            return 'HL' + int(hexid - 0x71BA00 + 0x7200, 16)
        if hexid >= 0x71C000 and hexid <= 0x71C099:
            return 'HL' + int(hexid - 0x71C000 + 0x8000, 16)
        if hexid >= 0x71C200 and hexid <= 0x71C299:
            return 'HL' + int(hexid - 0x71C200 + 0x8200, 16)
        return None
    
    #
    # Japan
    #

    def ja_reg(self, hexid):
        offset = hexid - 0x840000
        if offset < 0 or offset >= 229840:
            return None
        
        reg = 'JA'

        digit1 = math.floor(offset / 22984)
        if digit1 < 0 or digit1 > 9:
            return None
        reg += digit1
        offset %= 22984

        digit2 = math.floor(offset / 916)
        if digit2 < 0 or digit2 > 9:
            return None
        reg += digit2
        offset %= 916

        if offset < 340:
            digit3 = math.floor(offset / 34)
            reg += digit3
            offset %= 34

            if offset < 10:
                return reg + offset
            offset -= 10
            return reg + self.limited_alphabet[offset]
        
        offset -= 340
        letter3 = math.floor(offset/24)
        return reg + self.limited_alphabet[letter3] + self.limited_alphabet[offset % 24]
