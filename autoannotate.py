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


def getTimeSpans(raw_txt):
    spans = []

    hour = r'([0-1]?[0-9]|2[0-3])'
    minutes = r'([0-5][0-9])'
    seconds = r'([0-5][0-9])'
    suffix = r'([ap].?m.?)'

    formats = []

    formats.append(hour+r'[\.:\s*]?'+minutes+r'?[\.:\s]*'+seconds+r'[\.\s]*'+suffix)
    formats.append(hour+r'[\.:\s*]?'+minutes+r'[\.\s]*'+suffix)
    formats.append(hour+r'[\.:\s*]?'+minutes+r'[\.:\s]*'+seconds)
    formats.append(hour+r'[\.\-\s*]?'+suffix)

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
    day = r"((0[1-9]|[12]\d|3[01])|([1-9]|[12]\d|3[01]))"
    year_large = r"([12][0-9]{3})"
    year_small = r"((19|20)\d{2})"

    formats = []

    formats.append(day+r'\\'+month+r'\\'+year_large)
    formats.append(month+r'\\'+day+r'\\'+year_large)
    formats.append(week_day+r'[\.,\s]*'+month+r'[\.,\s]*'+day+r'[\.,\s]*'+year_large)
    formats.append(week_day+r'[\.,\s]*'+month+r'[\.,\s]*'+day)
    formats.append(month+r'[\.,\s]*'+day+r'[\.,\s]*'+year_large)
    formats.append(day+r'[\-\s]?'+month)
    formats.append(month+r'[\.,\s]*'+day)
    formats.append(month+r'[\.,\s]*'+year_large)
    formats.append(year_large+r'\s*((to)|-|(and))\s*'+year_large)
    formats.append(year_small)

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
        r"America",
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
    pattern = r"\bshaykh al islam mohammed ibn 'abd al-wahhab al-tanaimi\b|\babdullah bin abdulaziz al-sa'ud\b|\blgustafson_karen cardiel, daisy\b|\bgustafson_karer cardiel, daisy\b|\bgustafson_karen cardiel, daisy\b|\bthomas-greenfield, linda(ms)\b|\bvictor manuel rivera moreno\b|\bmohammed yussef el magariaf\b|\baustin-ferguson, kathleen t\b|\bmullah abdul ghani baradar\b|\bmabrouk issa abu harroura\b|\babdel hakim alamin belhaj\b|\bassuncao afonso dos anjos\b|\bpatriarch mesrop mutafyan\b|\bluz elena guerrero guerra\b|\bchristopher m\. schnaubelt\b|\breverend deacon nektarios\b|\bcardinal joachim meisner\b|\bthomas-greenfield, linda\b|\bmohammed yussef magariaf\b|\bcharles luoma-overstreet\b|\bsail al-islam al-qadhafi\b|\bk\.s\. sachidananda murthy\b|\bjones-johnson, carolyn d\b|\bshaykh al islam mohammed\b|\bwilliam f\. buckley, jr\.\b|\bclaudia ivette gonzalez\b|\bkhalifa belgasim haftar\b|\bmcmullen, christopher j\b|\bkhalifa belqasim hefter\b|\bkhalifa belqasim haftar\b|\babd al-wahhab al-tamimi\b|\bhrod17@clintonemail\.com\b|\bdaniel patrick moynihan\b|\bpatriarch bartholomew i\b|\bjean-berttrand aristide\b|\bclaudia lvette gonzalez\b|\bclaudia !vette gonzalez\b|\bclaudia 'vette gonzalez\b|\bpatriarch, bartholomew\b|\bbarks-ruggles, erica 3\b|\bmiguel angel jaramillo\b|\bbernier-toth, michelle\b|\bpatriarch bartholomeos\b|\bhillary rodham clinton\b|\blilia alejandra garcia\b|\bchristopher schnaubelt\b|\btomlinson, christina b\b|\barturo gonzalez rascon\b|\bmartin luther king jr\.\b|\bjean-bertrand aristide\b|\banders fogh rasmussen\b|\boscar maynez grijalva\b|\bmustafa kemal ataturk\b|\babdulrahman ben yazza\b|\bslaughter, anne-marie\b|\bsaif al-islam qaddafi\b|\bjean-robert lafortune\b|\bjane dammen mcauliffe\b|\babd al-nasser shamata\b|\bwillard cleon skousen\b|\bpatriarch bartholomew\b|\belizabeth fitzsimmons\b|\bmalin, mary catherine\b|\bpatriarch vartholomew\b|\bgillis, christopher 3\b|\bmohamed hosni mubarak\b|\balexis de tocqueville\b|\bsullivan, stephanie s\b|\babdulrahman ben yezza\b|\b\.kbdel rahman el-keib\b|\banthony j\. limberakis\b|\bmortimer b\. zuckerman\b|\bfitzgerald, william e\b|\bsolirnan abd al-qadr\b|\babdel rahman el-keib\b|\bkreab gavin anderson\b|\braghavan jagannathan\b|\btomlinson, christina\b|\bhallett, stephanie l\b|\bdavid m, satterfield\b|\bklevorick, caitlin b\b|\bjacqueline novogratz\b|\bmohammed al-magariaf\b|\bpaulo espirito santo\b|\banne-marie slaughter\b|\bantonio munoz ortega\b|\bnelson w\. cunningham\b|\brandolph, lawrence m\b|\bsamuelson, heather f\b|\bjohn birks gillespie\b|\bantonios trakatellis\b|\brecep tayyip erdogan\b|\bstephanie l\. hallett\b|\bjames r\. stoner, jr\.\b|\bdwight d\. eisenhower\b|\bchas w\. freeman, jr\.\b|\bcrocker, bathsheba n\b|\bkennedy, j christian\b|\bdr\. allan e\. goodman\b|\belizabeth ontiveros\b|\bschlicher, ronald l\b|\byoussef al mangoush\b|\bmahmoud ahmadinejad\b|\bmcauliffe, marisa s\b|\bcie re m ccaski i i\b|\bjean-louis warnholz\b|\bsucharita narayanan\b|\bmustafa abdul jalil\b|\bmustafa abdel jalil\b|\belizabeth thornhill\b|\bmolly sanchez crowe\b|\byu\.ssef el magariaf\b|\bfeltrnan, jeffrey d\b|\bmuhammad zia ul haq\b|\bchristina tomlinson\b|\brodriguez, miguel e\b|\babdurrahirn el-keib\b|\bgeraldine seruyange\b|\bslattery, phillip t\b|\bmuhammad al-gharabi\b|\bcecilia covarrubias\b|\bbrassanini, david g\b|\bfarooq khan leghari\b|\bhi i i ay ci i nton\b|\bchristine dal bello\b|\bmceldowney, nancy e\b|\bdavid, jimmy carter\b|\bzulfikar ali bhutto\b|\bmcdonough, denis r\.\b|\bchristopher stevens\b|\byousuf raza gillani\b|\bdibble, elizabeth l\b|\bpriscilla hernandez\b|\bgeoffroy, gregory l\b|\bstevens mitt romnev\b|\bmuaimnar al qaddafi\b|\bmuhammad zia ul-haq\b|\bousetrill al juwaii\b|\bmuarnmar al qaddafi\b|\bchartrand, jennifer\b|\baf-fo-principals-dl\b|\babdurrahim el keib\b|\bmuhammad ayub khan\b|\bverveer, melanne s\b|\brobinson, brooks a\b|\bharris, jennifer m\b|\bfinley peter dunne\b|\bschwerin, daniel b\b|\bgilmore, kristin m\b|\bahmed abu khattala\b|\balexander hamilton\b|\bchristopher harich\b|\bfielder, rebecca a\b|\bsheldon whitehouse\b|\bsimpson, mordica m\b|\bjacqueline charles\b|\bshapiro, andrew \.3\b|\babdurrahim el-keib\b|\babu yahya al- libi\b|\babdelfattah younes\b|\bhenry a\. kissinger\b|\blakhdhir, kamala s\b|\bmohammed yussef el\b|\babdulbari al-arusi\b|\bwilliam f\. buckley\b|\bmaier, christina a\b|\bfranklin roosevelt\b|\bmacmanus, joseph e\b|\banthony limberakis\b|\balexander zaitchik\b|\bmuammar at qaddafi\b|\blebanese hizballah\b|\bmustafa abdel jail\b|\bstanley mcchrystal\b|\bmuammar al qaddafi\b|\breines, philippe i\b|\broebuck, william v\b|\bbenjamin netanyahu\b|\bkennedy, patrick f\b|\bnelson rockefeller\b|\babdelhalcim belhaj\b|\bmadeleine albright\b|\bmuhammad al-zahawi\b|\br\. donahue peebles\b|\bslobodan milosevic\b|\bverveer, melanne 5\b|\bamir mohammad agha\b|\babdelhakirn belhaj\b|\bjames a\. baker iii\b|\babdel latif sharif\b|\bmichael o'halloran\b|\bsanderson, janet a\b|\bmaxwell, raymond d\b|\bfeltman, jeffrey d\b|\brichardson, eric n\b|\banderson, brooke d\b|\besther chavez cano\b|\bdebasish chowdhury\b|\bbrooks a\. robinson\b|\bnuland, victoria 3\b|\bgulbadin hikmatyar\b|\bjean-claude bajeux\b|\btheodore roosevelt\b|\bslobodan milosevie\b|\bsullivan, jacob \.1\b|\bmustafa abdul jail\b|\bmohamed al-qadhafi\b|\babdullah bin zayed\b|\babdulaziz al-sasud\b|\babdelhakim belhaj\b|\bdwight eisenhower\b|\bcatherine hallock\b|\bmary beth leonard\b|\bsullivan, jacob 3\b|\bfriedrich, mary k\b|\brichard l\. kugler\b|\brichard holbrooke\b|\bbill strassberger\b|\brandolph mcgrorty\b|\bjeffrey donaldson\b|\blvlills, cheryl d\b|\bcaitlin m\. hayden\b|\bfrancisco sanchez\b|\bsidereas, evyenla\b|\bdavid j\. rothkopf\b|\bmustafa abdel mil\b|\bjosefina gonzalez\b|\bpacheco, martha a\b|\bmark anthony neal\b|\bdebbie almontaser\b|\bjeremy greenstock\b|\bmichael bloomberg\b|\bmustafa abdul jai\b|\bpatricio martinez\b|\bmacris, gregory p\b|\bcampbell, piper a\b|\bshapiro, daniel b\b|\bpolaschlk, joan a\b|\bbrigitte pressler\b|\blaszczych, joanne\b|\bposivak, stephen;\b|\barturo valenzuela\b|\bwilliam fulbright\b|\bohtagaki, johna 0\b|\bricardo seitenfus\b|\bhormats, robert d\b|\bcrowley, philip 1\b|\bmichael pelletier\b|\bmargaret thatcher\b|\bmohammed al-sissi\b|\bmartin mcguinness\b|\bsullivan, jacob i\b|\bronald e\. neumann\b|\bmustafa abushagur\b|\bgeorge h\. w\. bush\b|\bcaitlin klevorick\b|\bfrank shakespeare\b|\bshannon, thomas a\b|\bousama al jouwali\b|\bgerald mcloughlin\b|\btimothy j\. roemer\b|\bterrence a\. duffy\b|\bmorton abramowitz\b|\brussell, daniel a\b|\bburns, william \.1\b|\bobeidah al-jarrah\b|\brichard johannsen\b|\beizenstat, stuart\b|\bstephanie browner\b|\bcoleman, claire i\b|\bmuammar al qaddaf\b|\bsullivan, jacob j\b|\bcaspar weinberger\b|\bdonilon, thomas e\b|\bhoward metzenbaum\b|\bcoleman, claire l\b|\bkoutsis, steven c\b|\bfeisal abdul rauf\b|\bavigdor lieberman\b|\badolph a\. weinman\b|\bgarrard, steven d\b|\bcurtis, meghann a\b|\bbenjamin franklin\b|\bjamjoom, kareem n\b|\bchristopher meyer\b|\bjeannemarie smith\b|\bdavid klinghoffer\b|\bsullivan, jacob 1\b|\braja bhattacharya\b|\bsidney blumenthal\b|\bdrucker, milton k\b|\badam parkhomenko\b|\bharry mcpherson,\b|\barindam sengupta\b|\bverma, richard r\b|\bcharles grassley\b|\bolson, richard g\b|\bbader, jeffrey a\b|\brobert g\. kaiser\b|\bharold w\. geisel\b|\bjacobs, janice l\b|\bjames earl jones\b|\bmchale, judith a\b|\bmariela paniagua\b|\brichard viguerie\b|\bjiloty, lauren c\b|\bsullivan, jacobj\b|\bregan, michael b\b|\bfeltman, jeffrey\b|\bclaire mccaskill\b|\banne-marie brady\b|\bnuiand, victoria\b|\baxelrod, david m\b|\bpatricia ehrnman\b|\bmatthew g\. olsen\b|\bhanley, monica r\b|\bkirby, michael d\b|\bradovan karad2ie\b|\brajdeep sardesai\b|\bnicholas sarkozy\b|\bsherman, wendy r\b|\bbulgrin, julie k\b|\bdianne feinstein\b|\bbenito mussolini\b|\bgeorge h\.w\. bush\b|\bduguid, gordon k\b|\brandy neugebauer\b|\bcatlin m\. hayden\b|\bmitchell, george\b|\bburns, william j\b|\b'ramsay, jaime t\b|\bnick von mertens\b|\bjohnson, brock a\b|\balexey druzhinin\b|\btiseke kasambala\b|\bpervez musharraf\b|\bdavid n\. merrill\b|\bharvey sernovitz\b|\bburns, william 3\b|\bbarbara retzlaff\b|\bjames f\. dobbins\b|\bgordon, philip h\b|\bjacobs, janice 1\b|\bmeena shridharan\b|\ba/lax blumenthal\b|\bansar al-shariah\b|\bpierre esperance\b|\btimothy geithner\b|\basif ali zardari\b|\bsusan col i i ns\b|\bposivak, stephen\b|\bfrancois leotard\b|\bschrepel, dawn m\b|\bmcdonald, kara c\b|\babdelhamid rifai\b|\bgeorge voinovich\b|\bvartan gregorian\b|\bezra taft benson\b|\belizabeth bagley\b|\bwalsh, matthew p\b|\bchollet, derek h\b|\bpatriarch mesrop\b|\bdorothy ngalombi\b|\brussel, daniel r\b|\blawrence summers\b|\bdeborah mccarthy\b|\bsamira lzaguirre\b|\bousama at juwali\b|\bangela paiaveras\b|\bmike vanderboegh\b|\bschlesinger, jr\.\b|\bmohammed rvlorsi\b|\bousama al-juwali\b|\bhaji abdul jabar\b|\balija izetbegovi\b|\belmira ibraimova\b|\balford, edward m\b|\bhamad bin jassim\b|\bsukhwinder singh\b|\bandrea puchalsky\b|\bjohnson, james r\b|\babbaszadeh, myna\b|\bsimon, jessica l\b|\babbaszadeh, nima\b|\bjonathan pollard\b|\bjudith a\. mchale\b|\bjonathan m\. katz\b|\banil padmanabhan\b|\bchristine ashton\b|\bshailja kejriwal\b|\bmolly montgomery\b|\bsumilas, michele\b|\bmohamed magariaf\b|\bwilliam s\. white\b|\bsullivan, jacobi\b|\bpeter eisenhauer\b|\bthomas jefferson\b|\bsamira izaguirre\b|\bchristopher dodd\b|\bjean-paul sartre\b|\bjacob j sullivan\b|\bbashir al-kubty\b|\bgustafson_karen\b|\bhanky, monica r\b|\bhenry kissinger\b|\bharold w geissl\b|\blvette gonzalez\b|\bdamour, marie c\b|\bsmith, daniel b\b|\bcharge robinson\b|\bnides, thomas r\b|\bhillary clinton\b|\bmahmoud _fibril\b|\bmario lee lopez\b|\bomar al i3ashir\b|\babdulkadir aksu\b|\bprashanth rajan\b|\bezekiel emanuel\b|\bculver, chris d\b|\bjoseph stiglitz\b|\banthony campolo\b|\baustan goolsbee\b|\bmichael m ullen\b|\bstan mcchrystai\b|\bfawzi abu kitef\b|\badam j\. grotsky\b|\bstevens, john c\b|\bmohamed bujenah\b|\bmichael s\. lund\b|\bdwayne l\. cline\b|\beverett dirksen\b|\bsutphin, paul r\b|\bdominic asquith\b|\byigal schleifer\b|\bandrew sullivan\b|\beliot shapleigh\b|\bnorman ornstein\b|\bcharles schumer\b|\bsamuel freedman\b|\bbarry goldwater\b|\bkitty dimartino\b|\bsoledad aguilar\b|\bmatthew hiltzik\b|\bhoney alexander\b|\baustin-ferguson\b|\bdizzy gillespie\b|\bvalmoro, lona 1\b|\babdullah shamia\b|\bpatricia lamego\b|\bhubert humphrey\b|\bjames baker iii\b|\bmontek aluwalia\b|\bkarl eikenberry\b|\bstan mcchrystal\b|\bfred a\. shannon\b|\bhillary, cheryl\b|\bmichael janeway\b|\bmusharraf years\b|\bwalker, peggy j\b|\bdenis mcdonough\b|\bbrooks robinson\b|\bsufyan ben qumu\b|\bmesrop mutafyan\b|\byousef mangoush\b|\bgeorge mcgovern\b|\bsusan povenmire\b|\bosama al juwali\b|\btom pyszczynski\b|\beugene mccarthy\b|\bcline, dwayne l\b|\bfogarty, daniel\b|\bhillarv clinton\b|\bsharon d\. james\b|\bandrea mitchell\b|\beustace mullins\b|\bwalid al-sakran\b|\bsherlock holmes\b|\bosama al-juwali\b|\bbond, michele t\b|\bvalmoro, lona j\b|\bmitch mcconnell\b|\bmark carruthers\b|\bpratap g\. pawar\b|\bze'ev sternhell\b|\bmarshall petain\b|\babraham lincoln\b|\bnancy kachingwe\b|\bsufian bin qamu\b|\bsullivan, jacob\b|\bornar al bashir\b|\bmax blumenthal,\b|\bmills, cheryl 0\b|\brichard cordray\b|\bosama bin laden\b|\bwilliam zartman\b|\bdaniel benjamin\b|\bkatrina hourani\b|\bcoleman, claire\b|\bdavid schaecter\b|\byitzhak shapira\b|\blynne gadkowski\b|\bpolt, michael c\b|\bcoionia morelos\b|\bcarson, johnnie\b|\bmuammar gaddafi\b|\bj\. edgar hoover\b|\bbelqasim haftar\b|\bjohn c\. calhoun\b|\bdonald rumsfeld\b|\blauran lovelace\b|\bansar al sharia\b|\bbecky bernhardt\b|\blamar alexander\b|\bjohn f\. kennedy\b|\banushka asthana\b|\bdimitris reppas\b|\bhans binnendijk\b|\bemanuel cleaver\b|\bteddy roosevelt\b|\bjames s\. rogers\b|\bbasher al assad\b|\bjason straziuso\b|\brhoda margesson\b|\bmiller, james n\b|\bmishna gregoire\b|\bdavid shambaugh\b|\bnicolas sarkozy\b|\baubrey chernick\b|\bedwin a\. walker\b|\bsad\.dam hussein\b|\bbondy, steven c\b|\bgeorge mitchell\b|\bblanche lincoln\b|\bshubhangi desai\b|\bramsay, jaime t\b|\bhoward phillips\b|\bdebbie stabenow\b|\bmuammar qadhafi\b|\brusso, robert v\b|\brobert menendez\b|\bsamuel brinkley\b|\bmaggie williams\b|\bchas w\. freeman\b|\bmuammar qaddafi\b|\bprashant panday\b|\bmargaret scobey\b|\bcilia kerfuffie\b|\bkemal kerincsiz\b|\bharry mcpherson\b|\bevangeline arce\b|\broza otunbayeva\b|\bchristina romer\b|\bmandelson watch\b|\blouis b\. susman\b|\b°same al juwali\b|\bmo9rt zuckerman\b|\bjoseph mccarthy\b|\bmills, cheryl d\b|\bcharles peters\b|\bgaylord nelson\b|\bjames eastland\b|\bcardiel, daisy\b|\bmichael steele\b|\bj\. bracken lee\b|\bnewt gin<trich\b|\borville schell\b|\bholtz, greta c\b|\bosama al kwali\b|\bdaniel webster\b|\brobert gelbard\b|\bmort zuckerman\b|\bismail sallabi\b|\bsusilo bambang\b|\bjoann lockhart\b|\bsanjoy narayan\b|\brobert spencer\b|\brichard condon\b|\bmartha mendoza\b|\bhickey, mary e\b|\bsid blumenthal\b|\bilario pantano\b|\bcarlos pascual\b|\bdonny -kuehner\b|\bnuni berrusien\b|\balyson grunder\b|\bpeter robinson\b|\bwalter mondale\b|\bdennis gombert\b|\bs cheryl mills\b|\bstrobe talbott\b|\bmax blumenthal\b|\bhassan ziglarn\b|\bjohn m\. bryson\b|\bkelly, craig a\b|\btorn perriello\b|\bphilip bobbitt\b|\balbert r\. hunt\b|\bs\. akbar zaidi\b|\bnorman borlaug\b|\bpatricia lynch\b|\bsa-igha rat mi\b|\bbetsy whitaker\b|\bjanysh bakiyev\b|\bmary catherine\b|\bbeth gili\.nsky\b|\blindsey graham\b|\bjames s rogers\b|\bclaudia lvette\b|\barvizu, alex a\b|\bdavies, glyn t\b|\bgeorge schultz\b|\bryan christmas\b|\bsaud al-faisal\b|\bnicole peacock\b|\blyndon johnson\b|\bbernie sanders\b|\bdonald ritchie\b|\bport-au-prince\b|\bpeter claussen\b|\bmarianne scott\b|\bbarholomeos ii\b|\bdavid petraeus\b|\bmary 'landrieu\b|\bandrea santoro\b|\blord goldsmith\b|\bthais ruboneka\b|\brobert maguire\b|\bnina fedoroff,\b|\bdaniel, joshua\b|\bdeborah haynes\b|\bosama binladin\b|\bwilliam ehrman\b|\bjettison clegg\b|\bsanghar rahimi\b|\bmission steven\b|\bdick holbrooke\b|\bmohnimed morsi\b|\brichard shelby\b|\banthony weiner\b|\bmichael mullen\b|\barola, heidi r\b|\bdavid ignatius\b|\brebecca struwe\b|\bamax al sharia\b|\bhenry mcdonald\b|\bpraveen patkar\b|\bdavid rothkopf\b|\bross, dennis b\b|\bsaddam hussein\b|\bmichael bennet\b|\brobert a\. caro\b|\bsadaam hussein\b|\bomar al bashir\b|\bpark, pamela p\b|\brichard kugler\b|\bbenaim, daniel\b|\bgeorge w\. bush\b|\bedwina sagitto\b|\bandrew gravers\b|\bedward chaplin\b|\bchuck grassley\b|\bbrooke shearer\b|\bgregory macris\b|\bloh, anthony x\b|\bellen tauscher\b|\bsusan domowitz\b|\bmarisela ortiz\b|\bjack abriunoff\b|\bgoodman, allan\b|\bfavvzi abd all\b|\bmahmoud fibril\b|\bcharles mugabo\b|\brussell brooks\b|\bjohn e\. herbst\b|\bcharlie palmer\b|\bdavid domenici\b|\bbenazir bhutto\b|\bpiper campbell\b|\bosama biniadin\b|\bvladimir putin\b|\bmohammed badie\b|\balan greenspan\b|\bwells, alice g\b|\bstuart smalley\b|\bshenoa simpson\b|\banthony pigott\b|\blinda mcfadyen\b|\bjohna ohtagaki\b|\bpeter ricketts\b|\bcharles rangel\b|\bwoodrow wilson\b|\bsadiq al-mahdi\b|\bdanielle brian\b|\bgeorge osborne\b|\bharris, rian h\b|\bmaura connelly\b|\bahmad bukatela\b|\bgloria steinem\b|\bwood, robert a\b|\bmohammed morsi\b|\bcharlie crist,\b|\bsanjay sachdev\b|\botto preminger\b|\bshyam asolekar\b|\bkelvin kiyingi\b|\bjeff greenberg\b|\bmahmoud jibril\b|\bshaun woodward\b|\balcee hastings\b|\bdavid miliband\b|\bdavid horowitz\b|\bkarla rubinger\b|\bthomas shannon\b|\bherbert hoover\b|\bscarlis, basil\b|\bpreethi patkar\b|\bkenneth merten\b|\bmichael deaver\b|\bpeter martino\b|\bjames madison\b|\bwilliam hague\b|\bclifford levy\b|\bdonny kuehner\b|\bburns strider\b|\bmevlut kurban\b|\bsheikh hasina\b|\ball al-salabi\b|\botmar oehring\b|\bsherrod brown\b|\bjones, beth e\b|\brobert wexler\b|\btarun katiyal\b|\bjavier solana\b|\bali al-salabi\b|\bthomas menino\b|\bterri rookard\b|\bjake\.sulliyan\b|\bbigalke 'karl\b|\bcharlie flynn\b|\bmartin kramer\b|\bgeorge shultz\b|\bterri schiavo\b|\brichard levin\b|\btilmann geske\b|\bhale, david m\b|\bmike huckabee\b|\balberto wilde\b|\bdeng xiaoping\b|\bmohmmed morsi\b|\bchris mcshane\b|\bbraulio rosas\b|\bnewt gingrich\b|\bmalcolm smith\b|\bmohamad morsi\b|\blee bollinger\b|\brichard haass\b|\bcarlotta gall\b|\bmohamed hosni\b|\blauren jiloty\b|\bbruce wharton\b|\bmartha johnso\b|\bsimon johnson\b|\bhassan ziglam\b|\bderek chollet\b|\bdavid gregory\b|\bjake\.sullivan\b|\bdavid goldman\b|\bsolomon atayi\b|\blydia ellison\b|\bwolff, alex d\b|\bmary spanger,\b|\banne seshadri\b|\bcretz, gene a\b|\bgilmar mendes\b|\bmargery eagan\b|\bhissene habre\b|\bgeorge packer\b|\bolympia snowe\b|\bmarc grossman\b|\bharry hopkins\b|\bpaul folmsbee\b|\bjudith mchale\b|\bmustafa abdel\b|\bamy klobuchar\b|\bgeorge kennan\b|\bdavid axelrod\b|\bgeorge romney\b|\bchuck schumer\b|\bmiriam sapiro\b|\barlen specter\b|\bmustafa abdul\b|\bjames dobbins\b|\bbecky fielder\b|\bjoseph duffey\b|\btoner, mark c\b|\brice, susan e\b|\bnicholas gage\b|\bdenis mukwege\b|\bbartholomew i\b|\bhenry jackson\b|\bturk, david m\b|\bandrew mayock\b|\blauren joloty\b|\bwolfgang hade\b|\bshaw d\. janes\b|\bstilin, jacob\b|\bmarco aurelio\b|\bglen doherty,\b|\bkendrick meek\b|\bforman, james\b|\brobert hunter\b|\bsam brownback\b|\bbill o'reilly\b|\babedin, hurna\b|\bjake sullivan\b|\brachel maddow\b|\bnina fedoroff\b|\bgeorge tiller\b|\bclean skousen\b|\bjames o'keefe\b|\b'cheryl\.mills\b|\brogers cidosa\b|\bjudy trabulsi\b|\barnab goswami\b|\braj chengappa\b|\bjoe lieberman\b|\brichard nixon\b|\brichard lugar\b|\bmohamad sowan\b|\bmridual issar\b|\bchris stevens\b|\bkubiske, lisa\b|\brooney, megan\b|\bmull, stephen\b|\brobb browning\b|\bmills, cheryl\b|\bmohammed swan\b|\brush limbaugh\b|\btushar poddar\b|\bsusan collins\b|\bdavid manning\b|\btina flournoy\b|\bashley esarey\b|\bpamela geller\b|\bwailes, jacob\b|\byasser arafat\b|\bdavid cameron\b|\bsalim \.nabous\b|\bmatthew green\b|\brahi rn faiez\b|\barshiya sethi\b|\bsmita prakash\b|\bwalid shoebat\b|\brobyn remeika\b|\bsalah bishari\b|\babd al-wahhab\b|\bamir mohammad\b|\bbarks-ruggles\b|\bjon tollefson\b|\bdavid skorton\b|\bfawzi abd all\b|\bwilliam cohen\b|\bferuzan mehta\b|\bcleon skousen\b|\bkhushali shah\b|\bshekhar gupta\b|\boliver letwin\b|\bronald reagan\b|\bmahmoud abbas\b|\bcharles moose\b|\bjames clapper\b|\bkoch brothers\b|\bjones, paul w\b|\bkristallnacht\b|\bkarl semancik\b|\bedmund muskie\b|\ballan goodman\b|\btillman geske\b|\bjustin cooper\b|\bs akbar zaidi\b|\btaher sherkaz\b|\blael brainard\b|\bgeorge ketman\b|\bjohn b\. judis\b|\bsilvan shalom\b|\bfrank church\b|\bbashar assad\b|\bsean goldman\b|\btoiv, nora f\b|\bgordon brown\b|\bjohn paul ii\b|\blona valmoro\b|\bbekir ozturk\b|\bdaniel lynch\b|\bed gillespie\b|\bmarie damour\b|\budith mchale\b|\bjulien behal\b|\bcarsten holz\b|\bsean wilentz\b|\bmichael lund\b|\bhamid karzai\b|\blebron james\b|\bpaul vallely\b|\bhaji jhapour\b|\bjames salley\b|\bmohamoud (t)\b|\btim geithner\b|\blinda katehi\b|\bjoe macmanus\b|\bjoseph biden\b|\bsachar, alon\b|\bsam brinkley\b|\bduffy, terry\b|\babu khattala\b|\bnitin vaidya\b|\bcherie blair\b|\bneera tanden\b|\babedin, huma\b|\bglen doherty\b|\bursula burns\b|\bfrank munger\b|\blilia garcia\b|\bsally osberg\b|\bjimmy carter\b|\bfrida lambay\b|\bblair, oni k\b|\bpaul hinshaw\b|\bpeter orszag\b|\bandrew cedar\b|\bcooper udall\b|\babu harroura\b|\bisaac alaton\b|\bpeggy walker\b|\bpaul volcker\b|\bbitter, rena\b|\bgracien jean\b|\bdan restrepo\b|\bminint fawzi\b|\btommy franks\b|\bdavid wilson\b|\bjohn chilcot\b|\bcheryl\.millf\b|\bandrew frank\b|\bvijay chopra\b|\bpierre-louis\b|\bzheng bijian\b|\bmary spanger\b|\bkatie glueck\b|\bs\.m\. krishna\b|\babedln, hume\b|\bjim hoagiand\b|\btrey grayson\b|\blouis susman\b|\btony campolo\b|\bdavid harris\b|\btsou, leslie\b|\bminyon moore\b|\bjames warren\b|\brobert crane\b|\bheidi annabi\b|\bfeisai abdul\b|\brobert blake\b|\brudman, mara\b|\bandrew cuomo\b|\brupert smith\b|\bdaniel akaka\b|\bcheryl mills\b|\brobert welch\b|\bhoward baker\b|\bcheryl\.mills\b|\brichard mays\b|\badam grotsky\b|\bfarej darssi\b|\bsmith bagley\b|\btong, kurt w\b|\brhonda shore\b|\brobert gates\b|\bali tarhouni\b|\bnancy pelosi\b|\bjohn jenkins\b|\bdaniel bliss\b|\bsamuel adams\b|\bkevin tebbit\b|\bhickey, mary\b|\bsharon hardy\b|\blynn allison\b|\bbill clinton\b|\bdonna winton\b|\bmark lippert\b|\belizabeth ii\b|\bjohn schmitz\b|\bbenedict xvi\b|\bbetsy bassan\b|\ball tarhouni\b|\bhakan tastan\b|\bcorley kenna\b|\bsean haimity\b|\bjim hoagland\b|\bmel martinez\b|\babedin, hume\b|\blesley clark\b|\bjudas priest\b|\bleon panetta\b|\bscott roeder\b|\bsami abraham\b|\bsergio brito\b|\bjames pardew\b|\bbrandon webb\b|\bpenn rhodeen\b|\bahmadinej ad\b|\bsean hannity\b|\babd al jalil\b|\bsarah binder\b|\bperla, laura\b|\bjeff feltman\b|\brichard mack\b|\buday shankar\b|\bbarack obama\b|\brahm emanuel\b|\bkarl semacik\b|\bhuma abed in\b|\bjim allister\b|\bugur ya%ksel\b|\bnecati aydin\b|\bsanjaya baru\b|\bdusty rhodes\b|\bkelly, ian c\b|\broger lyners\b|\braila odinga\b|\blisa bardack\b|\bbarney frank\b|\bdaniel pipes\b|\babd al-jalil\b|\bbecker, john\b|\bdonna bryson\b|\btalwar, pune\b|\bpaul collier\b|\bgotoh, kay e\b|\btesone, mark\b|\bdoug hoffman\b|\bjohn boehner\b|\blisa kubiske\b|\bcolin powell\b|\bbab al-aziza\b|\bkaren coates\b|\bjacob javits\b|\bnachum segal\b|\babdullah bin\b|\bp\.j\. crowley\b|\bblum, orna t\b|\bkevin melton\b|\bhannah giles\b|\brockefellers\b|\bmcleod, mary\b|\bchas freeman\b|\bwestmoreland\b|\bdesk rebecca\b|\bdavid vitter\b|\bjeff merkley\b|\bsharon lowen\b|\brockefeller\b|\bwahliabis-m\b|\bjesse helms\b|\bturgut ozal\b|\bmark warner\b|\bshubada rao\b|\bdaniel gros\b|\bdaniel levy\b|\bnorman dodd\b|\bhugo chavez\b|\bmike castle\b|\bvince cable\b|\bdrew westen\b|\bamit tandon\b|\balbert hunt\b|\bsiria lopez\b|\bjana winter\b|\bellen barry\b|\bira shapiro\b|\bchris smith\b|\bnawaz shard\b|\bsam antonio\b|\bkim, yuri j\b|\bfouad ajami\b|\brobert byrd\b|\bjustin blum\b|\bturan topal\b|\bhma abedine\b|\bgrey wolves\b|\bed miliband\b|\bmason, whit\b|\bjack rakove\b|\bkapil sibal\b|\bg\. krishnan\b|\bbartholomew\b|\bmark takano\b|\bjohn mccain\b|\bjoe mellott\b|\bjuan carlos\b|\bcraig kelly\b|\bregina addo\b|\bg\.p\. putnam\b|\bted kennedy\b|\bidriss deby\b|\belena kagan\b|\bkim, sung y\b|\bvicente fox\b|\bjohn sexton\b|\banne wexler\b|\btony newton\b|\blohman, lee\b|\braieev syai\b|\brothschilds\b|\bsarah patin\b|\bugur yuksel\b|\bjames baker\b|\bgeorge bush\b|\bmitt romney\b|\bhuma abedin\b|\bgerald ford\b|\blaura lucas\b|\bmark zimmer\b|\bhoward stem\b|\byan xuetong\b|\boman shahan\b|\bban ki moon\b|\borhan kemal\b|\bdick cheney\b|\banil kapoor\b|\brajeev syal\b|\bunni mennon\b|\banwar sadat\b|\brich greene\b|\btom donilon\b|\babu-shakour\b|\bjeff jacoby\b|\bjim bunning\b|\bim hoagland\b|\bdean debnam\b|\blouis mazel\b|\bernie banks\b|\bemma ezeazu\b|\bross wilson\b|\bkelli adams\b|\banwar iqbal\b|\bamb stevens\b|\bpat kennedy\b|\baryeh eldad\b|\bjeff gannon\b|\bban ki-moon\b|\bsyed, zia s\b|\bsugash ghai\b|\bfloyd flake\b|\bmary pipher\b|\bklinghoffer\b|\blinda dewan\b|\bgerry adams\b|\bel magariaf\b|\bdick durbin\b|\bmike dewine\b|\bwayne morse\b|\bvanderboegh\b|\bjames jones\b|\bahmadinejad\b|\bjohn herbst\b|\btijen aybar\b|\bjim kennedy\b|\bmary scholl\b|\brene preval\b|\bvalmoro, b6\b|\bcheryl\.mill\b|\bsarah palin\b|\bal-mangoush\b|\btorrey goad\b|\bwiley drake\b|\bchris huhne\b|\bjohn haynes\b|\btom daschle\b|\bpeter boone\b|\btocqueville\b|\bbrian cowen\b|\babdulrahman\b|\bkent conrad\b|\bjohn breaux\b|\bsam pitroda\b|\bdeal hudson\b|\bsara devlin\b|\bruth marcus\b|\bsteny hoyer\b|\bdebra bowen\b|\brichardson\b|\balan feuer\b|\bgreg craig\b|\bjohn dunne\b|\balok gupta\b|\bnazarbayev\b|\bharry reid\b|\bjudd gregg\b|\bjohnsonian\b|\btviagariaf\b|\bliz cheney\b|\b01-28-2010\b|\bsteve wynn\b|\bjohn major\b|\bmark hyman\b|\bamit khare\b|\bjim demint\b|\bbeknazarov\b|\btom coburn\b|\btim roemer\b|\bmehna ghai\b|\bbill burns\b|\bjon tester\b|\bali bhutto\b|\blee ferran\b|\bkathleen t\b|\balger hiss\b|\bcony blair\b|\bneugebauer\b|\btrey gowdy\b|\bjeff skoll\b|\bdick armey\b|\babdulkadir\b|\bsuly ponce\b|\beikenberry\b|\bbeth jones\b|\behud barak\b|\bwed sep 09\b|\bjohn birks\b|\bsean smith\b|\bcarl levin\b|\bamb steven\b|\bnahma kazi\b|\babdel aziz\b|\broy spence\b|\bmcchrystal\b|\brahul john\b|\bali zeidan\b|\bsarah palm\b|\bbirch bayh\b|\beric siila\b|\byussef al-\b|\bryan sorba\b|\bmatt kibbe\b|\bdick lugar\b|\balex dupuy\b|\bcunningham\b|\banne-marie\b|\btomlinsonc\b|\bcarol kahn\b|\bemin sirin\b|\bfrank rich\b|\bkevin rudd\b|\bsta i bott\b|\bharold koh\b|\bbill frist\b|\bchancellor\b|\bjohn kerry\b|\bnick clegg\b|\bpj crowley\b|\bweb, ake g\b|\bmax baucus\b|\bbob inglis\b|\bblumenthal\b|\bjan piercy\b|\bann selzer\b|\bmeg keeton\b|\bmel gibson\b|\bravij shah\b|\bgeeta pasi\b|\bglenn beck\b|\bben cardin\b|\borly taitz\b|\bkay warren\b|\bvandeboegh\b|\bousama al-\b|\bnita lowey\b|\brothschild\b|\btarun basu\b|\bdavid laws\b|\bravi gupta\b|\bmark laity\b|\botunbayeva\b|\btoni getze\b|\bdavid frum\b|\btom jensen\b|\bjohn lewis\b|\bal franken\b|\blord boyce\b|\bsusan rice\b|\bjohn birch\b|\bchris dodd\b|\bglenn back\b|\bhaim saban\b|\bmuammar al\b|\btom harkin\b|\bben nelson\b|\bjohn simon\b|\bscozzafava\b|\blimberakis\b|\btony blair\b|\bkarimullah\b|\byoussef al\b|\bjack _mite\b|\bsam dubbin\b|\bhrant dink\b|\banne marie\b|\blarry king\b|\ballen drur\b|\brich verma\b|\bgreg bloom\b|\bken merten\b|\balok mehta\b|\balmontaser\b|\bralph reed\b|\btrent lott\b|\bjacqueline\b|\bal senussi\b|\buri avnery\b|\blynn roche\b|\bjohn thune\b|\bezra pound\b|\baleitiwali\b|\bfeinstein\b|\bkissinger\b|\bmandarins\b|\bpoplawski\b|\bgonzalez,\b|\beizenstat\b|\bjim odato\b|\balexander\b|\bo'donnell\b|\btom udall\b|\bbin laden\b|\bspeckhard\b|\ball zidan\b|\bkarl marx\b|\babu salim\b|\bmccaughey\b|\bmohamoucl\b|\babushagur\b|\bmacmillan\b|\bmusharraf\b|\bkerincsiz\b|\bnancy roc\b|\bjim jones\b|\bgabrielle\b|\bchristine\b|\bdavutogiu\b|\bbob gates\b|\bdan smith\b|\bnora toiv\b|\bmagariars\b|\btekebayev\b|\bsteinberg\b|\bron wyden\b|\bnetanyahu\b|\bgorbachev\b|\bpaulo e-s\b|\bizaguirre\b|\bma gariaf\b|\bholbrooke\b|\bsteven j\.\b|\bmccaskill\b|\b\.vlassa\.d\b|\bmcpherson\b|\bvan jones\b|\bdavutoglu\b|\bjoe duffy\b|\bkachingwe\b|\bgoldwater\b|\bdipu moni\b|\bglad bill\b|\bgoldsmith\b|\bmandelson\b|\bpuchalsky\b|\bjefferson\b|\bmesadieux\b|\bpreminger\b|\bedward m\.\b|\babushagar\b|\bben yazza\b|\bhezbollah\b|\bmcconnell\b|\babu kitef\b|\bnursultan\b|\blieberman\b|\bben smith\b|\bjohn mann\b|\btoby helm\b|\byudhoyono\b|\bevan bayh\b|\bcarl chan\b|\bslaughter\b|\bgeorge w\.\b|\bayub khan\b|\bmccrystal\b|\bbollinger\b|\bal-juwali\b|\bsue brown\b|\bkarl rove\b|\bjoe biden\b|\bjoe feuer\b|\bbelizaire\b|\bat juwali\b|\bperriello\b|\bben yezza\b|\bhooverite\b|\bal juwali\b|\blou dobbs\b|\brand paul\b|\boren sega\b|\bnavin sun\b|\bali zidan\b|\bmcdonough\b|\bgary hart\b|\bpelletier\b|\bcarlton a\b|\bian kelly\b|\bpickering\b|\bdoug band\b|\bpolaschik\b|\bmalcolm x\b|\brobertson\b|\bal-wahhab\b|\batembayev\b|\bsinn fein\b|\bdayutogiu\b|\bfawzi abd\b|\bmandeison\b|\bwhitehall\b|\blzaguirre\b|\bbob dylan\b|\bel — keib\b|\barthur m\.\b|\bpatricofs\b|\bgrassley\b|\bann beck\b|\bgregory:\b|\bmiliband\b|\ba\. knopf\b|\bstiglitz\b|\bpaterson\b|\bhumphrey\b|\bbstrider\b|\bchernoff\b|\bchernick\b|\bsidereas\b|\bgregoire\b|\bpuri das\b|\bchaitkin\b|\bo'reilly\b|\blyn lusi\b|\bval moro\b|\bbob dole\b|\bj\. edgar\b|\bphilip 1\b|\bjim crow\b|\bcherubin\b|\bcampbell\b|\bthurmond\b|\bmorrisoc\b|\bmcgovern\b|\bdetvlint\b|\bcamerfin\b|\bcheryl d\b|\bcapricia\b|\bholbrook\b|\bmedvedev\b|\bmichelle\b|\bqacklafl\b|\bles gelb\b|\bqacihafi\b|\bbenyezza\b|\bgrijalva\b|\ballister\b|\bbakiyevs\b|\bduvalier\b|\bmagariaf\b|\bjohn lee\b|\bgiffbrds\b|\bthearill\b|\bfluornoy\b|\bornstein\b|\bsbwhoeof\b|\bricketts\b|\bsullivan\b|\balbright\b|\bphilippe\b|\bchaudhry\b|\bsamantha\b|\buc davis\b|\bjosefina\b|\bcladeafi\b|\bsbwhoeop\b|\bfloyd m\.\b|\brobinson\b|\bmargaret\b|\bmohammed\b|\bal-acusi\b|\btarasios\b|\bal-arusi\b|\bgeithner\b|\bs\. akbar\b|\bmagariar\b|\bdaniel b\b|\bai-arusi\b|\btritevon\b|\bzulfikar\b|\bfosnight\b|\bchi minh\b|\bgingrich\b|\bmoriarty\b|\bpetraeus\b|\babdullah\b|\bmalunoud\b|\bfeingold\b|\bibn 'abd\b|\bmccarthy\b|\bbrinkley\b|\bjonathan\b|\bjoseph e\b|\bmangoush\b|\bbelgasim\b|\blimbaugh\b|\bhuckabee\b|\bholliday\b|\blarouche\b|\bhastings\b|\bal-anisi\b|\bhamelech\b|\bkhamenei\b|\bcronkite\b|\bmonrovia\b|\bthatcher\b|\bgonzalez\b|\bsl green\b|\btarhouni\b|\btauscher\b|\bjack lew\b|\babdullab\b|\bwilders\b|\bgadhafi\b|\bwoodrow\b|\bpreines\b|\bhabedin\b|\bpascual\b|\bchemick\b|\bjo lusi\b|\bshannon\b|\bfillary\b|\bjaneway\b|\bsbwhoeo\b|\bdonilon\b|\bschmidt\b|\bcharlie\b|\bwallace\b|\bdeschle\b|\bskousen\b|\bmorales\b|\barchons\b|\bel-kelb\b|\bha\.fter\b|\bfranken\b|\bclinton\b|\blalanne\b|\bmikhail\b|\bkennedy\b|\bbelhars\b|\bvolcker\b|\bsummers\b|\bgardner\b|\bpol pot\b|\bgravers\b|\bkhalifa\b|\bshapiro\b|\bcollins\b|\bed kemp\b|\bstewart\b|\bheather\b|\bsussman\b|\bsharron\b|\bzigiarn\b|\bosborne\b|\berica 3\b|\bjackson\b|\bmelanne\b|\bbhutto'\b|\bprern g\b|\bqadhafi\b|\baxelrod\b|\bqataris\b|\bgaddafi\b|\bnanda 5\b|\bcameron\b|\bspencer\b|\bmagaref\b|\broebuck\b|\bmurdoch\b|\bclapper\b|\bbuckley\b|\banthony\b|\bziglarn\b|\bzardari\b|\bal dhan\b|\bkessler\b|\brebecca\b|\bboehner\b|\bevyenia\b|\bkrishna\b|\bstevens\b|\bal-keib\b|\bhussein\b|\bk\.ennan\b|\bqaddafi\b|\bcochran\b|\brichard\b|\bhassadi\b|\bbunning\b|\berdogan\b|\bdoherty\b|\bshoebat\b|\bmustafa\b|\bdaalder\b|\baguilar\b|\bjon kyl\b|\bbarbara\b|\bel keib\b|\bgregory\b|\bpollard\b|\bwilliam\b|\bmichael\b|\bmartino\b|\bjohnson\b|\bgoldman\b|\bmanning\b|\boehring\b|\bsaddarn\b|\binsulza\b|\bemanuel\b|\blindsey\b|\blebaron\b|\bhillary\b|\bchi!cot\b|\bcollier\b|\bmohamad\b|\bmohamed\b|\bantonio\b|\briddick\b|\bchilcot\b|\bmerkley\b|\bel-keib\b|\bmoammar\b|\bben van\b|\bbakiyev\b|\bgillani\b|\bweather\b|\bschumer\b|\bsariyev\b|\bvalerie\b|\bo'keefe\b|\bel-kieb\b|\bcrowley\b|\byitzhak\b|\bverveer\b|\bkuehner\b|\bsanders\b|\bclaudia\b|\bgeitner\b|\bsarkozy\b|\bsheldon\b|\bal-keeb\b|\babraham\b|\bpodesta\b|\bdaschle\b|\bsolomon\b|\bschultz\b|\be1-kieb\b|\bjhapour\b|\bhousing\b|\bhastert\b|\bshapira\b|\bsantoro\b|\bclyburn\b|\bbobbitt\b|\bntanden\b|\bmichele\b|\bdobbins\b|\btunisia\b|\bjarrett\b|\bbastien\b|\bbennett\b|\byounes\b|\btebbit\b|\bkarzai\b|\barturo\b|\bpowell\b|\bcorker\b|\bsaddam\b|\bwalton\b|\bgeller\b|\bsophie\b|\bortega\b|\bbarack\b|\bsusman\b|\bconrad\b|\bsodini\b|\bwerner\b|\brafter\b|\bheftar\b|\bromney\b|\bal- ai\b|\bursula\b|\bgraver\b|\bjoseph\b|\bdamour\b|\bheintz\b|\bkapoor\b|\bsherif\b|\bziglam\b|\bkramer\b|\bjibril\b|\bl\.b\.j\.\b|\bdemint\b|\bkhalid\b|\bgeorge\b|\bmelton\b|\bkennan\b|\bharris\b|\b°barna\b|\bmaddow\b|\bclaire\b|\bcornyn\b|\bhudson\b|\bbelhaj\b|\bkerman\b|\btories\b|\bphilip\b|\bbrooke\b|\bnachum\b|\bdayton\b|\brupert\b|\boba ma\b|\bpeters\b|\bchitre\b|\bmarvin\b|\bharkin\b|\bsantos\b|\bsilvia\b|\bstalin\b|\bfabius\b|\bshaban\b|\bdooley\b|\bjuarez\b|\bharich\b|\bstrobe\b|\baubrey\b|\bidriss\b|\bdobson\b|\boba\.ma\b|\bkabila\b|\bcengiz\b|\brivkin\b|\bobarna\b|\bbaucus\b|\brascon\b|\binglis\b|\bthomas\b|\bhector\b|\bparvez\b|\bhefter\b|\bjuwali\b|\bshahan\b|\bbashir\b|\bhaftar\b|\btakano\b|\bzelaya\b|\bstruwe\b|\bmerkel\b|\bmassad\b|\behrman\b|\bhoover\b|\bjuan s\b|\bcoburn\b|\bsun zi\b|\bhalter\b|\bobaxna\b|\bhitler\b|\bhilary\b|\bobam\.a\b|\btiller\b|\bmoreno\b|\bholder\b|\brobert\b|\bpelosi\b|\boxford\b|\blittle\b|\bhashem\b|\bjabril\b|\bgarcia\b|\bkristy\b|\bmendes\b|\bfaisal\b|\bmullen\b|\bfoxman\b|\bsalehi\b|\bmccain\b|\bshelby\b|\bbenson\b|\bsharif\b|\blana j\b|\bgordon\b|\blyndon\b|\bnathan\b|\balbeit\b|\bcheney\b|\bweiner\b|\bwilson\b|\bdubbin\b|\bcantor\b|\bmormon\b|\bpreval\b|\bpastor\b|\bnelson\b|\bjavits\b|\bbennet\b|\bstupak\b|\bwarner\b|\bcheryl\b|\btapper\b|\bodinga\b|\bwisner\b|\beugene\b|\bsharia\b|\bsolana\b|\balfred\b|\bguerra\b|\bmchale\b|\bandrew\b|\bannabi\b|\bcarson\b|\bhassan\b|\breagan\b|\blouise\b|\bashton\b|\bcherie\b|\broemer\b|\bfallon\b|\bdurbin\b|\bmerten\b|\bdenis\b|\bderek\b|\bkerry\b|\bjones\b|\bmills\b|\bbetsy\b|\bsauer\b|\bsousa\b|\bpiper\b|\blevin\b|\boscar\b|\bhaass\b|\bortiz\b|\bkazan\b|\bjalil\b|\bburns\b|\bgrist\b|\barutz\b|\barusi\b|\bpaige\b|\b!aura\b|\bsirin\b|\blewis\b|\bjalii\b|\bbadie\b|\bkumar\b|\bjabar\b|\bshura\b|\bpitts\b|\bsorba\b|\bosama\b|\bsteve\b|\bclegg\b|\bsarah\b|\bsmith\b|\bocher\b|\bchuck\b|\bdelay\b|\bharry\b|\bbaker\b|\bdavid\b|\bhelms\b|\bzaidi\b|\bponce\b|\bsheva\b|\bcolin\b|\babbas\b|\bgheit\b|\bchris\b|\bpeter\b|\bmarie\b|\brandy\b|\bjafil\b|\bboyce\b|\brandi\b|\bmalin\b|\bbrady\b|\bsowan\b|\bcowen\b|\bterry\b|\bscott\b|\bpatin\b|\bhenry\b|\blugar\b|\bbarna\b|\brosie\b|\bzidan\b|\bsegal\b|\bmorsi\b|\bwelch\b|\blarry\b|\bhague\b|\bnixon\b|\bluers\b|\bborwn\b|\barmey\b|\brobyn\b|\broses\b|\bhasan\b|\bgiles\b|\bcasey\b|\bzheng\b|\bgates\b|\bialil\b|\bjoyce\b|\bpeggy\b|\bwhite\b|\bmeraj\b|\btaitz\b|\bphiii\b|\bglenn\b|\bgregg\b|\budall\b|\btorat\b|\buribe\b|\bmeese\b|\bobeda\b|\bmarat\b|\blibya\b|\bstrom\b|\biqbal\b|\bhamid\b|\bmeyer\b|\bsally\b|\bhabre\b|\banton\b|\bbrown\b|\bsadie\b|\bbiden\b|\bjaill\b|\bfrank\b|\btorah\b|\brosas\b|\bnge,b\b|\brabbi\b|\bleahy\b|\bstraw\b|\bjames\b|\bshaun\b|\bangle\b|\bblair\b|\bsalon\b|\bpalin\b|\bsusan\b|\bsnowe\b|\blopez\b|\bassad\b|\broger\b|\bhamas\b|\botmar\b|\brabin\b|\bobama\b|\bputin\b|\bsingh\b|\bpipes\b|\bbecky\b|\bcretz\b|\breid\b|\baziz\b|\bnero\b|\bjill\b|\bpaul\b|\bgeed\b|\bkarl\b|\btony\b|\bnewt\b|\bsean\b|\bjohn\b|\bsade\b|\bcaro\b|\bmack\b|\bphil\b|\bqamu\b|\bbeck\b|\brush\b|\bayub\b|\blund\b|\bmani\b|\bdink\b|\bhuma\b|\beric\b|\brand\b|\bhaim\b|\bh rn\b|\bmark\b|\bjake\b|\bryan\b|\bjack\b|\bshah\b|\bburr\b|\bclay\b|\bjail\b|\belia\b|\btrig\b|\byang\b|\bpalm\b|\balec\b|\bibid\b|\bsami\b|\bmatt\b|\brauf\b|\baksu\b|\bcoup\b|\bhart\b|\bmeek\b|\brove\b|\bdede\b|\blevy\b|\bdodd\b|\bford\b|\baiwa\b|\bjeff\b|\bmike\b|\bdeby\b|\btory\b|\b9/11\b|\brice\b|\bglen\b|\bholz\b|\bkeib\b|\bgary\b|\bjose\b|\bjuan\b|\bbart\b|\bhill\b|\bnick\b|\bruss\b|\bdick\b|\bjahr\b|\bpenn\b|\brahm\b|\bagha\b|\bbill\b|\bwebb\b|\bkeit\b|\bmarc\b|\bbayh\b|\bbush\b|\blona\b|\bkay\b|\babz\b|\bstu\b|\bann\b|\bsam\b|\bpam\b|\bkyl\b|\bjfk\b|\bamr\b|\bjen\b|\bhsf\b|\bmcc\b|\bjon\b|\bliz\b|\bhbj\b|\blyn\b|\bzia\b|\bmcd\b|\bbob\b|\brob\b|\ball\b|\bdan\b|\bmao\b|\bjim\b|\bhb3\b|\bal-\b|\byan\b|\bban\b|\btom\b|\bel-\b|\bwjc\b|\bjoe\b|\bron\b|\bsby\b|\bdfm\b|\bali\b|\bmax\b|\baui\b|\bcdm\b|\bski\b|\bemb\b|\bsid\b|\bhrc\b|\bsbu\b|\bch\b|\bcb\b|\bnn\b|\bho\b|\bdp\b|\bw\.\b|\bel\b|\bdd\b|\bp3\b|\bal\b|\bmo\b|\bed\b|\btx\b|\bpj\b|\bh\b"

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
        getSpans(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+", raw_txt, "EMAIL")
    )
    allAnnotations.extend(getTimeSpans(raw_txt))
    allAnnotations.extend(getDateSpans(raw_txt))
    allAnnotations.extend(getCountrySpans(raw_txt))
    allAnnotations.extend(getStateSpans(raw_txt))
    allAnnotations.extend(getPhoneSpans(raw_txt))
    allAnnotations.extend(getNameSpans(raw_txt))

    return {"named_entity": sorted(allAnnotations, key=lambda x: x["start"])}


def simp_span(annot):
    if not annot:
        return ''
    return str(annot.get('start')) + '-' + str(annot.get('end'))

def simp_tag(annot):
    if not annot:
        return ''
    return (
        annot.get('tag') + ' ' +
        str(annot.get('properties', {}).get('ADDRESS-SUBTYPE') or '') +
        str(annot.get('properties', {}).get('DATE-TIME-SUBTYPE') or '')
    )

def arbitrate(doc, context=50, width=50):
    from rich import print
    count = 0
    canon = []
    j_annot = sorted(doc['annotations']['named_entity'], key= lambda x: x['start'])
    l_annot = sorted(doc['annotations_v2']['named_entity'], key= lambda x: x['start'])
    k_annot = getBasicAnnotations(doc.get('raw_text'))['named_entity']
    print(f"Get ready to cross check around {max(len(j_annot), len(l_annot))} docs")
    readchar()
    while j_annot and k_annot and l_annot:
        cj, ck, cl = [None, None, None]
        start = min(j_annot[0]['start'], k_annot[0]['start'], l_annot[0]['start'])
        text = doc['raw_text']
        if j_annot[0]['start'] == start:
            cj = j_annot.pop(0)
        if k_annot[0]['start'] == start:
            ck = k_annot.pop(0)
        if l_annot[0]['start'] == start:
            cl = l_annot.pop(0)
        end = (cj or ck or cl)['end']
        print(f"[red]{text[start-context:start]}[/][yellow]{text[start:end+1]}[/][red]{text[end+1:end+context]}[/]")
        print('')
        print(f"{simp_tag(cj):<50} -- {simp_tag(ck):^50} -- {simp_tag(cl):>50}")
        if cj == ck == cl:
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
        end = canon[-1]['end']
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

    if args.arbitrate:
        for doc in documents:
            # TODO: Allow option of choosing doc
            annots = arbitrate(doc)
            doc["annotations"] = {
                "named_entity": sorted(annots, key=lambda x: x["start"])
            }
        with open(args.input + '.new', "w") as json_file:
            for doc in documents:
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
