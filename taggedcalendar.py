#! /usr/bin/env python

"""
Module for simple text-based calendars with tagging of specific dates.
"""

from __future__ import with_statement
import sys
import datetime
import locale as _locale
from calendar import TextCalendar
from calendar import month_name, month_abbr
from calendar import day_name, day_abbr
from calendar import formatstring
from calendar import SUNDAY, MONDAY
	
# example tags
TAG_BLACK = '\033[0;30m%s\033[0m'
TAG_DARKGRAY = '\033[1;30m%s\033[0m'
TAG_LIGHTGRAY = '\033[0;37m%s\033[0m'
TAG_WHITE = '\033[1;37m%s\033[0m'
TAG_RED = '\033[0;31m%s\033[0m'
TAG_ORANGE = '\033[1;31m%s\033[0m'
TAG_DARKGREEN = '\033[0;32m%s\033[0m'
TAG_LIGHTGREEN = '\033[1;32m%s\033[0m'
TAG_DARKYELLOW = '\033[0;33m%s\033[0m'
TAG_LIGHTYELLOW = '\033[1;33m%s\033[0m'
TAG_DARKBLUE = '\033[0;34m%s\033[0m'
TAG_LIGHTBLUE = '\033[1;34m%s\033[0m'
TAG_DARKPURPLE = '\033[0;35m%s\033[0m'
TAG_LIGHTPURPLE = '\033[1;35m%s\033[0m'
TAG_DARKTEAL = '\033[0;36m%s\033[0m'
TAG_LIGHTTEAL = '\033[1;36m%s\033[0m'
TAG_NONE = '\033[0m%s\033[0m'

__all__ = ['TaggedTextCalendar', 'LocaleTaggedTextCalendar']

class TaggedTextCalendar(TextCalendar):
	"""
	Simple TaggedTextCalendar class.  Modifies the standard Python calendar
	module's TextCalendar class to provide for tagging of specific dates.
	Tagged dates are tagged with the string of your choice.  Most helpful
	for creating an ASCII Calendar with the tagged date color coded using
	default ASCII color codes.
	"""
	def __init__(self, firstweekday=0, tag_today=TAG_RED):
		super(TaggedTextCalendar, self).__init__(firstweekday)
		self._tags = {}
		self.addTag(datetime.date.today(), tag_today)
	# end __init__
	
	@property
	def tags(self):
		"""
		Property to return the current tags dictionary.
		"""
		return self._tags
	# end tags
	
	def addTag(self, date, tag):
		"""
		Insert a tag for a given date.  Date should be a datetime.date object
		(or derivative class), and tag should be a string format that you will
		wrap around the given date in your calendar (ie: "\033[0;33m%s\033[0m"
		will wrap your date in the ASCII color odes for Dark Yellow).
		"""
		assert isinstance(date, datetime.date), 'Argument date \"%s\" must' \
			'be a datetime.date object'
		self._tags[date] = tag
	# end addTag
	
	def removeTag(self, date):
		"""
		Remove a tag, if any, for a given date.
		"""
		assert isinstance(date, datetime.date), 'Argument date \"%s\" must' \
			'be a datetime.date object'
		if date in self.tags.keys():
			self._tags.pop(date)
	# end removeTag
	
	def formatday(self, date, display, width):
		"""
		Formats an individual date.  Should only be called by formatweek.
		"""
		result = ''
		if display:
			result = '%2i' % date.day
		result = result.center(width)
		if date in self.tags.keys():
			result = self.tags[date] % result
		return result
    # end formatday

	def formatweek(self, days, width, day_sep=' '):
		"""
		Formats a given week.  A week should be a list of seven tuples.
		First item is the datetime.date, second is a boolean indicating if the 
		given date should be displayed.  This will usually only be false if the
		given date in a week string falls outside the current month.
		"""
		result = []
		for date, display in days:
			result.append(self.formatday(date, display, width))        			
		return day_sep.join(result)
	# end formatweek

	def formatmonth(self, year, month, width=2, pad=1):
		"""
		Formats a single month calendar for the specified month and year.  Use 
		the prmonth method to print to stdout.
		"""
		width = max(2, width)
		pad = max(1, pad)
		
		result = []
		
		monthname = self.formatmonthname(year, month, (width + 1) * 7 - 1)
		result.append(monthname.rstrip())
		result.append('\n' * pad)
		weeknames = self.formatweekheader(width)
		result.append(weeknames.rstrip())
		result.append('\n' * pad)
		
		for week in self.monthdatescalendar(year, month):
			days = [(date, date.month == month) for date in week]
			result.append(self.formatweek(days, width).rstrip())
			result.append('\n' * pad)
			
		return ''.join(result)
	# end formatmonth
	
	def prmonth(self, year, month, width=0, pad=0):
		"""
		Print formatted calendar for single month for specified month and year.
		"""
		print self.formatmonth(year, month, width, pad)
	# end prmonth

	def formatyear(self, year, width=2, pad=1, spacing=6, months=3):
		"""
		Formats a 12 month calendar for the specified year.  Use the pryear 
		method to print to stdout.
		"""
		width = max(2, width)
		pad = max(1, pad)
		spacing = max(2, spacing)
		colwidth = (width + 1) * 7 - 1
		
		result = []
		yearname = repr(year).center(colwidth * months + spacing * (months - 1))
		result.append(yearname.rstrip())
		result.append('\n' * pad)
		
		header = self.formatweekheader(width)
		for (idx, row) in enumerate(self.yeardatescalendar(year, months)):
			start_month = months * idx + 1
			end_month = min(months * (idx + 1) + 1, 13)
			row_months = range(start_month, end_month)
			result.append('\n' * pad)
			
			names = (self.formatmonthname(year, m, colwidth, False) for m in \
				row_months)
			result.append(formatstring(names, colwidth, spacing).rstrip())
			result.append('\n' * pad)
			
			headers = (header for m in row_months)
			result.append(formatstring(headers, colwidth, spacing).rstrip())
			result.append('\n' * pad)
			
			thisrow = []
			for cal_idx, cal in enumerate(row):
				thiscal = []
				month = row_months[cal_idx]
				for week in cal:
					thisweek = []
					for date in week:
						if date.month != month:
							thisweek.append((date, False))
						else:
							thisweek.append((date, True))
					thiscal.append(thisweek)
				thisrow.append(thiscal)
			
			height = max(len(cal) for cal in thisrow)
			for j in range(height):
				weeks = []
				for cal in thisrow:
					if j >= len(cal):
						weeks.append('')
					else:
						weeks.append(self.formatweek(cal[j], width))
				result.append(formatstring(weeks, colwidth, spacing).rstrip())
				result.append('\n' * pad)
		return ''.join(result)
	# end formatyear
	
	def pryear(self, year, width=0, pad=0, spacing=6, months=3):
		"""
		Print formatted calendar for 12 months for the specified year.
		"""
		print self.formatyear(year, width, pad, spacing, months)
	# end prmonth

class LocaleTaggedTextCalendar(TaggedTextCalendar):
    """
    This class can be passed a locale name in the constructor and will return
    a TaggedTextCalendar with month and weekday names in the specified locale. 
    If this locale includes an encoding all strings containing month and 
    weekday names will be returned as unicode.
    
    Note that proper print layout of calendars is inherently limited to fixed
    width fonts and not all fonts will be fixed in all locales.  Example 
    locales to try include: 'fr_FR.UTF-8', 'eu_ES.UTF-8', and 'en_US.US_ASCII'
    """

    def __init__(self, firstweekday=0, tag_today=TAG_RED, locale=None):
        TaggedTextCalendar.__init__(self, firstweekday=firstweekday, \
        	tag_today=tag_today)
        if locale is None:
            locale = _locale.getdefaultlocale()
        self.locale = locale
    # end __init__

    def formatweekday(self, day, width):
    	"""
    	Formats the weekday name as per the given locale.
    	"""
        with locale_context(self.locale) as encoding:
            if width >= 9:
                names = day_name
            else:
                names = day_abbr
            name = names[day]
            if encoding is not None:
                name = name.decode(encoding)
            return name[:width].center(width)
    # end formatweekday

    def formatmonthname(self, year, themonth, width, withyear=True):
    	"""
    	Formats the month name as per the given locale.
    	"""
        with locale_context(self.locale) as encoding:
            s = month_name[themonth]
            if encoding is not None:
                s = s.decode(encoding)
            if withyear:
                s = "%s %r" % (s, year)
            return s.center(width)
    # end formatmonthname

class locale_context:
	"""
	Context for setting up a locale for use in a with statement.
	"""
	def __init__(self, locale):
		self.locale = locale
	# end __init__
	
	def __enter__(self):
		self.oldlocale = _locale.getlocale(_locale.LC_TIME)
		_locale.setlocale(_locale.LC_TIME, self.locale)
	# end __enter__
	
	def __exit__(self, *args):
		_locale.setlocale(_locale.LC_TIME, self.oldlocale)
	# end __exit__
	
def main():
	import sys
	import optparse
	
	parser = optparse.OptionParser()
	usage = 'usage: %prog [options] [year [month]]'
	parser = optparse.OptionParser(usage=usage)

	parser.set_defaults(highlight=TAG_RED, firstweekday=SUNDAY)
    
	parser.add_option('-y', '--year', dest='year', type='int', \
		default=datetime.date.today().year, \
		help='set year [default: %default]')
    
	parser.add_option('-m', '--month', dest='month', type='int', \
		default=datetime.date.today().month, \
		help='set month [default: %default]')
        
	parser.add_option('--width', dest='width', type='int', default=1, \
		help='horizontal padding around dates [default: %default]')
        
	parser.add_option('--pad', dest='pad', type='int', default=1,
        help='vertical padding around weeks [default: %default]')
	
	parser.add_option('--full_year', action='store_true', 
    	dest='full_year', help='display calendar for the full year')
        
	parser.add_option('--spacing', dest='spacing', type='int', default=6,
        help='horizontal padding between months [default: %default] ' \
        '(with --full_year)')
        
	parser.add_option('--months', dest='months', type='int', default=3,
        help='months per row [default: %default] (with --full_year)')
        
	parser.add_option('-l', '--locale', dest='locale', default=None,
        help='locale to be used from month and weekday names')
        
	parser.add_option('-e', '--encoding', dest='encoding', default=None,
        help='encoding to use for output')
        
	parser.add_option('-t', '--tag_today', type='str', dest='tag_today', \
		default=TAG_RED, help='custom tag string ' \
		'in lieu of a direct color option [default: \"%s\"]' % \
		'\\033[0;31m%s\\033[0m')

	parser.add_option('--black', action='store_const', const=TAG_BLACK, 
    	dest='tag_today', \
    	help='tag current date as %s text.' % TAG_BLACK % 'black')
    	
	parser.add_option('--darkgray', action='store_const', const=TAG_DARKGRAY, 
    	dest='tag_today', \
    	help='tag current date as %s text.' % TAG_DARKGRAY % 'darkgray')
    	
	parser.add_option('--lightgray', action='store_const', const=TAG_LIGHTGRAY, 
    	dest='tag_today', \
    	help='tag current date as %s text.' % TAG_LIGHTGRAY % 'lightgray')
    	
	parser.add_option('--white', action='store_const', const=TAG_WHITE, 
    	dest='tag_today', \
    	help='tag current date as %s text.' % TAG_WHITE % 'white')
    	
	parser.add_option('--red', action='store_const', const=TAG_RED, 
    	dest='tag_today', \
    	help='tag current date as %s text.' % TAG_RED % 'red')
    	
	parser.add_option('--orange', action='store_const', const=TAG_ORANGE, 
    	dest='tag_today', \
    	help='tag current date as %s text.' % TAG_ORANGE % 'orange')
    	
	parser.add_option('--darkgreen', action='store_const', const=TAG_DARKGREEN, 
    	dest='tag_today', \
    	help='tag current date as %s text.' % TAG_DARKGREEN % 'darkgreen')
    	
	parser.add_option('--lightgreen', action='store_const', const=TAG_LIGHTGREEN, 
    	dest='tag_today', \
    	help='tag current date as %s text.' % TAG_LIGHTGREEN % 'lightgreen')
    	
	parser.add_option('--darkyellow', action='store_const', const=TAG_DARKYELLOW, 
    	dest='tag_today', \
    	help='tag current date as %s text.' % TAG_DARKYELLOW % 'darkyellow')
    	
	parser.add_option('--lightyellow', action='store_const', const=TAG_LIGHTYELLOW, 
    	dest='tag_today', \
    	help='tag current date as %s text.' % TAG_LIGHTYELLOW % 'lightyellow')
    	
	parser.add_option('--darkblue', action='store_const', const=TAG_DARKBLUE, 
    	dest='tag_today', \
    	help='tag current date as %s text.' % TAG_DARKBLUE % 'darkblue')
    	
	parser.add_option('--lightblue', action='store_const', const=TAG_LIGHTBLUE, 
    	dest='tag_today', \
    	help='tag current date as %s text.' % TAG_LIGHTBLUE % 'lightblue')
    	
	parser.add_option('--darkpurple', action='store_const', const=TAG_DARKPURPLE, 
    	dest='tag_today', \
    	help='tag current date as %s text.' % TAG_DARKPURPLE % 'darkpurple')
    	
	parser.add_option('--lightpurple', action='store_const', const=TAG_LIGHTPURPLE, 
    	dest='tag_today', \
    	help='tag current date as %s text.' % TAG_LIGHTPURPLE % 'lightpurple')
    	
	parser.add_option('--darkteal', action='store_const', const=TAG_DARKTEAL, 
    	dest='tag_today', \
    	help='tag current date as %s text.' % TAG_DARKTEAL % 'darkteal')
    	
	parser.add_option('--lightteal', action='store_const', const=TAG_LIGHTTEAL, 
    	dest='tag_today', \
    	help='tag current date as %s text.' % TAG_LIGHTTEAL % 'lightteal')
    	
	parser.add_option('--no_tag', action='store_const', const=TAG_NONE, 
    	dest='tag_today', help='remove and any all tag from current date')
    	
	parser.add_option('--monday_start', action='store_const', const=MONDAY, 
    	dest='firstweekday', help='set the start date for the week to Monday')
    
	(options, args) = parser.parse_args()
    
	if options.locale and not options.encoding:
		parser.error('if --locale is specified, --encoding is required')
		sys.exit(1)
		
	if options.locale:
		locale = '%s.%s' % (options.locale, options.encoding)
		cal = LocaleTaggedTextCalendar(firstweekday=options.firstweekday, \
			tag_today=options.tag_today, locale=locale)
	else:
		cal = TaggedTextCalendar(firstweekday=options.firstweekday, \
			tag_today=options.tag_today)
	
	if options.full_year:
		result = cal.formatyear(year=options.year, width=options.width, \
			pad=options.pad, spacing=options.spacing, months=options.months)
	else:
		result = cal.formatmonth(year=options.year, month=options.month, \
			width=options.width, pad=options.pad)
	
	if options.locale:
		result = result.encode(options.encoding)
		
	print result
# end main

if __name__ == '__main__':
	main()
