

class LangToFlag():
    """Language codes (ISO 639-1) and country codes (ISO 3166) are built a bit differently.
    This class turns language codes into a country flag. It however has to make some assumptions.
    Such as english speakers (ISO 639-1 -> en) are from the US (ISO 3166 -> us).
    However if it is specified e.g. en-gb such generalization is not made.
    Vietnam has a VI as language code while their country code is VN.
    The country code VI is Virgin Islands of the United States."""
    def __init__(self):
        self.offset = ord('🇦') - ord('A')

    def flag(self, code):
        return chr(ord(code[0]) + self.offset) + chr(ord(code[1]) + self.offset)

    def ltf(self, code:str):
        code = code.upper()

        if len(code) != 2:
            if   code[:2] == 'EN': code = code[-2:]  # country is further specified
            elif code[:2] == 'ZH': return self.flag('CN')  # chinese speakers are from China
            elif code[:2] == 'FR': return self.flag('FR')  # french speakers are from France
            elif code[:2] == 'NO': return self.flag('NO')  # norwegian speakers are from Norway
            else:
                print(code)
                code = code[-2:]

        if   code == 'EN': code = 'US'  # english speakers are from US
        elif code == 'VI': code = 'VN'  # vietnamese speakers are from vietnam; stupid virgin islands
        elif code == 'DA': code = 'DK'  # danish speakrs are from denmark
        elif code == 'CS': code = 'CZ'  # czech speakers are from Czech Republic
        elif code == 'KO': code = 'KR'  # korean speakers are from South Korea
        elif code == 'JA': code = 'JP'  # japanese speakers are from Japan
        elif code == 'EL': code = 'GR'  # greek speakers are from Greece
        elif code == 'UK': code = 'UA'  # ukrainian speakers are from Ukraine
        elif code == 'SV': code = 'SE'  # swedish speakers are from Schweden
        elif code == 'TL': code = 'PH'  # tagalog speakers are from Philippines
        elif code == 'AF': code = 'TA'  # afrikaans speakers are from South Africa
        elif code == 'BE': code = 'BY'
        elif code == 'BN': code = 'BD'
        elif code == 'BS': code = 'BA'
        elif code == 'MY': code = 'MM'
        elif code == 'ET': code = 'EE'
        elif code == 'HE': code = 'IL'
        elif code == 'MS': code = 'MY'
        elif code == 'RM': code = 'CH'

        return self.flag(code)
