""" TLEFetch """

import os
import sys
import stat
import json
import time
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dataclasses import dataclass

import requests

#
# This code can retrieve from either tle.ivanstanojevic.me or celestrak.org and uses the json format from the first one.
#

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
# Files are timestamped based on the date returned in the json date value in the file (which is the decoded epoch date anyway).
#
# CelesTrak is a three line acsii format and this code converts it back into the json format above.
#
# Date example... ~/.cache/tle-fetch/69792/69792.2026-07-05T05:54:20.tle.json
# Quick access... ~/.cache/tle-fetch/69792/69792.latest--tle--values.tle.json
#
# The dated file is "touch'ed" to adjust it's times to match the epoch. Hence ls -lt works (as does ls -l because of ISO date in name)
#
# No dependancies are used in this code. You're welcome to wrap this with "sgp4.api" for "Satrec" processing, or another library.
#

@dataclass
class TLE:
	""" TLE """
	name: str = ''
	""" name - optional comment line naming the satellite if using TLE/3LE """
	line1: str = ''
	""" line1 - first line of 2LE, second line of TLE/3LE """
	line2: str = ''
	""" line2 - second line of 2LE, third line of TLE/3LE """

	def __str__(self):
		""" __str__ """
		return '[%s,%s,%s]' % (self.name, self.line1, self.line2)

	@property
	def as_array(self):
		""" as_array """
		return [self.name, self.line1, self.line2]

	@property
	def tle2line(self):
		""" tle2line """
		return self.as_array[1:]

	@property
	def tle3line(self):
		""" tle3line """
		return self.as_array

	@property
	def epoch_age(self):
		""" epoch_age - Extract the epoch string """

		# line1, chars 18-31 (0-indexed)
		epoch_str = self.line1[18:32].strip()

		# Parse the year and the day of the year (including fractional day)
		year_two_digit = int(epoch_str[:2])
		day_fraction = float(epoch_str[2:])

		# Determine the full 4-digit year (assumes post-1957 for space age)
		epoch_year = (1900 if year_two_digit >= 57 else 2000) + year_two_digit

		# Convert fractional day to hours, minutes, seconds
		total_seconds = day_fraction * 24 * 60 * 60
		days = int(total_seconds // (24 * 60 * 60))
		remainder = total_seconds % (24 * 60 * 60)
		hours = int(remainder // (60 * 60))
		remainder %= (60 * 60)
		minutes = int(remainder // 60)
		seconds = int(remainder % 60)

		# Create a datetime object for the epoch starting with month, day being Jan/1'st and then adding the rest
		epoch_month = 1
		epoch_day = 1
		epoch_date_utc = datetime(epoch_year, epoch_month, epoch_day, tzinfo=timezone.utc) + timedelta(days=days - 1, hours=hours, minutes=minutes, seconds=seconds)

		# Calculate the age
		current_time_utc = datetime.now(timezone.utc).replace(microsecond=0)
		tle_age = current_time_utc - epoch_date_utc

		return epoch_date_utc, tle_age

class TLEFetchError(Exception):
	""" TLEFetchError """

class TLEFetch:
	""" TLEFetch """

	_SOURCES = {
		'Ivan': 'https://tle.ivanstanojevic.me/api/tle/%d',
		'CelesTrak': 'https://celestrak.org/NORAD/elements/gp.php?CATNR=%d&FORMAT=TLE',
	}

	_DIR_TLEFetch = '~/.cache/tle-fetch'

	_LATEST_PREFIX = 'latest--tle--values'
	_EXTENSION = 'tle.json'

	_TLE_AGE_OK = 18			# be ok with a TLE file that has an epoch that's up to the age of +/- 18 hours
	_FILE_AGE_OK = 2			# recheck after +/- 2 hours if the local file epoch is older than 18 hours (above)

	_RETRY_COUNT = 4			# try connection (in case of timeout) four times

	_session = None				# we keep the requests session open over many calls - more efficient

	def __init__(self, sat_id:int, source:str='Ivan', directory:str=None, debug:bool=False):
		""" ConstellationLocations """
		self._j = None
		self._tle = None
		self._debug = debug
		self._sat_id = sat_id
		if source not in self._SOURCES.keys():
			raise TLEFetchError('%s: source not supported' % (source)) from None
		self._source = source
		self._url = self._SOURCES[self._source] % (self.sat_id)
		if directory:
			self._directory = directory
		else:
			self._directory = os.getenv('TLECACHE_LOCATION')
			if not self._directory:
				self._directory = self._DIR_TLEFetch
		self._directory = Path(self._directory).expanduser() / str(self.sat_id)
		self._directory.mkdir(parents=True, exist_ok=True)
		if not self._directory.exists():
			raise TLEFetchError('%s: directory does not exist' % (self._directory)) from None

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

	@property
	def tle(self):
		""" tle"""
		self._get()
		if self._tle is None:
			self._tle = TLE(self._j['name'], self._j['line1'], self._j['line2'])
		return self._tle

	@property
	def tle2line(self):
		""" tle2line """
		self._get()
		return [self._j['line1'], self._j['line2']]

	@property
	def tle3line(self):
		""" tle3line """
		self._get()
		return [self._j['name'], self._j['line1'], self._j['line2']]

	def get(self):
		""" get """
		if self._debug:
			print('TLEFetch: GET', self._sat_id, file=sys.stderr, end=' ')
		# try local first...
		filename = self._local_filename()
		if filename.exists() and filename.stat().st_size > 0:
			try:
				self._file_read()
			except (FileNotFoundError,PermissionError):
				self._j = None
				self._tle = None
			if self._j:
				# see if the file is still young enough... make this slightly random to help not hit the server too much
				epoch_age_days, epoch_age_hours = self.epoch_age()
				if (epoch_age_days * 24 + epoch_age_hours) <= random.randint(self._TLE_AGE_OK-1, self._TLE_AGE_OK+1):
					return self._j
				# see if we fetched recently (via the age of the file) ...
				file_age = self._file_age()
				if file_age is not None and file_age <= random.randint(self._FILE_AGE_OK-1, self._FILE_AGE_OK+1) * 60 * 60:
					# we don't want to hit the server too often
					return self._j

		# we are here becuase the local file exists; but is old.
		# save away that value - just in case the network is failing.
		locally_acceptable_json = self._j

		# clearly worth network checking again ...
		self._j = None
		self._tle = None
		try:
			retry_count = self._RETRY_COUNT
			while self._j is None and retry_count > 0:
				self._network_read()
				retry_count -= 1
			if self._j is None:
				raise TLEFetchError('Timeout on connection after %d times' % (self._RETRY_COUNT)) from None
			# sanity check the response
			if self.sat_id != self.satelliteId:
				# we didn't read what we expected to!
				raise TLEFetchError('satelliteId mismatch on network fetch') from None
			# save away the network result
			try:
				self._file_write()
			except TLEFetchError as e:
				raise TLEFetchError(e) from None
		except TLEFetchError as e:
			# at this point we need to decide if a stale TLE is better than throwing an error
			if locally_acceptable_json is None:
				# we've got nothing! :(
				raise TLEFetchError(e) from None
			# use the last read value
			if self._debug:
				print('TLEFetch: USE_LOCAL', self._sat_id, file=sys.stderr)
			self._j = locally_acceptable_json

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
		current_time_utc = datetime.now(timezone.utc).replace(microsecond=0)
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
		if ':' in prefix:
			# Windows is so unhappy with colons in the filename :(
			prefix = prefix.replace(':', '-')
		return self._directory / (str(self.sat_id) + '.' + prefix + '.' + self._EXTENSION)

	def _file_read(self):
		""" _file_read """
		if self._debug:
			print('TLEFetch: FILE_READ', self._sat_id, file=sys.stderr)
		self._j = None
		self._tle = None
		with self._local_filename().open(mode='r', encoding='utf-8') as fd:
			self._j = json.load(fd)

	def _file_write(self):
		""" _file_write """
		if self._debug:
			print('TLEFetch: FILE_WRITE', self._sat_id, file=sys.stderr)
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
			if self._debug:
				print('TLEFetch: PERMISSION_ERROR', self._sat_id, file=sys.stderr)
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
		if self._debug:
			print('TLEFetch: NETWORK_READ', self._sat_id, file=sys.stderr)
		self._j = None
		self._tle = None
		def _network_fetch(url:str):
			""" _network_fetch() """
			headers = {
				# required to make website respond cleanly
				'Accept': 'application/json, text/plain',
				'Accept-Encoding': 'identity',
				'Referer': 'https://google.com/',
				'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
			}
			if TLEFetch._session is None:
				if self._debug:
					print('TLEFetch: NETWORK_SESSION', self._sat_id, file=sys.stderr)
				TLEFetch._session = requests.Session()
			response = TLEFetch._session.get(url, headers=headers, timeout=20)
			response.raise_for_status()
			return response

		try:
			response = _network_fetch(self._url)
		except requests.exceptions.Timeout:
			# classic can't connect issue with timeout - lets retry
			if self._debug:
				print('TLEFetch: TIMEOUT', self._sat_id, file=sys.stderr)
			return
		except requests.exceptions.ConnectionError as e:
			# classic can't connect issue
			try:
				root_os_error = e.args[0].reason.args[0]
			except (AttributeError, IndexError):
				root_os_error = e
			if self._debug:
				print('TLEFetch: HTTP Error', self._sat_id, 'code=', root_os_error, file=sys.stderr)
			raise TLEFetchError('HTTP Error %s: %s' % (root_os_error, self._url)) from None
		except requests.exceptions.HTTPError as e:
			# this would be something like a 404 (Not Found) or 406 (Not Acceptable) response
			if self._debug:
				print('TLEFetch: HTTP Error', self._sat_id, 'code=', e.response.status_code, file=sys.stderr)
			if 400 <= e.response.status_code < 500:
				raise TLEFetchError('HTTP Client Error %d: %s' % (e.response.status_code, self._url)) from None
			raise TLEFetchError('HTTP Server Error %d: %s' % (e.response.status_code, self._url)) from None
		except requests.exceptions.RequestException as e:
			# something else happened - not great!
			if self._debug:
				print('TLEFetch: HTTP Error', self._sat_id, 'code=', e, file=sys.stderr)
			# let it pass up - it could be important to see what happened
			raise TLEFetchError(e) from None

		# process results depending on source chosen.
		if self._source == 'Ivan':
			# so simple
			self._j = response.json()
			self._tle = None

		if self._source == 'CelesTrak':
			# syntetic creation of JSON data - it's kinda reversed; but so be it.
			tle_three_lines = response.text.splitlines()
			self._j = {
				# these three duplicate the info from Ivan ...
				'@context': 'https://www.w3.org/ns/hydra/context.jsonld',
				'@id': self._url,
				'@type': 'Tle',
				# now synthesize the rest ...
				'satelliteId': self._tle_to_sat_id(tle_three_lines[1]),
				'name': tle_three_lines[0].strip(),
				'date': self._tle_to_datetime(tle_three_lines[1]).isoformat(),
				'line1': tle_three_lines[1],
				'line2': tle_three_lines[2],
			}
			self._tle = None

	def _tle_to_sat_id(self, line1):
		""" _tle_to_sat_id """
		return int(line1[2:7].strip())

	def _tle_to_datetime(self, line1):
		""" _tle_to_datetime """
		# Extract the epoch substring from TLE line 1 (columns 19-32)
		epoch_str = line1[18:32].strip()
		year_two_digit = int(epoch_str[:2])
		day_fraction = float(epoch_str[2:])
		# Calculate full 4-digit year (e.g., 2026)
		year = (2000 if year_two_digit < 57 else 1900) + year_two_digit
		# Calculate days and fractional seconds
		day_of_year = int(day_fraction)
		fraction = day_fraction - day_of_year
		# Convert day of year to month and day
		# Create a base date on Jan 1st of that year
		base_date = datetime(year, 1, 1)
		# timedelta takes days, so we add (day_of_year - 1) days
		# plus the fractional day converted to hours/minutes/seconds
		epoch_datetime = base_date + timedelta(days=day_of_year - 1, seconds=fraction * 86400)
		# dump the microseconds - we don't need that much accuracy and dump the timezone
		epoch_datetime = epoch_datetime.replace(microsecond=0, tzinfo=timezone.utc)
		return epoch_datetime

def _main(args=None):
	""" _main """

	debug = False
	if args and len(args) >= 1:
		debug = bool(args[0] == '-d')

	source = 'CelesTrak'

	satellites = {
		25544:	'ISS',
		36411:	'GOES 15',
		58584:	'Arktika-M 2',
		49260:	'Landsat 9',
		48274:	'CSS',
		20580:	'HST',
		28485:	'Swift',
		69792:	'LINK',
		64537:	'Otter Pup 2',
		64539:	'ElaraSat',
	}

	for sat_id, variable_name in satellites.items():
		variable_name = variable_name.replace('-', '_').replace(' ', '_').lower()
		try:
			tf = TLEFetch(sat_id, source=source, debug=debug)
			# j = tf.get()
			tle = tf.tle
		except TLEFetchError as e:
			print('ERROR: TLEFetchError: %s' % (e), file=sys.stderr)
			continue
		if debug:
			epoch_age_days, epoch_age_hours = tf.epoch_age()
			print('# age: %s %s %s %s' % (
				epoch_age_days, 'days' if epoch_age_days > 1 else 'day',
				epoch_age_hours, 'hours' if epoch_age_hours > 1 else 'hour',
			), end='\t')

		print('#', tf.satelliteId, tle.name, tf.date.isoformat())
		print('%s_%d_tle = [' % (variable_name, sat_id))
		print('\t' + "'" + tle.line1 + "',")
		print('\t' + "'" + tle.line2 + "',")
		print(']')
		print('')

	if debug:
		print('', file=sys.stderr)

if __name__ == '__main__':
	_main(args=sys.argv[1:])
