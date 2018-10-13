'''
The CLI for Squeakernet FLP. 
'''

import sys
from squeakernet import feeder, scale, db, speech, web
from squeakernet.logcategory import LogCategory

HELP = '''Squeakernet FLP: The Feline Lifestyle Platform

See squeakernet.ini for settings.

Usage:
  "python sqn.py <command> [<argument1> [<argument2]]"

Commands:

  help: Show this message.
  feed: *Dispense kibbles.
  startweb: *Run the squeakernet web server.
  logweight: *Read weight from the scale and write it to the database.
  logs <?category>: Print logs from the database. See LogCategory.py.
  lastfeed: Show time and amount of last feeding.
  writelog <message>: Write an arbitrary log message.
  say <phrase>: Speak a phrase for the kitties to enjoy.

Any comands* that access GPIO must be run 
as superuser or the universe will explode.
'''

def main():

    if len(sys.argv) < 2:
        print HELP
        return

    command = sys.argv[1]
    
    if command == 'help':
        print HELP
    if command == 'feed':
        feeder.feed_the_cats()
    elif command == 'startweb':
        web.start()
    elif command == "logweight":
        scale.log_weight()
    elif command == 'logs':
        if len(sys.argv) > 2:
            print_logs(sys.argv[2].upper())
        else:
            print_logs()
    elif command == 'lastfeed':
        log = db.get_last_log(LogCategory.FEED)
        print 'Dispensed %.2fg of kibbles at %s.' % (log.reading, log.date)
    elif command == 'writelog':
        if sys.argv > 2:
            db.write_log(LogCategory.SYSTEM, sys.argv[2])
            print 'Log written to database.'
        else:
            print 'writelog: No log was provided to write.'
    elif command == 'say':
        if sys.argv > 2:
            speech.say(sys.argv[2])
        else:
            print 'say: no phrase was provided to speak.'

    else:
        print 'Unknown command.'

def print_logs(category = None):
    if category and not hasattr(LogCategory, category):
        raise SystemError('There is no log category called "%s".' % category)
    
    logs = db.get_logs(category and LogCategory[category] or None)
    for log in logs:
        print '\t'.join([str(x) for x in log])

if __name__ == "__main__":
    main()