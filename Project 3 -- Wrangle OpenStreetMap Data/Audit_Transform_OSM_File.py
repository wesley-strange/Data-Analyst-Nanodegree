#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

#Map files in project folder
#OSMFILE = "sample10.osm"
OSMFILE = "chicago_illinois.osm"

###############################################################################
# Define regular expressions
# lower: all lowercase letters. Ex: "phone"
# lower_colon: all lowercase letters with colon inside. Ex: "addr:street"
# problemchars: contains problematic characters. Ex: "me&you"
# housenumber_re: grabs housenum from full address. Ex: "100 Grant" grabs "100"
# street_prefixes_re: grabs prefix from street. Ex: "South Grant" grabs "South"
# street_suffixes_re: grabs the suffix from street. Ex: "Grant St" grabs "St"
###############################################################################
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
housenumber_re = re.compile(r'\A\d+\S?\d+\b', re.IGNORECASE)
street_prefixes_re = re.compile(r'\A\S+\.?', re.IGNORECASE)
street_suffixes_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

###############################################################################
# Define Gold Standard Data
# cities_in_illinois: Gold Standard used to validate Illinois cities. The 
#   source below did not contain a full list, so additional cities were added.
#   https://en.wikipedia.org/wiki/List_of_towns_and_villages_in_Illinois
# county_postcode_mapping: Gold Standard used to validate Illinois Counties.
#   http://www.unitedstateszipcodes.org/il/
# postcode_county_mapping: Gold Standard used to validate Illinois Post Codes
#   to County mappings.
#   http://www.unitedstateszipcodes.org/il/
# postcode_city_mapping: Gold Standard used to validate Illinois Post Codes
#   to City mappings.
#   http://www.unitedstateszipcodes.org/il/
###############################################################################
cities_in_illinois = ['Addieville', 'Addison', 'Adeline', 'Albany', 'Albers', 'Alexis', 'Algonquin', 'Alhambra', 'Allendale', 'Allenville', 'Allerton', 'Alma', 'Alorton', 'Alpha', 'Alsey', 'Alsip', 'Alto Pass', 'Altona', 'Alvan', 'Anchor', 'Andalusia', 'Andover', 'Antioch', 'Apple River', 'Arenzville', 'Argenta', 'Arlington', 'Arlington Heights', 'Armington', 'Aroma Park', 'Arrowsmith', 'Arthur', 'Ashkum', 'Ashland', 'Ashmore', 'Ashton', 'Atwood', 'Augusta', 'Aurora', 'Aviston', 'Avon', 'Baldwin', 'Banner', 'Bannockburn', 'Bardolph', 'Barrington', 'Barrington Hills', 'Bartelso', 'Bartlett', 'Bartonville', 'Basco', 'Batavia', 'Batchtown', 'Bath', 'Bay View Gardens', 'Baylis', 'Beach Park', 'Beaverville', 'Beckemeyer', 'Bedford Park', 'Beecher', 'Beecher City', 'Belgium', 'Belknap', 'Belle Rive', 'Bellevue', 'Bellflower', 'Bellmont', 'Bellwood', 'Bement', 'Bensenville', 'Benson', 'Bentley', 'Berkeley', 'Berlin', 'Berwyn', 'Bethalto', 'Bethany', 'Big Rock', 'Biggsville', 'Bingham', 'Bishop Hill', 'Bismarck', 'Blandinsville', 'Bloomingdale', 'Blue Island', 'Blue Mound', 'Bluffs', 'Bluford', 'Bolingbrook', 'Bondville', 'Bone Gap', 'Bonfield', 'Bonnie', 'Bourbonnais', 'Bowen', 'Braceville', 'Bradford', 'Bradley', 'Bridgeview', 'Brighton', 'Brimfield', 'Broadlands', 'Broadview', 'Broadwell', 'Brocton', 'Brookfield', 'Brooklyn', 'Broughton', 'Browning', 'Browns', 'Brownstown', 'Brussels', 'Bryant', 'Buckingham', 'Buckley', 'Buckner', 'Buda', 'Buffalo', 'Buffalo Grove', 'Bull Valley', 'Bulpitt', 'Buncombe', 'Bureau Junction', 'Burlington', 'Burnham', 'Burnt Prairie', 'Burr Ridge', 'Bush', 'Bushnell', 'Butler', 'Cabery', 'Cahokia', 'Caledonia', 'Calhoun', 'Calumet City', 'Calumet Park', 'Camargo', 'Cambria', 'Cambridge', 'Camden', 'Camp Point', 'Campbell Hill', 'Campton Hills', 'Campus', 'Cantrall', 'Capron', 'Carbon Cliff', 'Carbon Hill', 'Carlock', 'Carol Stream', 'Carpentersville', 'Carrier Mills', 'Cary', 'Caseyville', 'Catlin', 'Cave-In-Rock', 'Cedar Point', 'Cedarville', 'Central City', 'Cerro Gordo', 'Chadwick', 'Chandlerville', 'Channahon', 'Chapin', 'Chatham', 'Chebanse', 'Cherry', 'Cherry Valley', 'Chesterfield', 'Chicago', 'Chicago Heights', 'Chicago Ridge', 'Cicero', 'Cisco', 'Cisne', 'Cissna Park', 'Claremont', 'Clarendon Hills', 'Clay City', 'Clayton', 'Clear Lake', 'Cleveland', 'Clifton', 'Coal City', 'Coal Valley', 'Coalton', 'Coatsburg', 'Cobden', 'Coleta', 'Colfax', 'Colp', 'Columbus', 'Compton', 'Concord', 'Congerville', 'Cooksville', 'Cordova', 'Cornell', 'Coulterville', 'Cowden', 'Crainville', 'Crescent City', 'Crest Hill', 'Creston', 'Crestwood', 'Crete', 'Creve Coeur', 'Crossville', 'Crystal Lake', 'Cullom', 'Curran', 'Cutler', 'Cypress', 'Dahlgren', 'Dakota', 'Dalton City', 'Dalzell', 'Damiansville', 'Dana', 'Danforth', 'Danvers', 'Darien', 'Davis', 'Davis Junction', 'Dawson', 'De Land', 'De Pue', 'De Soto', 'Deer Creek', 'Deer Grove', 'Deer Park', 'Deerfield', 'Des Plaines', 'Detroit', 'DeWitt', 'Diamond', 'Dieterich', 'Divernon', 'Dix', 'Dixmoor', 'Dolton', 'Dongola', 'Donnellson', 'Donovan', 'Dorchester', 'Dover', 'Dowell', 'Downers Grove', 'Downs', 'Du Bois', 'Dunfermline', 'Dunlap', 'Dupo', 'Durand', 'Dwight', 'Eagarville', 'East Alton', 'East Brooklyn', 'East Cape Girardeau', 'East Carondelet', 'East Dundee', 'East Galesburg', 'East Gillespie', 'East Hazel Crest', 'Easton', 'Eddyville', 'Edgewood', 'Edinburg', 'El Dara', 'Elburn', 'Eldred', 'Elgin', 'Elizabeth', 'Elizabethtown', 'Elk Grove Village', 'Elkhart', 'Elkville', 'Elliott', 'Ellis Grove', 'Ellisville', 'Ellsworth', 'Elmhurst', 'Elmwood Park', 'Elsah', 'Elvaston', 'Elwood', 'Emden', 'Emington', 'Energy', 'Enfield', 'Equality', 'Erie', 'Essex', 'Evanston', 'Evansville', 'Evergreen Park', 'Ewing', 'Exeter', 'Fairmont City', 'Fairmount', 'Fairview', 'Farina', 'Farmersville', 'Fayetteville', 'Ferris', 'Fidelity', 'Fieldon', 'Fillmore', 'Findlay', 'Fisher', 'Fithian', 'Flanagan', 'Flat Rock', 'Florence', 'Flossmoor', 'Foosland', 'Ford Heights', 'Forest City', 'Forest Park', 'Forest View', 'Forrest', 'Forreston', 'Forsyth', 'Fox Lake', 'Fox River Grove', 'Frankfort', 'Franklin', 'Franklin Grove', 'Franklin Park', 'Freeburg', 'Freeman Spur', 'Fults', 'Galatia', 'Gardner', 'Garrett', 'Gays', 'Geneva', 'German Valley', 'Germantown', 'Germantown Hills', 'Gifford', 'Gilberts', 'Gladstone', 'Glasford', 'Glasgow', 'Glen Carbon', 'Glen Ellyn', 'Glencoe', 'Glendale Heights', 'Glenview', 'Glenwood', 'Godfrey', 'Godley', 'Golden', 'Golden Gate', 'Golf', 'Good Hope', 'Goodfield', 'Goreville', 'Gorham', 'Grand Ridge', 'Grandview', 'Grant Park', 'Grantfork', 'Granville', 'Grayslake', 'Green Oaks', 'Green Valley', 'Greenup', 'Greenview', 'Greenwood', 'Gridley', 'Gulfport', 'Gurnee', 'Hainesville', 'Hamburg', 'Hamel', 'Hammond', 'Hampshire', 'Hampton', 'Hanaford', 'Hanna City', 'Hanover', 'Hanover Park', 'Hardin', 'Harmon', 'Harristown', 'Hartford', 'Hartsburg', 'Harvel', 'Harvey', 'Harwood Heights', 'Hawthorn Woods', 'Hazel Crest', 'Hebron', 'Hecker', 'Henderson', 'Hennepin', 'Henning', 'Herrick', 'Herscher', 'Hettick', 'Heyworth', 'Hidalgo', 'Highland Park', 'Hillcrest', 'Hillsdale', 'Hillside', 'Hillview', 'Hinckley', 'Hindsboro', 'Hinsdale', 'Hodgkins', 'Hoffman', 'Hoffman Estates', 'Holiday Hills', 'Hollowayville', 'Homer', 'Homer Glen', 'Homewood', 'Hooppole', 'Hopedale', 'Hopewell', 'Hopkins Park', 'Hoyleton', 'Hudson', 'Huey', 'Hull', 'Humboldt', 'Hume', 'Huntley', 'Hutsonville', 'Illiopolis', 'Ina', 'Indian Creek', 'Indian Head Park', 'Indianola', 'Industry', 'Inverness', 'Iola', 'Ipava', 'Iroquois', 'Irving', 'Irvington', 'Irwin', 'Island Lake', 'Itasca', 'Iuka', 'Ivesdale', 'Jeffersonville', 'Jeisyville', 'Jerome', 'Jewett', 'Johnsburg', 'Johnsonville', 'Joliet', 'Joppa', 'Joy', 'Junction', 'Junction City', 'Justice', 'Kampsville', 'Kane', 'Kaneville', 'Kangley', 'Kansas', 'Kappa', 'Karnak', 'Kaskaskia', 'Keenes', 'Keensburg', 'Kell', 'Kempton', 'Kenilworth', 'Kenney', 'Keyesport', 'Kilbourne', 'Kildeer', 'Kincaid', 'Kinderhook', 'Kingston', 'Kingston Mines', 'Kinsman', 'Kirkland', 'Kirkwood', 'La Fayette', 'La Grange', 'La Grange Park', 'La Moille', 'La Rose', 'Ladd', 'Lake Barrington', 'Lake Bluff', 'Lake Forest', 'Lake in the Hills', 'Lake Ka-ho', 'Lake Villa', 'Lake Zurich', 'Lakemoor', 'Lakewood', 'Lansing', 'Latham', 'Leaf River', 'Lee', 'Leland', 'Lemont', 'Lena', 'Lenzburg', 'Leonore', 'Lerna', 'Liberty', 'Libertyville', 'Lily Lake', 'Lima', 'Limestone', 'Lincolnshire', 'Lincolnwood', 'Lindenhurst', 'Lisbon', 'Lisle', 'Little York', 'Littleton', 'Liverpool', 'Livingston', 'Loami', 'Lockport', 'Loda', 'Lomax', 'Lombard', 'London Mills', 'Long Creek', 'Long Grove', 'Long Point', 'Longview', 'Loraine', 'Lostant', 'Louisville', 'Lovington', 'Ludlow', 'Lyndon', 'Lynnville', 'Lynwood', 'Lyons', 'Macedonia', 'Machesney Park', 'Mackinaw', 'Maeystown', 'Magnolia', 'Mahomet', 'Makanda', 'Malden', 'Malta', 'Manchester', 'Manhattan', 'Manito', 'Manlius', 'Mansfield', 'Manteno', 'Maple Park', 'Mapleton', 'Maquon', 'Marietta', 'Marine', 'Marissa', 'Mark', 'Markham', 'Martinton', 'Maryville', 'Matherville', 'Matteson', 'Maunie', 'Maywood', 'Mazon', 'McClure', 'McCook', 'McCullom Lake', 'McLean', 'McNabb', 'Mechanicsburg', 'Media', 'Medora', 'Melrose Park', 'Melvin', 'Mendon', 'Menominee', 'Meredosia', 'Merrionette Park', 'Metamora', 'Metcalf', 'Mettawa', 'Middletown', 'Midlothian', 'Milan', 'Milford', 'Mill Creek', 'Mill Shoals', 'Millbrook', 'Milledgeville', 'Millington', 'Millstadt', 'Milton', 'Mineral', 'Minier', 'Minooka', 'Modesto', 'Mokena', 'Monee', 'Monroe Center', 'Montgomery', 'Montrose', 'Morris', 'Morrisonville', 'Morton', 'Morton Grove', 'Mound Station', 'Mount Auburn', 'Mount Clare', 'Mount Erie', 'Mount Morris', 'Mount Prospect', 'Mount Zion', 'Moweaqua', 'Muddy', 'Mulberry Grove', 'Muncie', 'Mundelein', 'Murrayville', 'Naperville', 'Naplate', 'Nebo', 'Nelson', 'Neponset', 'New Athens', 'New Baden', 'New Bedford', 'New Berlin', 'New Burnside', 'New Douglas', 'New Grand Chain', 'New Haven', 'New Holland', 'New Lenox', 'New Milford', 'New Minden', 'New Salem', 'Newark', 'Niantic', 'Niles', 'Noble', 'Nora', 'Norridge', 'Norris', 'Norris City', 'North Aurora', 'North Barrington', 'North City', 'North Henderson', 'North Pekin', 'North Riverside', 'North Utica', 'Northbrook', 'Northfield', 'Northlake', 'Norwood', 'Oak Brook', 'Oak Forest', 'Oak Grove', 'Oak Lawn', 'Oak Park', 'Oakbrook Terrace', 'Oakdale', 'Oakford', 'Oakwood', 'Oakwood Hills', 'Oblong', 'Oconee', 'Odell', 'Odin', 'Ogden', 'Ohio', 'Ohlman', 'Okawville', 'Old Mill Creek', 'Old Ripley', 'Old Shawneetown', 'Olmsted', 'Olympia Fields', 'Omaha', 'Onarga', 'Oquawka', 'Orangeville', 'Oreana', 'Orion', 'Orland Hills', 'Orland Park', 'Oswego', 'Owaneco', 'Palatine', 'Palestine', 'Palmer', 'Palmyra', 'Palos Heights', 'Palos Park', 'Panama', 'Panola', 'Papineau', 'Park Forest', 'Park Ridge', 'Parkersburg', 'Patoka', 'Paw Paw', 'Pawnee', 'Payson', 'Pearl', 'Pearl City', 'Pecatonica', 'Peoria Heights', 'Peotone', 'Percy', 'Perry', 'Pesotum', 'Phillipstown', 'Philo', 'Phoenix', 'Pierron', 'Pingree Grove', 'Piper City', 'Pittsburg', 'Plainfield', 'Plainville', 'Plattville', 'Pleasant Hill', 'Pleasant Plains', 'Plymouth', 'Pocahontas', 'Pontoon Beach', 'Pontoosuc', 'Poplar Grove', 'Port Barrington', 'Port Byron', 'Posen', 'Potomac', 'Prairie City', 'Prairie du Rocher', 'Prairie Grove', 'Princeville', 'Prospect Heights', 'Pulaski', 'Radom', 'Raleigh', 'Ramsey', 'Rankin', 'Ransom', 'Rantoul', 'Rapids City', 'Raritan', 'Raymond', 'Reddick', 'Redmon', 'Reynolds', 'Richmond', 'Richton Park', 'Richview', 'Ridge Farm', 'Ridgway', 'Ridott', 'Ringwood', 'Rio', 'Ripley', 'River Forest', 'River Grove', 'Riverdale', 'Riverside', 'Riverton', 'Riverwoods', 'Roanoke', 'Robbins', 'Roberts', 'Rochester', 'Rock City', 'Rockbridge', 'Rockdale', 'Rockton', 'Rockwood', 'Rolling Meadows', 'Romeoville', 'Roscoe', 'Rose Hill', 'Roselle', 'Rosemont', 'Roseville', 'Rossville', 'Round Lake', 'Round Lake Beach', 'Round Lake Heights', 'Round Lake Park', 'Roxana', 'Royal', 'Royal Lakes', 'Royalton', 'Ruma', 'Russellville', 'Rutland', 'Sadorus', 'Sailor Springs', 'St. Anne', 'St. Augustine', 'St. Charles', 'St. David', 'St. Jacob', 'St. Johns', 'St. Joseph', 'St. Libory', 'St. Peter', 'Ste. Marie', 'Sammons Point', 'San Jose', 'Sandoval', 'Sauget', 'Sauk Village', 'Saunemin', 'Savoy', 'Sawyerville', 'Saybrook', 'Scales Mound', 'Schaumburg', 'Schiller Park', 'Schram City', 'Sciota', 'Scottville', 'Seaton', 'Seatonville', 'Secor', 'Seneca', 'Shabbona', 'Shannon', 'Sheffield', 'Sheldon', 'Sheridan', 'Sherman', 'Sherrard', 'Shiloh', 'Shipman', 'Shorewood', 'Shumway', 'Sibley', 'Sidell', 'Sidney', 'Simpson', 'Sims', 'Skokie', 'Sleepy Hollow', 'Smithboro', 'Smithfield', 'Smithton', 'Somonauk', 'Sorento', 'South Barrington', 'South Chicago Heights', 'South Elgin', 'South Holland', 'South Jacksonville', 'South Pekin', 'South Roxana', 'South Wilmington', 'Southern View', 'Sparland', 'Spaulding', 'Spillertown', 'Spring Bay', 'Spring Grove', 'Springerton', 'Standard', 'Standard City', 'Stanford', 'Steeleville', 'Steger', 'Steward', 'Stewardson', 'Stickney', 'Stillman Valley', 'Stockton', 'Stone Park', 'Stonefort', 'Stonington', 'Stoy', 'Strasburg', 'Strawn', 'Streamwood', 'Stronghurst', 'Sublette', 'Sugar Grove', 'Summerfield', 'Summit', 'Sun River Terrace', 'Swansea', 'Symerton', 'Table Grove', 'Tallula', 'Tamaroa', 'Tamms', 'Tampico', 'Taylor Springs', 'Tennessee', 'Teutopolis', 'Thawville', 'Thayer', 'Thebes', 'Third Lake', 'Thomasboro', 'Thompsonville', 'Thomson', 'Thornton', 'Tilden', 'Tilton', 'Timberlane', 'Time', 'Tinley Park', 'Tiskilwa', 'Toledo', 'Tolono', 'Tonica', 'Tovey', 'Towanda', 'Tower Hill', 'Tower Lakes', 'Tremont', 'Trout Valley', 'Troy Grove', 'Ullin', 'Union', 'Union Hill', 'University Park', 'Ursa', 'Utica', 'Valier', 'Valley City', 'Valmeyer', 'Varna', 'Venedy', 'Vergennes', 'Vermilion', 'Vermont', 'Vernon', 'Vernon Hills', 'Verona', 'Versailles', 'Victoria', 'Villa Park', 'Viola', 'Virgil', 'Volo', 'Wadsworth', 'Waggoner', 'Walnut', 'Walnut Hill', 'Walshville', 'Waltonville', 'Wapella', 'Warren', 'Warrensburg', 'Warrenville', 'Washburn', 'Washington Park', 'Wataga', 'Waterman', 'Watson', 'Wauconda', 'Wayne', 'Wayne City', 'Waynesville', 'Weldon', 'Wellington', 'Wenonah', 'West Brooklyn', 'West Chicago', 'West City', 'West Dundee', 'West Point', 'West Salem', 'Westchester', 'Western Springs', 'Westfield', 'Westmont', 'Westville', 'Wheaton', 'Wheeler', 'Wheeling', 'White City', 'Whiteash', 'Williamsfield', 'Williamson', 'Williamsville', 'Willisville', 'Willow Hill', 'Willow Springs', 'Willowbrook', 'Wilmette', 'Wilmington', 'Wilsonville', 'Windsor', 'Winfield', 'Winnebago', 'Winnetka', 'Winslow', 'Winthrop Harbor', 'Wonder Lake', 'Woodhull', 'Woodland', 'Woodlawn', 'Woodridge', 'Woodson', 'Woodstock', 'Worden', 'Worth', 'Wyanet', 'Xenia', 'Yale', 'Yates City', 'Yorkville']
county_postcode_mapping = {u'Wayne': [62446, 62809, 62823, 62833, 62837, 62842, 62843, 62850, 62851, 62878, 62886, 62895], u'Monroe': [62236, 62244, 62248, 62256, 62279, 62295, 62298], u'St. Clair': [62059, 62071, 62202, 62222, 62224], u'Stark': [61426, 61449, 61479, 61483, 61491], u'Madison': [62001, 62002, 62010, 62018, 62021, 62024, 62025, 62026, 62034, 62035, 62040, 62046, 62048, 62058, 62060, 62061, 62062, 62067, 62074, 62084, 62087, 62090, 62095, 62097, 62234, 62249, 62281, 62294], u'Mclean': [61702, 61709, 61710, 61758, 61790, 61791, 61799], u'Bond': [62019, 62086, 62246, 62253, 62273, 62275, 62284], u'Lee': [60530, 60553, 61006, 61021, 61031, 61042, 61057, 61310, 61318, 61324, 61331, 61353, 61367, 61378], u'Edwards': [62476, 62806, 62815, 62818, 62844], u'Adams': [62301, 62305, 62306, 62320, 62324, 62325, 62338, 62339, 62346, 62347, 62348, 62349, 62351, 62359, 62360, 62365, 62376], u'Macoupin': [62009, 62014, 62023, 62033, 62063, 62069, 62079, 62085, 62088, 62093, 62626, 62630, 62640, 62649, 62667, 62672, 62674, 62683, 62685, 62690], u'Marion': [62801, 62807, 62849, 62853, 62854, 62870, 62875, 62881, 62882, 62892, 62893], u'Knox': [61401, 61402, 61410, 61414, 61428, 61430, 61436, 61439, 61448, 61458, 61467, 61472, 61474, 61485, 61488, 61489, 61572], u'Williamson': [62902, 62915, 62918, 62921, 62922, 62933, 62948, 62949, 62951, 62959, 62974], u'Fulton': [61427, 61431, 61432, 61433, 61441, 61459, 61477, 61482, 61484, 61501, 61519, 61520, 61524, 61531, 61542, 61543, 61544, 61553, 61563], u'Champaign': [60949, 61801, 61802, 61803, 61815, 61816, 61820, 61821, 61822, 61824, 61825, 61826, 61840, 61843, 61845, 61847, 61849, 61851, 61852, 61853, 61859, 61862, 61863, 61864, 61866, 61871, 61872, 61873, 61874, 61875, 61877, 61878, 61880], u'Coles': [61912, 61920, 61931, 61938, 61943, 62435, 62440], u'McDonough': [61411, 61416, 61420, 61422, 61438, 61440, 61455, 61470, 61475, 62326, 62367, 62374], u'Woodford': [61516, 61530, 61545, 61548, 61561, 61570, 61729, 61733, 61738, 61742, 61760, 61771], u'Pike': [62312, 62314, 62323, 62340, 62343, 62345, 62352, 62355, 62356, 62357, 62361, 62362, 62363, 62366, 62370], u'McLean': [61701, 61704, 61705, 61720, 61722, 61724, 61725, 61726, 61728, 61730, 61731, 61732, 61736, 61737, 61744, 61745, 61748, 61752, 61753, 61754, 61761, 61770, 61772, 61774, 61776], u'Whiteside': [61037, 61071, 61081, 61230, 61243, 61250, 61251, 61252, 61261, 61270, 61277, 61283], u'Saline': [62917, 62930, 62935, 62946, 62965, 62977, 62987], u'Franklin': [62805, 62812, 62819, 62822, 62825, 62836, 62840, 62856, 62865, 62874, 62884, 62890, 62891, 62896, 62897, 62983, 62999], u'Logan': [61723, 61751, 62512, 62518, 62519, 62541, 62543, 62548, 62634, 62635, 62643, 62656, 62666, 62671], u'Mercer': [61231, 61260, 61263, 61272, 61276, 61279, 61281, 61442, 61465, 61466, 61476, 61486], u'Johnson': [62909, 62912, 62923, 62939, 62943, 62967, 62972, 62985, 62995], u'Lawrence': [62417, 62439, 62460, 62466], u'Alexander': [62914, 62957, 62962, 62969, 62988, 62990, 62993], u'Henry': [61233, 61234, 61235, 61238, 61241, 61254, 61258, 61262, 61273, 61274, 61413, 61419, 61434, 61443, 61468, 61490], u'Crawford': [62413, 62427, 62433, 62449, 62451, 62454, 62464], u'Boone': [61008, 61011, 61012, 61038, 61065], u'Cumberland': [62428, 62436, 62447, 62462, 62468, 62469], u'Edgar': [61917, 61924, 61932, 61933, 61940, 61944, 61949, 61955], u'Clinton': [62215, 62216, 62218, 62219, 62230, 62231, 62245, 62250, 62252, 62265, 62266, 62293], u'Schuyler': [61452, 62319, 62344, 62624, 62639, 62681], u'Clark': [62420, 62423, 62441, 62442, 62474, 62477, 62478], u'Clay': [62426, 62434, 62824, 62839, 62858, 62879, 62899], u'Macon': [61756, 62501, 62513, 62514, 62521, 62522, 62523, 62524, 62525, 62526, 62532, 62535, 62537, 62544, 62549, 62551, 62554, 62573], u'Dupage': [60101, 60103, 60105, 60106, 60108, 60116, 60117, 60122, 60125, 60126, 60128, 60132, 60133, 60137, 60138, 60139, 60143, 60148, 60157, 60172, 60181, 60184, 60185, 60186, 60187, 60188, 60189, 60190, 60191, 60197, 60199, 60399, 60502, 60504, 60514, 60515, 60516, 60517, 60519, 60521, 60522, 60523, 60527, 60532, 60540, 60555, 60559, 60561, 60563, 60565, 60566, 60567, 60570, 60597, 60599], u'DuPage': [60101, 60103, 60105, 60106, 60108, 60116, 60117, 60122, 60125, 60126, 60128, 60132, 60133, 60137, 60138, 60139, 60143, 60148, 60157, 60172, 60181, 60184, 60185, 60186, 60187, 60188, 60189, 60190, 60191, 60197, 60199, 60399, 60502, 60504, 60514, 60515, 60516, 60517, 60519, 60521, 60522, 60523, 60527, 60532, 60540, 60555, 60559, 60561, 60563, 60565, 60566, 60567, 60570, 60597, 60599], u'Putnam': [61326, 61327, 61335, 61336, 61340, 61363, 61560], u'Christian': [62083, 62510, 62517, 62531, 62538, 62540, 62546, 62547, 62555, 62556, 62557, 62567, 62568, 62570], u'Ford': [60919, 60933, 60936, 60946, 60952, 60957, 60959, 60962, 61773], u'Kendall': [60512, 60536, 60538, 60541, 60543, 60545, 60560], u'Piatt': [61813, 61818, 61830, 61839, 61854, 61855, 61856, 61884, 61929, 61936], u'Scott': [62610, 62621, 62663, 62694], u'White': [62820, 62821, 62827, 62834, 62835, 62861, 62862, 62869], u'Montgomery': [62015, 62017, 62032, 62049, 62051, 62056, 62075, 62076, 62077, 62089, 62091, 62094, 62533, 62560, 62572], u'Moultrie': [61914, 61925, 61928, 61937, 61951], u'Kane': [60109, 60110, 60118, 60119, 60121, 60123, 60124, 60134, 60136, 60140, 60144, 60147, 60151, 60170, 60174, 60175, 60177, 60183, 60505, 60506, 60507, 60510, 60511, 60539, 60542, 60554, 60568, 60572, 60598], u'Bureau': [61312, 61314, 61315, 61317, 61320, 61322, 61323, 61328, 61329, 61330, 61337, 61338, 61344, 61345, 61346, 61349, 61356, 61359, 61361, 61362, 61368, 61374, 61376, 61379, 61421], u'Vermilion': [60932, 60942, 60960, 60963, 61810, 61811, 61812, 61814, 61817, 61831, 61832, 61833, 61834, 61841, 61844, 61846, 61848, 61850, 61857, 61858, 61865, 61870, 61876, 61883], u'Livingston': [60420, 60460, 60920, 60921, 60929, 60934, 61311, 61313, 61319, 61333, 61739, 61740, 61741, 61743, 61764, 61769, 61775], u'Gallatin': [62867, 62871, 62934, 62954, 62979, 62984], u'Effingham': [62401, 62411, 62414, 62424, 62443, 62461, 62467, 62473], u'Mason': [61532, 61546, 61567, 62617, 62633, 62644, 62655, 62664, 62682], u'Calhoun': [62006, 62013, 62036, 62045, 62047, 62053, 62065, 62070], u'Jefferson': [62810, 62814, 62816, 62830, 62846, 62864, 62866, 62872, 62883, 62889, 62894, 62898], u'Dekalb': [60111, 60112, 60115, 60135, 60145, 60146, 60150, 60178, 60520, 60548, 60550, 60552, 60556], u'Pope': [62928, 62938, 62947], u'Marshall': [61369, 61375, 61377, 61424, 61537, 61540, 61541, 61565], u'Pulaski': [62941, 62953, 62956, 62963, 62964, 62970, 62973, 62976, 62992, 62996], u'Tazewell': [61534, 61535, 61550, 61554, 61555, 61558, 61564, 61568, 61571, 61610, 61611, 61721, 61734, 61747, 61755, 61759], u'Ogle': [60113, 60129, 61007, 61010, 61015, 61020, 61030, 61043, 61047, 61049, 61052, 61054, 61061, 61064, 61068, 61084, 61091], u'Mchenry': [60039], u'Henderson': [61418, 61425, 61437, 61454, 61460, 61469, 61471, 61480], u'Menard': [62613, 62642, 62659, 62673, 62675, 62688], u'Grundy': [60407, 60416, 60424, 60437, 60444, 60447, 60450, 60474, 60479], u'Hancock': [61450, 62311, 62313, 62316, 62321, 62329, 62330, 62334, 62336, 62341, 62354, 62358, 62373, 62379, 62380], u'Carroll': [61014, 61046, 61051, 61053, 61074, 61078, 61285], u'Winnebago': [61016, 61024, 61063, 61072, 61073, 61077, 61079, 61080, 61088, 61101, 61102, 61103, 61104, 61105, 61106, 61107, 61108, 61109, 61110, 61111, 61112, 61114, 61115, 61125, 61126, 61130, 61131, 61132], u'Stephenson': [61013, 61018, 61019, 61027, 61032, 61039, 61044, 61048, 61050, 61060, 61062, 61067, 61070, 61089], u'Morgan': [62601, 62628, 62631, 62638, 62650, 62651, 62660, 62665, 62668, 62692, 62695], u'De Witt': [61727, 61735, 61749, 61750, 61777, 61778, 61842, 61882], u'Perry': [62237, 62238, 62274, 62832, 62888, 62997], u'Jasper': [62432, 62445, 62448, 62459, 62475, 62479, 62480, 62481], u'Wabash': [62410, 62811, 62852, 62855, 62863], u'McHenry': [60001, 60012, 60013, 60014, 60021, 60033, 60034, 60042, 60050, 60051, 60071, 60072, 60081, 60097, 60098, 60102, 60142, 60152, 60156, 60180], u'Cass': [62611, 62612, 62618, 62622, 62627, 62691], u'La Salle': [60470, 60518, 60531, 60537, 60549, 60551, 60557, 61301, 61316, 61321, 61325, 61332, 61334, 61341, 61342, 61348, 61350, 61354, 61358, 61360, 61364, 61370, 61371, 61372, 61373], u'Greene': [62016, 62027, 62044, 62050, 62054, 62078, 62081, 62082, 62092, 62098], u'St Clair': [62201, 62203, 62204, 62205, 62206, 62207, 62208, 62220, 62221, 62223, 62225, 62226, 62232, 62239, 62240, 62243, 62254, 62255, 62257, 62258, 62260, 62264, 62269, 62282, 62285, 62289], u'Sangamon': [62515, 62520, 62530, 62536, 62539, 62545, 62558, 62561, 62563, 62615, 62625, 62629, 62661, 62662, 62670, 62677, 62684, 62689, 62693, 62701, 62702, 62703, 62704, 62705, 62706, 62707, 62708, 62711, 62712, 62713, 62715, 62716, 62719, 62721, 62722, 62723, 62726, 62736, 62739, 62746, 62756, 62757, 62761, 62762, 62763, 62764, 62765, 62766, 62767, 62769, 62776, 62777, 62781, 62786, 62791, 62794, 62796], u'Lake': [60002, 60015, 60020, 60030, 60031, 60035, 60037, 60040, 60041, 60044, 60045, 60046, 60047, 60048, 60049, 60060, 60061, 60064, 60069, 60073, 60075, 60079, 60083, 60084, 60085, 60086, 60087, 60088, 60089, 60092, 60096, 60099], u'Hardin': [62919, 62931, 62955, 62982], u'Washington': [62214, 62263, 62268, 62271, 62803, 62808, 62831, 62848, 62876, 62877], u'Jersey': [62012, 62022, 62028, 62030, 62031, 62037, 62052], u'Brown': [62353, 62375, 62378], u'Douglas': [61910, 61911, 61913, 61919, 61930, 61941, 61942, 61953, 61956], u'Randolph': [62217, 62233, 62241, 62242, 62259, 62261, 62272, 62277, 62278, 62280, 62286, 62288, 62292, 62297], u'Union': [62905, 62906, 62920, 62926, 62952, 62961, 62998], u'Richland': [62419, 62421, 62425, 62450, 62452, 62868], u'Fayette': [62011, 62080, 62247, 62262, 62418, 62458, 62471, 62838, 62857, 62880, 62885], u'Peoria': [61451, 61517, 61523, 61525, 61526, 61528, 61529, 61533, 61536, 61539, 61547, 61552, 61559, 61562, 61569, 61601, 61602, 61603, 61604, 61605, 61606, 61607, 61612, 61613, 61614, 61615, 61616, 61625, 61629, 61630, 61633, 61634, 61635, 61636, 61637, 61638, 61639, 61641, 61643, 61650, 61651, 61652, 61653, 61654, 61655, 61656], u'Jackson': [62901, 62903, 62907, 62916, 62924, 62927, 62932, 62940, 62942, 62950, 62958, 62966, 62971, 62975, 62994], u'Massac': [62908, 62910, 62960], u'Kankakee': [60901, 60910, 60913, 60914, 60915, 60917, 60922, 60935, 60940, 60941, 60944, 60950, 60954, 60958, 60961, 60964, 60969], u'Cook': [60004, 60005, 60006, 60007, 60008, 60009, 60010, 60011, 60016, 60017, 60018, 60019, 60022, 60025, 60026, 60029, 60038, 60043, 60053, 60055, 60056, 60062, 60065, 60067, 60068, 60070, 60074, 60076, 60077, 60078, 60082, 60090, 60091, 60093, 60094, 60095, 60104, 60107, 60120, 60130, 60131, 60141, 60153, 60154, 60155, 60159, 60160, 60161, 60162, 60163, 60164, 60165, 60168, 60169, 60171, 60173, 60176, 60179, 60192, 60193, 60194, 60195, 60196, 60201, 60202, 60203, 60204, 60208, 60209, 60290, 60301, 60302, 60303, 60304, 60305, 60402, 60406, 60409, 60411, 60412, 60415, 60419, 60422, 60425, 60426, 60428, 60429, 60430, 60438, 60439, 60443, 60445, 60452, 60453, 60454, 60455, 60456, 60457, 60458, 60459, 60461, 60462, 60463, 60464, 60465, 60466, 60467, 60469, 60471, 60472, 60473, 60475, 60476, 60477, 60478, 60480, 60482, 60487, 60499, 60501, 60513, 60525, 60526, 60534, 60546, 60558, 60601, 60602, 60603, 60604, 60605, 60606, 60607, 60608, 60609, 60610, 60611, 60612, 60613, 60614, 60615, 60616, 60617, 60618, 60619, 60620, 60621, 60622, 60623, 60624, 60625, 60626, 60628, 60629, 60630, 60631, 60632, 60633, 60634, 60636, 60637, 60638, 60639, 60640, 60641, 60642, 60643, 60644, 60645, 60646, 60647, 60649, 60651, 60652, 60653, 60654, 60655, 60656, 60657, 60659, 60660, 60661, 60663, 60664, 60666, 60668, 60669, 60670, 60673, 60674, 60675, 60677, 60678, 60679, 60680, 60681, 60682, 60684, 60685, 60686, 60687, 60688, 60689, 60690, 60691, 60693, 60694, 60695, 60696, 60697, 60699, 60701, 60706, 60707, 60712, 60714, 60803, 60804, 60805, 60827], u'Jo Daviess': [61001, 61025, 61028, 61036, 61041, 61059, 61075, 61085, 61087], u'Shelby': [61957, 62422, 62431, 62438, 62444, 62463, 62465, 62534, 62550, 62553, 62565, 62571], u'Hamilton': [62817, 62828, 62829, 62859, 62860, 62887], u'Will': [60401, 60403, 60404, 60408, 60410, 60417, 60421, 60423, 60431, 60432, 60433, 60434, 60435, 60436, 60440, 60441, 60442, 60446, 60448, 60449, 60451, 60468, 60481, 60484, 60490, 60491, 60503, 60544, 60564, 60585, 60586], u'Iroquois': [60911, 60912, 60918, 60924, 60926, 60927, 60928, 60930, 60931, 60938, 60939, 60945, 60948, 60951, 60953, 60955, 60956, 60966, 60967, 60968, 60970, 60973, 60974], u'Warren': [61412, 61415, 61417, 61423, 61435, 61447, 61453, 61462, 61473, 61478], u'Rock Island': [61201, 61204, 61232, 61236, 61237, 61239, 61240, 61242, 61244, 61256, 61257, 61259, 61264, 61265, 61266, 61275, 61278, 61282, 61284, 61299]}
postcode_county_mapping = {60001:'McHenry',60002:'Lake',60004:'Cook',60005:'Cook',60006:'Cook',60007:'Cook',60008:'Cook',60009:'Cook',60010:'Cook',60011:'Cook',60012:'McHenry',60013:'McHenry',60014:'McHenry',60015:'Lake',60016:'Cook',60017:'Cook',60018:'Cook',60019:'Cook',60020:'Lake',60021:'McHenry',60022:'Cook',60025:'Cook',60026:'Cook',60029:'Cook',60030:'Lake',60031:'Lake',60033:'McHenry',60034:'McHenry',60035:'Lake',60037:'Lake',60038:'Cook',60039:'Mchenry',60040:'Lake',60041:'Lake',60042:'McHenry',60043:'Cook',60044:'Lake',60045:'Lake',60046:'Lake',60047:'Lake',60048:'Lake',60049:'Lake',60050:'McHenry',60051:'McHenry',60053:'Cook',60055:'Cook',60056:'Cook',60060:'Lake',60061:'Lake',60062:'Cook',60064:'Lake',60065:'Cook',60067:'Cook',60068:'Cook',60069:'Lake',60070:'Cook',60071:'McHenry',60072:'McHenry',60073:'Lake',60074:'Cook',60075:'Lake',60076:'Cook',60077:'Cook',60078:'Cook',60079:'Lake',60081:'McHenry',60082:'Cook',60083:'Lake',60084:'Lake',60085:'Lake',60086:'Lake',60087:'Lake',60088:'Lake',60089:'Lake',60090:'Cook',60091:'Cook',60092:'Lake',60093:'Cook',60094:'Cook',60095:'Cook',60096:'Lake',60097:'McHenry',60098:'McHenry',60099:'Lake',60101:'Dupage',60102:'McHenry',60103:'Dupage',60104:'Cook',60105:'Dupage',60106:'Dupage',60107:'Cook',60108:'Dupage',60109:'Kane',60110:'Kane',60111:'Dekalb',60112:'Dekalb',60113:'Ogle',60115:'Dekalb',60116:'Dupage',60117:'Dupage',60118:'Kane',60119:'Kane',60120:'Cook',60121:'Kane',60122:'Dupage',60123:'Kane',60124:'Kane',60125:'Dupage',60126:'Dupage',60128:'Dupage',60129:'Ogle',60130:'Cook',60131:'Cook',60132:'Dupage',60133:'Dupage',60134:'Kane',60135:'Dekalb',60136:'Kane',60137:'Dupage',60138:'Dupage',60139:'Dupage',60140:'Kane',60141:'Cook',60142:'McHenry',60143:'Dupage',60144:'Kane',60145:'Dekalb',60146:'Dekalb',60147:'Kane',60148:'Dupage',60150:'Dekalb',60151:'Kane',60152:'McHenry',60153:'Cook',60154:'Cook',60155:'Cook',60156:'McHenry',60157:'Dupage',60159:'Cook',60160:'Cook',60161:'Cook',60162:'Cook',60163:'Cook',60164:'Cook',60165:'Cook',60168:'Cook',60169:'Cook',60170:'Kane',60171:'Cook',60172:'Dupage',60173:'Cook',60174:'Kane',60175:'Kane',60176:'Cook',60177:'Kane',60178:'Dekalb',60179:'Cook',60180:'McHenry',60181:'Dupage',60183:'Kane',60184:'Dupage',60185:'Dupage',60186:'Dupage',60187:'Dupage',60188:'Dupage',60189:'Dupage',60190:'Dupage',60191:'Dupage',60192:'Cook',60193:'Cook',60194:'Cook',60195:'Cook',60196:'Cook',60197:'Dupage',60199:'Dupage',60201:'Cook',60202:'Cook',60203:'Cook',60204:'Cook',60208:'Cook',60209:'Cook',60290:'Cook',60301:'Cook',60302:'Cook',60303:'Cook',60304:'Cook',60305:'Cook',60399:'Dupage',60401:'Will',60402:'Cook',60403:'Will',60404:'Will',60406:'Cook',60407:'Grundy',60408:'Will',60409:'Cook',60410:'Will',60411:'Cook',60412:'Cook',60415:'Cook',60416:'Grundy',60417:'Will',60419:'Cook',60420:'Livingston',60421:'Will',60422:'Cook',60423:'Will',60424:'Grundy',60425:'Cook',60426:'Cook',60428:'Cook',60429:'Cook',60430:'Cook',60431:'Will',60432:'Will',60433:'Will',60434:'Will',60435:'Will',60436:'Will',60437:'Grundy',60438:'Cook',60439:'Cook',60440:'Will',60441:'Will',60442:'Will',60443:'Cook',60444:'Grundy',60445:'Cook',60446:'Will',60447:'Grundy',60448:'Will',60449:'Will',60450:'Grundy',60451:'Will',60452:'Cook',60453:'Cook',60454:'Cook',60455:'Cook',60456:'Cook',60457:'Cook',60458:'Cook',60459:'Cook',60460:'Livingston',60461:'Cook',60462:'Cook',60463:'Cook',60464:'Cook',60465:'Cook',60466:'Cook',60467:'Cook',60468:'Will',60469:'Cook',60470:'La Salle',60471:'Cook',60472:'Cook',60473:'Cook',60474:'Grundy',60475:'Cook',60476:'Cook',60477:'Cook',60478:'Cook',60479:'Grundy',60480:'Cook',60481:'Will',60482:'Cook',60484:'Will',60487:'Cook',60490:'Will',60491:'Will',60499:'Cook',60501:'Cook',60502:'Dupage',60503:'Will',60504:'Dupage',60505:'Kane',60506:'Kane',60507:'Kane',60510:'Kane',60511:'Kane',60512:'Kendall',60513:'Cook',60514:'Dupage',60515:'Dupage',60516:'Dupage',60517:'Dupage',60518:'La Salle',60519:'Dupage',60520:'Dekalb',60521:'Dupage',60522:'Dupage',60523:'Dupage',60525:'Cook',60526:'Cook',60527:'Dupage',60530:'Lee',60531:'La Salle',60532:'Dupage',60534:'Cook',60536:'Kendall',60537:'La Salle',60538:'Kendall',60539:'Kane',60540:'Dupage',60541:'Kendall',60542:'Kane',60543:'Kendall',60544:'Will',60545:'Kendall',60546:'Cook',60548:'Dekalb',60549:'La Salle',60550:'Dekalb',60551:'La Salle',60552:'Dekalb',60553:'Lee',60554:'Kane',60555:'Dupage',60556:'Dekalb',60557:'La Salle',60558:'Cook',60559:'Dupage',60560:'Kendall',60561:'Dupage',60563:'Dupage',60564:'Will',60565:'Dupage',60566:'Dupage',60567:'Dupage',60568:'Kane',60570:'Dupage',60572:'Kane',60585:'Will',60586:'Will',60597:'Dupage',60598:'Kane',60599:'Dupage',60601:'Cook',60602:'Cook',60603:'Cook',60604:'Cook',60605:'Cook',60606:'Cook',60607:'Cook',60608:'Cook',60609:'Cook',60610:'Cook',60611:'Cook',60612:'Cook',60613:'Cook',60614:'Cook',60615:'Cook',60616:'Cook',60617:'Cook',60618:'Cook',60619:'Cook',60620:'Cook',60621:'Cook',60622:'Cook',60623:'Cook',60624:'Cook',60625:'Cook',60626:'Cook',60628:'Cook',60629:'Cook',60630:'Cook',60631:'Cook',60632:'Cook',60633:'Cook',60634:'Cook',60636:'Cook',60637:'Cook',60638:'Cook',60639:'Cook',60640:'Cook',60641:'Cook',60642:'Cook',60643:'Cook',60644:'Cook',60645:'Cook',60646:'Cook',60647:'Cook',60649:'Cook',60651:'Cook',60652:'Cook',60653:'Cook',60654:'Cook',60655:'Cook',60656:'Cook',60657:'Cook',60659:'Cook',60660:'Cook',60661:'Cook',60663:'Cook',60664:'Cook',60666:'Cook',60668:'Cook',60669:'Cook',60670:'Cook',60673:'Cook',60674:'Cook',60675:'Cook',60677:'Cook',60678:'Cook',60679:'Cook',60680:'Cook',60681:'Cook',60682:'Cook',60684:'Cook',60685:'Cook',60686:'Cook',60687:'Cook',60688:'Cook',60689:'Cook',60690:'Cook',60691:'Cook',60693:'Cook',60694:'Cook',60695:'Cook',60696:'Cook',60697:'Cook',60699:'Cook',60701:'Cook',60706:'Cook',60707:'Cook',60712:'Cook',60714:'Cook',60803:'Cook',60804:'Cook',60805:'Cook',60827:'Cook',60901:'Kankakee',60910:'Kankakee',60911:'Iroquois',60912:'Iroquois',60913:'Kankakee',60914:'Kankakee',60915:'Kankakee',60917:'Kankakee',60918:'Iroquois',60919:'Ford',60920:'Livingston',60921:'Livingston',60922:'Kankakee',60924:'Iroquois',60926:'Iroquois',60927:'Iroquois',60928:'Iroquois',60929:'Livingston',60930:'Iroquois',60931:'Iroquois',60932:'Vermilion',60933:'Ford',60934:'Livingston',60935:'Kankakee',60936:'Ford',60938:'Iroquois',60939:'Iroquois',60940:'Kankakee',60941:'Kankakee',60942:'Vermilion',60944:'Kankakee',60945:'Iroquois',60946:'Ford',60948:'Iroquois',60949:'Champaign',60950:'Kankakee',60951:'Iroquois',60952:'Ford',60953:'Iroquois',60954:'Kankakee',60955:'Iroquois',60956:'Iroquois',60957:'Ford',60958:'Kankakee',60959:'Ford',60960:'Vermilion',60961:'Kankakee',60962:'Ford',60963:'Vermilion',60964:'Kankakee',60966:'Iroquois',60967:'Iroquois',60968:'Iroquois',60969:'Kankakee',60970:'Iroquois',60973:'Iroquois',60974:'Iroquois',61001:'Jo Daviess',61006:'Lee',61007:'Ogle',61008:'Boone',61010:'Ogle',61011:'Boone',61012:'Boone',61013:'Stephenson',61014:'Carroll',61015:'Ogle',61016:'Winnebago',61018:'Stephenson',61019:'Stephenson',61020:'Ogle',61021:'Lee',61024:'Winnebago',61025:'Jo Daviess',61027:'Stephenson',61028:'Jo Daviess',61030:'Ogle',61031:'Lee',61032:'Stephenson',61036:'Jo Daviess',61037:'Whiteside',61038:'Boone',61039:'Stephenson',61041:'Jo Daviess',61042:'Lee',61043:'Ogle',61044:'Stephenson',61046:'Carroll',61047:'Ogle',61048:'Stephenson',61049:'Ogle',61050:'Stephenson',61051:'Carroll',61052:'Ogle',61053:'Carroll',61054:'Ogle',61057:'Lee',61059:'Jo Daviess',61060:'Stephenson',61061:'Ogle',61062:'Stephenson',61063:'Winnebago',61064:'Ogle',61065:'Boone',61067:'Stephenson',61068:'Ogle',61070:'Stephenson',61071:'Whiteside',61072:'Winnebago',61073:'Winnebago',61074:'Carroll',61075:'Jo Daviess',61077:'Winnebago',61078:'Carroll',61079:'Winnebago',61080:'Winnebago',61081:'Whiteside',61084:'Ogle',61085:'Jo Daviess',61087:'Jo Daviess',61088:'Winnebago',61089:'Stephenson',61091:'Ogle',61101:'Winnebago',61102:'Winnebago',61103:'Winnebago',61104:'Winnebago',61105:'Winnebago',61106:'Winnebago',61107:'Winnebago',61108:'Winnebago',61109:'Winnebago',61110:'Winnebago',61111:'Winnebago',61112:'Winnebago',61114:'Winnebago',61115:'Winnebago',61125:'Winnebago',61126:'Winnebago',61130:'Winnebago',61131:'Winnebago',61132:'Winnebago',61201:'Rock Island',61204:'Rock Island',61230:'Whiteside',61231:'Mercer',61232:'Rock Island',61233:'Henry',61234:'Henry',61235:'Henry',61236:'Rock Island',61237:'Rock Island',61238:'Henry',61239:'Rock Island',61240:'Rock Island',61241:'Henry',61242:'Rock Island',61243:'Whiteside',61244:'Rock Island',61250:'Whiteside',61251:'Whiteside',61252:'Whiteside',61254:'Henry',61256:'Rock Island',61257:'Rock Island',61258:'Henry',61259:'Rock Island',61260:'Mercer',61261:'Whiteside',61262:'Henry',61263:'Mercer',61264:'Rock Island',61265:'Rock Island',61266:'Rock Island',61270:'Whiteside',61272:'Mercer',61273:'Henry',61274:'Henry',61275:'Rock Island',61276:'Mercer',61277:'Whiteside',61278:'Rock Island',61279:'Mercer',61281:'Mercer',61282:'Rock Island',61283:'Whiteside',61284:'Rock Island',61285:'Carroll',61299:'Rock Island',61301:'La Salle',61310:'Lee',61311:'Livingston',61312:'Bureau',61313:'Livingston',61314:'Bureau',61315:'Bureau',61316:'La Salle',61317:'Bureau',61318:'Lee',61319:'Livingston',61320:'Bureau',61321:'La Salle',61322:'Bureau',61323:'Bureau',61324:'Lee',61325:'La Salle',61326:'Putnam',61327:'Putnam',61328:'Bureau',61329:'Bureau',61330:'Bureau',61331:'Lee',61332:'La Salle',61333:'Livingston',61334:'La Salle',61335:'Putnam',61336:'Putnam',61337:'Bureau',61338:'Bureau',61340:'Putnam',61341:'La Salle',61342:'La Salle',61344:'Bureau',61345:'Bureau',61346:'Bureau',61348:'La Salle',61349:'Bureau',61350:'La Salle',61353:'Lee',61354:'La Salle',61356:'Bureau',61358:'La Salle',61359:'Bureau',61360:'La Salle',61361:'Bureau',61362:'Bureau',61363:'Putnam',61364:'La Salle',61367:'Lee',61368:'Bureau',61369:'Marshall',61370:'La Salle',61371:'La Salle',61372:'La Salle',61373:'La Salle',61374:'Bureau',61375:'Marshall',61376:'Bureau',61377:'Marshall',61378:'Lee',61379:'Bureau',61401:'Knox',61402:'Knox',61410:'Knox',61411:'McDonough',61412:'Warren',61413:'Henry',61414:'Knox',61415:'Warren',61416:'McDonough',61417:'Warren',61418:'Henderson',61419:'Henry',61420:'McDonough',61421:'Bureau',61422:'McDonough',61423:'Warren',61424:'Marshall',61425:'Henderson',61426:'Stark',61427:'Fulton',61428:'Knox',61430:'Knox',61431:'Fulton',61432:'Fulton',61433:'Fulton',61434:'Henry',61435:'Warren',61436:'Knox',61437:'Henderson',61438:'McDonough',61439:'Knox',61440:'McDonough',61441:'Fulton',61442:'Mercer',61443:'Henry',61447:'Warren',61448:'Knox',61449:'Stark',61450:'Hancock',61451:'Peoria',61452:'Schuyler',61453:'Warren',61454:'Henderson',61455:'McDonough',61458:'Knox',61459:'Fulton',61460:'Henderson',61462:'Warren',61465:'Mercer',61466:'Mercer',61467:'Knox',61468:'Henry',61469:'Henderson',61470:'McDonough',61471:'Henderson',61472:'Knox',61473:'Warren',61474:'Knox',61475:'McDonough',61476:'Mercer',61477:'Fulton',61478:'Warren',61479:'Stark',61480:'Henderson',61482:'Fulton',61483:'Stark',61484:'Fulton',61485:'Knox',61486:'Mercer',61488:'Knox',61489:'Knox',61490:'Henry',61491:'Stark',61501:'Fulton',61516:'Woodford',61517:'Peoria',61519:'Fulton',61520:'Fulton',61523:'Peoria',61524:'Fulton',61525:'Peoria',61526:'Peoria',61528:'Peoria',61529:'Peoria',61530:'Woodford',61531:'Fulton',61532:'Mason',61533:'Peoria',61534:'Tazewell',61535:'Tazewell',61536:'Peoria',61537:'Marshall',61539:'Peoria',61540:'Marshall',61541:'Marshall',61542:'Fulton',61543:'Fulton',61544:'Fulton',61545:'Woodford',61546:'Mason',61547:'Peoria',61548:'Woodford',61550:'Tazewell',61552:'Peoria',61553:'Fulton',61554:'Tazewell',61555:'Tazewell',61558:'Tazewell',61559:'Peoria',61560:'Putnam',61561:'Woodford',61562:'Peoria',61563:'Fulton',61564:'Tazewell',61565:'Marshall',61567:'Mason',61568:'Tazewell',61569:'Peoria',61570:'Woodford',61571:'Tazewell',61572:'Knox',61601:'Peoria',61602:'Peoria',61603:'Peoria',61604:'Peoria',61605:'Peoria',61606:'Peoria',61607:'Peoria',61610:'Tazewell',61611:'Tazewell',61612:'Peoria',61613:'Peoria',61614:'Peoria',61615:'Peoria',61616:'Peoria',61625:'Peoria',61629:'Peoria',61630:'Peoria',61633:'Peoria',61634:'Peoria',61635:'Peoria',61636:'Peoria',61637:'Peoria',61638:'Peoria',61639:'Peoria',61641:'Peoria',61643:'Peoria',61650:'Peoria',61651:'Peoria',61652:'Peoria',61653:'Peoria',61654:'Peoria',61655:'Peoria',61656:'Peoria',61701:'McLean',61702:'Mclean',61704:'McLean',61705:'McLean',61709:'Mclean',61710:'Mclean',61720:'McLean',61721:'Tazewell',61722:'McLean',61723:'Logan',61724:'McLean',61725:'McLean',61726:'McLean',61727:'De Witt',61728:'McLean',61729:'Woodford',61730:'McLean',61731:'McLean',61732:'McLean',61733:'Woodford',61734:'Tazewell',61735:'De Witt',61736:'McLean',61737:'McLean',61738:'Woodford',61739:'Livingston',61740:'Livingston',61741:'Livingston',61742:'Woodford',61743:'Livingston',61744:'McLean',61745:'McLean',61747:'Tazewell',61748:'McLean',61749:'De Witt',61750:'De Witt',61751:'Logan',61752:'McLean',61753:'McLean',61754:'McLean',61755:'Tazewell',61756:'Macon',61758:'Mclean',61759:'Tazewell',61760:'Woodford',61761:'McLean',61764:'Livingston',61769:'Livingston',61770:'McLean',61771:'Woodford',61772:'McLean',61773:'Ford',61774:'McLean',61775:'Livingston',61776:'McLean',61777:'De Witt',61778:'De Witt',61790:'Mclean',61791:'Mclean',61799:'Mclean',61801:'Champaign',61802:'Champaign',61803:'Champaign',61810:'Vermilion',61811:'Vermilion',61812:'Vermilion',61813:'Piatt',61814:'Vermilion',61815:'Champaign',61816:'Champaign',61817:'Vermilion',61818:'Piatt',61820:'Champaign',61821:'Champaign',61822:'Champaign',61824:'Champaign',61825:'Champaign',61826:'Champaign',61830:'Piatt',61831:'Vermilion',61832:'Vermilion',61833:'Vermilion',61834:'Vermilion',61839:'Piatt',61840:'Champaign',61841:'Vermilion',61842:'De Witt',61843:'Champaign',61844:'Vermilion',61845:'Champaign',61846:'Vermilion',61847:'Champaign',61848:'Vermilion',61849:'Champaign',61850:'Vermilion',61851:'Champaign',61852:'Champaign',61853:'Champaign',61854:'Piatt',61855:'Piatt',61856:'Piatt',61857:'Vermilion',61858:'Vermilion',61859:'Champaign',61862:'Champaign',61863:'Champaign',61864:'Champaign',61865:'Vermilion',61866:'Champaign',61870:'Vermilion',61871:'Champaign',61872:'Champaign',61873:'Champaign',61874:'Champaign',61875:'Champaign',61876:'Vermilion',61877:'Champaign',61878:'Champaign',61880:'Champaign',61882:'De Witt',61883:'Vermilion',61884:'Piatt',61910:'Douglas',61911:'Douglas',61912:'Coles',61913:'Douglas',61914:'Moultrie',61917:'Edgar',61919:'Douglas',61920:'Coles',61924:'Edgar',61925:'Moultrie',61928:'Moultrie',61929:'Piatt',61930:'Douglas',61931:'Coles',61932:'Edgar',61933:'Edgar',61936:'Piatt',61937:'Moultrie',61938:'Coles',61940:'Edgar',61941:'Douglas',61942:'Douglas',61943:'Coles',61944:'Edgar',61949:'Edgar',61951:'Moultrie',61953:'Douglas',61955:'Edgar',61956:'Douglas',61957:'Shelby',62001:'Madison',62002:'Madison',62006:'Calhoun',62009:'Macoupin',62010:'Madison',62011:'Fayette',62012:'Jersey',62013:'Calhoun',62014:'Macoupin',62015:'Montgomery',62016:'Greene',62017:'Montgomery',62018:'Madison',62019:'Bond',62021:'Madison',62022:'Jersey',62023:'Macoupin',62024:'Madison',62025:'Madison',62026:'Madison',62027:'Greene',62028:'Jersey',62030:'Jersey',62031:'Jersey',62032:'Montgomery',62033:'Macoupin',62034:'Madison',62035:'Madison',62036:'Calhoun',62037:'Jersey',62040:'Madison',62044:'Greene',62045:'Calhoun',62046:'Madison',62047:'Calhoun',62048:'Madison',62049:'Montgomery',62050:'Greene',62051:'Montgomery',62052:'Jersey',62053:'Calhoun',62054:'Greene',62056:'Montgomery',62058:'Madison',62059:'St. Clair',62060:'Madison',62061:'Madison',62062:'Madison',62063:'Macoupin',62065:'Calhoun',62067:'Madison',62069:'Macoupin',62070:'Calhoun',62071:'St. Clair',62074:'Madison',62075:'Montgomery',62076:'Montgomery',62077:'Montgomery',62078:'Greene',62079:'Macoupin',62080:'Fayette',62081:'Greene',62082:'Greene',62083:'Christian',62084:'Madison',62085:'Macoupin',62086:'Bond',62087:'Madison',62088:'Macoupin',62089:'Montgomery',62090:'Madison',62091:'Montgomery',62092:'Greene',62093:'Macoupin',62094:'Montgomery',62095:'Madison',62097:'Madison',62098:'Greene',62201:'St Clair',62202:'St. Clair',62203:'St Clair',62204:'St Clair',62205:'St Clair',62206:'St Clair',62207:'St Clair',62208:'St Clair',62214:'Washington',62215:'Clinton',62216:'Clinton',62217:'Randolph',62218:'Clinton',62219:'Clinton',62220:'St Clair',62221:'St Clair',62222:'St. Clair',62223:'St Clair',62224:'St. Clair',62225:'St Clair',62226:'St Clair',62230:'Clinton',62231:'Clinton',62232:'St Clair',62233:'Randolph',62234:'Madison',62236:'Monroe',62237:'Perry',62238:'Perry',62239:'St Clair',62240:'St Clair',62241:'Randolph',62242:'Randolph',62243:'St Clair',62244:'Monroe',62245:'Clinton',62246:'Bond',62247:'Fayette',62248:'Monroe',62249:'Madison',62250:'Clinton',62252:'Clinton',62253:'Bond',62254:'St Clair',62255:'St Clair',62256:'Monroe',62257:'St Clair',62258:'St Clair',62259:'Randolph',62260:'St Clair',62261:'Randolph',62262:'Fayette',62263:'Washington',62264:'St Clair',62265:'Clinton',62266:'Clinton',62268:'Washington',62269:'St Clair',62271:'Washington',62272:'Randolph',62273:'Bond',62274:'Perry',62275:'Bond',62277:'Randolph',62278:'Randolph',62279:'Monroe',62280:'Randolph',62281:'Madison',62282:'St Clair',62284:'Bond',62285:'St Clair',62286:'Randolph',62288:'Randolph',62289:'St Clair',62292:'Randolph',62293:'Clinton',62294:'Madison',62295:'Monroe',62297:'Randolph',62298:'Monroe',62301:'Adams',62305:'Adams',62306:'Adams',62311:'Hancock',62312:'Pike',62313:'Hancock',62314:'Pike',62316:'Hancock',62319:'Schuyler',62320:'Adams',62321:'Hancock',62323:'Pike',62324:'Adams',62325:'Adams',62326:'McDonough',62329:'Hancock',62330:'Hancock',62334:'Hancock',62336:'Hancock',62338:'Adams',62339:'Adams',62340:'Pike',62341:'Hancock',62343:'Pike',62344:'Schuyler',62345:'Pike',62346:'Adams',62347:'Adams',62348:'Adams',62349:'Adams',62351:'Adams',62352:'Pike',62353:'Brown',62354:'Hancock',62355:'Pike',62356:'Pike',62357:'Pike',62358:'Hancock',62359:'Adams',62360:'Adams',62361:'Pike',62362:'Pike',62363:'Pike',62365:'Adams',62366:'Pike',62367:'McDonough',62370:'Pike',62373:'Hancock',62374:'McDonough',62375:'Brown',62376:'Adams',62378:'Brown',62379:'Hancock',62380:'Hancock',62401:'Effingham',62410:'Wabash',62411:'Effingham',62413:'Crawford',62414:'Effingham',62417:'Lawrence',62418:'Fayette',62419:'Richland',62420:'Clark',62421:'Richland',62422:'Shelby',62423:'Clark',62424:'Effingham',62425:'Richland',62426:'Clay',62427:'Crawford',62428:'Cumberland',62431:'Shelby',62432:'Jasper',62433:'Crawford',62434:'Clay',62435:'Coles',62436:'Cumberland',62438:'Shelby',62439:'Lawrence',62440:'Coles',62441:'Clark',62442:'Clark',62443:'Effingham',62444:'Shelby',62445:'Jasper',62446:'Wayne',62447:'Cumberland',62448:'Jasper',62449:'Crawford',62450:'Richland',62451:'Crawford',62452:'Richland',62454:'Crawford',62458:'Fayette',62459:'Jasper',62460:'Lawrence',62461:'Effingham',62462:'Cumberland',62463:'Shelby',62464:'Crawford',62465:'Shelby',62466:'Lawrence',62467:'Effingham',62468:'Cumberland',62469:'Cumberland',62471:'Fayette',62473:'Effingham',62474:'Clark',62475:'Jasper',62476:'Edwards',62477:'Clark',62478:'Clark',62479:'Jasper',62480:'Jasper',62481:'Jasper',62501:'Macon',62510:'Christian',62512:'Logan',62513:'Macon',62514:'Macon',62515:'Sangamon',62517:'Christian',62518:'Logan',62519:'Logan',62520:'Sangamon',62521:'Macon',62522:'Macon',62523:'Macon',62524:'Macon',62525:'Macon',62526:'Macon',62530:'Sangamon',62531:'Christian',62532:'Macon',62533:'Montgomery',62534:'Shelby',62535:'Macon',62536:'Sangamon',62537:'Macon',62538:'Christian',62539:'Sangamon',62540:'Christian',62541:'Logan',62543:'Logan',62544:'Macon',62545:'Sangamon',62546:'Christian',62547:'Christian',62548:'Logan',62549:'Macon',62550:'Shelby',62551:'Macon',62553:'Shelby',62554:'Macon',62555:'Christian',62556:'Christian',62557:'Christian',62558:'Sangamon',62560:'Montgomery',62561:'Sangamon',62563:'Sangamon',62565:'Shelby',62567:'Christian',62568:'Christian',62570:'Christian',62571:'Shelby',62572:'Montgomery',62573:'Macon',62601:'Morgan',62610:'Scott',62611:'Cass',62612:'Cass',62613:'Menard',62615:'Sangamon',62617:'Mason',62618:'Cass',62621:'Scott',62622:'Cass',62624:'Schuyler',62625:'Sangamon',62626:'Macoupin',62627:'Cass',62628:'Morgan',62629:'Sangamon',62630:'Macoupin',62631:'Morgan',62633:'Mason',62634:'Logan',62635:'Logan',62638:'Morgan',62639:'Schuyler',62640:'Macoupin',62642:'Menard',62643:'Logan',62644:'Mason',62649:'Macoupin',62650:'Morgan',62651:'Morgan',62655:'Mason',62656:'Logan',62659:'Menard',62660:'Morgan',62661:'Sangamon',62662:'Sangamon',62663:'Scott',62664:'Mason',62665:'Morgan',62666:'Logan',62667:'Macoupin',62668:'Morgan',62670:'Sangamon',62671:'Logan',62672:'Macoupin',62673:'Menard',62674:'Macoupin',62675:'Menard',62677:'Sangamon',62681:'Schuyler',62682:'Mason',62683:'Macoupin',62684:'Sangamon',62685:'Macoupin',62688:'Menard',62689:'Sangamon',62690:'Macoupin',62691:'Cass',62692:'Morgan',62693:'Sangamon',62694:'Scott',62695:'Morgan',62701:'Sangamon',62702:'Sangamon',62703:'Sangamon',62704:'Sangamon',62705:'Sangamon',62706:'Sangamon',62707:'Sangamon',62708:'Sangamon',62711:'Sangamon',62712:'Sangamon',62713:'Sangamon',62715:'Sangamon',62716:'Sangamon',62719:'Sangamon',62721:'Sangamon',62722:'Sangamon',62723:'Sangamon',62726:'Sangamon',62736:'Sangamon',62739:'Sangamon',62746:'Sangamon',62756:'Sangamon',62757:'Sangamon',62761:'Sangamon',62762:'Sangamon',62763:'Sangamon',62764:'Sangamon',62765:'Sangamon',62766:'Sangamon',62767:'Sangamon',62769:'Sangamon',62776:'Sangamon',62777:'Sangamon',62781:'Sangamon',62786:'Sangamon',62791:'Sangamon',62794:'Sangamon',62796:'Sangamon',62801:'Marion',62803:'Washington',62805:'Franklin',62806:'Edwards',62807:'Marion',62808:'Washington',62809:'Wayne',62810:'Jefferson',62811:'Wabash',62812:'Franklin',62814:'Jefferson',62815:'Edwards',62816:'Jefferson',62817:'Hamilton',62818:'Edwards',62819:'Franklin',62820:'White',62821:'White',62822:'Franklin',62823:'Wayne',62824:'Clay',62825:'Franklin',62827:'White',62828:'Hamilton',62829:'Hamilton',62830:'Jefferson',62831:'Washington',62832:'Perry',62833:'Wayne',62834:'White',62835:'White',62836:'Franklin',62837:'Wayne',62838:'Fayette',62839:'Clay',62840:'Franklin',62842:'Wayne',62843:'Wayne',62844:'Edwards',62846:'Jefferson',62848:'Washington',62849:'Marion',62850:'Wayne',62851:'Wayne',62852:'Wabash',62853:'Marion',62854:'Marion',62855:'Wabash',62856:'Franklin',62857:'Fayette',62858:'Clay',62859:'Hamilton',62860:'Hamilton',62861:'White',62862:'White',62863:'Wabash',62864:'Jefferson',62865:'Franklin',62866:'Jefferson',62867:'Gallatin',62868:'Richland',62869:'White',62870:'Marion',62871:'Gallatin',62872:'Jefferson',62874:'Franklin',62875:'Marion',62876:'Washington',62877:'Washington',62878:'Wayne',62879:'Clay',62880:'Fayette',62881:'Marion',62882:'Marion',62883:'Jefferson',62884:'Franklin',62885:'Fayette',62886:'Wayne',62887:'Hamilton',62888:'Perry',62889:'Jefferson',62890:'Franklin',62891:'Franklin',62892:'Marion',62893:'Marion',62894:'Jefferson',62895:'Wayne',62896:'Franklin',62897:'Franklin',62898:'Jefferson',62899:'Clay',62901:'Jackson',62902:'Williamson',62903:'Jackson',62905:'Union',62906:'Union',62907:'Jackson',62908:'Massac',62909:'Johnson',62910:'Massac',62912:'Johnson',62914:'Alexander',62915:'Williamson',62916:'Jackson',62917:'Saline',62918:'Williamson',62919:'Hardin',62920:'Union',62921:'Williamson',62922:'Williamson',62923:'Johnson',62924:'Jackson',62926:'Union',62927:'Jackson',62928:'Pope',62930:'Saline',62931:'Hardin',62932:'Jackson',62933:'Williamson',62934:'Gallatin',62935:'Saline',62938:'Pope',62939:'Johnson',62940:'Jackson',62941:'Pulaski',62942:'Jackson',62943:'Johnson',62946:'Saline',62947:'Pope',62948:'Williamson',62949:'Williamson',62950:'Jackson',62951:'Williamson',62952:'Union',62953:'Pulaski',62954:'Gallatin',62955:'Hardin',62956:'Pulaski',62957:'Alexander',62958:'Jackson',62959:'Williamson',62960:'Massac',62961:'Union',62962:'Alexander',62963:'Pulaski',62964:'Pulaski',62965:'Saline',62966:'Jackson',62967:'Johnson',62969:'Alexander',62970:'Pulaski',62971:'Jackson',62972:'Johnson',62973:'Pulaski',62974:'Williamson',62975:'Jackson',62976:'Pulaski',62977:'Saline',62979:'Gallatin',62982:'Hardin',62983:'Franklin',62984:'Gallatin',62985:'Johnson',62987:'Saline',62988:'Alexander',62990:'Alexander',62992:'Pulaski',62993:'Alexander',62994:'Jackson',62995:'Johnson',62996:'Pulaski',62997:'Perry',62998:'Union',62999:'Franklin'}
postcode_city_mapping = {61440: [u'Industry'], 61441: [u'Ipava'], 61442: [u'Keithsburg'], 61443: [u'Kewanee'], 61447: [u'Kirkwood'], 61448: [u'Knoxville'], 61449: [u'La Fayette'], 61450: [u'La Harpe'], 61451: [u'Laura'], 61452: [u'Littleton'], 61453: [u'Little York'], 61454: [u'Lomax'], 61455: [u'Macomb'], 61458: [u'Maquon'], 61459: [u'Marietta'], 61460: [u'Media'], 61462: [u'Monmouth'], 61465: [u'New Windsor'], 61466: [u'North Henderson', u'N Henderson'], 61467: [u'Oneida'], 61468: [u'Ophiem'], 61469: [u'Oquawka'], 61470: [u'Prairie City'], 61471: [u'Raritan'], 61472: [u'Rio'], 61473: [u'Roseville'], 61474: [u'Saint Augustine', u'St Augustine'], 61475: [u'Sciota', u'Blandinsville'], 61476: [u'Seaton'], 61477: [u'Smithfield'], 61478: [u'Smithshire'], 61479: [u'Speer'], 61480: [u'Stronghurst'], 61482: [u'Table Grove'], 61483: [u'Toulon'], 61484: [u'Vermont'], 61485: [u'Victoria'], 61486: [u'Viola'], 61488: [u'Wataga'], 61489: [u'Williamsfield'], 61490: [u'Woodhull'], 61491: [u'Wyoming'], 61501: [u'Astoria'], 61516: [u'Benson'], 61517: [u'Brimfield'], 61519: [u'Bryant'], 61520: [u'Canton', u'Banner'], 61523: [u'Chillicothe'], 61524: [u'Dunfermline'], 61525: [u'Dunlap'], 61526: [u'Edelstein'], 61528: [u'Edwards'], 61529: [u'Elmwood'], 61530: [u'Eureka'], 61531: [u'Farmington', u'Middlegrove'], 61532: [u'Forest City'], 61533: [u'Glasford'], 61534: [u'Green Valley'], 61535: [u'Groveland'], 61536: [u'Hanna City'], 61537: [u'Henry'], 61539: [u'Kingston Mines', u'Kingston Mine'], 61540: [u'Lacon'], 61541: [u'La Rose'], 61542: [u'Lewistown'], 61543: [u'Liverpool'], 61544: [u'London Mills'], 61545: [u'Lowpoint', u'Cazenovia'], 61546: [u'Manito'], 61547: [u'Mapleton'], 61548: [u'Metamora', u'Germantown Hills', u'Germantwn Hls'], 61550: [u'Morton'], 61552: [u'Mossville'], 61553: [u'Norris'], 61554: [u'Pekin', u'Marquette Heights', u'Marquette Hts', u'North ...'], 61555: [u'Pekin'], 61558: [u'Pekin'], 61559: [u'Princeville'], 61560: [u'Putnam'], 61561: [u'Roanoke'], 61562: [u'Rome'], 61563: [u'Saint David'], 61564: [u'South Pekin'], 61565: [u'Sparland', u'Hopewell'], 61567: [u'Topeka'], 61568: [u'Tremont'], 61569: [u'Trivoli'], 61570: [u'Washburn'], 61571: [u'Washington'], 61572: [u'Yates City'], 61601: [u'Peoria'], 61602: [u'Peoria'], 61603: [u'Peoria'], 61604: [u'Peoria', u'Bellevue', u'West Peoria'], 61605: [u'Peoria'], 61606: [u'Peoria'], 61607: [u'Peoria', u'Bartonville'], 61610: [u'Creve Coeur', u'Peoria'], 61611: [u'East Peoria', u'Bayview Garde', u'Bayview Gardens', u'Peoria', u'...'], 61612: [u'Peoria'], 61613: [u'Peoria'], 61614: [u'Peoria'], 61615: [u'Peoria'], 61616: [u'Peoria Heights', u'Peoria', u'Peoria Hts'], 61625: [u'Peoria'], 61629: [u'Peoria'], 61630: [u'Peoria', u'East Peoria'], 61633: [u'Peoria'], 61634: [u'Peoria'], 61635: [u'East Peoria', u'Peoria'], 61636: [u'Peoria'], 61637: [u'Peoria'], 61638: [u'Peoria'], 61639: [u'Peoria'], 61641: [u'Peoria'], 61643: [u'Peoria'], 61650: [u'Peoria'], 61651: [u'Peoria'], 61652: [u'Peoria'], 61653: [u'Peoria'], 61654: [u'Peoria'], 61655: [u'Peoria'], 61656: [u'Peoria'], 61701: [u'Bloomington'], 61702: [u'Bloomington'], 61704: [u'Bloomington'], 61705: [u'Bloomington'], 61709: [u'Bloomington'], 61710: [u'Bloomington'], 61720: [u'Anchor'], 61721: [u'Armington'], 61722: [u'Arrowsmith'], 61723: [u'Atlanta'], 61724: [u'Bellflower'], 61725: [u'Carlock'], 61726: [u'Chenoa'], 61727: [u'Clinton'], 61728: [u'Colfax'], 61729: [u'Congerville'], 61730: [u'Cooksville'], 61731: [u'Cropsey'], 61732: [u'Danvers'], 61733: [u'Deer Creek'], 61734: [u'Delavan'], 61735: [u'Dewitt', u'De Witt'], 61736: [u'Downs', u'Holder'], 61737: [u'Ellsworth'], 61738: [u'El Paso', u'Kappa', u'Panola'], 61739: [u'Fairbury'], 61740: [u'Flanagan'], 61741: [u'Forrest'], 61742: [u'Goodfield'], 61743: [u'Graymont'], 61744: [u'Gridley'], 61745: [u'Heyworth'], 61747: [u'Hopedale'], 61748: [u'Hudson'], 61749: [u'Kenney'], 61750: [u'Lane'], 61751: [u'Lawndale'], 61752: [u'Le Roy'], 61753: [u'Lexington'], 61754: [u'Mc Lean'], 61755: [u'Mackinaw'], 61756: [u'Maroa'], 61758: [u'Merna'], 61759: [u'Minier'], 61760: [u'Minonk'], 61761: [u'Normal', u'Merna'], 61764: [u'Pontiac'], 61769: [u'Saunemin'], 61770: [u'Saybrook'], 61771: [u'Secor'], 61772: [u'Shirley'], 61773: [u'Sibley'], 61774: [u'Stanford'], 61775: [u'Strawn'], 61776: [u'Towanda'], 61777: [u'Wapella'], 61778: [u'Waynesville'], 61790: [u'Normal'], 61791: [u'Bloomington'], 61799: [u'Bloomington'], 61801: [u'Urbana'], 61802: [u'Urbana'], 61803: [u'Urbana'], 61810: [u'Allerton'], 61811: [u'Alvin'], 61812: [u'Armstrong'], 61813: [u'Bement'], 61814: [u'Bismarck'], 61815: [u'Bondville'], 61816: [u'Broadlands'], 61817: [u'Catlin'], 61818: [u'Cerro Gordo'], 61820: [u'Champaign'], 61821: [u'Champaign'], 61822: [u'Champaign'], 61824: [u'Champaign'], 61825: [u'Champaign'], 61826: [u'Champaign'], 61830: [u'Cisco'], 61831: [u'Collison'], 61832: [u'Danville'], 61833: [u'Tilton', u'Danville'], 61834: [u'Danville'], 61839: [u'De Land'], 61840: [u'Dewey'], 61841: [u'Fairmount'], 61842: [u'Farmer City'], 61843: [u'Fisher'], 61844: [u'Fithian'], 61845: [u'Foosland'], 61846: [u'Georgetown'], 61847: [u'Gifford'], 61848: [u'Henning'], 61849: [u'Homer'], 61850: [u'Indianola'], 61851: [u'Ivesdale'], 61852: [u'Longview'], 61853: [u'Mahomet'], 61854: [u'Mansfield'], 61855: [u'Milmine'], 61856: [u'Monticello', u'Lodge'], 61857: [u'Muncie'], 61858: [u'Oakwood'], 61859: [u'Ogden'], 61862: [u'Penfield'], 61863: [u'Pesotum'], 61864: [u'Philo'], 61865: [u'Potomac'], 61866: [u'Rantoul'], 61870: [u'Ridge Farm'], 61871: [u'Royal'], 61872: [u'Sadorus'], 61873: [u'Saint Joseph'], 61874: [u'Savoy'], 61875: [u'Seymour'], 61876: [u'Sidell'], 61877: [u'Sidney'], 61878: [u'Thomasboro'], 61880: [u'Tolono'], 61882: [u'Weldon'], 61883: [u'Westville'], 61884: [u'White Heath'], 61910: [u'Arcola'], 61911: [u'Arthur', u'Cadwell'], 61912: [u'Ashmore'], 61913: [u'Atwood'], 61914: [u'Bethany'], 61917: [u'Brocton'], 61919: [u'Camargo'], 61920: [u'Charleston'], 61924: [u'Chrisman'], 61925: [u'Dalton City'], 61928: [u'Gays'], 61929: [u'Hammond', u'Pierson Sta', u'Pierson Station'], 61930: [u'Hindsboro'], 61931: [u'Humboldt'], 61932: [u'Hume'], 61933: [u'Kansas'], 61936: [u'La Place'], 61937: [u'Lovington', u'Lake City'], 61938: [u'Mattoon'], 61940: [u'Metcalf'], 61941: [u'Murdock'], 61942: [u'Newman'], 61943: [u'Oakland'], 61944: [u'Paris'], 61949: [u'Redmon'], 61951: [u'Sullivan', u'Allenville', u'Kirksville'], 61953: [u'Tuscola'], 61955: [u'Vermilion'], 61956: [u'Villa Grove'], 61957: [u'Windsor'], 62001: [u'Alhambra'], 62002: [u'Alton'], 62006: [u'Batchtown'], 62009: [u'Benld'], 62010: [u'Bethalto'], 62011: [u'Bingham'], 62012: [u'Brighton'], 62013: [u'Brussels', u'Meppen'], 62014: [u'Bunker Hill'], 62015: [u'Butler'], 62016: [u'Carrollton'], 62017: [u'Coffeen'], 62018: [u'Cottage Hills'], 62019: [u'Donnellson'], 62021: [u'Dorsey'], 62022: [u'Dow'], 62023: [u'Eagarville'], 62024: [u'East Alton'], 62025: [u'Edwardsville'], 62026: [u'Edwardsville'], 62027: [u'Eldred'], 62028: [u'Elsah'], 62030: [u'Fidelity'], 62031: [u'Fieldon'], 62032: [u'Fillmore'], 62033: [u'Gillespie', u'Dorchester'], 62034: [u'Glen Carbon'], 62035: [u'Godfrey'], 62036: [u'Golden Eagle'], 62037: [u'Grafton'], 62040: [u'Granite City', u'Mitchell', u'Pontoon Beach'], 62044: [u'Greenfield'], 62045: [u'Hamburg'], 62046: [u'Hamel'], 62047: [u'Hardin'], 62048: [u'Hartford'], 62049: [u'Hillsboro'], 62050: [u'Hillview'], 62051: [u'Irving'], 62052: [u'Jerseyville', u'Otterville'], 62053: [u'Kampsville'], 62054: [u'Kane'], 62056: [u'Litchfield'], 62058: [u'Livingston'], 62059: [u'Lovejoy', u'Brooklyn'], 62060: [u'Madison'], 62061: [u'Marine'], 62062: [u'Maryville'], 62063: [u'Medora'], 62065: [u'Michael'], 62067: [u'Moro'], 62069: [u'Mount Olive'], 62070: [u'Mozier'], 62071: [u'National Stock Yards', u'Natl Stock Yd'], 62074: [u'New Douglas'], 62075: [u'Nokomis'], 62076: [u'Ohlman'], 62077: [u'Panama'], 62078: [u'Patterson'], 62079: [u'Piasa'], 62080: [u'Ramsey'], 62081: [u'Rockbridge'], 62082: [u'Roodhouse'], 62083: [u'Rosamond'], 62084: [u'Roxana'], 62085: [u'Sawyerville'], 62086: [u'Sorento'], 62087: [u'South Roxana'], 62088: [u'Staunton'], 62089: [u'Taylor Springs', u'Taylor Spgs'], 62090: [u'Venice'], 62091: [u'Walshville'], 62092: [u'White Hall'], 62093: [u'Wilsonville'], 62094: [u'Witt'], 62095: [u'Wood River'], 62097: [u'Worden'], 62098: [u'Wrights'], 62201: [u'East Saint Louis', u'E Saint Louis', u'Fairmont City', u'Sauget'], 62202: [u'East Saint Louis', u'E Saint Louis'], 62203: [u'East Saint Louis', u'Centreville', u'E Saint Louis'], 62204: [u'East Saint Louis', u'E Saint Louis', u'Washington Pk'], 62205: [u'East Saint Louis', u'Centreville', u'E Saint Louis'], 62206: [u'East Saint Louis', u'Cahokia', u'E Saint Louis', u'Sauget'], 62207: [u'East Saint Louis', u'Alorton', u'Centreville', u'E Saint Louis'], 62208: [u'Fairview Heights', u'E Saint Louis', u'East Saint Louis', u'Fairvie...'], 62214: [u'Addieville', u'Venedy'], 62215: [u'Albers', u'Damiansville'], 62216: [u'Aviston'], 62217: [u'Baldwin'], 62218: [u'Bartelso'], 62219: [u'Beckemeyer'], 62220: [u'Belleville', u'Swansea'], 62221: [u'Belleville', u'Swansea'], 62222: [u'Belleville'], 62223: [u'Belleville', u'Swansea'], 62224: [u'Mascoutah'], 62225: [u'Scott Air Force Base', u'Scott Afb'], 62226: [u'Belleville', u'Swansea'], 62230: [u'Breese'], 62231: [u'Carlyle', u'Shattuc'], 62232: [u'Caseyville'], 62233: [u'Chester'], 62234: [u'Collinsville'], 62236: [u'Columbia'], 62237: [u'Coulterville', u'Swanwick'], 62238: [u'Cutler'], 62239: [u'Dupo'], 62240: [u'East Carondelet', u'E Carondelet'], 62241: [u'Ellis Grove'], 62242: [u'Evansville'], 62243: [u'Freeburg'], 62244: [u'Fults'], 62245: [u'Germantown'], 62246: [u'Greenville'], 62247: [u'Hagarstown'], 62248: [u'Hecker'], 62249: [u'Highland'], 62250: [u'Hoffman'], 62252: [u'Huey'], 62253: [u'Keyesport'], 62254: [u'Lebanon'], 62255: [u'Lenzburg'], 62256: [u'Maeystown'], 62257: [u'Marissa'], 62258: [u'Mascoutah', u'Fayetteville'], 62259: [u'Menard'], 62260: [u'Millstadt'], 62261: [u'Modoc', u'Pr Du Rocher', u'Prairie Du Rocher'], 62262: [u'Mulberry Grove', u'Mulberry Grv'], 62263: [u'Nashville'], 62264: [u'New Athens'], 62265: [u'New Baden'], 62266: [u'New Memphis'], 62268: [u'Oakdale'], 62269: [u'O Fallon', u'Belleville', u'Shiloh'], 62271: [u'Okawville'], 62272: [u'Percy'], 62273: [u'Pierron'], 62274: [u'Pinckneyville'], 62275: [u'Pocahontas'], 62277: [u'Prairie Du Rocher', u'Pr Du Rocher'], 62278: [u'Red Bud', u'Redbud', u'Ruma'], 62279: [u'Renault'], 62280: [u'Rockwood'], 62281: [u'Saint Jacob'], 62282: [u'Saint Libory'], 62284: [u'Smithboro'], 62285: [u'Smithton'], 62286: [u'Sparta'], 62288: [u'Steeleville'], 62289: [u'Summerfield'], 62292: [u'Tilden'], 62293: [u'Trenton'], 62294: [u'Troy'], 62295: [u'Valmeyer'], 62297: [u'Walsh'], 62298: [u'Waterloo'], 62301: [u'Quincy'], 62305: [u'Quincy'], 62306: [u'Quincy'], 62311: [u'Augusta'], 62312: [u'Barry'], 62313: [u'Basco'], 62314: [u'Baylis'], 62316: [u'Bowen'], 62319: [u'Camden'], 62320: [u'Camp Point', u'Columbus'], 62321: [u'Carthage'], 62323: [u'Chambersburg'], 62324: [u'Clayton'], 62325: [u'Coatsburg'], 62326: [u'Colchester'], 62329: [u'Colusa'], 62330: [u'Dallas City', u'Adrian', u'Burnside', u'Pontoosuc'], 62334: [u'Elvaston'], 62336: [u'Ferris'], 62338: [u'Fowler'], 62339: [u'Golden'], 62340: [u'Griggsville'], 62341: [u'Hamilton'], 62343: [u'Hull'], 62344: [u'Huntsville'], 62345: [u'Kinderhook'], 62346: [u'La Prairie'], 62347: [u'Liberty'], 62348: [u'Lima'], 62349: [u'Loraine'], 62351: [u'Mendon'], 62352: [u'Milton'], 62353: [u'Mount Sterling', u'Mt Sterling'], 62354: [u'Nauvoo'], 62355: [u'Nebo'], 62356: [u'New Canton'], 62357: [u'New Salem'], 62358: [u'Niota'], 62359: [u'Paloma'], 62360: [u'Payson'], 62361: [u'Pearl'], 62362: [u'Perry'], 62363: [u'Pittsfield', u'Detroit', u'Summer Hill'], 62365: [u'Plainville'], 62366: [u'Pleasant Hill'], 62367: [u'Plymouth', u'Colmar'], 62370: [u'Rockport'], 62373: [u'Sutter'], 62374: [u'Tennessee'], 62375: [u'Timewell'], 62376: [u'Ursa'], 62378: [u'Versailles'], 62379: [u'Warsaw'], 62380: [u'West Point'], 62401: [u'Effingham'], 62410: [u'Allendale'], 62411: [u'Altamont'], 62413: [u'Annapolis'], 62414: [u'Beecher City'], 62417: [u'Bridgeport'], 62418: [u'Brownstown'], 62419: [u'Calhoun'], 62420: [u'Casey'], 62421: [u'Claremont'], 62422: [u'Cowden'], 62423: [u'Dennison'], 62424: [u'Dieterich'], 62425: [u'Dundas'], 62426: [u'Edgewood', u'Laclede'], 62427: [u'Flat Rock', u'Birds'], 62428: [u'Greenup', u'Hazel Dell'], 62431: [u'Herrick'], 62432: [u'Hidalgo'], 62433: [u'Hutsonville'], 62434: [u'Ingraham'], 62435: [u'Janesville'], 62436: [u'Jewett'], 62438: [u'Lakewood'], 62439: [u'Lawrenceville'], 62440: [u'Lerna', u'Janesville'], 62441: [u'Marshall'], 62442: [u'Martinsville'], 62443: [u'Mason'], 62444: [u'Mode', u'Beecher City'], 62445: [u'Montrose'], 62446: [u'Mount Erie'], 62447: [u'Neoga'], 62448: [u'Newton'], 62449: [u'Oblong'], 62450: [u'Olney'], 62451: [u'Palestine'], 62452: [u'Parkersburg'], 62454: [u'Robinson'], 62458: [u'Saint Elmo'], 62459: [u'Sainte Marie'], 62460: [u'Saint Francisville', u'St Francisvle'], 62461: [u'Shumway'], 62462: [u'Sigel'], 62463: [u'Stewardson'], 62464: [u'Stoy'], 62465: [u'Strasburg'], 62466: [u'Sumner'], 62467: [u'Teutopolis'], 62468: [u'Toledo'], 62469: [u'Trilla'], 62471: [u'Vandalia'], 62473: [u'Watson'], 62474: [u'Westfield'], 62475: [u'West Liberty'], 62476: [u'West Salem'], 62477: [u'West Union'], 62478: [u'West York'], 62479: [u'Wheeler'], 62480: [u'Willow Hill'], 62481: [u'Yale'], 62501: [u'Argenta', u'Newburg', u'Oakley'], 62510: [u'Assumption'], 62512: [u'Beason'], 62513: [u'Blue Mound'], 62514: [u'Boody'], 62515: [u'Buffalo', u'Buffalo Hart', u'Lanesville'], 62517: [u'Bulpitt'], 62518: [u'Chestnut'], 62519: [u'Cornland'], 62520: [u'Dawson'], 62521: [u'Decatur', u'Long Creek'], 62522: [u'Decatur'], 62523: [u'Decatur'], 62524: [u'Decatur'], 62525: [u'Decatur'], 62526: [u'Decatur', u'Bearsdale'], 62530: [u'Divernon', u'Cimic'], 62531: [u'Edinburg', u'Edenburg'], 62532: [u'Elwin'], 62533: [u'Farmersville'], 62534: [u'Findlay', u'Yantisville'], 62535: [u'Forsyth'], 62536: [u'Glenarm'], 62537: [u'Harristown'], 62538: [u'Harvel'], 62539: [u'Illiopolis'], 62540: [u'Kincaid'], 62541: [u'Lake Fork'], 62543: [u'Latham'], 62544: [u'Macon'], 62545: [u'Mechanicsburg', u'Bolivia', u'Roby'], 62546: [u'Morrisonville'], 62547: [u'Mount Auburn'], 62548: [u'Mount Pulaski'], 62549: [u'Mt Zion', u'Hervey City', u'Mount Zion'], 62550: [u'Moweaqua', u'Radford'], 62551: [u'Niantic'], 62553: [u'Oconee'], 62554: [u'Oreana'], 62555: [u'Owaneco'], 62556: [u'Palmer', u'Clarksdale'], 62557: [u'Pana', u'Dunkel', u'Millersville'], 62558: [u'Pawnee', u'Sicily'], 62560: [u'Raymond'], 62561: [u'Riverton', u'Spaulding'], 62563: [u'Rochester', u'Berry', u'Breckenridge', u'New City'], 62565: [u'Shelbyville', u'Clarksburg', u'Duvall', u'Henton', u'Middlesworth...'], 62567: [u'Stonington'], 62568: [u'Taylorville', u'Hewittsville', u'Jeiseyville', u'Langleyville', u'...'], 62570: [u'Tovey'], 62571: [u'Tower Hill', u'Dollville', u'Hinton'], 62572: [u'Waggoner', u'Atwater'], 62573: [u'Warrensburg', u'Heman'], 62601: [u'Alexander'], 62610: [u'Alsey'], 62611: [u'Arenzville'], 62612: [u'Ashland', u'Newmansville', u'Prentice', u'Yatesville'], 62613: [u'Athens', u'Fancy Prairie'], 62615: [u'Auburn'], 62617: [u'Bath', u'Lynchburg', u'Snicarte'], 62618: [u'Beardstown'], 62621: [u'Bluffs', u'Exeter'], 62622: [u'Bluff Springs'], 62624: [u'Browning', u'Bader', u'Bluff City'], 62625: [u'Cantrall'], 62626: [u'Carlinville', u'Comer', u'Enos', u'Womac'], 62627: [u'Chandlerville', u'Panther Creek'], 62628: [u'Chapin'], 62629: [u'Chatham'], 62630: [u'Chesterfield', u'Hagaman'], 62631: [u'Concord'], 62633: [u'Easton', u'Biggs', u'Poplar City'], 62634: [u'Elkhart', u'Broadwell'], 62635: [u'Emden'], 62638: [u'Franklin', u'Clements', u'Rees'], 62639: [u'Frederick'], 62640: [u'Girard', u'Mcvey', u'Standard City'], 62642: [u'Greenview', u'Hubly', u'Sweet Water'], 62643: [u'Hartsburg'], 62644: [u'Havana', u'Eckard', u'Enion'], 62649: [u'Hettick'], 62650: [u'Jacksonville', u'Arcadia', u'Arnold', u'Lynnville', u'Merritt', u'Pis...'], 62651: [u'Jacksonville'], 62655: [u'Kilbourne'], 62656: [u'Lincoln'], 62659: [u'Lincolns New Salem', u'Lincoln Nw Sl'], 62660: [u'Literberry'], 62661: [u'Loami'], 62662: [u'Lowder'], 62663: [u'Manchester'], 62664: [u'Mason City', u'Luther', u'Teheran'], 62665: [u'Meredosia', u'Naples'], 62666: [u'Middletown'], 62667: [u'Modesto'], 62668: [u'Murrayville', u'Nortonville'], 62670: [u'New Berlin', u'Bates', u'Berlin', u'Curran', u'Old Berlin'], 62671: [u'New Holland'], 62672: [u'Nilwood'], 62673: [u'Oakford'], 62674: [u'Palmyra', u'Barr'], 62675: [u'Petersburg', u'Atterberry', u'Tice'], 62677: [u'Pleasant Plains', u'Farmingdale', u'Pleasant Plns', u'Richland', u'Sa...'], 62681: [u'Rushville', u'Pleasant View', u'Ray'], 62682: [u'San Jose'], 62683: [u'Scottville'], 62684: [u'Sherman', u'Barclay'], 62685: [u'Shipman', u'Plainview', u'Royal Lakes'], 62688: [u'Tallula'], 62689: [u'Thayer'], 62690: [u'Virden'], 62691: [u'Virginia', u'Little Indian'], 62692: [u'Waverly'], 62693: [u'Williamsville'], 62694: [u'Winchester', u'Riggston'], 62695: [u'Woodson'], 62701: [u'Springfield'], 62702: [u'Springfield', u'Grandview'], 62703: [u'Springfield', u'Southern View'], 62704: [u'Springfield', u'Jerome', u'Leland Grove'], 62705: [u'Springfield'], 62706: [u'Springfield'], 62707: [u'Springfield', u'Andrew', u'Archer', u'Bissell', u'Bradfordton', u'Cl...'], 62708: [u'Springfield'], 62711: [u'Springfield'], 62712: [u'Springfield'], 62713: [u'Springfield'], 62715: [u'Springfield'], 62716: [u'Springfield'], 62719: [u'Springfield'], 62721: [u'Springfield'], 62722: [u'Springfield'], 62723: [u'Springfield'], 62726: [u'Springfield'], 62736: [u'Springfield'], 62739: [u'Springfield'], 62746: [u'Springfield'], 62756: [u'Springfield'], 62757: [u'Springfield'], 62761: [u'Springfield'], 62762: [u'Springfield'], 62763: [u'Springfield'], 62764: [u'Springfield'], 62765: [u'Springfield'], 62766: [u'Springfield'], 62767: [u'Springfield'], 62769: [u'Springfield'], 62776: [u'Springfield'], 62777: [u'Springfield'], 62781: [u'Springfield'], 62786: [u'Springfield'], 62791: [u'Springfield'], 62794: [u'Springfield'], 62796: [u'Springfield'], 62801: [u'Centralia'], 62803: [u'Hoyleton'], 62805: [u'Akin'], 62806: [u'Albion'], 62807: [u'Alma'], 62808: [u'Ashley'], 62809: [u'Barnhill'], 62810: [u'Belle Rive'], 62811: [u'Bellmont'], 62812: [u'Benton'], 62814: [u'Bluford'], 62815: [u'Bone Gap'], 62816: [u'Bonnie', u'Nason'], 62817: [u'Broughton', u'Dale'], 62818: [u'Browns'], 62819: [u'Buckner'], 62820: [u'Burnt Prairie'], 62821: [u'Carmi'], 62822: [u'Christopher'], 62823: [u'Cisne'], 62824: [u'Clay City'], 62825: [u'Coello'], 62827: [u'Crossville'], 62828: [u'Dahlgren'], 62829: [u'Dale'], 62830: [u'Dix'], 62831: [u'Du Bois'], 62832: [u'Du Quoin'], 62833: [u'Ellery'], 62834: [u'Emma'], 62835: [u'Enfield'], 62836: [u'Ewing'], 62837: [u'Fairfield'], 62838: [u'Farina', u'Iola', u'Loogootee'], 62839: [u'Flora'], 62840: [u'Frankfort Heights', u'Frankfort Hts'], 62842: [u'Geff'], 62843: [u'Golden Gate'], 62844: [u'Grayville'], 62846: [u'Ina'], 62848: [u'Irvington'], 62849: [u'Iuka'], 62850: [u'Johnsonville'], 62851: [u'Keenes'], 62852: [u'Keensburg'], 62853: [u'Kell'], 62854: [u'Kinmundy'], 62855: [u'Lancaster'], 62856: [u'Logan'], 62857: [u'Loogootee'], 62858: [u'Louisville', u'Bible Grove'], 62859: [u'Mc Leansboro', u'Dale'], 62860: [u'Macedonia'], 62861: [u'Maunie'], 62862: [u'Mill Shoals'], 62863: [u'Mount Carmel'], 62864: [u'Mount Vernon'], 62865: [u'Mulkeytown'], 62866: [u'Nason'], 62867: [u'New Haven'], 62868: [u'Noble'], 62869: [u'Norris City', u'Herald'], 62870: [u'Odin'], 62871: [u'Omaha'], 62872: [u'Opdyke'], 62874: [u'Orient'], 62875: [u'Patoka'], 62876: [u'Radom'], 62877: [u'Richview'], 62878: [u'Rinard'], 62879: [u'Sailor Springs', u'Sailor Spgs'], 62880: [u'Saint Peter'], 62881: [u'Salem'], 62882: [u'Sandoval'], 62883: [u'Scheller'], 62884: [u'Sesser'], 62885: [u'Shobonier'], 62886: [u'Sims'], 62887: [u'Springerton'], 62888: [u'Tamaroa'], 62889: [u'Texico'], 62890: [u'Thompsonville', u'Akin'], 62891: [u'Valier'], 62892: [u'Vernon'], 62893: [u'Walnut Hill'], 62894: [u'Waltonville'], 62895: [u'Wayne City'], 62896: [u'West Frankfort', u'W Frankfort'], 62897: [u'Whittington'], 62898: [u'Woodlawn'], 62899: [u'Xenia'], 62901: [u'Carbondale'], 62902: [u'Carbondale'], 62903: [u'Carbondale'], 62905: [u'Alto Pass'], 62906: [u'Anna'], 62907: [u'Ava'], 62908: [u'Belknap'], 62909: [u'Boles'], 62910: [u'Brookport', u'Hamletsburg', u'New Liberty'], 62912: [u'Buncombe'], 62914: [u'Cairo', u'Cache'], 62915: [u'Cambria'], 62916: [u'Campbell Hill'], 62917: [u'Carrier Mills'], 62918: [u'Carterville'], 62919: [u'Cave In Rock'], 62920: [u'Cobden'], 62921: [u'Colp'], 62922: [u'Creal Springs'], 62923: [u'Cypress'], 62924: [u'De Soto'], 62926: [u'Dongola'], 62927: [u'Dowell'], 62928: [u'Eddyville'], 62930: [u'Eldorado'], 62931: [u'Elizabethtown'], 62932: [u'Elkville'], 62933: [u'Energy'], 62934: [u'Equality'], 62935: [u'Galatia', u'Harco'], 62938: [u'Golconda', u'Brownfield', u'Temple Hill'], 62939: [u'Goreville'], 62940: [u'Gorham'], 62941: [u'Grand Chain'], 62942: [u'Grand Tower'], 62943: [u'Grantsburg'], 62946: [u'Harrisburg'], 62947: [u'Herod'], 62948: [u'Herrin'], 62949: [u'Hurst'], 62950: [u'Jacob'], 62951: [u'Johnston City'], 62952: [u'Jonesboro'], 62953: [u'Joppa'], 62954: [u'Junction'], 62955: [u'Karbers Ridge'], 62956: [u'Karnak'], 62957: [u'Mc Clure'], 62958: [u'Makanda'], 62959: [u'Marion'], 62960: [u'Metropolis'], 62961: [u'Millcreek'], 62962: [u'Miller City'], 62963: [u'Mound City'], 62964: [u'Mounds'], 62965: [u'Muddy'], 62966: [u'Murphysboro'], 62967: [u'New Burnside'], 62969: [u'Olive Branch'], 62970: [u'Olmsted'], 62971: [u'Oraville'], 62972: [u'Ozark', u'Tunnel Hill'], 62973: [u'Perks'], 62974: [u'Pittsburg'], 62975: [u'Pomona'], 62976: [u'Pulaski'], 62977: [u'Raleigh'], 62979: [u'Ridgway'], 62982: [u'Rosiclare'], 62983: [u'Royalton'], 62984: [u'Shawneetown'], 62985: [u'Simpson', u'Robbs'], 62987: [u'Stonefort'], 62988: [u'Tamms', u'Elco'], 62990: [u'Thebes', u'Gale'], 62992: [u'Ullin'], 62993: [u'Unity', u'Tamms'], 62994: [u'Vergennes'], 62995: [u'Vienna'], 62996: [u'Villa Ridge'], 62997: [u'Willisville'], 62998: [u'Wolf Lake'], 62999: [u'Zeigler'], 60001: [u'Alden'], 60002: [u'Antioch', u'Old Mill Creek', u'Old Mill Crk'], 60004: [u'Arlington Heights', u'Arlington Hts'], 60005: [u'Arlington Heights', u'Arlington Hts'], 60006: [u'Arlington Heights', u'Arlington Hts'], 60007: [u'Elk Grove Village', u'Elk Grove Vlg'], 60008: [u'Rolling Meadows', u'Rolling Mdws'], 60009: [u'Elk Grove Village', u'Elk Grove Vlg'], 60010: [u'Barrington', u'Deer Park', u'Fox River Valley Gardens', u'Fox...'], 60011: [u'Barrington'], 60012: [u'Crystal Lake', u'Bull Valley'], 60013: [u'Cary', u'Oakwood Hills', u'Trout Valley'], 60014: [u'Crystal Lake', u'Village Of Lakewood', u'Vlg Of Lakewd'], 60015: [u'Deerfield', u'Bannockburn', u'Riverwoods'], 60016: [u'Des Plaines'], 60017: [u'Des Plaines'], 60018: [u'Des Plaines', u'Rosemont'], 60019: [u'Des Plaines', u'Rosemont'], 60020: [u'Fox Lake', u'Volo'], 60021: [u'Fox River Grove', u'Fox River Grv'], 60022: [u'Glencoe'], 60025: [u'Glenview'], 60026: [u'Glenview'], 60029: [u'Golf'], 60030: [u'Grayslake', u'Gages Lake', u'Hainesville', u'Third Lake', u'Vol...'], 60031: [u'Gurnee'], 60033: [u'Harvard'], 60034: [u'Hebron'], 60035: [u'Highland Park'], 60037: [u'Fort Sheridan', u'Highland Park'], 60038: [u'Palatine'], 60039: [u'Crystal Lake'], 60040: [u'Highwood'], 60041: [u'Ingleside', u'Volo'], 60042: [u'Island Lake'], 60043: [u'Kenilworth'], 60044: [u'Lake Bluff'], 60045: [u'Lake Forest', u'Mettawa'], 60046: [u'Lake Villa', u'Lindenhurst', u'Old Mill Creek', u'Old Mill Cr...'], 60047: [u'Lake Zurich', u'Hawthorn Wds', u'Hawthorn Woods', u'Kildeer', u'L...'], 60048: [u'Libertyville'], 60049: [u'Lake Zurich', u'Long Grove'], 60050: [u'Mchenry', u'Bull Valley', u'Holiday Hills', u'Johnsburg', u'L...'], 60051: [u'Mchenry', u'Holiday Hills', u'Johnsburg', u'Lakemoor', u'Volo'], 60053: [u'Morton Grove'], 60055: [u'Palatine'], 60056: [u'Mount Prospect', u'Mt Prospect'], 60060: [u'Mundelein', u'Long Grove'], 60061: [u'Vernon Hills', u'Indian Creek'], 60062: [u'Northbrook'], 60064: [u'North Chicago', u'Abbott Park', u'Downey'], 60065: [u'Northbrook'], 60067: [u'Palatine', u'Hoffman Est', u'Hoffman Estates', u'Inverness'], 60068: [u'Park Ridge'], 60069: [u'Lincolnshire', u'Prairie View', u'Prairieview'], 60070: [u'Prospect Heights', u'Prospect Hts'], 60071: [u'Richmond', u'Solon Mills'], 60072: [u'Ringwood'], 60073: [u'Round Lake', u'Hainesville', u'Round Lake Beach', u'Round Lak...'], 60074: [u'Palatine', u'Kildeer'], 60075: [u'Russell'], 60076: [u'Skokie'], 60077: [u'Skokie'], 60078: [u'Palatine'], 60079: [u'Waukegan'], 60081: [u'Spring Grove'], 60082: [u'Techny'], 60083: [u'Wadsworth', u'Beach Park', u'Old Mill Creek', u'Old Mill Crk'], 60084: [u'Wauconda', u'Lake Barrington', u'Lk Barrington'], 60085: [u'Waukegan', u'Park City'], 60086: [u'North Chicago'], 60087: [u'Waukegan', u'Beach Park'], 60088: [u'Great Lakes', u'North Chicago'], 60089: [u'Buffalo Grove'], 60090: [u'Wheeling'], 60091: [u'Wilmette'], 60092: [u'Libertyville'], 60093: [u'Winnetka', u'Northfield'], 60094: [u'Palatine'], 60095: [u'Palatine'], 60096: [u'Winthrop Harbor', u'Winthrop Hbr'], 60097: [u'Wonder Lake', u'Bull Valley'], 60098: [u'Woodstock', u'Bull Valley'], 60099: [u'Zion', u'Beach Park'], 60101: [u'Addison'], 60102: [u'Algonquin', u'Lake In The Hills', u'Lk In The Hls'], 60103: [u'Bartlett', u'Ontarioville'], 60104: [u'Bellwood'], 60105: [u'Bensenville'], 60106: [u'Bensenville'], 60107: [u'Streamwood'], 60108: [u'Bloomingdale'], 60109: [u'Burlington'], 60110: [u'Carpentersville', u'Carpentersvle'], 60111: [u'Clare'], 60112: [u'Cortland'], 60113: [u'Creston'], 60115: [u'Dekalb'], 60116: [u'Carol Stream'], 60117: [u'Bloomingdale'], 60118: [u'Dundee', u'East Dundee', u'Sleepy Hollow', u'West Dundee'], 60119: [u'Elburn', u'Campton Hills'], 60120: [u'Elgin', u'Hoffman Est'], 60121: [u'Elgin'], 60122: [u'Carol Stream'], 60123: [u'Elgin'], 60124: [u'Elgin', u'Campton Hills', u'Plato Center'], 60125: [u'Carol Stream', u'Electronic Data Systems'], 60126: [u'Elmhurst'], 60128: [u'Carol Stream'], 60129: [u'Esmond'], 60130: [u'Forest Park'], 60131: [u'Franklin Park', u'Schiller Park'], 60132: [u'Carol Stream'], 60133: [u'Hanover Park', u'Bartlett'], 60134: [u'Geneva'], 60135: [u'Genoa'], 60136: [u'Gilberts'], 60137: [u'Glen Ellyn', u'Glendale Heights', u'Glendale Hts'], 60138: [u'Glen Ellyn'], 60139: [u'Glendale Heights', u'Glendale Hts'], 60140: [u'Hampshire', u'Campton Hills', u'Pingree Grove'], 60141: [u'Hines'], 60142: [u'Huntley'], 60143: [u'Itasca'], 60144: [u'Kaneville'], 60145: [u'Kingston'], 60146: [u'Kirkland'], 60147: [u'Lafox'], 60148: [u'Lombard'], 60150: [u'Malta'], 60151: [u'Maple Park', u'Virgil'], 60152: [u'Marengo'], 60153: [u'Maywood', u'Broadview'], 60154: [u'Westchester'], 60155: [u'Broadview', u'Maywood'], 60156: [u'Lake In The Hills', u'Algonquin', u'Lk In The Hls'], 60157: [u'Medinah'], 60159: [u'Schaumburg'], 60160: [u'Melrose Park'], 60161: [u'Melrose Park'], 60162: [u'Hillside'], 60163: [u'Berkeley', u'Hillside', u'Melrose Park'], 60164: [u'Melrose Park', u'Northlake'], 60165: [u'Stone Park', u'Melrose Park'], 60168: [u'Schaumburg'], 60169: [u'Hoffman Estates', u'Hoffman Est'], 60170: [u'Plato Center'], 60171: [u'River Grove'], 60172: [u'Roselle'], 60173: [u'Schaumburg'], 60174: [u'Saint Charles', u'Campton Hills', u'St Charles'], 60175: [u'Saint Charles', u'Campton Hills', u'St Charles'], 60176: [u'Schiller Park'], 60177: [u'South Elgin'], 60178: [u'Sycamore'], 60179: [u'Hoffman Estates', u'Hoffman Est', u'Schaumburg'], 60180: [u'Union'], 60181: [u'Villa Park', u'Oakbrook Ter', u'Oakbrook Terrace'], 60183: [u'Wasco'], 60184: [u'Wayne'], 60185: [u'West Chicago', u'Northwoods'], 60186: [u'West Chicago'], 60187: [u'Wheaton'], 60188: [u'Carol Stream'], 60189: [u'Wheaton'], 60190: [u'Winfield'], 60191: [u'Wood Dale'], 60192: [u'Hoffman Estates', u'Hoffman Est'], 60193: [u'Schaumburg'], 60194: [u'Schaumburg'], 60195: [u'Schaumburg', u'Hoffman Est', u'Hoffman Estates'], 60196: [u'Schaumburg', u'Hoffman Est', u'Hoffman Estates'], 60197: [u'Carol Stream'], 60199: [u'Carol Stream'], 60201: [u'Evanston'], 60202: [u'Evanston'], 60203: [u'Evanston'], 60204: [u'Evanston'], 60208: [u'Evanston'], 60209: [u'Evanston'], 60290: [u'Chicago'], 60301: [u'Oak Park'], 60302: [u'Oak Park'], 60303: [u'Oak Park'], 60304: [u'Oak Park'], 60305: [u'River Forest'], 60399: [u'Wood Dale', u'Bensenville'], 60401: [u'Beecher'], 60402: [u'Berwyn', u'Forest View', u'Stickney'], 60403: [u'Crest Hill', u'Joliet'], 60404: [u'Shorewood', u'Joliet'], 60406: [u'Blue Island'], 60407: [u'Braceville', u'Godley'], 60408: [u'Braidwood'], 60409: [u'Calumet City'], 60410: [u'Channahon'], 60411: [u'Chicago Heights', u'Chicago Hts', u'Ford Heights', u'Lynwood', u'S Ch...'], 60412: [u'Chicago Heights', u'Chicago Hts'], 60415: [u'Chicago Ridge'], 60416: [u'Coal City', u'Carbon Hill', u'Diamond'], 60417: [u'Crete'], 60419: [u'Dolton'], 60420: [u'Dwight'], 60421: [u'Elwood'], 60422: [u'Flossmoor', u'Homewood'], 60423: [u'Frankfort'], 60424: [u'Gardner'], 60425: [u'Glenwood'], 60426: [u'Harvey', u'Dixmoor', u'Markham', u'Phoenix'], 60428: [u'Markham', u'Harvey'], 60429: [u'Hazel Crest'], 60430: [u'Homewood'], 60431: [u'Joliet', u'Shorewood'], 60432: [u'Joliet'], 60433: [u'Joliet'], 60434: [u'Joliet'], 60435: [u'Joliet', u'Crest Hill', u'Shorewood'], 60436: [u'Joliet', u'Rockdale', u'Shorewood'], 60437: [u'Kinsman'], 60438: [u'Lansing'], 60439: [u'Lemont'], 60440: [u'Bolingbrook'], 60441: [u'Lockport', u'Homer Glen'], 60442: [u'Manhattan', u'Wilton Center'], 60443: [u'Matteson'], 60444: [u'Mazon'], 60445: [u'Midlothian', u'Crestwood'], 60446: [u'Romeoville', u'Lockport'], 60447: [u'Minooka'], 60448: [u'Mokena'], 60449: [u'Monee'], 60450: [u'Morris'], 60451: [u'New Lenox'], 60452: [u'Oak Forest'], 60453: [u'Oak Lawn'], 60454: [u'Oak Lawn'], 60455: [u'Bridgeview', u'Bedford Park', u'Oak Lawn'], 60456: [u'Hometown', u'Oak Lawn'], 60457: [u'Hickory Hills', u'Oak Lawn'], 60458: [u'Justice', u'Bedford Park', u'Oak Lawn'], 60459: [u'Burbank', u'Bedford Park', u'Oak Lawn'], 60460: [u'Odell'], 60461: [u'Olympia Fields', u'Olympia Flds'], 60462: [u'Orland Park'], 60463: [u'Palos Heights'], 60464: [u'Palos Park'], 60465: [u'Palos Hills'], 60466: [u'Park Forest', u'University Park', u'University Pk'], 60467: [u'Orland Park'], 60468: [u'Peotone'], 60469: [u'Posen'], 60470: [u'Ransom'], 60471: [u'Richton Park'], 60472: [u'Robbins'], 60473: [u'South Holland'], 60474: [u'South Wilmington', u'S Wilmington'], 60475: [u'Steger', u'Chicago Heights', u'Chicago Hts'], 60476: [u'Thornton'], 60477: [u'Tinley Park', u'Orland Hills'], 60478: [u'Country Club Hills', u'Cntry Clb Hls', u'Ctry Clb Hls', u'Tinley Park'], 60479: [u'Verona'], 60480: [u'Willow Springs', u'Willow Spgs'], 60481: [u'Wilmington', u'Custer Park'], 60482: [u'Worth'], 60484: [u'University Park', u'Park Forest', u'University Pk'], 60487: [u'Tinley Park', u'Orland Hills'], 60490: [u'Bolingbrook'], 60491: [u'Homer Glen', u'Lockport'], 60499: [u'Bedford Park', u'South Suburban', u'South Suburbn'], 60501: [u'Summit Argo', u'Argo', u'Bedford Park', u'Summit'], 60502: [u'Aurora'], 60503: [u'Aurora'], 60504: [u'Aurora'], 60505: [u'Aurora'], 60506: [u'Aurora'], 60507: [u'Aurora'], 60510: [u'Batavia'], 60511: [u'Big Rock'], 60512: [u'Bristol'], 60513: [u'Brookfield'], 60514: [u'Clarendon Hills', u'Clarendon Hls'], 60515: [u'Downers Grove'], 60516: [u'Downers Grove'], 60517: [u'Woodridge', u'Downers Grove'], 60518: [u'Earlville'], 60519: [u'Eola'], 60520: [u'Hinckley'], 60521: [u'Hinsdale', u'Oak Brk Mall', u'Oak Brook', u'Oak Brook Mall'], 60522: [u'Hinsdale', u'Oak Brook'], 60523: [u'Oak Brook', u'Hinsdale'], 60525: [u'La Grange', u'Countryside', u'Hodgkins', u'Ind Head Park', u'In...'], 60526: [u'La Grange Park', u'La Grange Pk'], 60527: [u'Willowbrook', u'Burr Ridge'], 60530: [u'Lee'], 60531: [u'Leland'], 60532: [u'Lisle'], 60534: [u'Lyons'], 60536: [u'Millbrook'], 60537: [u'Millington'], 60538: [u'Montgomery', u'Montgmry'], 60539: [u'Mooseheart', u'Batavia'], 60540: [u'Naperville'], 60541: [u'Newark'], 60542: [u'North Aurora'], 60543: [u'Oswego'], 60544: [u'Plainfield'], 60545: [u'Plano'], 60546: [u'Riverside', u'N Riverside', u'North Riverside'], 60548: [u'Sandwich'], 60549: [u'Serena'], 60550: [u'Shabbona'], 60551: [u'Sheridan'], 60552: [u'Somonauk'], 60553: [u'Steward'], 60554: [u'Sugar Grove'], 60555: [u'Warrenville'], 60556: [u'Waterman'], 60557: [u'Wedron'], 60558: [u'Western Springs', u'Western Sprgs'], 60559: [u'Westmont'], 60560: [u'Yorkville'], 60561: [u'Darien'], 60563: [u'Naperville'], 60564: [u'Naperville'], 60565: [u'Naperville'], 60566: [u'Naperville'], 60567: [u'Naperville'], 60568: [u'Aurora'], 60570: [u'Hinsdale', u'Oak Brook'], 60572: [u'Aurora', u'Fox Valley'], 60585: [u'Plainfield'], 60586: [u'Plainfield'], 60597: [u'Fox Valley', u'Rates And Classification'], 60598: [u'Aurora'], 60599: [u'Fox Valley'], 60601: [u'Chicago'], 60602: [u'Chicago'], 60603: [u'Chicago'], 60604: [u'Chicago'], 60605: [u'Chicago'], 60606: [u'Chicago'], 60607: [u'Chicago'], 60608: [u'Chicago'], 60609: [u'Chicago'], 60610: [u'Chicago'], 60611: [u'Chicago'], 60612: [u'Chicago'], 60613: [u'Chicago'], 60614: [u'Chicago'], 60615: [u'Chicago'], 60616: [u'Chicago'], 60617: [u'Chicago'], 60618: [u'Chicago'], 60619: [u'Chicago'], 60620: [u'Chicago'], 60621: [u'Chicago'], 60622: [u'Chicago'], 60623: [u'Chicago'], 60624: [u'Chicago'], 60625: [u'Chicago'], 60626: [u'Chicago'], 60628: [u'Chicago'], 60629: [u'Chicago', u'Bedford Park'], 60630: [u'Chicago', u'Jefferson Park', u'Jefferson Pk'], 60631: [u'Chicago'], 60632: [u'Chicago'], 60633: [u'Chicago', u'Burnham'], 60634: [u'Chicago'], 60636: [u'Chicago'], 60637: [u'Chicago'], 60638: [u'Chicago', u'Bedford Park'], 60639: [u'Chicago'], 60640: [u'Chicago'], 60641: [u'Chicago'], 60642: [u'Chicago'], 60643: [u'Chicago', u'Calumet Park'], 60644: [u'Chicago'], 60645: [u'Chicago'], 60646: [u'Chicago', u'Lincolnwood'], 60647: [u'Chicago'], 60649: [u'Chicago'], 60651: [u'Chicago'], 60652: [u'Chicago'], 60653: [u'Chicago'], 60654: [u'Chicago'], 60655: [u'Chicago', u'Merrionett Pk', u'Merrionette Park'], 60656: [u'Chicago', u'Harwood Heights', u'Harwood Hts', u'Norridge'], 60657: [u'Chicago'], 60659: [u'Chicago'], 60660: [u'Chicago'], 60661: [u'Chicago'], 60663: [u'Chicago'], 60664: [u'Chicago'], 60666: [u'Chicago'], 60668: [u'Chicago'], 60669: [u'Chicago'], 60670: [u'Chicago'], 60673: [u'Chicago'], 60674: [u'Chicago'], 60675: [u'Chicago'], 60677: [u'Chicago'], 60678: [u'Chicago'], 60679: [u'Chicago'], 60680: [u'Chicago'], 60681: [u'Chicago'], 60682: [u'Chicago'], 60684: [u'Chicago'], 60685: [u'Chicago'], 60686: [u'Chicago'], 60687: [u'Chicago'], 60688: [u'Chicago'], 60689: [u'Chicago'], 60690: [u'Chicago'], 60691: [u'Chicago'], 60693: [u'Chicago'], 60694: [u'Chicago'], 60695: [u'Chicago'], 60696: [u'Chicago'], 60697: [u'Chicago'], 60699: [u'Chicago'], 60701: [u'Chicago'], 60706: [u'Harwood Heights', u'Chicago', u'Harwood Hts', u'Norridge'], 60707: [u'Elmwood Park', u'Chicago'], 60712: [u'Lincolnwood'], 60714: [u'Niles'], 60803: [u'Alsip', u'Chicago', u'Merrionett Pk', u'Merrionette Park'], 60804: [u'Cicero', u'Chicago'], 60805: [u'Evergreen Park', u'Chicago', u'Evergreen Pk'], 60827: [u'Riverdale', u'Calumet Park', u'Chicago'], 60901: [u'Kankakee', u'Irwin'], 60910: [u'Aroma Park'], 60911: [u'Ashkum'], 60912: [u'Beaverville'], 60913: [u'Bonfield'], 60914: [u'Bourbonnais'], 60915: [u'Bradley'], 60917: [u'Buckingham'], 60918: [u'Buckley'], 60919: [u'Cabery'], 60920: [u'Campus'], 60921: [u'Chatsworth'], 60922: [u'Chebanse', u'Sammons Point'], 60924: [u'Cissna Park'], 60926: [u'Claytonville'], 60927: [u'Clifton'], 60928: [u'Crescent City'], 60929: [u'Cullom'], 60930: [u'Danforth'], 60931: [u'Donovan'], 60932: [u'East Lynn'], 60933: [u'Elliott'], 60934: [u'Emington'], 60935: [u'Essex'], 60936: [u'Gibson City'], 60938: [u'Gilman'], 60939: [u'Goodwine'], 60940: [u'Grant Park'], 60941: [u'Herscher'], 60942: [u'Hoopeston'], 60944: [u'Hopkins Park'], 60945: [u'Iroquois'], 60946: [u'Kempton'], 60948: [u'Loda'], 60949: [u'Ludlow'], 60950: [u'Manteno'], 60951: [u'Martinton'], 60952: [u'Melvin'], 60953: [u'Milford'], 60954: [u'Momence'], 60955: [u'Onarga'], 60956: [u'Papineau'], 60957: [u'Paxton'], 60958: [u'Pembroke Township', u'Pembroke Twp'], 60959: [u'Piper City'], 60960: [u'Rankin', u'Clarence'], 60961: [u'Reddick'], 60962: [u'Roberts'], 60963: [u'Rossville'], 60964: [u'Saint Anne', u'Sun River Ter', u'Sun River Terrace'], 60966: [u'Sheldon'], 60967: [u'Stockland'], 60968: [u'Thawville'], 60969: [u'Union Hill'], 60970: [u'Watseka'], 60973: [u'Wellington'], 60974: [u'Woodland'], 61001: [u'Apple River'], 61006: [u'Ashton'], 61007: [u'Baileyville'], 61008: [u'Belvidere'], 61010: [u'Byron'], 61011: [u'Caledonia'], 61012: [u'Capron'], 61013: [u'Cedarville'], 61014: [u'Chadwick'], 61015: [u'Chana'], 61016: [u'Cherry Valley'], 61018: [u'Dakota'], 61019: [u'Davis'], 61020: [u'Davis Junction', u'Davis Jct'], 61021: [u'Dixon', u'Nelson'], 61024: [u'Durand'], 61025: [u'East Dubuque'], 61027: [u'Eleroy'], 61028: [u'Elizabeth'], 61030: [u'Forreston'], 61031: [u'Franklin Grove', u'Franklin Grv'], 61032: [u'Freeport', u'Scioto Mills'], 61036: [u'Galena'], 61037: [u'Galt'], 61038: [u'Garden Prairie', u'Garden Pr'], 61039: [u'German Valley'], 61041: [u'Hanover'], 61042: [u'Harmon'], 61043: [u'Holcomb'], 61044: [u'Kent'], 61046: [u'Lanark'], 61047: [u'Leaf River', u'Egan'], 61048: [u'Lena'], 61049: [u'Lindenwood'], 61050: [u'Mc Connell'], 61051: [u'Milledgeville'], 61052: [u'Monroe Center'], 61053: [u'Mount Carroll'], 61054: [u'Mount Morris'], 61057: [u'Nachusa'], 61059: [u'Nora'], 61060: [u'Orangeville'], 61061: [u'Oregon'], 61062: [u'Pearl City'], 61063: [u'Pecatonica'], 61064: [u'Polo'], 61065: [u'Poplar Grove'], 61067: [u'Ridott'], 61068: [u'Rochelle', u'Kings'], 61070: [u'Rock City'], 61071: [u'Rock Falls'], 61072: [u'Rockton'], 61073: [u'Roscoe'], 61074: [u'Savanna'], 61075: [u'Scales Mound'], 61077: [u'Seward'], 61078: [u'Shannon'], 61079: [u'Shirland'], 61080: [u'South Beloit'], 61081: [u'Sterling', u'Coleta'], 61084: [u'Stillman Valley', u'Stillman Vly'], 61085: [u'Stockton'], 61087: [u'Warren'], 61088: [u'Winnebago'], 61089: [u'Winslow'], 61091: [u'Woosung'], 61101: [u'Rockford'], 61102: [u'Rockford'], 61103: [u'Rockford', u'Machesney Park', u'Machesney Pk'], 61104: [u'Rockford'], 61105: [u'Rockford'], 61106: [u'Rockford'], 61107: [u'Rockford'], 61108: [u'Rockford'], 61109: [u'Rockford'], 61110: [u'Rockford'], 61111: [u'Loves Park', u'Machesney Park', u'Machesney Pk'], 61112: [u'Rockford'], 61114: [u'Rockford'], 61115: [u'Machesney Park', u'Loves Park', u'Machesney Pk'], 61125: [u'Rockford'], 61126: [u'Rockford'], 61130: [u'Loves Park'], 61131: [u'Loves Park'], 61132: [u'Loves Park'], 61201: [u'Rock Island'], 61204: [u'Rock Island'], 61230: [u'Albany'], 61231: [u'Aledo'], 61232: [u'Andalusia'], 61233: [u'Andover'], 61234: [u'Annawan'], 61235: [u'Atkinson'], 61236: [u'Barstow'], 61237: [u'Buffalo Prairie', u'Buffalo Pr'], 61238: [u'Cambridge'], 61239: [u'Carbon Cliff'], 61240: [u'Coal Valley'], 61241: [u'Colona', u'Cleveland', u'Green Rock'], 61242: [u'Cordova'], 61243: [u'Deer Grove'], 61244: [u'East Moline'], 61250: [u'Erie'], 61251: [u'Fenton'], 61252: [u'Fulton'], 61254: [u'Geneseo'], 61256: [u'Hampton'], 61257: [u'Hillsdale'], 61258: [u'Hooppole'], 61259: [u'Illinois City'], 61260: [u'Joy'], 61261: [u'Lyndon'], 61262: [u'Lynn Center'], 61263: [u'Matherville'], 61264: [u'Milan', u'Oak Grove'], 61265: [u'Moline'], 61266: [u'Moline'], 61270: [u'Morrison'], 61272: [u'New Boston'], 61273: [u'Orion'], 61274: [u'Osco'], 61275: [u'Port Byron'], 61276: [u'Preemption'], 61277: [u'Prophetstown'], 61278: [u'Rapids City'], 61279: [u'Reynolds'], 61281: [u'Sherrard'], 61282: [u'Silvis'], 61283: [u'Tampico'], 61284: [u'Taylor Ridge'], 61285: [u'Thomson'], 61299: [u'Rock Island'], 61301: [u'La Salle'], 61310: [u'Amboy'], 61311: [u'Ancona'], 61312: [u'Arlington'], 61313: [u'Blackstone'], 61314: [u'Buda'], 61315: [u'Bureau'], 61316: [u'Cedar Point'], 61317: [u'Cherry'], 61318: [u'Compton'], 61319: [u'Cornell', u'Manville'], 61320: [u'Dalzell'], 61321: [u'Dana'], 61322: [u'Depue'], 61323: [u'Dover'], 61324: [u'Eldena'], 61325: [u'Grand Ridge'], 61326: [u'Granville'], 61327: [u'Hennepin'], 61328: [u'Kasbeer'], 61329: [u'Ladd'], 61330: [u'La Moille'], 61331: [u'Lee Center'], 61332: [u'Leonore'], 61333: [u'Long Point'], 61334: [u'Lostant'], 61335: [u'Mc Nabb'], 61336: [u'Magnolia'], 61337: [u'Malden'], 61338: [u'Manlius'], 61340: [u'Mark'], 61341: [u'Marseilles'], 61342: [u'Mendota'], 61344: [u'Mineral'], 61345: [u'Neponset'], 61346: [u'New Bedford'], 61348: [u'Oglesby'], 61349: [u'Ohio'], 61350: [u'Ottawa'], 61353: [u'Paw Paw'], 61354: [u'Peru'], 61356: [u'Princeton', u'Hollowayville'], 61358: [u'Rutland'], 61359: [u'Seatonville'], 61360: [u'Seneca'], 61361: [u'Sheffield'], 61362: [u'Spring Valley'], 61363: [u'Standard'], 61364: [u'Streator'], 61367: [u'Sublette'], 61368: [u'Tiskilwa'], 61369: [u'Toluca'], 61370: [u'Tonica'], 61371: [u'Triumph'], 61372: [u'Troy Grove'], 61373: [u'Utica'], 61374: [u'Van Orin'], 61375: [u'Varna'], 61376: [u'Walnut', u'Normandy'], 61377: [u'Wenona'], 61378: [u'West Brooklyn'], 61379: [u'Wyanet'], 61401: [u'Galesburg'], 61402: [u'Galesburg'], 61410: [u'Abingdon'], 61411: [u'Adair'], 61412: [u'Alexis'], 61413: [u'Alpha'], 61414: [u'Altona'], 61415: [u'Avon'], 61416: [u'Bardolph'], 61417: [u'Berwick'], 61418: [u'Biggsville'], 61419: [u'Bishop Hill'], 61420: [u'Blandinsville'], 61421: [u'Bradford'], 61422: [u'Bushnell'], 61423: [u'Cameron'], 61424: [u'Camp Grove'], 61425: [u'Carman'], 61426: [u'Castleton'], 61427: [u'Cuba'], 61428: [u'Dahinda'], 61430: [u'East Galesburg', u'E Galesburg'], 61431: [u'Ellisville'], 61432: [u'Fairview'], 61433: [u'Fiatt'], 61434: [u'Galva'], 61435: [u'Gerlaw'], 61436: [u'Gilson', u'Delong'], 61437: [u'Gladstone'], 61438: [u'Good Hope'], 61439: [u'Henderson']}

###############################################################################
# Define Dictionary / List Corretion Mappings
# correcting_state_list: identifies incorrect spelling or valid state "IL"
# correcting_cities_mapping: returns cleaned city names
# street_prefixes_mapping: returns cleaned street prefixes
# street_suffixes_mapping: returns cleaned street suffixes
# street_names_mapping: returns cleaned street names
###############################################################################
correcting_state_list = ["IL - Illinois","il","Il.","Illinois","Il"]
correcting_cities_mapping = {'Woodbridge':'Woodridge','Carpentesville':'Carpentersville','elgin':'Elgin','Barrinton':'Barrington','Chicago, IL':'Chicago','Crest Hill, IL':'Crest Hill','chicago':'Chicago','libertyville':'Libertyville','plainfield':'Plainfield','Bollingbrook':'Bolingbrook','BOLINGBROOK':'Bolingbrook','forest Park':'Forest Park','BUFFALO GROVE':'Buffalo Grove','St Charles':'St. Charles','Elk Grove':'Elk Grove Village','Saint Charles':'St. Charles','Joliet, Illinois':'Joliet','huntley':'Huntley','st charles':'St. Charles','mount prospect':'Mount Prospect','Melrose Park, IL':'Melrose Park','riverside':'Riverside','ROMEOVILLE':'Romeoville','crystal lake':'Crystal Lake','elmhurst':'Elmhurst'}
street_prefixes_mapping = {"N":"North","N.":"North","north":"North","E":"East","E.":"East","east":"East","S":"South","S.":"South","south":"South","W":"West","W.":"West","west":"West","St":"Saint","St.":"Saint","SUNSET":"Sunset","randall":"Randall","pfingsten":"Pfingsten","dunham":"Dunham"}
street_suffixes_mapping = {"Acenue":"Avenue","AVENUE":"Avenue","Ave":"Avenue","Ave.":"Avenue","Blvd":"Boulevard","blvd":"Boulevard","Blvd.":"Boulevard","Blvd.  ":"Boulevard","Cir":"Circle","Ct":"Court","Ct.":"Court","Dr":"Drive","Dr.":"Drive", "Hwy":"Highway", "Hwy.":"Highway","HWY":"Highway","Ln":"Lane","Pkwy":"Parkway","Pl":"Place","Plz":"Plaza","Rd":"Road","RD":"Road","Rd.":"Road","St":"Street","St.":"Street","St,":"Street","Ter":"Terrace","Trl":"Trail"}
street_names_mapping = {"1050 Essington Rd. Joliet, IL 60435":"Essington Road","West. Algonquin Road":"West Algonquin Road","IL-59 #8":"IL-59"}

###############################################################################
# Define Other Dictionaries / Lists
# CREATED: identify the keys that should be combined into node["created"] dict
###############################################################################
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

###############################################################################
# @desc: Audit the node["address"]["country"] field for accuracy. Always "US".
# @param: node["address"]["country"]
# @return: node["address"]["country"]
###############################################################################
def audit_country(country):
    return "US"


###############################################################################
# @desc: Audit the node["address"]["state"] field for accuracy and consistency.
#   The state should conform to the standard two-letter format of "IL". 
# @param: node["address"]["state"], bad_data_flag
# @return: node["address"]["state"], bad_data_flag
###############################################################################
def audit_state(state, flag):
    if state == "IL":       
        return state, flag # return as-is since it's equal to the standard "IL"
    elif state in correcting_state_list:
        return "IL", flag  # return state as the corrected standard "IL" value
    else:
        flag = True
        return state, flag # state is not Illinois, return flagged as bad data
        
        
###############################################################################
# @desc: Audit the node["address"]["city"] field for accuracy and consistency.
# @param: node["address"]["city"] field, bad_data_flag
# @return: node["address"]["city"] field, bad_data_flag
###############################################################################
def audit_city(city_name,flag):
    if city_name in cities_in_illinois:
        return city_name, flag  # return as-is since it's a valid city
    elif city_name in correcting_cities_mapping:
        return correcting_cities_mapping[city_name], flag  # return corrected
    else:                                                  # city name
        flag = True
        return city_name, flag  # city is not valid, return flagged as bad data


###############################################################################
# @desc: Audit the node["address"]["postcode"] field for accuracy, validity, 
#   and consistency. 
# @param: str node["address"]["postcode"], str node["tiger"]["zip-left"], 
#   bool bad_data_flag
# @retrun: int node["address"]["postcode"],bool bad_data_flag
###############################################################################
def audit_postcode(postcode,tiger_postcode,flag):
    # trims the postcode down to a 5 digit integer value for consistency
    # returns None if error is encountered
    try:
        postcode = int(postcode[0:5])
    except (TypeError, ValueError):
        postcode = None  
    # trims the tiger_postcode down to a 5 digit integer value for consistency
    # returns None if error is encountered
    try:
        tiger_postcode = int(tiger_postcode[0:5])
    except (TypeError, ValueError):
        tiger_postcode = None    
    # Option 1: return valid postcode.
    # Option 2: return valid tiger_postcode.
    # Option 3: return postcode flagged as bad data
    if postcode and tiger_postcode:
        if postcode in postcode_county_mapping:
            return postcode, flag   # return valid illinois postcode
        elif tiger_postcode in postcode_county_mapping:
            return tiger_postcode, flag  # return valid illinois postcode
        else:
            return postcode, True  # return flagged as bad data
    elif postcode:
        if postcode in postcode_county_mapping:
            return postcode, flag  # return valid illinois postcode
        else:
            return postcode, True  # return flagged as bad data
    elif tiger_postcode:
        if tiger_postcode in postcode_county_mapping:
            return tiger_postcode, flag  # return valid illinois postcode
        else:
            return postcode, True  # return flagged as bad data
    else:
        return postcode, True  # return flagged as bad data


###############################################################################
# @desc: Audit the node["address"]["county"] field for accuracy and validity.
# @param: str node["address"]["county"], str node["tiger"]["county"], 
#   bool bad_data_flag
# @return: str node["address"]["county"], bool bad_data_flag
###############################################################################
def audit_county(county, tiger_county, flag):
    if county and tiger_county:
        # tiger_county contains county and state in some order
        # examples: ("Cook, IL" or "IL;Cook")
        # this line splits the county and state into two separate variables
        tiger_county = re.split("[,;:]", tiger_county)
        
        # option1: if county is valid, then return it
        # option2: if tiger_county list contains a valid county, then return it
        # option3: return county flagged as bad data
        if county in county_postcode_mapping:
            return county, flag  # return valid county
        elif type(tiger_county) is list and len(tiger_county) >= 2:
            tiger_county[0] = tiger_county[0].strip()
            tiger_county[1] = tiger_county[1].strip()
            # first checks to make sure the county is in Illinois
            if tiger_county[0] == "IL" or tiger_county[1] == "IL":
                if tiger_county[0] in county_postcode_mapping:
                    return tiger_county[0], flag  # return valid tiger_county
                elif tiger_county[1] in county_postcode_mapping:
                    return tiger_county[1], flag  # return valid tiger_county      
                else:
                    return tiger_county, True  # return as bad data
            else:
                return county, True  # return as bad data
        else:
            return county, True  # return as bad data
    elif county:
        # option1: if county is valid, then return it
        # option2: return county flagged as bad data
        if county in county_postcode_mapping:
            return county, flag  # return valid county
        else:
            return county, True  # return flagged as bad data
    elif tiger_county:  
        # tiger_county contains county and state in some order
        # examples: ("Cook, IL" or "IL;Cook")
        # this line splits the county and state into two separate variables        
        tiger_county = re.split("[,;:]", tiger_county)
        
        # option1: if tiger_county list contains a valid county, then return it
        # option2: return county flagged as bad data
        if type(tiger_county) is list and len(tiger_county) >= 2:
            tiger_county[0] = tiger_county[0].strip()
            tiger_county[1] = tiger_county[1].strip()
            if tiger_county[0] == "IL" or tiger_county[1] == "IL":
                if tiger_county[0] in county_postcode_mapping:
                    return tiger_county[0], flag  # return valid tiger_county
                elif tiger_county[1] in county_postcode_mapping:
                    return tiger_county[1], flag  # return valid tiger_county
                else:
                    return tiger_county, True  # return as bad data
            else:
                return tiger_county, True  # return as bad data
        else:
            return county, True  # return as bad data
    else:
        return None, True  # return as bad data
        
        
###############################################################################
# @desc: Audit the node["address"]["street"] field for accuracy and consistency
# @param: node["address"]["street"]
# @return: node["address"]["street"]
###############################################################################
def audit_street(street):
    # Manually fixes some of the incorrect street nmaes using mapping dict
    if street in street_names_mapping:
        street = street_names_mapping[street]
    else:
        housenumber = housenumber_re.search(street)
        # if housenumber is found in street field it is removed.
        if housenumber:
            housenumber = housenumber.group()
            street = street.replace(housenumber,"")  # removes housenumber
            street = street.strip()  # strip leading/trailing blanks
        
        # audit the street field to fix prefix/suffix inconsistencies
        i = 0
        s = street.split(" ")    # split field into multiple words
        updated_street = ""
        while i < len(s):
            if s[i] in street_suffixes_mapping:
                s[i] = street_suffixes_mapping[s[i]]  # cleans suffix
            elif s[i] in street_prefixes_mapping:
                s[i] = street_prefixes_mapping[s[i]]  # cleans prefix
            updated_street = updated_street + s[i] + " "    # recombine words 
            i = i + 1      
        street = updated_street.strip()
        
        # audit the street field to fix inconsistencies in the naming
        # convention of the IL/US highways. This is completed by replacing 
        # common inconsistencies with consistent name. ("Route 59" --> "IL-59".
        if street.find("Route") >= 0 or street.find("US") >= 0:
            if street.find("IL Route ") >= 0:
                street = street.replace("IL Route ","IL-")
            elif street.find("Route IL ") >= 0:
                street = street.replace("Route IL ","IL-")
            elif street.find("Route ") >= 0:
                street = street.replace("Route ","IL-")
            elif street.find("US Highway ") >= 0:
                street = street.replace("US Highway ","US-")
            elif street.find("US ") >= 0:
                street = street.replace("US ","US-")
            elif street.find("U.S. ") >= 0:
                street = street.replace("U.S. ","US-")  
    return street


###############################################################################
# @desc: audits the node["address"]["full"] field for accuracy and consistency.
# @params: node
# @return node
###############################################################################
def audit_full_address(node):
    # grabs house number from node["address"]["full"] using regular expression
    housenumber = housenumber_re.search(node["address"]["full"])  
    
    # if node["address"]["housenumber"] and housenumber are not the same
    # then assign the value of housenumber to node["address"]["housenumber"]
    if housenumber and "housenumber" in node["address"]:
        if node["address"]["housenumber"] != housenumber.group():
            node["address"]["housenumber"] = housenumber.group()    
    
    # audit node["address"]["full"] to fix prefix/suffix inconsistencies
    i = 0
    f = node["address"]["full"].split(" ")   # split field into multiple words
    updated_f = ""
    while i < len(f):
        if f[i] in street_suffixes_mapping:
            f[i] = street_suffixes_mapping[f[i]]  # cleans suffix
        elif f[i] in street_prefixes_mapping:
            f[i] = street_prefixes_mapping[f[i]]  # cleans prefix
        updated_f = updated_f + f[i] + " "    # recombine into one word
        i = i + 1  
    node["address"]["full"] = updated_f.strip()
    
    # audit the node["address"]["full"] field to fix inconsistencies in the
    # naming convention of the IL/US highways. This is completed by replacing 
    # common inconsistencies with consistent name. ("Route 59" --> "IL-59".
    if node["address"]["full"].find("Route") >= 0 or \
                                    node["address"]["full"].find("US") >= 0:
        if node["address"]["full"].find("IL Route ") >= 0:
            node["address"]["full"] = node["address"]["full"].replace( \
                                                        "IL Route ","IL-")
        elif node["address"]["full"].find("Route IL ") >= 0:
            node["address"]["full"] = node["address"]["full"].replace( \
                                                        "Route IL ","IL-")
        elif node["address"]["full"].find("Route ") >= 0:
            node["address"]["full"] = node["address"]["full"].replace( \
                                                        "Route ","IL-")
        elif node["address"]["full"].find("US Highway ") >= 0:
            node["address"]["full"] = node["address"]["full"].replace( \
                                                        "US Highway ","US-")
        elif node["address"]["full"].find("US ") >= 0:
            node["address"]["full"] = node["address"]["full"].replace( \
                                                        "US ","US-")
        elif node["address"]["full"].find("U.S. ") >= 0:
            node["address"]["full"] = node["address"]["full"].replace( \
                                                        "U.S. ","US-")
    
    # validate that the combination of node["address"]["housenumber"] and 
    # node["address"]["street"] is the same value as node["address"]["full"]
    # if not, then return the more prominent value out of the two
    if "street" in node["address"] and "housenumber" in node["address"]:
        address = node["address"]["housenumber"] + " " + \
                                                    node["address"]["street"]
        if node["address"]["full"].find(address) >= 0:
            return node
        else:
            if len(address) > len(node["address"]["full"]):
                node["address"]["full"] = address
            return node
    else:
        return node


###############################################################################
# @desc: audit the address dict for completion. If address data is missing
#   that can be derived from other address data, then this function will 
#   populate that missing data. For example, you can use Postal Code to derive 
#   the County {60001:'McHenry'}.
# @input: node
# @return: node - updated
# @other params: postcode_county_mapping - derive county from postal code
###############################################################################
def audit_address_completeness(node):
    if "postcode" in node["address"]:
        if "county" not in node["address"]:
            node["address"]["county"] = postcode_county_mapping[
                                                node["address"]["postcode"]]
        if "state" not in node["address"]:
            node["address"]["state"] = "IL"
        if "country" not in node["address"]:
            node["address"]["country"] = "US"       
    elif "city" in node["address"]:
        if "state" not in node["address"]:
            node["address"]["state"] = "IL"
        if "country" not in node["address"]:
            node["address"]["country"] = "US"
    elif "county" in node["address"]:
        if "state" not in node["address"]:
            node["address"]["state"] = "IL"
        if "country" not in node["address"]:
            node["address"]["country"] = "US"
    elif "state" in node["address"]:
        if "country" not in node["address"]:
            node["address"]["country"] = "US" 
    return node


###############################################################################
# @desc: audits the contact phone number field for validity and to ensure the
#   contact follows a consistent format.
# @input: node["contact"]["phone"]
# @return: node["contact"]["phone"]
###############################################################################
def audit_phone_number(phone):
    phone = phone.translate(None, "+ -()")     #remove all non-digit chars
    
    # if phone number is 10 or 11 digits return reformatted phone number
    # else return None since the phone number is invalid
    if len(phone) == 10:
        phone = "("+phone[0:3]+")"+phone[3:6]+"-"+phone[6:]
        return phone
    elif len(phone) == 11:
        phone = "("+phone[1:4]+")"+phone[4:7]+"-"+phone[7:]
        return phone
    else:
        return None
    
    
###############################################################################
# @desc: Transforms an element from the OSM file into python dictionary format
#   in preparation for loading into the MongoDB database.
# @param: element
# @return: node
###############################################################################
def shape_element(element):
    node = {}
    # Only interested in "node" and "way" elements
    if element.tag == "node" or element.tag == "way" :
        node["type"] = element.tag
        
        # add each attribute to the node dictionary
        for a in element.attrib:
            # if attribute is in CREATED list, then add it to the created dict
            if a in CREATED:
                if "created" not in node:   
                    node["created"] = {}   # Adds "created" dict if absent
                node["created"][a] = element.attrib[a]
            # creates list to store latitudinal and longitudinal data
            elif a in ["lat", "lon"]:
                    if "pos" not in node:
                        node["pos"] = [None,None]   # adds "pos" list if absent
                    if a == "lat":
                        node["pos"][0] = float(element.attrib[a])
                    else:
                        node["pos"][1] = float(element.attrib[a])
            else:
                node[a] = element.attrib[a]
        
        # iterates through each tag in the element
        for tag in element.iter("tag"):
            if problemchars.search(tag.attrib["k"]):   # discards bad data
                continue
                
            # if statement to confirm if lower_colon re is true
            if lower_colon.search(tag.attrib["k"]):
                # combines address fields into "address" dictionary                
                if tag.attrib["k"].find("addr") != -1:
                    if "address" not in node:
                        node["address"] = {}  # adds "address" dict if absent
                    sub_attr = tag.attrib["k"].split(":")
                    node["address"][sub_attr[1]] = tag.attrib["v"]
                # combines tiger fields into "tiger" dictionary
                elif tag.attrib["k"].find("tiger") != -1:
                    if "tiger" not in node:
                        node["tiger"] = {}  # adds "tiger" dict if absent
                    sub_attr = tag.attrib["k"].split(":")
                    node["tiger"][sub_attr[1]] = tag.attrib["v"]
                # combines gnis fields into "gnis" dictionary
                elif tag.attrib["k"].find("gnis") != -1:
                    if "gnis" not in node:
                        node["gnis"] = {}  # adds "gnis" dict if absent
                    sub_attr = tag.attrib["k"].split(":")
                    node["gnis"][sub_attr[1]] = tag.attrib["v"]
                # combines contact fields into "contact" dictionary
                elif tag.attrib["k"].find("contact") != -1:
                    if "contact" not in node:
                        node["contact"] = {}  # adds "contact" dict if absent
                    sub_attr = tag.attrib["k"].split(":")
                    node["contact"][sub_attr[1]] = tag.attrib["v"]
                # combines contact fields into "building" dictionary
                elif tag.attrib["k"].find("building") != -1:
                    if "building" not in node:
                        node["building"] = {}  # adds "building" dict if absent
                    sub_attr = tag.attrib["k"].split(":")
                    node["building"][sub_attr[1]] = tag.attrib["v"]
                # else store data as regular key-value pair
                else:
                    node[tag.attrib["k"]] = tag.attrib["v"]
            #elif no colon is found in tag.attrib["k"]
            elif tag.attrib["k"].find(":") == -1:
                if tag.attrib["k"] == "building":  # catch "building" tag
                    if "building" not in node:     # up front and assign to the 
                        node["building"] = {}      # node["building"]["type"]
                    node["building"]["type"] = tag.attrib["v"]  # field
                else:
                    node[tag.attrib["k"]] = tag.attrib["v"]
            
        # iterates through each nd in the element and stores them in list
        for nd in element.iter("nd"):
            if "node_refs" not in node:
                node["node_refs"] = []  # adds "node_refs" list if absent
            node["node_refs"].append(nd.attrib["ref"])
            
        return node
    else:
        return None   # discard data if the element is not "node" or "way"


###############################################################################
# @desc: Performs a series of audits on the node dictionary data.
# @param: dict node
# @return: dict node - updated dictionary containing cleaned data
###############################################################################
def audit_element(node):
    bad_data_flag = False    # assumes data is good to start
    
    # audit node["contact"]["phone"] (if applicable)
    if "contact" in node:
        if "phone" in node["contact"]:
            node["contact"]["phone"] = audit_phone_number(
                                                    node["contact"]["phone"])
    
    if "address" in node and "tiger" in node:
        # audit node["address"]["country"] (if applicable)
        if "country" in node["address"]:
            node["address"]["country"] = audit_country(
                                                    node["address"]["country"])
        # audit node["address"]["state"] (if applicable)
        if "state" in node["address"]:
            node["address"]["state"], bad_data_flag = audit_state(
                                                    node["address"]["state"], 
                                                    bad_data_flag)     
        # audit node["address"]["city"] (if applicable)
        if "city" in node["address"]:
            node["address"]["city"], bad_data_flag = audit_city(
                                                    node["address"]["city"], 
                                                    bad_data_flag)                
        # audit node["address"]["street"] (if applicable)        
        if "street" in node["address"]:
            node["address"]["street"] = audit_street(node["address"]["street"])       
        
        # audit node["address"]["full"] (if applicable)
        if "full" in node["address"]:
            node = audit_full_address(node)
        #======================================================================
        # Audit node["address"]["postcode"] if applicable
        # IF block to determine which parameters to pass into the audit_postcode
        # function. node["address"]["postcode"] or node["tiger"]["zip-left"]
        # or both. If neither are available then there is no audit executed.
        #======================================================================
        if "postcode" in node["address"] and "zip_left" in node["tiger"]:
            node["address"]["postcode"], bad_data_flag = audit_postcode(
                                                node["address"]["postcode"], 
                                                node["tiger"]["zip_left"], 
                                                bad_data_flag)
        elif "postcode" in node["address"]:
            node["address"]["postcode"], bad_data_flag = audit_postcode(
                                                node["address"]["postcode"], 
                                                None, 
                                                bad_data_flag)
        elif "zip_left" in node["tiger"]:
            node["address"]["postcode"], bad_data_flag = audit_postcode(
                                                None, 
                                                node["tiger"]["zip_left"], 
                                                bad_data_flag)
        #======================================================================
        # Audit node["address"]["county"] if applicable
        # IF block to determine which parameters to pass into the audit_county
        # function. Either node["address"]["county"] or node["tiger"]["county"]
        # or both. If neither are available then there is no audit executed.
        #======================================================================
        if "county" in node["address"] and "county" in node["tiger"]:
            node["address"]["county"], bad_data_flag = audit_county(
                                                    node["address"]["county"], 
                                                    node["tiger"]["county"], 
                                                    bad_data_flag)
        elif "county" in node["address"]:
            node["address"]["county"], bad_data_flag = audit_county(
                                                    node["address"]["county"], 
                                                    None, 
                                                    bad_data_flag)
        elif "county" in node["tiger"]:
            node["address"]["county"], bad_data_flag = audit_county(
                                                    None, 
                                                    node["tiger"]["county"], 
                                                    bad_data_flag)  
        # returns None if the data is bad                        
        if bad_data_flag:
            return None
        else:
            # audit node["address"] fields for compleness (if applicable)
            if "state" in node["address"] or "city" in node["address"] \
                                            or "postcode" in node["address"] \
                                            or "county" in node["address"]:
                node = audit_address_completeness(node)
            return node
    elif "address" in node:
        # audit node["address"]["country"] (if applicable)
        if "country" in node["address"]:
            node["address"]["country"] = audit_country(
                                                    node["address"]["country"])
        # audit node["address"]["state"] (if applicable)
        if "state" in node["address"]:
            node["address"]["state"], bad_data_flag = audit_state(
                                                    node["address"]["state"], 
                                                    bad_data_flag)
        # audit node["address"]["city"] (if applicable)
        if "city" in node["address"]:
            node["address"]["city"], bad_data_flag = audit_city(
                                                    node["address"]["city"], 
                                                    bad_data_flag)
        # audit node["address"]["street"] (if applicable)
        if "street" in node["address"]:
            node["address"]["street"] = audit_street(node["address"]["street"])
        # audit node["address"]["full"] (if applicable)
        if "full" in node["address"]:
            node = audit_full_address(node)
        # audit node["address"]["postcode"] (if applicable)
        if "postcode" in node["address"]:
            node["address"]["postcode"], bad_data_flag = audit_postcode(
                                                node["address"]["postcode"], 
                                                None, 
                                                bad_data_flag)
        # audit node["address"]["county"] (if applicable)
        if "county" in node["address"]:
            node["address"]["county"], bad_data_flag = audit_county(
                                                node["address"]["county"], 
                                                None, 
                                                bad_data_flag)
        # returns None if the data is bad 
        if bad_data_flag:
            return None
        else:
            # audit node["address"] fields for compleness (if applicable)
            if "state" in node["address"] or "city" in node["address"] \
                                            or "postcode" in node["address"] \
                                            or "county" in node["address"]:
                node = audit_address_completeness(node)
            return node
    elif "tiger" in node:
        # audit node["address"]["postcode"] (if applicable) 
        if "zip_left" in node["tiger"]:
            node["address"] = {}
            node["address"]["postcode"], bad_data_flag = audit_postcode(
                                                    None, 
                                                    node["tiger"]["zip_left"], 
                                                    bad_data_flag)
        # audit node["address"]["county"] (if applicable)
        if "county" in node["tiger"]:
            node["address"] = {}
            node["address"]["county"], bad_data_flag = audit_county(
                                                    None, 
                                                    node["tiger"]["county"], 
                                                    bad_data_flag)
        # returns None if the data is bad
        if bad_data_flag:
            return None
        else:
            # audit node["address"] fields for compleness (if applicable)
            if "address" in node:
                if "postcode" in node["address"] or "county" in node["address"]:
                    node = audit_address_completeness(node)
            return node
    else:    
        return node

        
###############################################################################
# @desc: Parses the OSM file by element, tranforms the xml data into JSON dict
#   format, audits/cleans the data, then outputs the data into a JSON document. 
# @param: file_in - OSM file, pretty - pretty print indicator
# @output: file_out - JSON document containing cleaned data
###############################################################################
def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)  # Create JSON output file
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):  # parses OSM file by elem
            el = shape_element(element)  # transforms XML data into JSON format
            if el:
                el = audit_element(el)  # audits/cleans the JSON data
                # if data is good, then it is output to the JSON document
                if el:
                    if pretty:
                        fo.write(json.dumps(el, indent=2)+"\n")
                    else:
                        fo.write(json.dumps(el) + "\n")


###############################################################################
# @desc: Initiate the OSM file processing.
###############################################################################  
if __name__ == "__main__":
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option 
    # adds additional spaces to the output, making it significantly larger.
    process_map(OSMFILE, False)