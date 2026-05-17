""" Constellation Database """

# https://en.wikipedia.org/wiki/IAU_designated_constellations
# In contemporary astronomy, 88 constellations are recognized by the International Astronomical Union (IAU).

# The same list as https://www.iau.org/IAU/Iau/Science/What-we-do/The-Constellations.aspx
# We don't need all the columns; but, they are left there for completeness reasons
# Also see https://commons.wikimedia.org/wiki/File:Constellations,_equirectangular_plot.svg
# For a positioning check

# Wikipedia was scraped with approx' the following code
#
# import requests
# from bs4 import BeautifulSoup
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' }
# url = "https://en.wikipedia.org/wiki/IAU_designated_constellations"
# response = requests.get(url, headers=headers)
# response.raise_for_status()
# soup = BeautifulSoup(response.text, "html.parser")
# table = soup.find("div", {"id": "bodyContent"}).find_next("table")
# # Extract headers
# headers = [th.get_text(strip=True) for th in table.find_all("th")]
# print(headers)
# # Extract rows
# for row in table.find_all("tr")[1:]:
#     cols = [td.get_text(strip=True) for td in row.find_all("td")]
#     print(cols)

import re
from .StarCatalog.constellation import Constellation

class ConstellationDatabase:
	""" ConstellationDatabase """

	_data = [
		['Constellation',	'IAU Abbr',	'NASA Abbr',	'Genitive',		'Origin',			'Meaning',		'Brightest star Name',	'Brightest star Vis. mag.'],
		['Andromeda',		'And',		'Andr',		'Andromedae',		'ancient (Ptolemy)',		'Andromeda(mythological character)',	'Alpheratz',	'2.06'],
		['Antlia',		'Ant',		'Antl',		'Antliae',		'1756,Lacaille, as Antlia Pneumatica',	'(air) pump',	'α Antliae',	'4.25'],
		['Apus',		'Aps',		'Apus',		'Apodis',		'1598,Plancius,Keyser,de Houtman',	'bird-of-paradise',	'α Apodis',	'3.83'],
		['Aquarius',		'Aqr',		'Aqar',		'Aquarii',		'ancient (Ptolemy)',		'water-bearer',	'Sadalsuud',	'2.87'],
		['Aquila',		'Aql',		'Aqil',		'Aquilae',		'ancient (Ptolemy)',		'eagle',	'Altair',	'0.76'],
		['Ara',			'Ara',		'Arae',		'Arae',			'ancient (Ptolemy)',		'altar',	'β Arae',	'2.84'],
		['Aries',		'Ari',		'Arie',		'Arietis',		'ancient (Ptolemy)',		'ram',	'Hamal',	'2.00'],
		['Auriga',		'Aur',		'Auri',		'Aurigae',		'ancient (Ptolemy)',		'charioteer',	'Capella',	'0.08'],
		['Boötes',		'Boo',		'Boot',		'Boötis',		'ancient (Ptolemy)',		'herdsman',	'Arcturus',	'-0.05'],
		['Caelum',		'Cae',		'Cael',		'Caeli',		'1756,Lacaille, as Caelum Sculptorium',	'chiselor engraving tool',	'α Caeli',	'4.46'],
		['Camelopardalis',	'Cam',		'Caml',		'Camelopardalis',	'1613,Plancius',			'giraffe',	'β Camelo\xadpardalis',	'4.02'],
		['Cancer',		'Cnc',		'Canc',		'Cancri',		'ancient (Ptolemy)',		'crab',	'β Cancri',	'3.52'],
		['Canes Venatici',	'CVn',		'CVen',		'Canum Venaticorum',	'1690,Firmamentum Sobiescianum,Hevelius',	'hunting dogs',	'Cor Caroli',	'2.81'],
		['Canis Major',		'CMa',		'CMaj',		'Canis Majoris',	'ancient (Ptolemy)',		'greater dog',	'Sirius',	'-1.46'],
		['Canis Minor',		'CMi',		'CMin',		'Canis Minoris',	'ancient (Ptolemy)',		'lesser dog',	'Procyon',	'0.34'],
		['Capricornus',		'Cap',		'Capr',		'Capricorni',		'ancient (Ptolemy)',		'sea goat',	'Deneb Algedi',	'2.83'],
		['Carina',		'Car',		'Cari',		'Carinae',		'ancient (Ptolemy); 1756,Lacaille, split from Argo Navis',	'keel',	'Canopus',	'-0.74'],
		['Cassiopeia',		'Cas',		'Cass',		'Cassiopeiae',		'ancient (Ptolemy)',		'Cassiopeia(mythological character)',	'Schedar',	'2.24'],
		['Centaurus',		'Cen',		'Cent',		'Centauri',		'ancient (Ptolemy)',		'centaur',	'Alpha Centauri',	'-0.27'],
		['Cepheus',		'Cep',		'Ceph',		'Cephei',		'ancient (Ptolemy)',		'Cepheus(mythological character)',	'Alderamin',	'2.46'],
		['Cetus',		'Cet',		'Ceti',		'Ceti',			'ancient (Ptolemy)',		'sea monster(later interpreted as a whale)',	'Diphda',	'2.02'],
		['Chamaeleon',		'Cha',		'Cham',		'Chamaeleontis',	'1598,Plancius,Keyser,de Houtman',	'chameleon',		'α Chamae\xadleontis',	'4.06'],
		['Circinus',		'Cir',		'Circ',		'Circini',		'1756,Lacaille',		'compasses',	'α Circini',	'3.19'],
		['Columba',		'Col',		'Colm',		'Columbae',		'1592,Plancius, split from Canis Major',	'dove',			'Phact',	'2.65'],
		['Coma Berenices',	'Com',		'Coma',		'Comae Berenices',	'ancient (Ptolemy); 1536,Caspar Vopel, split from Leo',	"Berenice's hair",	'β Comae Berenices',	'4.26'],
		['Corona Australis',	'CrA',		'CorA',		'Coronae Australis',	'ancient (Ptolemy)',		'southerncrown',	'α Coronae Australis',	'4.10'],
		['Corona Borealis',	'CrB',		'CorB',		'Coronae Borealis',	'ancient (Ptolemy)',		'northern crown',	'Alphecca',	'2.24'],
		['Corvus',		'Crv',		'Corv',		'Corvi',		'ancient (Ptolemy)',		'crow',	'Gienah',	'2.59'],
		['Crater',		'Crt',		'Crat',		'Crateris',		'ancient (Ptolemy)',		'cup',	'δ Crateris',	'3.56'],
		['Crux',		'Cru',		'Cruc',		'Crucis',		'1589,Plancius, split from Centaurus',	'southerncross',	'Acrux',	'0.76'],
		['Cygnus',		'Cyg',		'Cygn',		'Cygni',		'ancient (Ptolemy)',		'swanor Northern Cross',	'Deneb',	'1.25'],
		['Delphinus',		'Del',		'Dlph',		'Delphini',		'ancient (Ptolemy)',		'dolphin',	'β Delphini',	'3.62'],
		['Dorado',		'Dor',		'Dora',		'Doradus',		'1598,Plancius,Keyser,de Houtman',	'mahi-mahi(dolphinfish)',	'α Doradus',	'3.28'],
		['Draco',		'Dra',		'Drac',		'Draconis',		'ancient (Ptolemy)',		'dragon',	'Eltanin',	'2.23'],
		['Equuleus',		'Equ',		'Equl',		'Equulei',		'ancient (Ptolemy)',		'pony',	'α Equulei',	'3.92'],
		['Eridanus',		'Eri',		'Erid',		'Eridani',		'ancient (Ptolemy)',		'river Eridanus(mythology)',	'Achernar',	'0.46'],
		['Fornax',		'For',		'Forn',		'Fornacis',		'1756,Lacaille, as Fourneau Chymique',	'(chemical)furnace',	'α Fornacis',	'3.85'],
		['Gemini',		'Gem',		'Gemi',		'Geminorum',		'ancient (Ptolemy)',		'twins',	'Pollux',	'1.14'],
		['Grus',		'Gru',		'Grus',		'Gruis',		'1598,Plancius,Keyser,de Houtman',	'crane(bird)',		'Alnair',	'1.74'],
		['Hercules',		'Her',		'Herc',		'Herculis',		'ancient (Ptolemy)',		'Hercules(mythological character)',	'Korne\xadphoros',	'2.81'],
		['Horologium',		'Hor',		'Horo',		'Horologii',		'1756,Lacaille',		'pendulum clock',	'α Horologii',	'3.85'],
		['Hydra',		'Hya',		'Hyda',		'Hydrae',		'ancient (Ptolemy)',		'Hydra(mythological creature)',	'Alphard',	'2.00'],
		['Hydrus',		'Hyi',		'Hydi',		'Hydri',		'1598,Plancius,Keyser,de Houtman',	'lesserwater snake',	'β Hydri',	'2.80'],
		['Indus',		'Ind',		'Indi',		'Indi',			'1598,Plancius,Keyser,de Houtman',	'Indian(of unspecified type)',	'α Indi',	'3.11'],
		['Lacerta',		'Lac',		'Lacr',		'Lacertae',		'1690,Firmamentum Sobiescianum,Hevelius',	'lizard',	'α Lacertae',	'3.76'],
		['Leo Minor',		'LMi',		'LMin',		'Leonis Minoris',	'1690,Firmamentum Sobiescianum,Hevelius',	'lesser lion',	'46 Leonis Minoris',	'3.83'],
		['Leo',			'Leo',		'Leon',		'Leonis',		'ancient (Ptolemy)',		'lion',	'Regulus',	'1.35'],
		['Lepus',		'Lep',		'Leps',		'Leporis',		'ancient (Ptolemy)',		'hare',	'Arneb',	'2.59'],
		['Libra',		'Lib',		'Libr',		'Librae',		'ancient (Ptolemy)',		'balance',	'Zuben\xadeschemali',	'2.61'],
		['Lupus',		'Lup',		'Lupi',		'Lupi',			'ancient (Ptolemy)',		'wolf',	'α Lupi',	'2.30'],
		['Lynx',		'Lyn',		'Lync',		'Lyncis',		'1690,Firmamentum Sobiescianum,Hevelius',	'lynx',	'α Lyncis',	'3.14'],
		['Lyra',		'Lyr',		'Lyra',		'Lyrae',		'ancient (Ptolemy)',		'lyre/harp',	'Vega',	'0.02'],
		['Mensa',		'Men',		'Mens',		'Mensae',		'1756,Lacaille, as Mons Mensæ',		'Table Mountain(South Africa)',	'α Mensae',	'5.09'],
		['Microscopium',	'Mic',		'Micr',		'Microscopii',		'1756,Lacaille',		'microscope',	'γ Microscopii',	'4.68'],
		['Monoceros',		'Mon',		'Mono',		'Monocerotis',		'1613,Plancius',			'unicorn',	'β Monocerotis',	'3.74'],
		['Musca',		'Mus',		'Musc',		'Muscae',		'1598,Plancius,Keyser,de Houtman',	'fly',			'α Muscae',	'2.69'],
		['Norma',		'Nor',		'Norm',		'Normae',		'1756,Lacaille',		"carpenter's level",	'γ2Normae',	'4.02'],
		['Octans',		'Oct',		'Octn',		'Octantis',		'1756,Lacaille',		'octant (instrument)',	'ν Octantis',	'3.73'],
		['Ophiuchus',		'Oph',		'Ophi',		'Ophiuchi',		'ancient (Ptolemy)',		'serpent-bearer',	'Rasalhague',	'2.07'],
		['Orion',		'Ori',		'Orio',		'Orionis',		'ancient (Ptolemy)',		'Orion(mythological character)',	'Rigel',	'0.13'],
		['Pavo',		'Pav',		'Pavo',		'Pavonis',		'1598,Plancius,Keyser,de Houtman',	'peacock',		'Peacock',	'1.94'],
		['Pegasus',		'Peg',		'Pegs',		'Pegasi',		'ancient (Ptolemy)',		'Pegasus(mythological winged horse)',	'Enif',	'2.40'],
		['Perseus',		'Per',		'Pers',		'Persei',		'ancient (Ptolemy)',		'Perseus(mythological character)',	'Mirfak',	'1.82'],
		['Phoenix',		'Phe',		'Phoe',		'Phoenicis',		'1598,Plancius,Keyser,de Houtman',	'phoenix',		'Ankaa',	'2.38'],
		['Pictor',		'Pic',		'Pict',		'Pictoris',		'1756,Lacaille, as Equuleus Pictoris', "Painter (originally 'painter's easel')",	'α Pictoris',	'3.27'],
		['Pisces',		'Psc',		'Pisc',		'Piscium',		'ancient (Ptolemy)',		'fish(plural)',	'Alpherg',	'3.61'],
		['Piscis Austrinus',	'PsA',		'PscA',		'Piscis Austrini',	'ancient (Ptolemy)',		'southern fish',	'Fomalhaut',	'1.16'],
		['Puppis',		'Pup',		'Pupp',		'Puppis',		'ancient (Ptolemy); 1756,Lacaille, split from Argo Navis',	'poop deck',	'Naos',	'2.25'],
		['Pyxis',		'Pyx',		'Pyxi',		'Pyxidis',		'1756,Lacaille, as Pyxis Nautica',	"mariner's compass",	'α Pyxidis',	'3.67'],
		['Reticulum',		'Ret',		'Reti',		'Reticuli',		'1756,Lacaille',		'eyepiece graticule',	'α Reticuli',	'3.32'],
		['Sagitta',		'Sge',		'Sgte',		'Sagittae',		'ancient (Ptolemy)',		'arrow',	'γ Sagittae',	'3.47'],
		['Sagittarius',		'Sgr',		'Sgtr',		'Sagittarii',		'ancient (Ptolemy)',		'archer',	'Kaus Australis',	'1.85'],
		['Scorpius',		'Sco',		'Scor',		'Scorpii',		'ancient (Ptolemy)',		'scorpion',	'Antares',	'0.91'],
		['Sculptor',		'Scl',		'Scul',		'Sculptoris',		'1756,Lacaille, as Apparatus Sculptoris', "sculptor(originally 'sculptor's studio')",	'α Sculptoris',	'4.30'],
		['Scutum',		'Sct',		'Scut',		'Scuti',		'1690,Firmamentum Sobiescianum,Hevelius',	'shield (of Sobieski)',	'α Scuti',	'3.83'],
		['Serpens',		'Ser',		'Serp',		'Serpentis',		'ancient (Ptolemy)',		'snake',	'Unukalhai',	'2.62'],
		['Sextans',		'Sex',		'Sext',		'Sextantis',		'1690,Firmamentum Sobiescianum,Hevelius',	'sextant',	'α Sextantis',	'4.49'],
		['Taurus',		'Tau',		'Taur',		'Tauri',		'ancient (Ptolemy)',		'bull',	'Aldebaran',	'0.86'],
		['Telescopium',		'Tel',		'Tele',		'Telescopii',		'1756,Lacaille',		'telescope',	'α Telescopii',	'3.51'],
		['Triangulum Australe',	'TrA',		'TrAu',		'Trianguli Australis',	'1598,Plancius,Keyser,de Houtman',	'southern triangle',	'Atria',	'1.91'],
		['Triangulum',		'Tri',		'Tria',		'Trianguli',		'ancient (Ptolemy)',		'triangle',	'β Trianguli',	'3.00'],
		['Tucana',		'Tuc',		'Tucn',		'Tucanae',		'1598,Plancius,Keyser,de Houtman',	'toucan',		'α Tucanae',	'2.86'],
		['Ursa Major',		'UMa',		'UMaj',		'Ursae Majoris',	'ancient (Ptolemy)',		'great bear',	'Alioth',	'1.77'],
		['Ursa Minor',		'UMi',		'UMin',		'Ursae Minoris',	'ancient (Ptolemy)',		'lesser bear',	'Polaris',	'1.98'],
		['Vela',		'Vel',		'Velr',		'Velorum',		'ancient (Ptolemy); 1756,Lacaille, split from Argo Navis',	'sails',	'γ Velorum',	'1.83'],
		['Virgo',		'Vir',		'Virg',		'Virginis',		'ancient (Ptolemy)',		'virgin, maiden',	'Spica',	'0.97'],
		['Volans',		'Vol',		'Voln',		'Volantis',		'1598,Plancius,Keyser,de Houtman, as Piscis Volans',	'flying fish',	'γ2Volantis',	'3.75'],
		['Vulpecula',		'Vul',		'Vulp',		'Vulpeculae',		'1690,Firmamentum Sobiescianum,Hevelius, as Vulpecula cum Ansere',	"littlefox(originally, 'little fox with the goose')",	'α Vulpeculae',	'4.40'],
	]
	_constellations = None
	_index = None

	def __init__(self):
		""" ConstellationDatabase """

	@classmethod
	def _build(cls):
		""" _build """
		if ConstellationDatabase._constellations:
			return
		ConstellationDatabase._constellations = [Constellation(*v) for v in ConstellationDatabase._data[1:]]
		ConstellationDatabase._index = {}
		for c in cls._constellations:
			for v in [c.constellation, c.iau_abbreviations, c.nasa_abbreviations, c.genitive, c.origin, c.meaning]:
				ConstellationDatabase._index[v.lower()] = c

	@classmethod
	def find(cls, name: str):
		""" find """
		cls._build()
		try:
			return cls._index[name.lower()]
		except:
			raise IndexError(name) from None

	@classmethod
	def all(cls):
		""" all """
		cls._build()
		return cls._constellations

	@classmethod
	def match(cls, pattern) -> list :
		""" match """
		cls._build()
		regex = re.compile(pattern, re.IGNORECASE)
		results = {}
		for keyword in set(filter(lambda v: regex.match(v), cls._index.keys())):
			results[cls.find(keyword)] = None
		return sorted(results.keys(), key=lambda v: v.constellation)

	@classmethod
	def fullmatch(cls, pattern) -> list :
		""" fullmatch """
		cls._build()
		regex = re.compile(pattern, re.IGNORECASE)
		results = {}
		for keyword in set(filter(lambda v: regex.fullmatch(v), cls._index.keys())):
			results[cls.find(keyword)] = None
		return sorted(results.keys(), key=lambda v: v.constellation)

	@classmethod
	def search(cls, pattern) -> list :
		""" search """
		cls._build()
		regex = re.compile(pattern, re.IGNORECASE)
		results = {}
		for keyword in set(filter(lambda v: regex.search(v), cls._index.keys())):
			results[cls.find(keyword)] = None
		return sorted(results.keys(), key=lambda v: v.constellation)

	@classmethod
	def __len__(cls):
		""" __len__ """
		cls._build()
		return len(cls._constellations)

def _main(args=None):
	""" _main """

	cd = ConstellationDatabase()

	print('# Constellations =', len(cd))
	for name in ['Orion', 'TRIANGULI AUSTRALIS', 'Sco', 'great bear', 'Norma']:
		print('%-20s= %s' % (name, str(cd.find(name))[0:150]))
	print('')

	for c in cd.all():
		if c.constellation == c.iau_abbreviations or c.constellation == c.nasa_abbreviations:
			print('same:', c.constellation, c.iau_abbreviations, c.nasa_abbreviations, c.meaning)
	print('')

	what = r'Roger|Rabbit'
	print('search()', what)
	for c in cd.search(what):
		print('\t', c)
	print('')

	what = r'great'
	print('search()', what)
	for c in cd.search(what):
		print('\t', c)
	print('')

	what = r'Lacaille'
	print('search()', what)
	for c in cd.search(what):
		print('\t', c)
	print('')

	what = r'Australis|Majoris'
	print('search()', what)
	for c in cd.search(what):
		print('\t', c)
	print('')
	print('match()', what)
	for c in cd.match(what):
		print('\t', c)
	print('')

	what = r'Leo|Ursa'
	print('match()', what)
	for c in cd.match(what):
		print('\t', c)
	print('')

	what = r'Leo'
	print('match()', what)
	for c in cd.match(what):
		print('\t', c)
	print('')

	what = r'Leo'
	print('fullmatch()', what)
	for c in cd.fullmatch(what):
		print('\t', c)
	print('')

if __name__ == '__main__':
	_main()
