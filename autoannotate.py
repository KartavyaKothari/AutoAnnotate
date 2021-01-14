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
    gender_words = ['lord','lady','sir','maam','ma\'am','madam','he','her','she','his','him','man','woman','men','women','mr','mrs','brother','sister','wife','husband','uncle','male','female','son','daughter','father','mother', 'king', 'queen', 'himself', 'herself', 'motherhood', 'fatherhood', 'bitch', 'manhood', 'womanhood']
    
    for gender in set(gender_words):
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
    pattern = r'(((mon|tues?|wed(nes?)|thu(rs)?|fri|sat(ur)?|sun)(day)?)[.,\s]*((jan|febr?)(uary)?|mar(ch)?|apr(il)?|may|june?|july?|aug(ust)?|sept?(ember)?|oct(ober)?|nov(ember)?|dec(ember)?)[.,\s]?((0[1-9]|[12]\d|3[01])|([1-9]|[12]\d|3[01]))[.,\s]*[12][0-9]{3})|(((mon|tues?|wed(nes?)|thu(rs)?|fri|sat(ur)?|sun)(day)?)[.,\s]*((jan|febr?)(uary)?|mar(ch)?|apr(il)?|may|june?|july?|aug(ust)?|sept?(ember)?|oct(ober)?|nov(ember)?|dec(ember)?)[.,\s]?((0[1-9]|[12]\d|3[01])|([1-9]|[12]\d|3[01])))|((jan|febr?)(uary)?|mar(ch)?|apr(il)?|may|june?|july?|aug(ust)?|sept?(ember)?|oct(ober)?|nov(ember)?|dec(ember)?)[.,\s]*[12][0-9]{3}|(19|20)\d{2}'
    indexes = [(i.start(),i.end()) for i in re.finditer(pattern,raw_txt,flags=re.IGNORECASE)]
    for t in indexes:
        ne = {"properties":{"DATE-TIME-SUBTYPE":"DATE"}}
        ne["start"] = t[0]
        ne["end"] = t[1]
        ne["tag"] = "DATE-TIME"
        ne["extent"] = raw_txt[t[0]:t[1]]
        spans.append(ne)
    return spans

def getYearRangeSpans(raw_txt):
    spans = []
    pattern = r'((19|20)\d{2})\s*((to)|-|(and))\s*((19|20)\d{2})'
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
    list_countries = [r'\bAfghanistan\b',r'\bAlbania\b',r'\bAlgeria\b',r'\bAndorra\b',r'\bAngola\b',r'\bAntigua\s&\sDeps\b',r'\bArgentina\b',r'\bArmenia\b',r'\bAustralia\b',r'\bAustria\b',r'\bAzerbaijan\b',r'\bBahamas\b',r'\bBahrain\b',r'\bBangladesh\b',r'\bBarbados\b',r'\bBelarus\b',r'\bBelgium\b',r'\bBelize\b',r'\bBenin\b',r'\bBhutan\b',r'\bBolivia\b',r'\bBosnia\sHerzegovina\b',r'\bBotswana\b',r'\bBrazil\b',r'\bbritain\b',r'\bBrunei\b',r'\bBulgaria\b',r'\bBurkina\b',r'\bBurundi\b',r'\bCambodia\b',r'\bCameroon\b',r'\bCanada\b',r'\bCape\sVerde\b',r'\bCentral\sAfrican\sRep\b',r'\bChad\b',r'\bChile\b',r'\bChina\b',r'\bColombia\b',r'\bComoros\b',r'\bCongo\b',r'\bCongo\b',r'\bCosta\sRica\b',r'\bCroatia\b',r'\bCuba\b',r'\bCyprus\b',r'\bCzech\sRepublic\b',r'\bDenmark\b',r'\bDjibouti\b',r'\bDominica\b',r'\bDominican\sRepublic\b',r'\bEast\sTimor\b',r'\bEcuador\b',r'\bEgypt\b',r'\bEl\sSalvador\b',r'\bEquatorial\sGuinea\b',r'\bEritrea\b',r'\bEstonia\b',r'\bEthiopia\b',r'\bFiji\b',r'\bFinland\b',r'\bFrance\b',r'\bGabon\b',r'\bGambia\b',r'\bGeorgia\b',r'\bGermany\b',r'\bGhana\b',r'\bGreece\b',r'\bGrenada\b',r'\bGuatemala\b',r'\bGuinea\b',r'\bGuinea-Bissau\b',r'\bGuyana\b',r'\bHaiti\b',r'\bHonduras\b',r'\bHungary\b',r'\bIceland\b',r'\bIndia\b',r'\bIndonesia\b',r'\bIran\b',r'\bIraq\b',r'\bIreland\b',r'\bIsrael\b',r'\bItaly\b',r'\bIvory\sCoast\b',r'\bJamaica\b',r'\bJapan\b',r'\bJordan\b',r'\bKazakhstan\b',r'\bKenya\b',r'\bKiribati\b',r'\bKorea\sNorth\b',r'\bKorea\sSouth\b',r'\bKosovo\b',r'\bKuwait\b',r'\bKyrgyzstan\b',r'\bLaos\b',r'\bLatvia\b',r'\bLebanon\b',r'\bLesotho\b',r'\bLiberia\b',r'\bLibya\b',r'\bLiechtenstein\b',r'\bLithuania\b',r'\bLuxembourg\b',r'\bMacedonia\b',r'\bMadagascar\b',r'\bMalawi\b',r'\bMalaysia\b',r'\bMaldives\b',r'\bMali\b',r'\bMalta\b',r'\bMarshall\sIslands\b',r'\bMauritania\b',r'\bMauritius\b',r'\bMexico\b',r'\bMicronesia\b',r'\bMoldova\b',r'\bMonaco\b',r'\bMongolia\b',r'\bMontenegro\b',r'\bMorocco\b',r'\bMozambique\b',r'\bMyanmar\b',r'\bNamibia\b',r'\bNauru\b',r'\bNepal\b',r'\bNetherlands\b',r'\bNew\sZealand\b',r'\bNicaragua\b',r'\bNiger\b',r'\bNigeria\b',r'\bNorway\b',r'\bOman\b',r'\bPakistan\b',r'\bPalau\b',r'\bPanama\b',r'\bPapua\sNew\sGuinea\b',r'\bParaguay\b',r'\bPeru\b',r'\bPhilippines\b',r'\bPoland\b',r'\bPortugal\b',r'\bQatar\b',r'\bRomania\b',r'\bRussian\sFederation\b',r'\bRwanda\b',r'\bSt\sKitts\s&\sNevis\b',r'\bSt\sLucia\b',r'\bSaint\sVincent\s&\sthe\sGrenadines\b',r'\bSamoa\b',r'\bSan\sMarino\b',r'\bSao\sTome\s&\sPrincipe\b',r'\bSaudi\sArabia\b',r'\bSenegal\b',r'\bSerbia\b',r'\bSeychelles\b',r'\bSierra\sLeone\b',r'\bSingapore\b',r'\bSlovakia\b',r'\bSlovenia\b',r'\bSolomon\sIslands\b',r'\bSomalia\b',r'\bSouth\sAfrica\b',r'\bSouth\sSudan\b',r'\bSpain\b',r'\bSri\sLanka\b',r'\bSudan\b',r'\bSuriname\b',r'\bSwaziland\b',r'\bSweden\b',r'\bSwitzerland\b',r'\bSyria\b',r'\bTaiwan\b',r'\bTajikistan\b',r'\bTanzania\b',r'\bThailand\b',r'\bTogo\b',r'\bTonga\b',r'\bTrinidad\s&\sTobago\b',r'\bTunisia\b',r'\bTurkey\b',r'\bTurkmenistan\b',r'\bTuvalu\b',r'\bUganda\b',r'\bUkraine\b',r'\bUnited\sArab\sEmirates\b',r'\bU\.?A\.?E\.?\b',r'\bUnited\sKingdom\b',r'\bU\.?K\.?\b',r'\bUnited\sStates\b',r'\bu[\s.]*s\.?\b',r'\bUruguay\b',r'\bUzbekistan\b',r'\bVanuatu\b',r'\bVatican\sCity\b',r'\bVenezuela\b',r'\bVietnam\b',r'\bYemen\b',r'\bZambia\b',r'\bZimbabwe\b']

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

def getPhoneSpans(raw_txt):
    spans = []
    pattern = r'\d(\.|\s*|\-)\d(\.|\s*|\-)\d(\.|\s*|\-)\d(\.|\s*|\-)\d(\.|\s*|\-)\d(\.|\s*|\-)\d(\.|\s*|\-)\d(\.|\s*|\-)\d(\.|\s*|\-)\d(\.|\s*|\-)'
    indexes = [(i.start(),i.end()) for i in re.finditer(pattern,raw_txt,flags=re.IGNORECASE)]
    for t in indexes:
        ne = {}
        ne["start"] = t[0]
        ne["end"] = t[1]
        ne["tag"] = "PHONE"
        ne["extent"] = raw_txt[t[0]:t[1]]
        spans.append(ne)
    return spans

def getNameSpans(raw_txt):
    spans = []
    pattern = r"\bshaykh al islam mohammed ibn 'abd al-wahhab al-tanaimi\b|\babdullah bin abdulaziz al-sa'ud\b|\bthomas-greenfield, linda(ms)\b|\baustin-ferguson, kathleen t\b|\bmohammed yussef el magariaf\b|\babdel hakim alamin belhaj\b|\bassuncao afonso dos anjos\b|\breverend deacon nektarios\b|\bmabrouk issa abu harroura\b|\bpatriarch mesrop mutafyan\b|\bsail al-islam al-qadhafi\b|\bshaykh al islam mohammed\b|\bjones-johnson, carolyn d\b|\bthomas-greenfield, linda\b|\bcardinal joachim meisner\b|\babd al-wahhab al-tamimi\b|\bpatriarch bartholomew i\b|\bhrod17@clintonemail.com\b|\bdaniel patrick moynihan\b|\bkhalifa belqasim haftar\b|\bkhalifa belqasim hefter\b|\bpatriarch, bartholomew\b|\bmartin luther king jr.\b|\bpatriarch bartholomeos\b|\bbernier-toth, michelle\b|\bbarks-ruggles, erica 3\b|\btomlinson, christina b\b|\bhillary rodham clinton\b|\bmohamed hosni mubarak\b|\bgillis, christopher 3\b|\bslaughter, anne-marie\b|\bjean-robert lafortune\b|\bmalin, mary catherine\b|\bfitzgerald, william e\b|\bpatriarch vartholomew\b|\bjane dammen mcauliffe\b|\bpatriarch bartholomew\b|\balexis de tocqueville\b|\bsaif al-islam qaddafi\b|\babd al-nasser shamata\b|\babdulrahman ben yezza\b|\banthony j. limberakis\b|\bmustafa kemal ataturk\b|\bsolirnan abd al-qadr\b|\bcrocker, bathsheba n\b|\brecep tayyip erdogan\b|\bjacqueline novogratz\b|\bstephanie l. hallett\b|\bkennedy, j christian\b|\banne-marie slaughter\b|\bdr. allan e. goodman\b|\bdavid m, satterfield\b|\bkreab gavin anderson\b|\bklevorick, caitlin b\b|\babdel rahman el-keib\b|\bhallett, stephanie l\b|\bnelson w. cunningham\b|\bdwight d. eisenhower\b|\brandolph, lawrence m\b|\bantonios trakatellis\b|\btomlinson, christina\b|\bsamuelson, heather f\b|\bjames r. stoner, jr.\b|\bcie re m ccaski i i\b|\bmuhammad al-gharabi\b|\byoussef al mangoush\b|\bdibble, elizabeth l\b|\bmuaimnar al qaddafi\b|\bhi i i ay ci i nton\b|\byu.ssef el magariaf\b|\bmcdonough, denis r.\b|\bstevens mitt romnev\b|\bjean-louis warnholz\b|\bmcauliffe, marisa s\b|\bchristopher stevens\b|\bmustafa abdel jalil\b|\bgeoffroy, gregory l\b|\brodriguez, miguel e\b|\bchristina tomlinson\b|\bfeltrnan, jeffrey d\b|\bschlicher, ronald l\b|\bousetrill al juwaii\b|\baf-fo-principals-dl\b|\bmceldowney, nancy e\b|\babdurrahim el keib\b|\bbenjamin netanyahu\b|\bfielder, rebecca a\b|\bsheldon whitehouse\b|\bslobodan milosevie\b|\bschwerin, daniel b\b|\banthony limberakis\b|\babdulaziz al-sasud\b|\breines, philippe i\b|\banderson, brooke d\b|\bgilmore, kristin m\b|\bmuammar at qaddafi\b|\bmaxwell, raymond d\b|\bfranklin roosevelt\b|\bmuhammad al-zahawi\b|\bmohammed yussef el\b|\bjacqueline charles\b|\blakhdhir, kamala s\b|\bmustafa abdel jail\b|\br. donahue peebles\b|\broebuck, william v\b|\bfinley peter dunne\b|\babdullah bin zayed\b|\brobinson, brooks a\b|\bshapiro, andrew .3\b|\bmustafa abdul jail\b|\bbrooks a. robinson\b|\bnuland, victoria 3\b|\bverveer, melanne s\b|\bmohamed al-qadhafi\b|\bsanderson, janet a\b|\bmuammar al qaddafi\b|\bkennedy, patrick f\b|\bharris, jennifer m\b|\babdurrahim el-keib\b|\bahmed abu khattala\b|\bmaier, christina a\b|\babdelfattah younes\b|\bfeltman, jeffrey d\b|\bverveer, melanne 5\b|\babdulbari al-arusi\b|\bsullivan, jacob .1\b|\brichardson, eric n\b|\bmacmanus, joseph e\b|\barturo valenzuela\b|\bcampbell, piper a\b|\bhormats, robert d\b|\bgeorge h. w. bush\b|\babdelhakim belhaj\b|\bchristopher meyer\b|\blvlills, cheryl d\b|\bterrence a. duffy\b|\bsullivan, jacob 3\b|\bdavid klinghoffer\b|\bsullivan, jacob j\b|\bmustafa abdul jai\b|\bshapiro, daniel b\b|\bcoleman, claire l\b|\bmohammed al-sissi\b|\bsullivan, jacob i\b|\bcaitlin klevorick\b|\bousama al jouwali\b|\bwilliam fulbright\b|\bdavid j. rothkopf\b|\bstephanie browner\b|\bfriedrich, mary k\b|\bsullivan, jacob 1\b|\bsidney blumenthal\b|\bshannon, thomas a\b|\bmuammar al qaddaf\b|\bmartin mcguinness\b|\bmargaret thatcher\b|\blaszczych, joanne\b|\bpolaschlk, joan a\b|\bdonilon, thomas e\b|\brussell, daniel a\b|\bjeremy greenstock\b|\bkoutsis, steven c\b|\bjamjoom, kareem n\b|\bricardo seitenfus\b|\bcaspar weinberger\b|\bjeannemarie smith\b|\brandolph mcgrorty\b|\bhoward metzenbaum\b|\bohtagaki, johna 0\b|\bcurtis, meghann a\b|\badolph a. weinman\b|\beizenstat, stuart\b|\bfrancisco sanchez\b|\bcoleman, claire i\b|\bjeffrey donaldson\b|\bobeidah al-jarrah\b|\bburns, william .1\b|\bsidereas, evyenla\b|\bthomas jefferson\b|\badam parkhomenko\b|\bjames earl jones\b|\blawrence summers\b|\bmohammed rvlorsi\b|\bgeorge voinovich\b|\bmchale, judith a\b|\bjacobs, janice l\b|\bclaire mccaskill\b|\bwalsh, matthew p\b|\brobert g. kaiser\b|\bsherman, wendy r\b|\bmohamed magariaf\b|\bhanley, monica r\b|\bburns, william j\b|\bbarbara retzlaff\b|\bsusan col i i ns\b|\babbaszadeh, myna\b|\bmitchell, george\b|\bburns, william 3\b|\bjiloty, lauren c\b|\baxelrod, david m\b|\bharry mcpherson,\b|\bhamad bin jassim\b|\bchollet, derek h\b|\bsullivan, jacobi\b|\btimothy geithner\b|\bvartan gregorian\b|\bschrepel, dawn m\b|\bmatthew g. olsen\b|\bradovan karad2ie\b|\bjohnson, brock a\b|\bousama at juwali\b|\bdianne feinstein\b|\brichard viguerie\b|\bsullivan, jacobj\b|\babbaszadeh, nima\b|\bdeborah mccarthy\b|\bnicholas sarkozy\b|\btiseke kasambala\b|\bcharles grassley\b|\balexey druzhinin\b|\bfeltman, jeffrey\b|\bwilliam s. white\b|\bgordon, philip h\b|\bpatriarch mesrop\b|\bkirby, michael d\b|\belmira ibraimova\b|\bchristopher dodd\b|\bbader, jeffrey a\b|\bdavid n. merrill\b|\bverma, richard r\b|\bnuiand, victoria\b|\bcatlin m. hayden\b|\bmolly montgomery\b|\bolson, richard g\b|\bansar al-shariah\b|\belizabeth bagley\b|\brussel, daniel r\b|\balford, edward m\b|\bcharles schumer\b|\bharold w geissl\b|\bandrew sullivan\b|\babdullah shamia\b|\bnides, thomas r\b|\bcharge robinson\b|\beugene mccarthy\b|\bbasher al assad\b|\bsufyan ben qumu\b|\bmargaret scobey\b|\bdimitris reppas\b|\baustan goolsbee\b|\bgeorge mitchell\b|\bmuammar gaddafi\b|\bmichael janeway\b|\banthony campolo\b|\bbashir al-kubty\b|\brobert menendez\b|\bhubert humphrey\b|\brichard cordray\b|\bansar al sharia\b|\bcoleman, claire\b|\bsullivan, jacob\b|\bbelqasim haftar\b|\bpolt, michael c\b|\bhoney alexander\b|\bmesrop mutafyan\b|\bwalker, peggy j\b|\bgeorge mcgovern\b|\bjoseph mccarthy\b|\bmark carruthers\b|\bmills, cheryl d\b|\beverett dirksen\b|\bmaggie williams\b|\bomar al i3ashir\b|\bvalmoro, lona j\b|\bcline, dwayne l\b|\blouis b. susman\b|\bjohn f. kennedy\b|\byigal schleifer\b|\bnancy kachingwe\b|\blamar alexander\b|\byousef mangoush\b|\bnorman ornstein\b|\bsad.dam hussein\b|\bharry mcpherson\b|\brhoda margesson\b|\bjason straziuso\b|\bstevens, john c\b|\bmichael m ullen\b|\b°same al juwali\b|\bdonald rumsfeld\b|\bbond, michele t\b|\bosama al-juwali\b|\bchristina romer\b|\brusso, robert v\b|\bsutphin, paul r\b|\bmuammar qaddafi\b|\bdaniel benjamin\b|\bteddy roosevelt\b|\bmiller, james n\b|\broza otunbayeva\b|\bcarson, johnnie\b|\bdebbie stabenow\b|\babdulkadir aksu\b|\bkemal kerincsiz\b|\bmohamed bujenah\b|\bfogarty, daniel\b|\bwalid al-sakran\b|\bfawzi abu kitef\b|\bmitch mcconnell\b|\bbondy, steven c\b|\bmahmoud _fibril\b|\bhillarv clinton\b|\bmuammar qadhafi\b|\bj. edgar hoover\b|\bbrooks robinson\b|\bedwin a. walker\b|\bmills, cheryl 0\b|\bblanche lincoln\b|\baustin-ferguson\b|\bhillary clinton\b|\bchas w. freeman\b|\bhanky, monica r\b|\bvalmoro, lona 1\b|\bdenis mcdonough\b|\bjohn c. calhoun\b|\bsufian bin qamu\b|\bcilia kerfuffie\b|\bjoseph stiglitz\b|\bhillary, cheryl\b|\bdwayne l. cline\b|\bdavid schaecter\b|\bcharlie palmer\b|\bdanielle brian\b|\bsaddam hussein\b|\bshaun woodward\b|\bsadaam hussein\b|\bwalter mondale\b|\bscarlis, basil\b|\bkarla rubinger\b|\bchuck grassley\b|\bjohna ohtagaki\b|\balbert r. hunt\b|\bdavid petraeus\b|\bwilliam ehrman\b|\bsadiq al-mahdi\b|\bmahmoud fibril\b|\bdaniel, joshua\b|\blyndon johnson\b|\bosama biniadin\b|\bpark, pamela p\b|\blinda mcfadyen\b|\bgaylord nelson\b|\bsaud al-faisal\b|\bdavid domenici\b|\bdonald ritchie\b|\bdaniel webster\b|\bsa-igha rat mi\b|\bellen tauscher\b|\botto preminger\b|\bbarholomeos ii\b|\brobert a. caro\b|\brebecca struwe\b|\bharris, rian h\b|\bnorman borlaug\b|\bcharles rangel\b|\bmaura connelly\b|\bcarlos pascual\b|\bnuni berrusien\b|\bhassan ziglarn\b|\bismail sallabi\b|\bross, dennis b\b|\bpiper campbell\b|\bkenneth merten\b|\bstuart smalley\b|\bpatricia lynch\b|\bsid blumenthal\b|\bamax al sharia\b|\bstrobe talbott\b|\bwoodrow wilson\b|\bbernie sanders\b|\barvizu, alex a\b|\bmahmoud jibril\b|\bdavies, glyn t\b|\brichard condon\b|\bdavid miliband\b|\bomar al bashir\b|\bpeter robinson\b|\bjames s rogers\b|\brichard shelby\b|\bosama binladin\b|\bthomas shannon\b|\bsusilo bambang\b|\bjanysh bakiyev\b|\bdavid rothkopf\b|\bgeorge osborne\b|\bholtz, greta c\b|\bbrooke shearer\b|\bgoodman, allan\b|\bmohammed morsi\b|\bmary catherine\b|\bwells, alice g\b|\bbenaim, daniel\b|\bwood, robert a\b|\bhickey, mary e\b|\bjames eastland\b|\blindsey graham\b|\bs cheryl mills\b|\bgeorge w. bush\b|\bgloria steinem\b|\bgeorge schultz\b|\bhenry mcdonald\b|\bahmad bukatela\b|\bnina fedoroff,\b|\balcee hastings\b|\bherbert hoover\b|\bandrea santoro\b|\bmichael bennet\b|\bturk, david m\b|\bgeorge shultz\b|\bhassan ziglam\b|\bharry hopkins\b|\babedin, hurna\b|\brahi rn faiez\b|\bjames madison\b|\bjake.sullivan\b|\bpeter martino\b|\bsalah bishari\b|\bcretz, gene a\b|\btina flournoy\b|\bjake.sulliyan\b|\bmiriam sapiro\b|\botmar oehring\b|\bmalcolm smith\b|\btilmann geske\b|\brichard levin\b|\btaher sherkaz\b|\brichard lugar\b|\bmary spanger,\b|\bkendrick meek\b|\bglen doherty,\b|\bnina fedoroff\b|\bstilin, jacob\b|\bshaw d. janes\b|\brush limbaugh\b|\bwolff, alex d\b|\bsusan collins\b|\bjones, beth e\b|\bjoseph duffey\b|\bolympia snowe\b|\bjake sullivan\b|\bbecky fielder\b|\bbigalke 'karl\b|\bforman, james\b|\bsalim .nabous\b|\bdavid skorton\b|\bamy klobuchar\b|\bgeorge ketman\b|\bsimon johnson\b|\bdavid cameron\b|\bjudy trabulsi\b|\blauren joloty\b|\bmills, cheryl\b|\brooney, megan\b|\bchris stevens\b|\bjustin cooper\b|\bhale, david m\b|\bderek chollet\b|\bjudith mchale\b|\bchuck schumer\b|\bkhushali shah\b|\blael brainard\b|\bmartha johnso\b|\bburns strider\b|\babd al-wahhab\b|\bsherrod brown\b|\brice, susan e\b|\bwilliam cohen\b|\bgeorge kennan\b|\blauren jiloty\b|\bmevlut kurban\b|\bfawzi abd all\b|\bwailes, jacob\b|\bjoe lieberman\b|\ballan goodman\b|\bdavid axelrod\b|\bcarlotta gall\b|\bhissene habre\b|\bbartholomew i\b|\bwolfgang hade\b|\brobert wexler\b|\bjames clapper\b|\bnicholas gage\b|\bbarks-ruggles\b|\bmohamed hosni\b|\bmohammed swan\b|\bclifford levy\b|\bdenis mukwege\b|\bmargery eagan\b|\bronald reagan\b|\bgeorge packer\b|\bedmund muskie\b|\b'cheryl.mills\b|\brachel maddow\b|\bsam brownback\b|\btillman geske\b|\bnewt gingrich\b|\barlen specter\b|\bmull, stephen\b|\bhenry jackson\b|\bandrew mayock\b|\bperla, laura\b|\bursula burns\b|\bmark lippert\b|\bblair, oni k\b|\brichard mays\b|\bjames salley\b|\bjulien behal\b|\babedin, huma\b|\bsally osberg\b|\bsharon hardy\b|\bsarah binder\b|\bcolin powell\b|\bjohn boehner\b|\bdavid vitter\b|\babd al-jalil\b|\bsam brinkley\b|\brudman, mara\b|\babu harroura\b|\bpaul vallely\b|\brahm emanuel\b|\bjoseph biden\b|\btalwar, pune\b|\btoiv, nora f\b|\blinda katehi\b|\babu khattala\b|\bpaul volcker\b|\bpaul collier\b|\bsachar, alon\b|\bandrew frank\b|\bbenedict xvi\b|\bjacob javits\b|\bfarej darssi\b|\bp.j. crowley\b|\bcooper udall\b|\bhoward baker\b|\bkelly, ian c\b|\bhuma abed in\b|\bbekir ozturk\b|\bminint fawzi\b|\bpenn rhodeen\b|\btsou, leslie\b|\blesley clark\b|\bcheryl mills\b|\bisaac alaton\b|\bgotoh, kay e\b|\bcheryl.millf\b|\bjim allister\b|\brobert gates\b|\bhakan tastan\b|\bjeff merkley\b|\bmary spanger\b|\bsean wilentz\b|\bugur ya%ksel\b|\bkatie glueck\b|\bbrandon webb\b|\bcheryl.mills\b|\bpeggy walker\b|\bmcleod, mary\b|\bdan restrepo\b|\bjoe macmanus\b|\bjohn jenkins\b|\bheidi annabi\b|\bbecker, john\b|\bjohn chilcot\b|\bgracien jean\b|\bglen doherty\b|\btong, kurt w\b|\babd al jalil\b|\bbab al-aziza\b|\bdaniel akaka\b|\bjudas priest\b|\blebron james\b|\brobert welch\b|\bsmith bagley\b|\bmohamoud (t)\b|\bgordon brown\b|\babedin, hume\b|\bandrew cuomo\b|\bchas freeman\b|\blisa bardack\b|\bduffy, terry\b|\bpierre-louis\b|\bcherie blair\b|\bbarack obama\b|\bjohn paul ii\b|\btesone, mark\b|\bdonna bryson\b|\blouis susman\b|\bnecati aydin\b|\btony campolo\b|\bpeter orszag\b|\bminyon moore\b|\bmel martinez\b|\belizabeth ii\b|\babdullah bin\b|\braila odinga\b|\bbetsy bassan\b|\bali tarhouni\b|\bfrank church\b|\bjames warren\b|\bjeff feltman\b|\babedln, hume\b|\bbill clinton\b|\bneera tanden\b|\bfrank munger\b|\blona valmoro\b|\bnachum segal\b|\bkarl semacik\b|\bdesk rebecca\b|\btim geithner\b|\brobert blake\b|\bgerry adams\b|\bdean debnam\b|\borhan kemal\b|\bernie banks\b|\bhma abedine\b|\braieev syai\b|\bkent conrad\b|\bruth marcus\b|\boman shahan\b|\bjohn mccain\b|\bugur yuksel\b|\bjesse helms\b|\bban ki moon\b|\bpat kennedy\b|\bsam pitroda\b|\bdaniel gros\b|\blohman, lee\b|\brich greene\b|\bira shapiro\b|\bmike dewine\b|\bhuma abedin\b|\banne wexler\b|\bkim, yuri j\b|\bross wilson\b|\balbert hunt\b|\bmary pipher\b|\bban ki-moon\b|\bjustin blum\b|\bwayne morse\b|\bgeorge bush\b|\bjohn sexton\b|\bal-mangoush\b|\bidriss deby\b|\btocqueville\b|\bemma ezeazu\b|\bbartholomew\b|\bjohn breaux\b|\bsteny hoyer\b|\blinda dewan\b|\bcraig kelly\b|\bmason, whit\b|\bjuan carlos\b|\bklinghoffer\b|\bted kennedy\b|\bellen barry\b|\bfloyd flake\b|\btom donilon\b|\bgrey wolves\b|\bpeter boone\b|\bbrian cowen\b|\babdulrahman\b|\brobert byrd\b|\babu-shakour\b|\brene preval\b|\bvalmoro, b6\b|\bjim kennedy\b|\bdick durbin\b|\bjim bunning\b|\bamb stevens\b|\bkelli adams\b|\bchris smith\b|\bcheryl.mill\b|\btom daschle\b|\blaura lucas\b|\bhugo chavez\b|\bturan topal\b|\bsyed, zia s\b|\bkim, sung y\b|\bmark warner\b|\bwahliabis-m\b|\bmax baucus\b|\bwed sep 09\b|\bdick lugar\b|\bmark hyman\b|\bsteve wynn\b|\bbill burns\b|\bjudd gregg\b|\byoussef al\b|\bali zeidan\b|\bjim demint\b|\bkathleen t\b|\bjohn thune\b|\bbeknazarov\b|\bemin sirin\b|\blee ferran\b|\bjohnsonian\b|\bcony blair\b|\bgreg craig\b|\brich verma\b|\bkay warren\b|\btrent lott\b|\banne marie\b|\bjohn kerry\b|\bchancellor\b|\bpj crowley\b|\bal senussi\b|\babdulkadir\b|\bchris dodd\b|\bjon tester\b|\bamb steven\b|\btom jensen\b|\bbeth jones\b|\bhrant dink\b|\botunbayeva\b|\bken merten\b|\brichardson\b|\bben cardin\b|\bcunningham\b|\bjan piercy\b|\bjeff skoll\b|\blimberakis\b|\btomlinsonc\b|\bsta i bott\b|\banne-marie\b|\btom harkin\b|\bsusan rice\b|\ballen drur\b|\bjacqueline\b|\bcarl levin\b|\bharry reid\b|\bglenn beck\b|\bnita lowey\b|\bnazarbayev\b|\bbill frist\b|\bsean smith\b|\bjohn major\b|\bbirch bayh\b|\babdel aziz\b|\btviagariaf\b|\bben nelson\b|\broy spence\b|\bann selzer\b|\bweb, ake g\b|\bsam dubbin\b|\baleitiwali\b|\bnick clegg\b|\btony blair\b|\byussef al-\b|\bharold koh\b|\btom coburn\b|\bal franken\b|\bsteinberg\b|\bpreminger\b|\bjoe biden\b|\ball zidan\b|\bevan bayh\b|\bmacmillan\b|\babu salim\b|\bdoug band\b|\bhezbollah\b|\bgary hart\b|\bkerincsiz\b|\bnancy roc\b|\balexander\b|\bspeckhard\b|\bal-juwali\b|\bmagariars\b|\bbelizaire\b|\bjim jones\b|\bpolaschik\b|\babu kitef\b|\bjoe feuer\b|\bmccaskill\b|\bel — keib\b|\bma gariaf\b|\bmcconnell\b|\bdan smith\b|\babushagar\b|\bron wyden\b|\bjoe duffy\b|\bat juwali\b|\bmesadieux\b|\bian kelly\b|\beizenstat\b|\btom udall\b|\bkachingwe\b|\bsinn fein\b|\babushagur\b|\bben yezza\b|\bdavutogiu\b|\bholbrooke\b|\bal juwali\b|\blieberman\b|\btoby helm\b|\batembayev\b|\bnursultan\b|\bnora toiv\b|\bfeinstein\b|\bnetanyahu\b|\bgoldsmith\b|\bben smith\b|\byudhoyono\b|\bpatricofs\b|\bben yazza\b|\bmcpherson\b|\bkarl rove\b|\bmohamoucl\b|\bdavutoglu\b|\bali zidan\b|\bjim odato\b|\bglad bill\b|\btekebayev\b|\bal-wahhab\b|\bdayutogiu\b|\bhooverite\b|\bcronkite\b|\bcheryl d\b|\bmagariar\b|\bmagariaf\b|\bal-arusi\b|\bduvalier\b|\bholliday\b|\bsidereas\b|\babdullab\b|\bcherubin\b|\bqacihafi\b|\btarasios\b|\bmonrovia\b|\bgingrich\b|\bfeingold\b|\btauscher\b|\bann beck\b|\bcapricia\b|\bsl green\b|\bbenyezza\b|\bmalunoud\b|\bcamerfin\b|\bmargaret\b|\bhumphrey\b|\bpetraeus\b|\babdullah\b|\bsullivan\b|\bbob dole\b|\bhastings\b|\btritevon\b|\ballister\b|\bmedvedev\b|\bthearill\b|\bgrassley\b|\bsbwhoeop\b|\bval moro\b|\bcladeafi\b|\bbakiyevs\b|\bthatcher\b|\bmccarthy\b|\bdaniel b\b|\bai-arusi\b|\bal-acusi\b|\bbrinkley\b|\bornstein\b|\bsamantha\b|\bmangoush\b|\bfosnight\b|\brobinson\b|\blyn lusi\b|\bgeithner\b|\bmcgovern\b|\bfloyd m.\b|\bal-anisi\b|\bmichelle\b|\bmorrisoc\b|\bjack lew\b|\bjoseph e\b|\btarhouni\b|\buc davis\b|\bbstrider\b|\bpaterson\b|\bphilippe\b|\bibn 'abd\b|\bstiglitz\b|\bfluornoy\b|\bskousen\b|\bmichael\b|\berdogan\b|\bel-kelb\b|\bel-kieb\b|\bel-keib\b|\bkhalifa\b|\bstevens\b|\bmoammar\b|\bdaalder\b|\bpodesta\b|\bmagaref\b|\bsanders\b|\brichard\b|\bhastert\b|\berica 3\b|\blindsey\b|\bmerkley\b|\bsussman\b|\bal-keib\b|\bkessler\b|\boehring\b|\bweather\b|\bosborne\b|\bbarbara\b|\bbastien\b|\bsariyev\b|\broebuck\b|\bsummers\b|\bdeschle\b|\bjo lusi\b|\brebecca\b|\bemanuel\b|\bjaneway\b|\bschumer\b|\bbakiyev\b|\briddick\b|\bchilcot\b|\bal dhan\b|\bcochran\b|\bcollins\b|\bdoherty\b|\bheather\b|\bqaddafi\b|\bvolcker\b|\bmichele\b|\bstewart\b|\bcrowley\b|\bclinton\b|\bjon kyl\b|\bmustafa\b|\bgardner\b|\bverveer\b|\bclapper\b|\bkennedy\b|\bgadhafi\b|\bal-keeb\b|\bk.ennan\b|\bpreines\b|\bshannon\b|\bboehner\b|\bgaddafi\b|\bqadhafi\b|\btunisia\b|\bfillary\b|\bschultz\b|\bsantoro\b|\bmelanne\b|\baxelrod\b|\bntanden\b|\bdonilon\b|\bprern g\b|\bbelhars\b|\bfranken\b|\bevyenia\b|\barchons\b|\bshapiro\b|\bel keib\b|\bmohamed\b|\bhousing\b|\bhillary\b|\bhabedin\b|\binsulza\b|\bqataris\b|\blebaron\b|\be1-kieb\b|\bcameron\b|\bhassadi\b|\bbunning\b|\bgeitner\b|\bjackson\b|\bben van\b|\bjohnson\b|\bpascual\b|\bdaschle\b|\bmorales\b|\blalanne\b|\bbelhaj\b|\bdemint\b|\bgordon\b|\bidriss\b|\bshaban\b|\bandrew\b|\bobarna\b|\bromney\b|\byounes\b|\btapper\b|\bbashir\b|\bbaucus\b|\boxford\b|\bmerkel\b|\bsherif\b|\bnelson\b|\bwarner\b|\breagan\b|\bstruwe\b|\bbennet\b|\bmerten\b|\bcoburn\b|\broemer\b|\bsharif\b|\bhoover\b|\bharkin\b|\bcorker\b|\bcheryl\b|\bziglam\b|\bconrad\b|\bcherie\b|\bobaxna\b|\bpastor\b|\beugene\b|\bkristy\b|\bannabi\b|\bbrooke\b|\bbarack\b|\bmaddow\b|\bwilson\b|\bursula\b|\bdubbin\b|\bclaire\b|\blana j\b|\barturo\b|\bfabius\b|\bgeorge\b|\bcornyn\b|\bodinga\b|\bdurbin\b|\behrman\b|\bshahan\b|\bhashem\b|\bshelby\b|\bphilip\b|\bl.b.j.\b|\bzelaya\b|\bhefter\b|\bstrobe\b|\bpreval\b|\bsophie\b|\bsaddam\b|\bal- ai\b|\blittle\b|\bwerner\b|\bcengiz\b|\bkabila\b|\bheftar\b|\bmullen\b|\bnathan\b|\bhector\b|\bjavits\b|\bjibril\b|\bnachum\b|\bsusman\b|\brivkin\b|\bholder\b|\bhilary\b|\bfaisal\b|\bhitler\b|\bmccain\b|\bhaftar\b|\bkerman\b|\bdooley\b|\bkennan\b|\brosie\b|\bsally\b|\broger\b|\bobama\b|\bkerry\b|\bsadie\b|\b!aura\b|\bchris\b|\bbadie\b|\bgregg\b|\bjalii\b|\buribe\b|\budall\b|\bburns\b|\bpeggy\b|\bshaun\b|\bsusan\b|\bbrown\b|\bleahy\b|\bsirin\b|\bjames\b|\bmeyer\b|\bhague\b|\bpaige\b|\botmar\b|\bdelay\b|\bcowen\b|\bbarna\b|\bjalil\b|\bhabre\b|\bjones\b|\bcasey\b|\bscott\b|\bbiden\b|\bialil\b|\bgheit\b|\bterry\b|\bharry\b|\bputin\b|\bsousa\b|\bhamas\b|\bwelch\b|\bdavid\b|\blugar\b|\bgates\b|\boscar\b|\bnge,b\b|\bmorsi\b|\brandi\b|\barusi\b|\bzidan\b|\bcretz\b|\bblair\b|\blarry\b|\bmalin\b|\bobeda\b|\bmills\b|\bsegal\b|\bbecky\b|\bjaill\b|\bhenry\b|\blevin\b|\bsmith\b|\bkumar\b|\bassad\b|\bsnowe\b|\bhelms\b|\bderek\b|\bmarc\b|\bdeby\b|\beric\b|\btony\b|\bkeit\b|\bkeib\b|\breid\b|\bdick\b|\bmeek\b|\bbeck\b|\bjuan\b|\bbayh\b|\bclay\b|\bhuma\b|\byang\b|\bcaro\b|\bglen\b|\bjohn\b|\brahm\b|\baiwa\b|\bhart\b|\bryan\b|\bhill\b|\blona\b|\bbush\b|\baksu\b|\btory\b|\bsean\b|\bburr\b|\bmark\b|\bjill\b|\bdink\b|\bbill\b|\bwebb\b|\bruss\b|\bqamu\b|\bpenn\b|\bphil\b|\brove\b|\bjail\b|\bjake\b|\balec\b|\bgary\b|\bjose\b|\bnick\b|\brice\b|\bdodd\b|\bmatt\b|\bmani\b|\bjeff\b|\bshah\b|\bpaul\b|\bstu\b|\bski\b|\bhb3\b|\bpam\b|\bsbu\b|\bjfk\b|\bdfm\b|\bcdm\b|\bjan\b|\bjon\b|\bsid\b|\bhrc\b|\bdan\b|\bsby\b|\baui\b|\bjen\b|\bamr\b|\bbob\b|\bjoe\b|\bhbj\b|\bsam\b|\bhsf\b|\btom\b|\bwjc\b|\bban\b|\bann\b|\bjim\b|\brob\b|\blyn\b|\bkay\b|\babz\b|\bkyl\b|\bal\b|\bmo\b|\bnn\b|\bdd\b|\bdp\b|\btx\b|\bed\b|\bp3\b|\bcb\b|\bpj\b|\bh\b"

    indexes = [(i.start(),i.end()) for i in re.finditer(pattern,raw_txt,flags=re.IGNORECASE)]
    for t in indexes:
        ne = {}
        ne["start"] = t[0]
        ne["end"] = t[1]
        ne["tag"] = "NAME"
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
    allAnnotations.extend(getYearRangeSpans(raw_txt))
    allAnnotations.extend(getPhoneSpans(raw_txt))
    allAnnotations.extend(getNameSpans(raw_txt))
    
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
