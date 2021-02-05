import argparse
import json
import os
import re
from readchar import readchar


def getSpans(pattern, raw_txt, tag):
    spans = []
    indexes = [
        (i.start(), i.end()) for i in re.finditer(pattern, raw_txt, flags=re.IGNORECASE)
    ]
    for t in indexes:
        ne = {}
        ne["start"] = t[0]
        ne["end"] = t[1]
        ne["tag"] = tag
        ne["extent"] = raw_txt[t[0] : t[1]]
        spans.append(ne)
    return spans


def getGenderAnnotations(raw_txt):
    annotations = []
    gender_words = [
        "lord",
        "lady",
        "sir",
        "maam",
        "ma'am",
        "madam",
        "he",
        "her",
        "she",
        "his",
        "him",
        "man",
        "woman",
        "men",
        "women",
        "mr",
        "mrs",
        "brother",
        "sister",
        "wife",
        "husband",
        "uncle",
        "male",
        "female",
        "son",
        "daughter",
        "father",
        "mother",
        "king",
        "queen",
        "himself",
        "herself",
        "motherhood",
        "fatherhood",
        "bitch",
        "manhood",
        "womanhood",
    ]

    for gender in set(gender_words):
        annotations.extend(getSpans(r"\b" + gender + r"\b", raw_txt, "GENDER"))

    return annotations

def getUnameAnnotations(raw_txt):
    annotations = []
    words = [
        'kaxil',
        'ctr',
        'bhuvan',
        'vagrant'
    ]

    for gender in set(words):
        annotations.extend(getSpans(r"\b" + gender + r"\b", raw_txt, "USERNAME"))

    return annotations


def getTimeSpans(raw_txt):
    spans = []

    hour = r'([0-1]?[0-9]|2[0-3])'
    minutes = r'([0-5][0-9])'
    seconds = r'([0-5][0-9])'
    suffix = r'([ap].?m.?)'

    formats = []

    formats.append(r'\b'+hour+r':'+minutes+r':'+seconds+r':'+suffix+r'\b')
    formats.append(r'\b'+hour+r'\s'+minutes+r'\s'+seconds+r'\s'+suffix+r'\b')

    formats.append(r'\b'+hour+r':'+minutes+r':'+suffix+r'\b')
    formats.append(r'\b'+hour+r'\s'+minutes+r'\s'+suffix+r'\b')

    formats.append(r'\b'+hour+r':'+minutes+r':'+seconds+r'[\-\+]?,\d*'+r'\b')
    formats.append(r'\b'+hour+r':'+minutes+r':'+seconds+r'\b')
    formats.append(r'\b'+hour+r'[\.\-\s]'+suffix+r'\b')

    pattern = '|'.join(formats)

    indexes = [
        (i.start(), i.end()) for i in re.finditer(pattern, raw_txt, flags=re.IGNORECASE)
    ]
    for t in indexes:
        ne = {"properties": {"DATE-TIME-SUBTYPE": "TIME"}}
        ne["start"] = t[0]
        ne["end"] = t[1]
        ne["tag"] = "DATE-TIME"
        ne["extent"] = raw_txt[t[0] : t[1]]
        spans.append(ne)
    return spans


def getDateSpans(raw_txt):
    spans = []
    
    week_day = r"((mon|tues?|wed(nes?)|thu(rs)?|fri|sat(ur)?|sun)(day)?)"
    month = r"((jan|febr?)(uary)?|mar(ch)?|apr(il)?|may|june?|july?|aug(ust)?|sept?(ember)?|oct(ober)?|nov(ember)?|dec(ember)?)"
    month_digits = r"(0?[1-9]|1[012])"
    day = r"((0[1-9]|[12]\d|3[01])|([1-9]|[12]\d|3[01]))"
    year_small_digits = r"(\d\d)"
    year_large = r"([12][0-9]{3})"
    year_small = r"((19|20)\d{2})"

    formats = []

    formats.append(r'\b'+year_small+r'[\\|\-|/]'+month_digits+r'[\\|\-|/]'+day+r'\b')
    formats.append(r'\b'+year_small_digits+r'[\\|\-|/]'+month_digits+r'[\\|\-|/]'+day+r'\b')
    formats.append(r'\b'+day+r'[\\|\-|/]'+month_digits+r'[\\|\-|/]'+year_large+r'\b')
    formats.append(r'\b'+month_digits+r'[\\|\-|/]'+day+r'[\\|\-|/]'+year_large+r'\b')

    formats.append(r'\b'+year_small+r'[\\|\-|/]'+month+r'[\\|\-|/]'+day+r'\b')
    formats.append(r'\b'+year_small_digits+r'[\\|\-|/]'+month+r'[\\|\-|/]'+day+r'\b')
    formats.append(r'\b'+day+r'[\\|\-|/]'+month+r'[\\|\-|/]'+year_large+r'\b')
    formats.append(r'\b'+month+r'[\\|\-|/]'+day+r'[\\|\-|/]'+year_large+r'\b')

    formats.append(r'\b'+week_day+r'[\.,\s]*'+month+r'[\.,\s]*'+day+r'[\.,\s]*'+year_large+r'\b')
    formats.append(r'\b'+week_day+r'[\.,\s]*'+month+r'[\.,\s]*'+day+r'\b')
    formats.append(r'\b'+month+r'[\.,\s]*'+day+r'[\.,\s]*'+year_large+r'\b')
    formats.append(r'\b'+day+r'[\-\s]?'+month+r'\b')
    formats.append(r'\b'+month+r'[\.,\s]*'+day+r'\b')
    formats.append(r'\b'+month+r'[\.,\s]*'+year_large+r'\b')
    formats.append(r'\b'+year_large+r'\s*((to)|\-|(and))\s*'+year_large+r'\b')
    # formats.append(year_small)

    pattern = '|'.join(formats)

    indexes = [
        (i.start(), i.end()) for i in re.finditer(pattern, raw_txt, flags=re.IGNORECASE)
    ]
    for t in indexes:
        ne = {"properties": {"DATE-TIME-SUBTYPE": "DATE"}}
        ne["start"] = t[0]
        ne["end"] = t[1]
        ne["tag"] = "DATE-TIME"
        ne["extent"] = raw_txt[t[0] : t[1]]
        spans.append(ne)
    return spans


def getStateSpans(raw_txt):
    list_states = [r'\bAlabama',r'\bAlaska',r'\bAmerican Samoa',r'\bArizona',r'\bArkansas',r'\bCalifornia',r'\bColorado',r'\bConnecticut',r'\bDelaware',r'\bDistrict Of Columbia',r'\bFederated States Of Micronesia',r'\bFlorida',r'\bGeorgia',r'\bGuam',r'\bHawaii',r'\bIdaho',r'\bIllinois',r'\bIndiana',r'\bIowa',r'\bKansas',r'\bKentucky',r'\bLouisiana',r'\bMaine',r'\bMarshall Islands',r'\bMaryland',r'\bMassachusetts',r'\bMichigan',r'\bMinnesota',r'\bMississippi',r'\bMissouri',r'\bMontana',r'\bNebraska',r'\bNevada',r'\bNew Hampshire',r'\bNew Jersey',r'\bNew Mexico',r'\bNew York',r'\bNorth Carolina',r'\bNorth Dakota',r'\bNorthern Mariana Islands',r'\bOhio',r'\bOklahoma',r'\bOregon',r'\bPalau',r'\bPennsylvania',r'\bPuerto Rico',r'\bRhode Island',r'\bSouth Carolina',r'\bSouth Dakota',r'\bTennessee',r'\bTexas',r'\bUtah',r'\bVermont',r'\bVirgin Islands',r'\bVirginia',r'\bWashington',r'\bWest Virginia',r'\bWisconsin',r'\bWyoming']

    spans = []
    for pattern in list_states:
        indexes = [
            (i.start(), i.end())
            for i in re.finditer(pattern, raw_txt, flags=re.IGNORECASE)
        ]
        for t in indexes:
            entity = {"properties": {"ADDRESS-SUBTYPE": ["STATE"]}}
            entity["start"] = t[0]
            entity["end"] = t[1]
            entity["tag"] = "ADDRESS"
            entity["extent"] = raw_txt[t[0] : t[1]]
            spans.append(entity)
    return spans

def getCountrySpans(raw_txt):
    list_countries = [
        r"\bAfghanistan\b",
        r"\bAlbania\b",
        r"\bAlgeria\b",
        r"\bAmerica\b",
        r"\bAndorra\b",
        r"\bAngola\b",
        r"\bAntigua\s&\sDeps\b",
        r"\bArgentina\b",
        r"\bArmenia\b",
        r"\bAustralia\b",
        r"\bAustria\b",
        r"\bAzerbaijan\b",
        r"\bBahamas\b",
        r"\bBahrain\b",
        r"\bBangladesh\b",
        r"\bBarbados\b",
        r"\bBelarus\b",
        r"\bBelgium\b",
        r"\bBelize\b",
        r"\bBenin\b",
        r"\bBhutan\b",
        r"\bBolivia\b",
        r"\bBosnia\sHerzegovina\b",
        r"\bBotswana\b",
        r"\bBrazil\b",
        r"\bbritain\b",
        r"\bBrunei\b",
        r"\bBulgaria\b",
        r"\bBurkina\b",
        r"\bBurundi\b",
        r"\bCambodia\b",
        r"\bCameroon\b",
        r"\bCanada\b",
        r"\bCape\sVerde\b",
        r"\bCentral\sAfrican\sRep\b",
        r"\bChad\b",
        r"\bChile\b",
        r"\bChina\b",
        r"\bColombia\b",
        r"\bComoros\b",
        r"\bCongo\b",
        r"\bCongo\b",
        r"\bCosta\sRica\b",
        r"\bCroatia\b",
        r"\bCuba\b",
        r"\bCyprus\b",
        r"\bCzech\sRepublic\b",
        r"\bDenmark\b",
        r"\bDjibouti\b",
        r"\bDominica\b",
        r"\bDominican\sRepublic\b",
        r"\bEast\sTimor\b",
        r"\bEcuador\b",
        r"\bEgypt\b",
        r"\bEl\sSalvador\b",
        r"\bEquatorial\sGuinea\b",
        r"\bEritrea\b",
        r"\bEstonia\b",
        r"\bEthiopia\b",
        r"\bFiji\b",
        r"\bFinland\b",
        r"\bFrance\b",
        r"\bGabon\b",
        r"\bGambia\b",
        r"\bGeorgia\b",
        r"\bGermany\b",
        r"\bGhana\b",
        r"\bGreece\b",
        r"\bGrenada\b",
        r"\bGuatemala\b",
        r"\bGuinea\b",
        r"\bGuinea-Bissau\b",
        r"\bGuyana\b",
        r"\bHaiti\b",
        r"\bHonduras\b",
        r"\bHungary\b",
        r"\bIceland\b",
        r"\bIndia\b",
        r"\bIndonesia\b",
        r"\bIran\b",
        r"\bIraq\b",
        r"\bIreland\b",
        r"\bIsrael\b",
        r"\bItaly\b",
        r"\bIvory\sCoast\b",
        r"\bJamaica\b",
        r"\bJapan\b",
        r"\bJordan\b",
        r"\bKazakhstan\b",
        r"\bKenya\b",
        r"\bKiribati\b",
        r"\bKorea\sNorth\b",
        r"\bKorea\sSouth\b",
        r"\bKosovo\b",
        r"\bKuwait\b",
        r"\bKyrgyzstan\b",
        r"\bLaos\b",
        r"\bLatvia\b",
        r"\bLebanon\b",
        r"\bLesotho\b",
        r"\bLiberia\b",
        r"\bLibya\b",
        r"\bLiechtenstein\b",
        r"\bLithuania\b",
        r"\bLuxembourg\b",
        r"\bMacedonia\b",
        r"\bMadagascar\b",
        r"\bMalawi\b",
        r"\bMalaysia\b",
        r"\bMaldives\b",
        r"\bMali\b",
        r"\bMalta\b",
        r"\bMarshall\sIslands\b",
        r"\bMauritania\b",
        r"\bMauritius\b",
        r"\bMexico\b",
        r"\bMicronesia\b",
        r"\bMoldova\b",
        r"\bMonaco\b",
        r"\bMongolia\b",
        r"\bMontenegro\b",
        r"\bMorocco\b",
        r"\bMozambique\b",
        r"\bMyanmar\b",
        r"\bNamibia\b",
        r"\bNauru\b",
        r"\bNepal\b",
        r"\bNetherlands\b",
        r"\bNew\sZealand\b",
        r"\bNicaragua\b",
        r"\bNiger\b",
        r"\bNigeria\b",
        r"\bNorway\b",
        r"\bOman\b",
        r"\bPakistan\b",
        r"\bPalau\b",
        r"\bPanama\b",
        r"\bPapua\sNew\sGuinea\b",
        r"\bParaguay\b",
        r"\bPeru\b",
        r"\bPhilippines\b",
        r"\bPoland\b",
        r"\bPortugal\b",
        r"\bQatar\b",
        r"\bRomania\b",
        r"\bRussian\sFederation\b",
        r"\bRwanda\b",
        r"\bSt\sKitts\s&\sNevis\b",
        r"\bSt\sLucia\b",
        r"\bSaint\sVincent\s&\sthe\sGrenadines\b",
        r"\bSamoa\b",
        r"\bSan\sMarino\b",
        r"\bSao\sTome\s&\sPrincipe\b",
        r"\bSaudi\sArabia\b",
        r"\bSenegal\b",
        r"\bSerbia\b",
        r"\bSeychelles\b",
        r"\bSierra\sLeone\b",
        r"\bSingapore\b",
        r"\bSlovakia\b",
        r"\bSlovenia\b",
        r"\bSolomon\sIslands\b",
        r"\bSomalia\b",
        r"\bSouth\sAfrica\b",
        r"\bSouth\sSudan\b",
        r"\bSpain\b",
        r"\bSri\sLanka\b",
        r"\bSudan\b",
        r"\bSuriname\b",
        r"\bSwaziland\b",
        r"\bSweden\b",
        r"\bSwitzerland\b",
        r"\bSyria\b",
        r"\bTaiwan\b",
        r"\bTajikistan\b",
        r"\bTanzania\b",
        r"\bThailand\b",
        r"\bTogo\b",
        r"\bTonga\b",
        r"\bTrinidad\s&\sTobago\b",
        r"\bTunisia\b",
        r"\bTurkey\b",
        r"\bTurkmenistan\b",
        r"\bTuvalu\b",
        r"\bUganda\b",
        r"\bUkraine\b",
        r"\bUnited\sArab\sEmirates\b",
        r"\bU\.?A\.?E\.?\b",
        r"\bUnited\sKingdom\b",
        r"\bU\.?K\.?\b",
        r"\bUnited\sStates\b",
        r"\bu[\s.]*s\.?\b",
        r"\bUruguay\b",
        r"\bUzbekistan\b",
        r"\bVanuatu\b",
        r"\bVatican\sCity\b",
        r"\bVenezuela\b",
        r"\bVietnam\b",
        r"\bYemen\b",
        r"\bZambia\b",
        r"\bZimbabwe\b",
    ]

    spans = []
    for pattern in list_countries:
        indexes = [
            (i.start(), i.end())
            for i in re.finditer(pattern, raw_txt, flags=re.IGNORECASE)
        ]
        for t in indexes:
            entity = {"properties": {"ADDRESS-SUBTYPE": ["COUNTRY"]}}
            entity["start"] = t[0]
            entity["end"] = t[1]
            entity["tag"] = "ADDRESS"
            entity["extent"] = raw_txt[t[0] : t[1]]
            spans.append(entity)
    return spans


def getPhoneSpans(raw_txt):
    spans = []
    pattern = r"\d(\.|\s*|\-)\d(\.|\s*|\-)\d(\.|\s*|\-)\d(\.|\s*|\-)\d(\.|\s*|\-)\d(\.|\s*|\-)\d(\.|\s*|\-)\d(\.|\s*|\-)\d(\.|\s*|\-)\d(\.|\s*|\-)"
    indexes = [
        (i.start(), i.end()) for i in re.finditer(pattern, raw_txt, flags=re.IGNORECASE)
    ]
    for t in indexes:
        ne = {}
        ne["start"] = t[0]
        ne["end"] = t[1]
        ne["tag"] = "PHONE"
        ne["extent"] = raw_txt[t[0] : t[1]]
        spans.append(ne)
    return spans


def getNameSpans(raw_txt):
    spans = []
    pattern = r"\bshaykh al islam mohammed ibn 'abd al-wahhab al-tanaimi\b|\babdullah bin abdulaziz al-sa'ud\b|\blgustafson_karen cardiel, daisy\b|\bgustafson_karer cardiel, daisy\b|\bgustafson_karen cardiel, daisy\b|\bthomas-greenfield, linda(ms)\b|\baustin-ferguson, kathleen t\b|\bmohammed yussef el magariaf\b|\bvictor manuel rivera moreno\b|\bmullah abdul ghani baradar\b|\bmabrouk issa abu harroura\b|\bpatriarch mesrop mutafyan\b|\bchristopher m\. schnaubelt\b|\babdel hakim alamin belhaj\b|\bassuncao afonso dos anjos\b|\bluz elena guerrero guerra\b|\breverend deacon nektarios\b|\bcharles luoma-overstreet\b|\bjones-johnson, carolyn d\b|\bshaykh al islam mohammed\b|\bcardinal joachim meisner\b|\bthomas-greenfield, linda\b|\bmohammed yussef magariaf\b|\bsail al-islam al-qadhafi\b|\bk\.s\. sachidananda murthy\b|\bclaudia 'vette gonzalez\b|\bhrod17@clintonemail\.com\b|\bkhalifa belqasim hefter\b|\bclaudia lvette gonzalez\b|\bkhalifa belqasim haftar\b|\bdaniel patrick moynihan\b|\bclaudia !vette gonzalez\b|\bjean-berttrand aristide\b|\bmcmullen, christopher j\b|\babd al-wahhab al-tamimi\b|\bwilliam f\. buckley, jr\.\b|\bclaudia ivette gonzalez\b|\bpatriarch bartholomew i\b|\bkhalifa belgasim haftar\b|\blilia alejandra garcia\b|\bhillary rodham clinton\b|\bbarks-ruggles, erica 3\b|\barturo gonzalez rascon\b|\bmiguel angel jaramillo\b|\bchristopher schnaubelt\b|\bpatriarch, bartholomew\b|\bbernier-toth, michelle\b|\bmartin luther king jr\.\b|\btomlinson, christina b\b|\bjean-bertrand aristide\b|\bpatriarch bartholomeos\b|\bpatriarch vartholomew\b|\bgillis, christopher 3\b|\bmustafa kemal ataturk\b|\bsullivan, stephanie s\b|\balexis de tocqueville\b|\bslaughter, anne-marie\b|\boscar maynez grijalva\b|\belizabeth fitzsimmons\b|\babdulrahman ben yazza\b|\b\.kbdel rahman el-keib\b|\bmortimer b\. zuckerman\b|\banthony j\. limberakis\b|\bmohamed hosni mubarak\b|\bjean-robert lafortune\b|\babdulrahman ben yezza\b|\babd al-nasser shamata\b|\bsaif al-islam qaddafi\b|\bwillard cleon skousen\b|\bfitzgerald, william e\b|\bjane dammen mcauliffe\b|\bmalin, mary catherine\b|\banders fogh rasmussen\b|\bpatriarch bartholomew\b|\babdel rahman el-keib\b|\bpaulo espirito santo\b|\bklevorick, caitlin b\b|\bsolirnan abd al-qadr\b|\bsamuelson, heather f\b|\bstephanie l\. hallett\b|\bantonios trakatellis\b|\bjacqueline novogratz\b|\bkreab gavin anderson\b|\banne-marie slaughter\b|\bdwight d\. eisenhower\b|\bcrocker, bathsheba n\b|\bchas w\. freeman, jr\.\b|\brecep tayyip erdogan\b|\bdr\. allan e\. goodman\b|\bhallett, stephanie l\b|\bnelson w\. cunningham\b|\bmohammed al-magariaf\b|\brandolph, lawrence m\b|\bdavid m, satterfield\b|\bjames r\. stoner, jr\.\b|\bkennedy, j christian\b|\btomlinson, christina\b|\bjohn birks gillespie\b|\braghavan jagannathan\b|\bantonio munoz ortega\b|\byu\.ssef el magariaf\b|\byoussef al mangoush\b|\bdavid, jimmy carter\b|\bmuhammad al-gharabi\b|\bmuarnmar al qaddafi\b|\bmcdonough, denis r\.\b|\bgeoffroy, gregory l\b|\bhi i i ay ci i nton\b|\bchristina tomlinson\b|\bbrassanini, david g\b|\babdurrahirn el-keib\b|\bcecilia covarrubias\b|\bstevens mitt romnev\b|\bchristopher stevens\b|\bcie re m ccaski i i\b|\bfarooq khan leghari\b|\bmustafa abdul jalil\b|\bzulfikar ali bhutto\b|\bmceldowney, nancy e\b|\bmustafa abdel jalil\b|\bschlicher, ronald l\b|\bmahmoud ahmadinejad\b|\bgeraldine seruyange\b|\bchartrand, jennifer\b|\bpriscilla hernandez\b|\bmuhammad zia ul haq\b|\brodriguez, miguel e\b|\bslattery, phillip t\b|\bmolly sanchez crowe\b|\bmuhammad zia ul-haq\b|\bousetrill al juwaii\b|\bjean-louis warnholz\b|\bchristine dal bello\b|\bmcauliffe, marisa s\b|\bdibble, elizabeth l\b|\belizabeth thornhill\b|\bfeltrnan, jeffrey d\b|\byousuf raza gillani\b|\baf-fo-principals-dl\b|\bmuaimnar al qaddafi\b|\belizabeth ontiveros\b|\bsucharita narayanan\b|\bfeltman, jeffrey d\b|\bjacqueline charles\b|\bmaier, christina a\b|\babdulbari al-arusi\b|\brobinson, brooks a\b|\bshapiro, andrew \.3\b|\bjames a\. baker iii\b|\bbenjamin netanyahu\b|\blakhdhir, kamala s\b|\bfielder, rebecca a\b|\babdurrahim el-keib\b|\bsullivan, jacob \.1\b|\bwilliam f\. buckley\b|\bmuhammad ayub khan\b|\bkennedy, patrick f\b|\bmohammed yussef el\b|\babu yahya al- libi\b|\broebuck, william v\b|\bsheldon whitehouse\b|\bchristopher harich\b|\bjean-claude bajeux\b|\babdurrahim el keib\b|\bgulbadin hikmatyar\b|\bverveer, melanne s\b|\bschwerin, daniel b\b|\bslobodan milosevic\b|\bmuhammad al-zahawi\b|\bslobodan milosevie\b|\banderson, brooke d\b|\bharris, jennifer m\b|\bamir mohammad agha\b|\bahmed abu khattala\b|\breines, philippe i\b|\bverveer, melanne 5\b|\babdelhalcim belhaj\b|\bdebasish chowdhury\b|\bmohamed al-qadhafi\b|\bnelson rockefeller\b|\balexander zaitchik\b|\blebanese hizballah\b|\bmaxwell, raymond d\b|\bfinley peter dunne\b|\balexander hamilton\b|\bmacmanus, joseph e\b|\babdullah bin zayed\b|\bmuammar at qaddafi\b|\babdelfattah younes\b|\besther chavez cano\b|\babdel latif sharif\b|\bfranklin roosevelt\b|\bgilmore, kristin m\b|\brichardson, eric n\b|\bbrooks a\. robinson\b|\bmustafa abdel jail\b|\bstanley mcchrystal\b|\bmichael o'halloran\b|\btheodore roosevelt\b|\br\. donahue peebles\b|\babdulaziz al-sasud\b|\bmadeleine albright\b|\bnuland, victoria 3\b|\banthony limberakis\b|\babdelhakirn belhaj\b|\bsanderson, janet a\b|\bmuammar al qaddafi\b|\bmustafa abdul jail\b|\bhenry a\. kissinger\b|\bsimpson, mordica m\b|\bricardo seitenfus\b|\bobeidah al-jarrah\b|\bhoward metzenbaum\b|\bronald e\. neumann\b|\bcoleman, claire i\b|\bdwight eisenhower\b|\bjeannemarie smith\b|\bpatricio martinez\b|\bsidney blumenthal\b|\bdavid j\. rothkopf\b|\bjeremy greenstock\b|\bavigdor lieberman\b|\bchristopher meyer\b|\bcaitlin klevorick\b|\bgarrard, steven d\b|\babdelhakim belhaj\b|\bfrancisco sanchez\b|\bcurtis, meghann a\b|\bgerald mcloughlin\b|\bposivak, stephen;\b|\bmartin mcguinness\b|\bdonilon, thomas e\b|\bdavid klinghoffer\b|\bstephanie browner\b|\btimothy j\. roemer\b|\bshannon, thomas a\b|\bbenjamin franklin\b|\brichard johannsen\b|\bmorton abramowitz\b|\blvlills, cheryl d\b|\bbrigitte pressler\b|\bsullivan, jacob 3\b|\barturo valenzuela\b|\bpolaschlk, joan a\b|\bmark anthony neal\b|\bfrank shakespeare\b|\bjamjoom, kareem n\b|\bshapiro, daniel b\b|\bterrence a\. duffy\b|\bohtagaki, johna 0\b|\bmuammar al qaddaf\b|\bwilliam fulbright\b|\bbill strassberger\b|\bmichael pelletier\b|\bsullivan, jacob i\b|\bburns, william \.1\b|\brichard holbrooke\b|\bmustafa abushagur\b|\bmichael bloomberg\b|\bhormats, robert d\b|\braja bhattacharya\b|\bmargaret thatcher\b|\bmohammed al-sissi\b|\bdrucker, milton k\b|\bfeisal abdul rauf\b|\bcampbell, piper a\b|\bkoutsis, steven c\b|\bcoleman, claire l\b|\blaszczych, joanne\b|\bcatherine hallock\b|\bgeorge h\. w\. bush\b|\brussell, daniel a\b|\bcaspar weinberger\b|\bcaitlin m\. hayden\b|\bsullivan, jacob j\b|\brandolph mcgrorty\b|\bmary beth leonard\b|\bjosefina gonzalez\b|\bmacris, gregory p\b|\bdebbie almontaser\b|\brichard l\. kugler\b|\bmustafa abdel mil\b|\bsullivan, jacob 1\b|\bpacheco, martha a\b|\bsidereas, evyenla\b|\bmustafa abdul jai\b|\bcrowley, philip 1\b|\beizenstat, stuart\b|\bjeffrey donaldson\b|\badolph a\. weinman\b|\bfriedrich, mary k\b|\bousama al jouwali\b|\bhanley, monica r\b|\bmohamed magariaf\b|\bnuiand, victoria\b|\brajdeep sardesai\b|\bjudith a\. mchale\b|\bchristine ashton\b|\bsullivan, jacobi\b|\bbulgrin, julie k\b|\bjacob j sullivan\b|\brobert g\. kaiser\b|\bdavid n\. merrill\b|\belizabeth bagley\b|\bharry mcpherson,\b|\bhaji abdul jabar\b|\bansar al-shariah\b|\blawrence summers\b|\bmitchell, george\b|\bmchale, judith a\b|\banil padmanabhan\b|\bcatlin m\. hayden\b|\bharvey sernovitz\b|\bharold w\. geisel\b|\bchollet, derek h\b|\belmira ibraimova\b|\bpatriarch mesrop\b|\bpeter eisenhauer\b|\bradovan karad2ie\b|\bjean-paul sartre\b|\bousama al-juwali\b|\b'ramsay, jaime t\b|\bandrea puchalsky\b|\bgeorge h\.w\. bush\b|\btiseke kasambala\b|\bezra taft benson\b|\bjonathan pollard\b|\bvartan gregorian\b|\bburns, william 3\b|\bbenito mussolini\b|\bmolly montgomery\b|\bburns, william j\b|\badam parkhomenko\b|\babdelhamid rifai\b|\bmatthew g\. olsen\b|\brichard viguerie\b|\brandy neugebauer\b|\bmeena shridharan\b|\bjiloty, lauren c\b|\barindam sengupta\b|\bsumilas, michele\b|\bkirby, michael d\b|\btimothy geithner\b|\bwilliam s\. white\b|\basif ali zardari\b|\bschrepel, dawn m\b|\balija izetbegovi\b|\bjohnson, brock a\b|\bfeltman, jeffrey\b|\brussel, daniel r\b|\bsukhwinder singh\b|\bgordon, philip h\b|\bjacobs, janice l\b|\bverma, richard r\b|\bnicholas sarkozy\b|\bmariela paniagua\b|\bjames earl jones\b|\bangela paiaveras\b|\bbader, jeffrey a\b|\bjacobs, janice 1\b|\bsamira lzaguirre\b|\bdianne feinstein\b|\babbaszadeh, nima\b|\bregan, michael b\b|\bdeborah mccarthy\b|\bpatricia ehrnman\b|\bclaire mccaskill\b|\bmike vanderboegh\b|\bjames f\. dobbins\b|\bthomas jefferson\b|\bcharles grassley\b|\babbaszadeh, myna\b|\bhamad bin jassim\b|\balford, edward m\b|\balexey druzhinin\b|\ba/lax blumenthal\b|\bduguid, gordon k\b|\bpierre esperance\b|\bsherman, wendy r\b|\bgeorge voinovich\b|\bjonathan m\. katz\b|\banne-marie brady\b|\baxelrod, david m\b|\bbarbara retzlaff\b|\bnick von mertens\b|\bsullivan, jacobj\b|\bchristopher dodd\b|\bmohammed rvlorsi\b|\bsimon, jessica l\b|\bmcdonald, kara c\b|\bwalsh, matthew p\b|\bjohnson, james r\b|\bousama at juwali\b|\bposivak, stephen\b|\bdorothy ngalombi\b|\bpervez musharraf\b|\bfrancois leotard\b|\bshailja kejriwal\b|\bsamira izaguirre\b|\bolson, richard g\b|\bsusan col i i ns\b|\bschlesinger, jr\.\b|\bdwayne l\. cline\b|\baustin-ferguson\b|\bharold w geissl\b|\bdimitris reppas\b|\bosama al-juwali\b|\bmark carruthers\b|\bvalmoro, lona 1\b|\bansar al sharia\b|\bomar al i3ashir\b|\byousef mangoush\b|\bj\. edgar hoover\b|\beliot shapleigh\b|\bdebbie stabenow\b|\bandrew sullivan\b|\bstevens, john c\b|\blouis b\. susman\b|\bmesrop mutafyan\b|\bdenis mcdonough\b|\babdullah shamia\b|\byigal schleifer\b|\baustan goolsbee\b|\bmaggie williams\b|\bdonald rumsfeld\b|\bjason straziuso\b|\bedwin a\. walker\b|\bsad\.dam hussein\b|\blynne gadkowski\b|\beustace mullins\b|\bmario lee lopez\b|\bemanuel cleaver\b|\bmitch mcconnell\b|\bblanche lincoln\b|\bmarshall petain\b|\babdulkadir aksu\b|\bchristina romer\b|\bgustafson_karen\b|\bprashanth rajan\b|\bmichael s\. lund\b|\btom pyszczynski\b|\bsufyan ben qumu\b|\bwalker, peggy j\b|\bhillarv clinton\b|\bshubhangi desai\b|\bcilia kerfuffie\b|\beugene mccarthy\b|\bsamuel freedman\b|\bornar al bashir\b|\bjames baker iii\b|\b°same al juwali\b|\bfred a\. shannon\b|\bhoney alexander\b|\bbecky bernhardt\b|\bbasher al assad\b|\bbond, michele t\b|\bmandelson watch\b|\byitzhak shapira\b|\brobert menendez\b|\bbondy, steven c\b|\bramsay, jaime t\b|\bmichael m ullen\b|\bkitty dimartino\b|\bjohn c\. calhoun\b|\bcline, dwayne l\b|\bstan mcchrystai\b|\bsmith, daniel b\b|\bmargaret scobey\b|\bmahmoud _fibril\b|\bhans binnendijk\b|\bfogarty, daniel\b|\bosama al juwali\b|\bfawzi abu kitef\b|\bchas w\. freeman\b|\bosama bin laden\b|\bpatricia lamego\b|\bnorman ornstein\b|\bprashant panday\b|\babraham lincoln\b|\banthony campolo\b|\bnides, thomas r\b|\bkarl eikenberry\b|\bjames s\. rogers\b|\bmills, cheryl d\b|\bcarson, johnnie\b|\bgeorge mcgovern\b|\bhubert humphrey\b|\bteddy roosevelt\b|\bdominic asquith\b|\bjoseph mccarthy\b|\bhanky, monica r\b|\bmuammar qaddafi\b|\bhoward phillips\b|\bdavid shambaugh\b|\bmichael janeway\b|\bbrooks robinson\b|\bstan mcchrystal\b|\baubrey chernick\b|\blauran lovelace\b|\bsusan povenmire\b|\bdaniel benjamin\b|\bsamuel brinkley\b|\broza otunbayeva\b|\brichard cordray\b|\bkatrina hourani\b|\bmishna gregoire\b|\bjohn f\. kennedy\b|\bbarry goldwater\b|\bmatthew hiltzik\b|\banushka asthana\b|\brhoda margesson\b|\bmuammar gaddafi\b|\bhenry kissinger\b|\bsutphin, paul r\b|\bsullivan, jacob\b|\bcoionia morelos\b|\bmo9rt zuckerman\b|\bcharles schumer\b|\bharry mcpherson\b|\bmohamed bujenah\b|\bdavid schaecter\b|\bnicolas sarkozy\b|\blamar alexander\b|\bvalmoro, lona j\b|\bwilliam zartman\b|\bsharon d\. james\b|\bjoseph stiglitz\b|\bnancy kachingwe\b|\bcharge robinson\b|\bbelqasim haftar\b|\brusso, robert v\b|\bmuammar qadhafi\b|\bhillary clinton\b|\bbashir al-kubty\b|\bhillary, cheryl\b|\bezekiel emanuel\b|\bpolt, michael c\b|\bwalid al-sakran\b|\bcoleman, claire\b|\blvette gonzalez\b|\bgeorge mitchell\b|\bevangeline arce\b|\bsufian bin qamu\b|\bkemal kerincsiz\b|\bandrea mitchell\b|\bmusharraf years\b|\bmiller, james n\b|\bmax blumenthal,\b|\bmills, cheryl 0\b|\bculver, chris d\b|\beverett dirksen\b|\bdamour, marie c\b|\bmontek aluwalia\b|\bdizzy gillespie\b|\bsoledad aguilar\b|\badam j\. grotsky\b|\bze'ev sternhell\b|\bsherlock holmes\b|\bpratap g\. pawar\b|\bsa-igha rat mi\b|\bmahmoud jibril\b|\bshyam asolekar\b|\bsanghar rahimi\b|\btorn perriello\b|\bphilip bobbitt\b|\bmort zuckerman\b|\blinda mcfadyen\b|\bjeff greenberg\b|\bmohnimed morsi\b|\bmichael deaver\b|\bs\. akbar zaidi\b|\bdaniel, joshua\b|\bnewt gin<trich\b|\bclaudia lvette\b|\bmichael bennet\b|\bkelvin kiyingi\b|\bamax al sharia\b|\brichard kugler\b|\bdick holbrooke\b|\bdeborah haynes\b|\bcarlos pascual\b|\bgregory macris\b|\bpark, pamela p\b|\bbarholomeos ii\b|\bgeorge w\. bush\b|\bdavies, glyn t\b|\bdennis gombert\b|\brobert maguire\b|\bmartha mendoza\b|\bellen tauscher\b|\bwalter mondale\b|\bwoodrow wilson\b|\bdavid domenici\b|\bryan christmas\b|\bcharles peters\b|\bjettison clegg\b|\bport-au-prince\b|\bpatricia lynch\b|\barvizu, alex a\b|\bbenaim, daniel\b|\bmary catherine\b|\bedward chaplin\b|\bosama biniadin\b|\bchuck grassley\b|\blyndon johnson\b|\bfavvzi abd all\b|\bgloria steinem\b|\bjoann lockhart\b|\bcardiel, daisy\b|\bnorman borlaug\b|\bbetsy whitaker\b|\bjohn m\. bryson\b|\balyson grunder\b|\bmax blumenthal\b|\bdavid petraeus\b|\bhenry mcdonald\b|\bloh, anthony x\b|\banthony weiner\b|\bwells, alice g\b|\bsusan domowitz\b|\bismail sallabi\b|\bsaddam hussein\b|\bkenneth merten\b|\bomar al bashir\b|\brichard condon\b|\bstuart smalley\b|\brobert spencer\b|\bdavid ignatius\b|\bsaud al-faisal\b|\bgeorge osborne\b|\bjanysh bakiyev\b|\bjames s rogers\b|\bshenoa simpson\b|\blord goldsmith\b|\bmichael steele\b|\bnicole peacock\b|\bmary 'landrieu\b|\bpeter robinson\b|\bpeter claussen\b|\bvladimir putin\b|\bdavid miliband\b|\bedwina sagitto\b|\bmohammed badie\b|\bmarianne scott\b|\bjohna ohtagaki\b|\bsadaam hussein\b|\bj\. bracken lee\b|\bandrew gravers\b|\bhickey, mary e\b|\bshaun woodward\b|\bpeter ricketts\b|\bdanielle brian\b|\barola, heidi r\b|\bsusilo bambang\b|\bbernie sanders\b|\bscarlis, basil\b|\bjames eastland\b|\bstrobe talbott\b|\borville schell\b|\brobert a\. caro\b|\bcharles mugabo\b|\bsanjoy narayan\b|\bsadiq al-mahdi\b|\bjohn e\. herbst\b|\bjack abriunoff\b|\bsanjay sachdev\b|\bosama al kwali\b|\bmission steven\b|\bwood, robert a\b|\bmohammed morsi\b|\brussell brooks\b|\bthais ruboneka\b|\bdavid horowitz\b|\bosama binladin\b|\bpreethi patkar\b|\bthomas shannon\b|\bmichael mullen\b|\bdonny -kuehner\b|\balbert r\. hunt\b|\bholtz, greta c\b|\bkelly, craig a\b|\bandrea santoro\b|\bdonald ritchie\b|\bbeth gili\.nsky\b|\bcharles rangel\b|\balan greenspan\b|\brobert gelbard\b|\bilario pantano\b|\bmahmoud fibril\b|\bmarisela ortiz\b|\botto preminger\b|\bahmad bukatela\b|\balcee hastings\b|\bbrooke shearer\b|\brebecca struwe\b|\bs cheryl mills\b|\bkarla rubinger\b|\bhassan ziglarn\b|\bmaura connelly\b|\bgaylord nelson\b|\bdavid rothkopf\b|\bgeorge schultz\b|\bsid blumenthal\b|\bcharlie palmer\b|\bharris, rian h\b|\bpraveen patkar\b|\bpiper campbell\b|\bwilliam ehrman\b|\bnina fedoroff,\b|\blindsey graham\b|\bdaniel webster\b|\bherbert hoover\b|\bgoodman, allan\b|\bross, dennis b\b|\bcharlie crist,\b|\brichard shelby\b|\bnuni berrusien\b|\banthony pigott\b|\bbenazir bhutto\b|\bchris mcshane\b|\blydia ellison\b|\ballan goodman\b|\bwilliam hague\b|\bgeorge romney\b|\bhassan ziglam\b|\bcharles moose\b|\bsalah bishari\b|\bdavid skorton\b|\bmevlut kurban\b|\bjoseph duffey\b|\bsolomon atayi\b|\bmartha johnso\b|\byasser arafat\b|\bclean skousen\b|\bjake sullivan\b|\brogers cidosa\b|\bkoch brothers\b|\babedin, hurna\b|\babd al-wahhab\b|\bbarks-ruggles\b|\bmike huckabee\b|\bjones, beth e\b|\bchuck schumer\b|\bjones, paul w\b|\brahi rn faiez\b|\bmohamed hosni\b|\banne seshadri\b|\bmohamad sowan\b|\bgeorge tiller\b|\bjon tollefson\b|\bthomas menino\b|\bbartholomew i\b|\bmarco aurelio\b|\bcharlie flynn\b|\btarun katiyal\b|\bmarc grossman\b|\bkhushali shah\b|\btoner, mark c\b|\bmargery eagan\b|\brush limbaugh\b|\bferuzan mehta\b|\blael brainard\b|\bedmund muskie\b|\barshiya sethi\b|\bnicholas gage\b|\bderek chollet\b|\bdeng xiaoping\b|\bgilmar mendes\b|\btilmann geske\b|\bmartin kramer\b|\balberto wilde\b|\bjames madison\b|\brooney, megan\b|\bgeorge shultz\b|\bfawzi abd all\b|\bmahmoud abbas\b|\bdonny kuehner\b|\bterri rookard\b|\bjudith mchale\b|\brice, susan e\b|\bmridual issar\b|\bali al-salabi\b|\bjake\.sulliyan\b|\bcleon skousen\b|\bwalid shoebat\b|\bpaul folmsbee\b|\btillman geske\b|\bwilliam cohen\b|\b'cheryl\.mills\b|\barlen specter\b|\boliver letwin\b|\bkarl semancik\b|\brobert hunter\b|\bmustafa abdel\b|\bolympia snowe\b|\bpamela geller\b|\bmills, cheryl\b|\blee bollinger\b|\bmalcolm smith\b|\bs akbar zaidi\b|\bgeorge kennan\b|\bdavid axelrod\b|\bcretz, gene a\b|\ball al-salabi\b|\bamir mohammad\b|\bsilvan shalom\b|\bmiriam sapiro\b|\bclifford levy\b|\bhenry jackson\b|\bjudy trabulsi\b|\botmar oehring\b|\bwolff, alex d\b|\bdavid cameron\b|\bwailes, jacob\b|\bburns strider\b|\bjustin cooper\b|\bsalim \.nabous\b|\bmohamad morsi\b|\bhale, david m\b|\bturk, david m\b|\bmatthew green\b|\bgeorge ketman\b|\bbill o'reilly\b|\bkendrick meek\b|\barnab goswami\b|\brichard lugar\b|\bmustafa abdul\b|\bbigalke 'karl\b|\bnewt gingrich\b|\btina flournoy\b|\bkristallnacht\b|\braj chengappa\b|\bstilin, jacob\b|\bwolfgang hade\b|\bdavid goldman\b|\brobyn remeika\b|\bdavid gregory\b|\bsimon johnson\b|\bsherrod brown\b|\bjames clapper\b|\bchris stevens\b|\bronald reagan\b|\bjames o'keefe\b|\bbecky fielder\b|\bmohammed swan\b|\bgeorge packer\b|\bpeter martino\b|\bbruce wharton\b|\bglen doherty,\b|\brobert wexler\b|\bshekhar gupta\b|\btaher sherkaz\b|\brachel maddow\b|\bsusan collins\b|\bdavid manning\b|\bterri schiavo\b|\blauren joloty\b|\bmohmmed morsi\b|\bjake\.sullivan\b|\brobb browning\b|\brichard haass\b|\bbraulio rosas\b|\blauren jiloty\b|\bsam brownback\b|\bsheikh hasina\b|\bcarlotta gall\b|\bmary spanger,\b|\bharry hopkins\b|\bmull, stephen\b|\bjoe lieberman\b|\bashley esarey\b|\brichard nixon\b|\bjavier solana\b|\btushar poddar\b|\bamy klobuchar\b|\brichard levin\b|\bshaw d\. janes\b|\bandrew mayock\b|\bsmita prakash\b|\bnina fedoroff\b|\bhissene habre\b|\bjohn b\. judis\b|\bjames dobbins\b|\bforman, james\b|\bkubiske, lisa\b|\bdenis mukwege\b|\bkarl semacik\b|\blona valmoro\b|\bjacob javits\b|\babedin, huma\b|\bneera tanden\b|\bcherie blair\b|\bsharon hardy\b|\bjohn boehner\b|\bahmadinej ad\b|\bkaren coates\b|\bmcleod, mary\b|\brudman, mara\b|\budith mchale\b|\bblair, oni k\b|\btong, kurt w\b|\bbetsy bassan\b|\bsharon lowen\b|\btrey grayson\b|\bpaul collier\b|\bdaniel pipes\b|\bjohn paul ii\b|\bmary spanger\b|\bsachar, alon\b|\bmohamoud (t)\b|\bheidi annabi\b|\bsami abraham\b|\babu khattala\b|\bbecker, john\b|\bdaniel akaka\b|\bjeff merkley\b|\bjimmy carter\b|\btoiv, nora f\b|\bpenn rhodeen\b|\babdullah bin\b|\bjames salley\b|\bkevin tebbit\b|\bugur ya%ksel\b|\bhakan tastan\b|\blisa bardack\b|\brahm emanuel\b|\bminint fawzi\b|\btony campolo\b|\bdan restrepo\b|\bcarsten holz\b|\bdavid wilson\b|\bhannah giles\b|\bfrida lambay\b|\bnachum segal\b|\bsmith bagley\b|\bjames pardew\b|\bcheryl mills\b|\bbarack obama\b|\bnecati aydin\b|\bblum, orna t\b|\blilia garcia\b|\bfeisai abdul\b|\bcorley kenna\b|\bjudas priest\b|\bfrank munger\b|\bed gillespie\b|\blouis susman\b|\btesone, mark\b|\bcooper udall\b|\bdaniel lynch\b|\brhonda shore\b|\bnitin vaidya\b|\bnancy pelosi\b|\brockefellers\b|\babedln, hume\b|\bgordon brown\b|\braila odinga\b|\blisa kubiske\b|\bdaniel bliss\b|\bjohn jenkins\b|\bjoe macmanus\b|\bhamid karzai\b|\bkevin melton\b|\babu harroura\b|\bjeff feltman\b|\blinda katehi\b|\bkatie glueck\b|\bglen doherty\b|\bpaul volcker\b|\bmark lippert\b|\bsean wilentz\b|\bjohn schmitz\b|\bpeggy walker\b|\bisaac alaton\b|\bdavid harris\b|\bscott roeder\b|\badam grotsky\b|\bsamuel adams\b|\buday shankar\b|\bgotoh, kay e\b|\bsarah binder\b|\brobert blake\b|\brobert crane\b|\btim geithner\b|\btalwar, pune\b|\bgracien jean\b|\bursula burns\b|\bs\.m\. krishna\b|\bdusty rhodes\b|\bbill clinton\b|\bsean haimity\b|\bjohn chilcot\b|\bsean hannity\b|\bsergio brito\b|\bbrandon webb\b|\bvijay chopra\b|\bcheryl\.mills\b|\bbashar assad\b|\bjames warren\b|\babd al jalil\b|\bsanjaya baru\b|\broger lyners\b|\bduffy, terry\b|\bmel martinez\b|\btommy franks\b|\bbarney frank\b|\bfarej darssi\b|\brobert gates\b|\brichard mack\b|\bbitter, rena\b|\bcheryl\.millf\b|\bali tarhouni\b|\bjim allister\b|\belizabeth ii\b|\btsou, leslie\b|\blesley clark\b|\bandrew cedar\b|\bchas freeman\b|\bleon panetta\b|\bperla, laura\b|\bminyon moore\b|\bpierre-louis\b|\bcolin powell\b|\brichard mays\b|\bdavid vitter\b|\bbekir ozturk\b|\brobert welch\b|\bhoward baker\b|\bdesk rebecca\b|\bzheng bijian\b|\bbenedict xvi\b|\bpeter orszag\b|\brupert smith\b|\ball tarhouni\b|\bdoug hoffman\b|\bp\.j\. crowley\b|\bsam brinkley\b|\bwestmoreland\b|\bdonna winton\b|\bjoseph biden\b|\bhaji jhapour\b|\bkelly, ian c\b|\bdonna bryson\b|\blebron james\b|\bpaul hinshaw\b|\bjim hoagiand\b|\babedin, hume\b|\bandrew frank\b|\bandrew cuomo\b|\bsean goldman\b|\bjim hoagland\b|\bpaul vallely\b|\bhickey, mary\b|\bmichael lund\b|\blynn allison\b|\bfrank church\b|\bmarie damour\b|\bsally osberg\b|\bbab al-aziza\b|\babd al-jalil\b|\bhuma abed in\b|\bjulien behal\b|\brajeev syal\b|\belena kagan\b|\bsteny hoyer\b|\bcraig kelly\b|\bgrey wolves\b|\brene preval\b|\btony newton\b|\bbartholomew\b|\bjohn haynes\b|\bdick cheney\b|\bdaniel gros\b|\btocqueville\b|\bsugash ghai\b|\bmike castle\b|\bjana winter\b|\bkim, sung y\b|\bhuma abedin\b|\bjoe mellott\b|\bmary pipher\b|\blaura lucas\b|\bsiria lopez\b|\btom donilon\b|\bjack rakove\b|\bpeter boone\b|\bgeorge bush\b|\bdaniel levy\b|\bregina addo\b|\balbert hunt\b|\bmitt romney\b|\braieev syai\b|\bkim, yuri j\b|\bross wilson\b|\bsyed, zia s\b|\bfouad ajami\b|\bban ki-moon\b|\bsarah palin\b|\bdrew westen\b|\bnorman dodd\b|\brich greene\b|\banil kapoor\b|\bmark takano\b|\bhma abedine\b|\bjeff gannon\b|\bsam pitroda\b|\bwahliabis-m\b|\bjames jones\b|\bmary scholl\b|\bmark zimmer\b|\bmason, whit\b|\baryeh eldad\b|\bira shapiro\b|\bnawaz shard\b|\bturgut ozal\b|\bdebra bowen\b|\brobert byrd\b|\bcheryl\.mill\b|\bamb stevens\b|\bunni mennon\b|\byan xuetong\b|\bwiley drake\b|\bshubada rao\b|\babdulrahman\b|\bdick durbin\b|\bkent conrad\b|\btorrey goad\b|\bfloyd flake\b|\bg\.p\. putnam\b|\bdeal hudson\b|\bwayne morse\b|\bdean debnam\b|\bel magariaf\b|\bhugo chavez\b|\bted kennedy\b|\bsam antonio\b|\bvicente fox\b|\bgerry adams\b|\bchris smith\b|\bmark warner\b|\bemma ezeazu\b|\bpat kennedy\b|\bahmadinejad\b|\brothschilds\b|\bjustin blum\b|\bjames baker\b|\bklinghoffer\b|\bturan topal\b|\bgerald ford\b|\bkapil sibal\b|\babu-shakour\b|\bbrian cowen\b|\bjohn breaux\b|\bban ki moon\b|\borhan kemal\b|\bed miliband\b|\blinda dewan\b|\bmike dewine\b|\bugur yuksel\b|\bruth marcus\b|\bamit tandon\b|\bjesse helms\b|\bchris huhne\b|\bjeff jacoby\b|\banne wexler\b|\bellen barry\b|\bvince cable\b|\btom daschle\b|\bg\. krishnan\b|\banwar iqbal\b|\bjohn mccain\b|\bsara devlin\b|\bvanderboegh\b|\bjim kennedy\b|\blohman, lee\b|\boman shahan\b|\bjohn sexton\b|\bkelli adams\b|\bal-mangoush\b|\bvalmoro, b6\b|\bim hoagland\b|\bjim bunning\b|\bsarah patin\b|\bernie banks\b|\btijen aybar\b|\blouis mazel\b|\bhoward stem\b|\banwar sadat\b|\bidriss deby\b|\bjuan carlos\b|\bjohn herbst\b|\brockefeller\b|\behud barak\b|\broy spence\b|\bglenn beck\b|\btim roemer\b|\bjan piercy\b|\balger hiss\b|\blord boyce\b|\bhaim saban\b|\bnahma kazi\b|\bravij shah\b|\beikenberry\b|\bharold koh\b|\bal franken\b|\bjohnsonian\b|\bcony blair\b|\bali zeidan\b|\bjacqueline\b|\banne marie\b|\bdavid frum\b|\bsteve wynn\b|\bfrank rich\b|\bben cardin\b|\bbob inglis\b|\bben nelson\b|\bousama al-\b|\borly taitz\b|\banne-marie\b|\bdavid laws\b|\btoni getze\b|\bbeknazarov\b|\bsean smith\b|\bmehna ghai\b|\bkevin rudd\b|\bbeth jones\b|\bkarimullah\b|\bvandeboegh\b|\bcunningham\b|\balmontaser\b|\btony blair\b|\bamb steven\b|\beric siila\b|\bbill frist\b|\balok mehta\b|\bblumenthal\b|\bken merten\b|\bdick armey\b|\bbill burns\b|\bweb, ake g\b|\bmark hyman\b|\bravi gupta\b|\bjack _mite\b|\bmel gibson\b|\balok gupta\b|\bmatt kibbe\b|\blee ferran\b|\bnazarbayev\b|\botunbayeva\b|\btom jensen\b|\btrey gowdy\b|\bali bhutto\b|\baleitiwali\b|\byoussef al\b|\bsta i bott\b|\bann selzer\b|\bsarah palm\b|\bdick lugar\b|\bkay warren\b|\bmeg keeton\b|\bgreg craig\b|\bsuly ponce\b|\bbirch bayh\b|\bsam dubbin\b|\bgeeta pasi\b|\bcarol kahn\b|\bjohn major\b|\babdulkadir\b|\bmark laity\b|\bgreg bloom\b|\bemin sirin\b|\btom coburn\b|\brichardson\b|\bjohn thune\b|\bsusan rice\b|\bralph reed\b|\balan feuer\b|\brahul john\b|\b01-28-2010\b|\bjohn birch\b|\bkathleen t\b|\buri avnery\b|\bcarl levin\b|\bjim demint\b|\blimberakis\b|\bnita lowey\b|\brich verma\b|\btomlinsonc\b|\bryan sorba\b|\btarun basu\b|\bezra pound\b|\bjeff skoll\b|\bjon tester\b|\bscozzafava\b|\babdel aziz\b|\bneugebauer\b|\bmuammar al\b|\bglenn back\b|\bjohn kerry\b|\btom harkin\b|\bliz cheney\b|\bharry reid\b|\blynn roche\b|\bamit khare\b|\btviagariaf\b|\bjudd gregg\b|\bwed sep 09\b|\btrent lott\b|\bmcchrystal\b|\balex dupuy\b|\brothschild\b|\bjohn lewis\b|\bjohn dunne\b|\bchris dodd\b|\bpj crowley\b|\bhrant dink\b|\bnick clegg\b|\bchancellor\b|\bmax baucus\b|\bjohn simon\b|\bal senussi\b|\ballen drur\b|\bjohn birks\b|\blarry king\b|\byussef al-\b|\bben yezza\b|\bian kelly\b|\bpatricofs\b|\byudhoyono\b|\bdipu moni\b|\bkachingwe\b|\babushagar\b|\bnancy roc\b|\bglad bill\b|\bperriello\b|\bmohamoucl\b|\babu kitef\b|\bdayutogiu\b|\bayub khan\b|\bgabrielle\b|\babushagur\b|\bsteinberg\b|\bcarlton a\b|\bsteven j\.\b|\bnursultan\b|\bmandarins\b|\bmesadieux\b|\bmacmillan\b|\babu salim\b|\blou dobbs\b|\bmcpherson\b|\bdavutogiu\b|\bma gariaf\b|\bkerincsiz\b|\bchristine\b|\bevan bayh\b|\batembayev\b|\bdan smith\b|\bpickering\b|\bkarl rove\b|\bwhitehall\b|\bmandeison\b|\bpuchalsky\b|\bmcdonough\b|\bjim jones\b|\bhezbollah\b|\bbelizaire\b|\bpaulo e-s\b|\bgeorge w\.\b|\bfeinstein\b|\bcarl chan\b|\bmccrystal\b|\bjefferson\b|\bbin laden\b|\bslaughter\b|\bel — keib\b|\btekebayev\b|\beizenstat\b|\bmagariars\b|\bmandelson\b|\bdavutoglu\b|\balexander\b|\bjoe biden\b|\bbob gates\b|\bben yazza\b|\bdoug band\b|\bmccaskill\b|\bgoldwater\b|\bfawzi abd\b|\bnora toiv\b|\bgonzalez,\b|\bjohn mann\b|\bvan jones\b|\btoby helm\b|\bali zidan\b|\bkarl marx\b|\bron wyden\b|\bnetanyahu\b|\blzaguirre\b|\bkissinger\b|\bpelletier\b|\bbollinger\b|\bspeckhard\b|\bpreminger\b|\bo'donnell\b|\btom udall\b|\bsinn fein\b|\bpoplawski\b|\ball zidan\b|\bpolaschik\b|\brand paul\b|\brobertson\b|\bal-wahhab\b|\bat juwali\b|\bmalcolm x\b|\bedward m\.\b|\bal-juwali\b|\bben smith\b|\bizaguirre\b|\boren sega\b|\blieberman\b|\bnavin sun\b|\bjoe duffy\b|\bbob dylan\b|\bholbrooke\b|\bjim odato\b|\barthur m\.\b|\bgary hart\b|\bsue brown\b|\bjoe feuer\b|\bmccaughey\b|\bhooverite\b|\bgorbachev\b|\bmusharraf\b|\bal juwali\b|\b\.vlassa\.d\b|\bmcconnell\b|\bgoldsmith\b|\bj\. edgar\b|\bmonrovia\b|\bthearill\b|\balbright\b|\bcamerfin\b|\bjosefina\b|\bmichelle\b|\bkhamenei\b|\bthurmond\b|\btauscher\b|\bmcgovern\b|\bcladeafi\b|\bhuckabee\b|\blyn lusi\b|\bpuri das\b|\bcampbell\b|\bmedvedev\b|\bchernoff\b|\bmccarthy\b|\bjack lew\b|\bmargaret\b|\bchernick\b|\bsamantha\b|\bfloyd m\.\b|\bdetvlint\b|\bqacihafi\b|\bcheryl d\b|\bchi minh\b|\bann beck\b|\bsl green\b|\bo'reilly\b|\bgrijalva\b|\bhumphrey\b|\bval moro\b|\bal-acusi\b|\bpetraeus\b|\bchaitkin\b|\bdaniel b\b|\bmangoush\b|\blimbaugh\b|\babdullab\b|\bqacklafl\b|\bibn 'abd\b|\babdullah\b|\bsbwhoeof\b|\bpaterson\b|\bmagariaf\b|\bcronkite\b|\bzulfikar\b|\bchaudhry\b|\bfluornoy\b|\bbrinkley\b|\bbenyezza\b|\bgregoire\b|\bal-arusi\b|\bduvalier\b|\bornstein\b|\bjim crow\b|\bfeingold\b|\bai-arusi\b|\btarasios\b|\blarouche\b|\bricketts\b|\bmalunoud\b|\bholbrook\b|\bphilippe\b|\bhamelech\b|\bsidereas\b|\bmiliband\b|\buc davis\b|\bal-anisi\b|\bgiffbrds\b|\brobinson\b|\bjohn lee\b|\btritevon\b|\ballister\b|\bgregory:\b|\bhastings\b|\bphilip 1\b|\bmagariar\b|\bcherubin\b|\bles gelb\b|\btarhouni\b|\bsullivan\b|\ba\. knopf\b|\bthatcher\b|\bbelgasim\b|\bjoseph e\b|\bcapricia\b|\bbob dole\b|\bgrassley\b|\bstiglitz\b|\bgeithner\b|\bfosnight\b|\bbakiyevs\b|\bmoriarty\b|\bmohammed\b|\bgingrich\b|\bsbwhoeop\b|\bbstrider\b|\bs\. akbar\b|\bjonathan\b|\bholliday\b|\bmorrisoc\b|\bgonzalez\b|\bhillary\b|\bjackson\b|\bkessler\b|\bboehner\b|\babraham\b|\berica 3\b|\brichard\b|\bziglarn\b|\bzigiarn\b|\bpascual\b|\bsolomon\b|\bchilcot\b|\bjon kyl\b|\bha\.fter\b|\binsulza\b|\bsbwhoeo\b|\bmerkley\b|\bgadhafi\b|\bschumer\b|\byitzhak\b|\bgoldman\b|\bjhapour\b|\briddick\b|\be1-kieb\b|\bverveer\b|\brebecca\b|\bdobbins\b|\bqadhafi\b|\bshapiro\b|\bcameron\b|\bbastien\b|\bhassadi\b|\bvolcker\b|\bmorales\b|\bwilliam\b|\bhabedin\b|\bmurdoch\b|\berdogan\b|\barchons\b|\bchemick\b|\bjo lusi\b|\bgravers\b|\bhastert\b|\bcollins\b|\bfillary\b|\bal dhan\b|\bwilders\b|\bed kemp\b|\bdoherty\b|\bmanning\b|\bsharron\b|\bmohamed\b|\bsussman\b|\bbakiyev\b|\bpreines\b|\bmagaref\b|\bsariyev\b|\bben van\b|\bal-keeb\b|\bsanders\b|\bbhutto'\b|\bkrishna\b|\bel-kieb\b|\bdeschle\b|\bk\.ennan\b|\btunisia\b|\bjohnson\b|\boehring\b|\bpodesta\b|\bgardner\b|\bmoammar\b|\bevyenia\b|\blindsey\b|\bclinton\b|\bmustafa\b|\bel-kelb\b|\bpollard\b|\bbennett\b|\bgregory\b|\bzardari\b|\bmichael\b|\bkennedy\b|\bschmidt\b|\bprern g\b|\bsaddarn\b|\bbobbitt\b|\bkuehner\b|\bhussein\b|\bspencer\b|\bcollier\b|\bstewart\b|\bal-keib\b|\bo'keefe\b|\bweather\b|\bsantoro\b|\bcochran\b|\bvalerie\b|\bclyburn\b|\bel keib\b|\bemanuel\b|\bdonilon\b|\bclaudia\b|\bwoodrow\b|\bel-keib\b|\bcrowley\b|\bstevens\b|\banthony\b|\bkhalifa\b|\bmartino\b|\bshapira\b|\bjarrett\b|\bsummers\b|\bgeitner\b|\bqaddafi\b|\bpol pot\b|\bbuckley\b|\bcharlie\b|\broebuck\b|\bwallace\b|\bdaschle\b|\bosborne\b|\bsheldon\b|\bskousen\b|\bgillani\b|\bclapper\b|\baguilar\b|\bgaddafi\b|\bbunning\b|\bantonio\b|\bdaalder\b|\bfranken\b|\bshoebat\b|\bschultz\b|\bbelhars\b|\bchi!cot\b|\baxelrod\b|\bmelanne\b|\bmohamad\b|\bqataris\b|\bmichele\b|\blebaron\b|\bbarbara\b|\bsarkozy\b|\bhousing\b|\bmikhail\b|\bnanda 5\b|\bshannon\b|\bheather\b|\blalanne\b|\bntanden\b|\bjaneway\b|\bzelaya\b|\bmullen\b|\bbashir\b|\balfred\b|\bpeters\b|\bsaddam\b|\bcorker\b|\beugene\b|\bhitler\b|\bsharia\b|\bbaucus\b|\bobaxna\b|\bcengiz\b|\bmoreno\b|\breagan\b|\bal- ai\b|\bfabius\b|\bjoseph\b|\bshaban\b|\bhilary\b|\bbarack\b|\bjabril\b|\bstalin\b|\brupert\b|\bbrooke\b|\bsusman\b|\bcantor\b|\btebbit\b|\bidriss\b|\bmerkel\b|\blana j\b|\bgeorge\b|\broemer\b|\bshelby\b|\bharich\b|\barturo\b|\brobert\b|\blyndon\b|\brafter\b|\bsharif\b|\bgeller\b|\bkramer\b|\bfallon\b|\bwerner\b|\bursula\b|\btiller\b|\bfaisal\b|\bdurbin\b|\bmelton\b|\bweiner\b|\bfoxman\b|\bashton\b|\bstrobe\b|\bbelhaj\b|\bhashem\b|\bstupak\b|\bcherie\b|\bwalton\b|\boba ma\b|\bpelosi\b|\bmendes\b|\bhalter\b|\bsodini\b|\bmarvin\b|\bclaire\b|\bconrad\b|\bcheney\b|\bziglam\b|\bkhalid\b|\bnelson\b|\bdooley\b|\boxford\b|\bguerra\b|\bwisner\b|\brivkin\b|\bpowell\b|\bpreval\b|\binglis\b|\bobam\.a\b|\b°barna\b|\bl\.b\.j\.\b|\bkabila\b|\bcornyn\b|\bromney\b|\bandrew\b|\bmassad\b|\bodinga\b|\balbeit\b|\brascon\b|\bobarna\b|\bkerman\b|\bortega\b|\bkristy\b|\bhudson\b|\bharris\b|\bwilson\b|\bheintz\b|\bwarner\b|\bpastor\b|\bmccain\b|\bkapoor\b|\bkennan\b|\byounes\b|\btakano\b|\bdamour\b|\bcarson\b|\bjibril\b|\bannabi\b|\bhassan\b|\bkarzai\b|\blouise\b|\bdemint\b|\bshahan\b|\bcheryl\b|\bhector\b|\baubrey\b|\bheftar\b|\bnathan\b|\bjuan s\b|\bhefter\b|\bparvez\b|\bjuarez\b|\bharkin\b|\behrman\b|\bmerten\b|\bbennet\b|\bdobson\b|\bcoburn\b|\bsophie\b|\bstruwe\b|\bmaddow\b|\blittle\b|\bsantos\b|\bdayton\b|\bgordon\b|\bsalehi\b|\bgraver\b|\btapper\b|\bbenson\b|\bnachum\b|\bholder\b|\bhaftar\b|\bsolana\b|\bmormon\b|\bchitre\b|\bsilvia\b|\bgarcia\b|\bjavits\b|\bdubbin\b|\bphilip\b|\bjuwali\b|\bmchale\b|\btories\b|\bsun zi\b|\bhoover\b|\boba\.ma\b|\bthomas\b|\bsherif\b|\bkazan\b|\bjalil\b|\bputin\b|\bshura\b|\bpipes\b|\bkerry\b|\bsadie\b|\bchris\b|\bobama\b|\bpiper\b|\bpitts\b|\brandy\b|\bobeda\b|\bsauer\b|\bsowan\b|\bcretz\b|\btaitz\b|\blarry\b|\bblair\b|\bbarna\b|\bjones\b|\btorah\b|\bwelch\b|\bchuck\b|\budall\b|\bhenry\b|\b!aura\b|\bjames\b|\bshaun\b|\buribe\b|\bwhite\b|\bmeraj\b|\babbas\b|\barusi\b|\bfrank\b|\bzidan\b|\broger\b|\blevin\b|\bpeter\b|\brosie\b|\bsingh\b|\bhelms\b|\bocher\b|\bmorsi\b|\bmeese\b|\blibya\b|\bmeyer\b|\bpeggy\b|\bbaker\b|\botmar\b|\bpaige\b|\bcowen\b|\banton\b|\bsorba\b|\bgheit\b|\bgrist\b|\bmarie\b|\bphiii\b|\bgregg\b|\bmalin\b|\bbrady\b|\broses\b|\bhamid\b|\barmey\b|\bglenn\b|\barutz\b|\bbrown\b|\bjafil\b|\bzheng\b|\bmarat\b|\bsteve\b|\bhaass\b|\bsnowe\b|\bsegal\b|\bsally\b|\bgiles\b|\bluers\b|\bhabre\b|\bpatin\b|\bjabar\b|\bsheva\b|\bdavid\b|\bhague\b|\bhasan\b|\bialil\b|\bboyce\b|\bscott\b|\bburns\b|\brabin\b|\bponce\b|\bkumar\b|\brabbi\b|\bharry\b|\biqbal\b|\bborwn\b|\bclegg\b|\bsusan\b|\blopez\b|\bsalon\b|\bmills\b|\bortiz\b|\bjaill\b|\brobyn\b|\bangle\b|\bdelay\b|\bnge,b\b|\bnixon\b|\bdenis\b|\bbecky\b|\bassad\b|\bsmith\b|\bbadie\b|\blewis\b|\bterry\b|\bjalii\b|\bsirin\b|\bjoyce\b|\bosama\b|\bgates\b|\brandi\b|\bleahy\b|\brosas\b|\bcasey\b|\bhamas\b|\blugar\b|\bsousa\b|\bpalin\b|\bstrom\b|\bstraw\b|\btorat\b|\bzaidi\b|\bderek\b|\bcolin\b|\boscar\b|\bbiden\b|\bbetsy\b|\bsarah\b|\bpenn\b|\bshah\b|\bholz\b|\bphil\b|\bcoup\b|\bmack\b|\bmarc\b|\bnick\b|\breid\b|\bnero\b|\bkeib\b|\byang\b|\bjill\b|\blona\b|\bpaul\b|\bdick\b|\bh rn\b|\bmatt\b|\bruss\b|\bbayh\b|\bibid\b|\bbart\b|\bwebb\b|\bbush\b|\bjose\b|\bjeff\b|\bhill\b|\bhuma\b|\bbeck\b|\btory\b|\bhart\b|\bjuan\b|\baziz\b|\brush\b|\bdede\b|\btony\b|\bkeit\b|\bryan\b|\bhaim\b|\baiwa\b|\bmike\b|\brove\b|\bjack\b|\bjail\b|\brauf\b|\bpalm\b|\bgary\b|\bdodd\b|\bsade\b|\beric\b|\bagha\b|\bsean\b|\baksu\b|\bqamu\b|\balec\b|\bmani\b|\bmeek\b|\brahm\b|\brice\b|\bayub\b|\blevy\b|\bmark\b|\b9/11\b|\belia\b|\bbill\b|\bclay\b|\bgeed\b|\btrig\b|\brand\b|\bjohn\b|\bjahr\b|\bcaro\b|\bburr\b|\bjake\b|\bnewt\b|\bdink\b|\blund\b|\bglen\b|\bford\b|\bdeby\b|\bkarl\b|\bsami\b|\bann\b|\bhbj\b|\bhb3\b|\bjoe\b|\bal-\b|\bban\b|\bamr\b|\bjim\b|\bski\b|\bjen\b|\bali\b|\bsid\b|\bdan\b|\bmax\b|\bcdm\b|\byan\b|\bjon\b|\bron\b|\bmcc\b|\bsby\b|\bemb\b|\bpam\b|\bmcd\b|\bjfk\b|\bsam\b|\bzia\b|\btom\b|\bkyl\b|\bhsf\b|\blyn\b|\bbob\b|\bel-\b|\bliz\b|\bwjc\b|\bsbu\b|\baui\b|\brob\b|\bmao\b|\babz\b|\bdfm\b|\bhrc\b|\bstu\b|\bkay\b|\btx\b|\bp3\b|\bcb\b|\bmo\b|\bch\b|\bw\.\b|\bed\b|\bal\b|\bdp\b|\bho\b|\bpj\b|\bnn\b|\bdd\b|\bel\b|\bh\b"

    indexes = [
        (i.start(), i.end()) for i in re.finditer(pattern, raw_txt,
                                                  flags=re.IGNORECASE)
    ]
    for t in indexes:
        entity = {}
        entity["start"] = t[0]
        entity["end"] = t[1]
        entity["tag"] = "NAME"
        entity["extent"] = raw_txt[t[0] : t[1]]
        spans.append(entity)
    return spans


def getBasicAnnotations(raw_txt):
    allAnnotations = []
    allAnnotations.extend(getGenderAnnotations(raw_txt))
    allAnnotations.extend(
        getSpans(r"\b[a-zA-Z0-9+_.-]+@[a-zA-Z]+\.[a-zA-Z]+\b", raw_txt, "EMAIL")
    )
    allAnnotations.extend(getTimeSpans(raw_txt))
    allAnnotations.extend(getDateSpans(raw_txt))
    allAnnotations.extend(getCountrySpans(raw_txt))
    allAnnotations.extend(getStateSpans(raw_txt))
    # allAnnotations.extend(getPhoneSpans(raw_txt))
    allAnnotations.extend(getNameSpans(raw_txt))
    allAnnotations.extend(getUnameAnnotations(raw_txt))

    return {"named_entity": sorted(allAnnotations, key=lambda x: x["start"])}


def simp_span(annot):
    if not annot:
        return ''
    return str(annot.get('extent'))

def simp_tag(annot):
    if not annot:
        return ''
    return (
        annot.get('tag') + ' ' +
        str(annot.get('properties', {}).get('ADDRESS-SUBTYPE') or '') +
        str(annot.get('properties', {}).get('DATE-TIME-SUBTYPE') or '')
    )

INF = float('inf')

def arbitrate(doc, context=50, width=50):
    from rich import print
    count = 0
    canon = []
    j_annot = sorted(doc['annotations']['named_entity'], key= lambda x: x['start'])
    l_annot = sorted(doc['annotations_v2']['named_entity'], key= lambda x: x['start'])
    k_annot = getBasicAnnotations(doc.get('raw_text'))['named_entity']
    print(f"Get ready to cross check around {max(len(j_annot), len(k_annot), len(l_annot))} docs. IS_PII_POSSIBLE={doc.get('is_pii_possible', 'Unknown')}")
    readchar()
    # import pdb; pdb.set_trace();
    while j_annot or k_annot or l_annot:
        cj, ck, cl = [None, None, None]
        start = INF
        for c in j_annot, k_annot, l_annot:
            # print(c)
            if c:
                start = min(start, c[0]['start'])
        text = doc['raw_text']
        if j_annot and j_annot[0]['start'] == start:
            cj = j_annot.pop(0)
        if k_annot and k_annot[0]['start'] == start:
            ck = k_annot.pop(0)
        if l_annot and l_annot[0]['start'] == start:
            cl = l_annot.pop(0)
        # print(cj, ck, cl)
        end = (cj or ck or cl)['end']
        print(f"[red]{text[start-context:start]}[/][yellow]{text[start:end]}[/][red]{text[end:end+context]}[/]")
        print('')
        print(f"{simp_tag(cj):<50} -- {simp_tag(ck):^50} -- {simp_tag(cl):>50}")
        print(f"{simp_span(cj):<50} -- {simp_span(ck):^50} -- {simp_span(cl):>50}")
        if cj == cl and cj is not None:
            c = 'j'  # any one of those
        else:
            c = readchar()
        while c not in 'qjkls':
            c = readchar()
        if c == 'q':
            raise KeyboardInterrupt
        print(c)
        if cj and c == 'j':
            canon.append(cj)
        elif ck and c == 'k':
            canon.append(ck)
        elif cl and c == 'l':
            canon.append(cl)
        try:
            end = canon[-1]['end']
        except IndexError:
            for c in cj, ck, cl:
                if c:
                    end = min(end, c['end'])
        while j_annot and j_annot[0]['start'] < end:
            j_annot.pop(0)
        while k_annot and k_annot[0]['start'] < end:
            k_annot.pop(0)
        while l_annot and l_annot[0]['start'] < end:
            l_annot.pop(0)
        print('\n')
        count += 1
        print(count)
    return canon




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--arbitrate", action="store_true",
                        help="Flag if file needs to be arbitrated.")
    args = parser.parse_args()

    with open(args.input, "r") as json_file:
        documents = [json.loads(i) for i in list(json_file)]
        # for i, doc in enumerate(documents):
            # print(i+1, doc['is_pii_possible'], doc['language'], doc['excecption_type'])
        # import pdb; pdb.set_trace()

    if args.arbitrate:
        # TODO: Allow option of choosing doc
        with open(args.input + '.new', "w") as json_file:
            for i, doc in enumerate(documents):
                print(f"Doc {i+1} of {len(documents)}")
                # TODO: Allow option of choosing doc
                annots = arbitrate(doc)
                doc["annotations"] = {
                    "named_entity": sorted(annots, key=lambda x: x["start"])
                }
                json_file.write(json.dumps(doc) + "\n")
    else:
        with open(args.input, "w") as json_file:
            for document in documents:
                document["annotations"] = getBasicAnnotations(document["raw_text"])
                json_file.write(json.dumps(document) + "\n")


if __name__ == "__main__":
    main()
