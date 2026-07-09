""" TLEFetch """

import os
import stat
import json
import time
import random
from datetime import datetime, timezone
from pathlib import Path

import requests

#
# https://tle.ivanstanojevic.me/#docs
#
# {
#   "@context": "https://www.w3.org/ns/hydra/context.jsonld",
#   "@id": "https://tle.ivanstanojevic.me/api/tle/28485",
#   "@type": "Tle",
#   "satelliteId": 28485,
#   "name": "SWIFT",
#   "date": "2026-07-05T21:01:49+00:00",
#   "line1": "1 28485U 04047A   26186.87627307  .00061981  00000+0  47565-3 0  9999",
#   "line2": "2 28485  20.5532  40.5436 0000897 245.9890 114.0463 15.70286946189802"
# }
#
# Everything received is stored as json so that the metadata is preserved.
# Files are timestamped based on the date returned in the json porttion of the file (which is the decoded epoch date anyway).
#
# Date example... ~/.cache/tle.ivanstanojevic.me/69792/69792.2026-07-05T05:54:20.tle.json
# Quick access... ~/.cache/tle.ivanstanojevic.me/69792/69792.latest--tle--values.tle.json
#

class TLEFetchError(Exception):
	""" TLEFetchError """

class TLEFetch:
	""" TLEFetch """

	_URL_IVAN = 'https://tle.ivanstanojevic.me/api/tle/%d'
	_URL_CELESTRAK = 'https://celestrak.org/NORAD/elements/gp.php?CATNR=%d&FORMAT=TLE'

	_DIR_TLECache = '~/.cache/tle.ivanstanojevic.me'
	_LATEST_PREFIX = 'latest--tle--values'
	_EXTENSION = 'tle.json'
	_TLE_AGE_OK = 24			# be ok with a TLE file that has an epoch that's up to the age of +/- 24 hours
	_FILE_AGE_OK = 2			# recheck after +/- 2 hours if the local file epoch is older than 24 hours (above)

	def __init__(self, sat_id:int, source='Ivan', directory:str=None):
		""" ConstellationLocations """

		self._sat_id = sat_id

		if source not in ['Ivan', 'CelesTrak']:
			raise TLEFetchError('%s: source not supported' % (source)) from None

		self._url_source = source

		if self._url_source == 'Ivan':
			self._url = self._URL_IVAN % (self.sat_id)
		if self._url_source == 'CelesTrak':
			self._url = self._URL_CELESTRAK % (self.sat_id)

		if directory:
			self._directory = directory
		else:
			self._directory = os.getenv('TLECACHE_LOCATION')
			if not self._directory:
				self._directory = self._DIR_TLECache
		self._directory = Path(self._directory).expanduser() / str(self.sat_id)
		self._directory.mkdir(parents=True, exist_ok=True)
		if not self._directory.exists():
			raise TLEFetchError('%s: directory does not exist' % (self._directory)) from None

		self._j = None

	@property
	def sat_id(self):
		""" sat_id """
		return self._sat_id

	@property
	def satelliteId(self):
		""" satelliteId """
		self._get()
		return self._j['satelliteId']

	@property
	def name(self):
		""" name """
		self._get()
		return self._j['name']

	@property
	def date(self):
		""" date """
		self._get()
		try:
			return datetime.fromisoformat(self._j['date']).replace(tzinfo=timezone.utc)
		except ValueError:
			# should not happen; but if it does...
			raise TLEFetchError('date invalid in TLE info') from None

	def tle2line(self):
		""" tle2line """
		self._get()
		return [self._j['line1'], self._j['line2']]

	def tle3line(self):
		""" tle3line """
		self._get()
		return [self._j['name'], self._j['line1'], self._j['line2']]

	def get(self):
		""" get """
		# try local first...
		filename = self._local_filename()
		if filename.exists() and filename.stat().st_size > 0:
			try:
				self._file_read()
			except (FileNotFoundError,PermissionError):
				self._j = None
			# see if the file is still young enough... make this slightly random to help not hit the server too much
			epoch_age_days, epoch_age_hours = self.epoch_age()
			if (epoch_age_days * 24 + epoch_age_hours) <= random.randint(self._TLE_AGE_OK-1, self._TLE_AGE_OK+1):
				return self._j
			# see if we fetched recently (via the age of the file) ...
			file_age = self._file_age()
			if file_age is not None and file_age <= random.randint(self._FILE_AGE_OK-1, self._FILE_AGE_OK+1) * 60 * 60:
				# we don't want to hit the server too often
				return self._j

		# clearly worth network checking again ...
		try:
			self._network_read()
		except TLEFetchError as e:
			raise TLEFetchError(e) from None

		if self.sat_id != self.satelliteId:
			# we didn't read what we expected to!
			raise TLEFetchError('satelliteId mismatch on network fetch') from None

		try:
			self._file_write()
		except TLEFetchError as e:
			raise TLEFetchError(e) from None

		return self._j

	def epoch_age(self):
		""" epoch_age """
		self._get()
		if self._j is None:
			return 0, 0
		try:
			tle_epoch_utc = self.date
		except TLEFetchError:
			# should not happen; but if it does, we return zeros
			return 0, 0
		current_time_utc = datetime.now(timezone.utc)
		epoch_age_timedelta = current_time_utc - tle_epoch_utc

		epoch_age_days = int(epoch_age_timedelta.days)
		epoch_age_hours = int(epoch_age_timedelta.seconds / (60*60))
		return epoch_age_days, epoch_age_hours

	def _get(self):
		""" _get() """
		if self._j is None:
			_ = self.get()

	def _local_filename(self, prefix=None):
		""" _local_filename() """
		if prefix is None:
			prefix = self._LATEST_PREFIX
		return self._directory / (str(self.sat_id) + '.' + prefix + '.' + self._EXTENSION)

	def _file_read(self):
		""" _file_read """
		with self._local_filename().open(mode='r', encoding='utf-8') as fd:
			self._j = json.load(fd)

	def _file_write(self):
		""" _file_write """
		if self._j is None:
			raise TLEFetchError('no daat to write') from None

		# latest file ... no adjusted time ...
		filename = self._local_filename()
		with filename.open(mode='w', encoding='utf-8') as fd:
			json.dump(self._j, fd)

		# remove the +00:00 (TZ UTC) because it's just not needed
		date_prefix = self._j['date'][:-6]
		filename = self._local_filename(date_prefix)
		# dated file ... with adjusted access/modified time ...
		try:
			with filename.open(mode='w', encoding='utf-8') as fd:
				json.dump(self._j, fd)
			# match file mofified/created time to match epoch time
			timestamp = self.date.timestamp()
			os.utime(filename, times=(timestamp, timestamp))
			# set read only so it does not get rewritten again
			filename.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

		except PermissionError:
			# print('PERMISSION ERROR')
			# just means we already have that date saved-away - not an issue
			pass
		except Exception as e:
			# we could get other errors - maybe
			raise TLEFetchError(e) from None

	def _file_age(self):
		""" _file_age() """
		filename = self._local_filename()
		try:
			age = int(time.time() - os.stat(filename).st_mtime)
		except (FileNotFoundError,PermissionError):
			return None
		return age

	def _network_read(self):
		""" network_read """

		def _network_fetch(url:str):
			""" _network_fetch() """
			headers = {
				# required to make website respond cleanly
				'Accept-Encoding': 'text/plain',
				'Referer': 'https://google.com/',
				'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
			}
			response = requests.get(url, headers=headers, timeout=20)
			response.raise_for_status()
			return response

		try:
			response = _network_fetch(self._url)
		except requests.exceptions.Timeout:
			# classic can't connect issue with timeout
			raise TLEFetchError('HTTP Error %s: %s' % ('Timeout', self._url)) from None
		except requests.exceptions.ConnectionError as e:
			# classic can't connect issue
			try:
				root_os_error = e.args[0].reason.args[0]
			except (AttributeError, IndexError):
				root_os_error = e
			raise TLEFetchError('HTTP Error %s: %s' % (root_os_error, self._url)) from None
		except requests.exceptions.HTTPError as e:
			# this would be something like a 404 (Not Found) or 406 (Not Acceptable) response
			if 400 <= e.response.status_code < 500:
				raise TLEFetchError('HTTP Client Error %d: %s' % (e.response.status_code, self._url)) from None
			raise TLEFetchError('HTTP Server Error %d: %s' % (e.response.status_code, self._url)) from None
		except requests.exceptions.RequestException as e:
			# something else happened - not great!
			# let it pass up - it could be important to see what happened
			raise TLEFetchError(e) from None

		if self._url_source == 'Ivan':
			self._j = response.json()

		if self._url_source == 'CelesTrak':
			three_lines = response.text.splitlines()
			# syntetic creation of JSON data - it's kinda reversed; but so be it.
			self._j = {
				'satelliteId': self._tle_to_sat_id(three_lines[1]),
				'name': three_lines[0].strip(),
				'date': self._tle_to_datetime(three_lines[1]),
				'line1': three_lines[1],
				'line2': three_lines[2],
			}

	def _tle_to_sat_id(self, line1):
		""" _tle_to_sat_id """
		return int(line_1[2:8].strip())

	def _tle_to_datetime(self, line1):
		""" _tle_to_datetime """

		# Extract the epoch substring from TLE line 1 (columns 19-32)
		epoch_str = line1[18:32].strip()

		year_str = epoch_str[:2]
		day_fraction = epoch_str[2:]

		# Calculate full 4-digit year (e.g., 2026)
		year = int(year_str)
		year += 2000 if year < 57 else 1900

		# Calculate days and fractional seconds
		total_days = float(day_fraction)
		day_of_year = int(total_days)
		fraction = total_days - day_of_year

		# Convert day of year to month and day
		# Create a base date on Jan 1st of that year
		base_date = datetime(year, 1, 1).replace(tzinfo=timezone.utc)

		# timedelta takes days, so we add (day_of_year - 1) days
		# plus the fractional day converted to hours/minutes/seconds
		epoch_datetime = base_date + timedelta(days=day_of_year - 1, seconds=fraction * 86400)

		return epoch_datetime

def _main(args=None):
	""" _main """

	debug = False
	if args and len(args) >= 1:
		debug = bool(args[0] == '-d')

	source = 'CelesTrak'

	satellites = {
		'iss': 25544,
		'goes_15': 36411,
		'arktika_m2': 58584,
		'landsat_9': 49260,
		'css': 48274,
		'hst': 20580,
		'swift_telescope': 28485,
		'link_rescue': 69792,
	}

	for name, sat_id in satellites.items():
		tf = TLEFetch(sat_id, source=source)
		# j = tf.get()
		tle = tf.tle3line()
		if debug:
			epoch_age_days, epoch_age_hours = tf.epoch_age()
			print('# age: %s %s %s %s' % (
				epoch_age_days, 'days' if epoch_age_days > 1 else 'day',
				epoch_age_hours, 'hours' if epoch_age_hours > 1 else 'hour',
			), end='\t')

		print('#', tf.satelliteId, tf.name, tf.date.isoformat())
		print('%s_%d_tle = [' % (name, sat_id))
		print('\t' + "'" + tle[1] + "',")
		print('\t' + "'" + tle[2] + "',")
		print(']')
		print('')

if __name__ == '__main__':
	import sys			# pylint: disable=C0415
	_main(args=sys.argv[1:])
