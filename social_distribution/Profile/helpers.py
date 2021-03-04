import pytz
import dateutil.parser

# Beautify created_at timestamp in github api
def timestamp_beautify(created_at):
	edmonton_timezone = pytz.timezone('America/Edmonton')
	timestamp = dateutil.parser.parse(created_at).astimezone(edmonton_timezone)
	return timestamp.strftime("%c")

