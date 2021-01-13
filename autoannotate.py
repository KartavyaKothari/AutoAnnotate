import json
import os
import re
import argparse

def getSpans(pattern,raw_txt,tag):
    spans = []
    indexes = [(i.start(),i.end()) for i in re.finditer(pattern,raw_txt,flags=re.IGNORECASE)]
    for t in indexes:
        ne = {}
        ne["start"] = t[0]
        ne["end"] = t[1]
        ne["tag"] = tag
        ne["extent"] = raw_txt[t[0]:t[1]]
        spans.append(ne)
    return spans

def getGenderAnnotations(raw_txt):
    annotations = []
    gender_words = ['he','her','she','his','him','man','woman','men','women','mr','mrs','brother','sister','wife','husband','uncle','male','female','son','daughter','father','mother', 'king', 'queen', 'himself', 'herself', 'motherhood', 'fatherhood', 'bitch', 'manhood', 'womanhood']
    for gender in gender_words:
        annotations.extend(getSpans(r'\b'+gender+r'\b',raw_txt,"GENDER"))
  
    return annotations

def getTimeSpans(raw_txt):
    spans = []
    pattern = r'([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]|([0-1]?[0-9]|2[0-3]):[0-5][0-9]\s[aApP][mM]|([0-1]?[0-9]|2[0-3]):[0-5][0-9]|[0-1]?[0-9][aApP][mM]'
    indexes = [(i.start(),i.end()) for i in re.finditer(pattern,raw_txt,flags=re.IGNORECASE)]
    for t in indexes:
        ne = {"properties":{"DATE-TIME-SUBTYPE":"TIME"}}
        ne["start"] = t[0]
        ne["end"] = t[1]
        ne["tag"] = "DATE-TIME"
        ne["extent"] = raw_txt[t[0]:t[1]]
        spans.append(ne)
    return spans

def getDateSpans(raw_txt):
    spans = []
    pattern = r'(((mon|tues?|wed(nes?)|thu(rs)?|fri|sat(ur)?|sun)(day)?)[,\s]*((jan|febr?)(uary)?|mar(ch)?|apr(il)?|may|june?|july?|aug(ust)?|sept?(ember)?|oct(ober)?|nov(ember)?|dec(ember)?)[,\s]?((0[1-9]|[12]\d|3[01])|([1-9]|[12]\d|3[01]))[,\s]*[12][0-9]{3})|(((mon|tues?|wed(nes?)|thu(rs)?|fri|sat(ur)?|sun)(day)?)[,\s]*((jan|febr?)(uary)?|mar(ch)?|apr(il)?|may|june?|july?|aug(ust)?|sept?(ember)?|oct(ober)?|nov(ember)?|dec(ember)?)[,\s]?((0[1-9]|[12]\d|3[01])|([1-9]|[12]\d|3[01])))|((jan|febr?)(uary)?|mar(ch)?|apr(il)?|may|june?|july?|aug(ust)?|sept?(ember)?|oct(ober)?|nov(ember)?|dec(ember)?)[,\s]*[12][0-9]{3}'
    indexes = [(i.start(),i.end()) for i in re.finditer(pattern,raw_txt,flags=re.IGNORECASE)]
    for t in indexes:
        ne = {"properties":{"DATE-TIME-SUBTYPE":"DATE"}}
        ne["start"] = t[0]
        ne["end"] = t[1]
        ne["tag"] = "DATE-TIME"
        ne["extent"] = raw_txt[t[0]:t[1]]
        spans.append(ne)
    return spans
    
def getCountrySpans(raw_txt):
    list_countries = [r'Afghanistan',r'Albania',r'Algeria',r'Andorra',r'Angola',r'Antigua\s&\sDeps',r'Argentina',r'Armenia',r'Australia',r'Austria',r'Azerbaijan',r'Bahamas',r'Bahrain',r'Bangladesh',r'Barbados',r'Belarus',r'Belgium',r'Belize',r'Benin',r'Bhutan',r'Bolivia',r'Bosnia\sHerzegovina',r'Botswana',r'Brazil',r'Brunei',r'Bulgaria',r'Burkina',r'Burundi',r'Cambodia',r'Cameroon',r'Canada',r'Cape\sVerde',r'Central\sAfrican\sRep',r'Chad',r'Chile',r'China',r'Colombia',r'Comoros',r'Congo',r'Congo',r'Costa\sRica',r'Croatia',r'Cuba',r'Cyprus',r'Czech\sRepublic',r'Denmark',r'Djibouti',r'Dominica',r'Dominican\sRepublic',r'East\sTimor',r'Ecuador',r'Egypt',r'El\sSalvador',r'Equatorial\sGuinea',r'Eritrea',r'Estonia',r'Ethiopia',r'Fiji',r'Finland',r'France',r'Gabon',r'Gambia',r'Georgia',r'Germany',r'Ghana',r'Greece',r'Grenada',r'Guatemala',r'Guinea',r'Guinea-Bissau',r'Guyana',r'Haiti',r'Honduras',r'Hungary',r'Iceland',r'India',r'Indonesia',r'Iran',r'Iraq',r'Ireland',r'Israel',r'Italy',r'Ivory\sCoast',r'Jamaica',r'Japan',r'Jordan',r'Kazakhstan',r'Kenya',r'Kiribati',r'Korea\sNorth',r'Korea\sSouth',r'Kosovo',r'Kuwait',r'Kyrgyzstan',r'Laos',r'Latvia',r'Lebanon',r'Lesotho',r'Liberia',r'Libya',r'Liechtenstein',r'Lithuania',r'Luxembourg',r'Macedonia',r'Madagascar',r'Malawi',r'Malaysia',r'Maldives',r'Mali',r'Malta',r'Marshall\sIslands',r'Mauritania',r'Mauritius',r'Mexico',r'Micronesia',r'Moldova',r'Monaco',r'Mongolia',r'Montenegro',r'Morocco',r'Mozambique',r'Myanmar',r'Namibia',r'Nauru',r'Nepal',r'Netherlands',r'New\sZealand',r'Nicaragua',r'Niger',r'Nigeria',r'Norway',r'Oman',r'Pakistan',r'Palau',r'Panama',r'Papua\sNew\sGuinea',r'Paraguay',r'Peru',r'Philippines',r'Poland',r'Portugal',r'Qatar',r'Romania',r'Russian\sFederation',r'Rwanda',r'St\sKitts\s&\sNevis',r'St\sLucia',r'Saint\sVincent\s&\sthe\sGrenadines',r'Samoa',r'San\sMarino',r'Sao\sTome\s&\sPrincipe',r'Saudi\sArabia',r'Senegal',r'Serbia',r'Seychelles',r'Sierra\sLeone',r'Singapore',r'Slovakia',r'Slovenia',r'Solomon\sIslands',r'Somalia',r'South\sAfrica',r'South\sSudan',r'Spain',r'Sri\sLanka',r'Sudan',r'Suriname',r'Swaziland',r'Sweden',r'Switzerland',r'Syria',r'Taiwan',r'Tajikistan',r'Tanzania',r'Thailand',r'Togo',r'Tonga',r'Trinidad\s&\sTobago',r'Tunisia',r'Turkey',r'Turkmenistan',r'Tuvalu',r'Uganda',r'Ukraine',r'United\sArab\sEmirates',r'United\sKingdom',r'United\sStates',r'\bu[\s.]*s.?\b',r'Uruguay',r'Uzbekistan',r'Vanuatu',r'Vatican\sCity',r'Venezuela',r'Vietnam',r'Yemen',r'Zambia',r'Zimbabwe']
    spans = []
    for pattern in list_countries:
        indexes = [(i.start(),i.end()) for i in re.finditer(pattern,raw_txt,flags=re.IGNORECASE)]
        for t in indexes:
            ne = {"properties":{"ADDRESS-SUBTYPE":["COUNTRY"]}}
            ne["start"] = t[0]
            ne["end"] = t[1]
            ne["tag"] = "ADDRESS"
            ne["extent"] = raw_txt[t[0]:t[1]]
            spans.append(ne)
    return spans

def getBasicAnnotations(raw_txt):
    allAnnotations = []
    allAnnotations.extend(getGenderAnnotations(raw_txt))
    allAnnotations.extend(getSpans(r'[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+',raw_txt,"EMAIL"))
    allAnnotations.extend(getTimeSpans(raw_txt))
    allAnnotations.extend(getDateSpans(raw_txt))
    allAnnotations.extend(getCountrySpans(raw_txt))
    
    return {"named_entity":sorted(allAnnotations,key=lambda x: x["start"])}

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Input file path")
    av = ap.parse_args()

    with open(av.input, 'r') as json_file:
        documents = [json.loads(i) for i in list(json_file)]

    with open(av.input, 'w') as json_file:
        for document in documents:
            document["annotations"] = getBasicAnnotations(document["raw_text"])
            json_file.write(json.dumps(document) + "\n")      
