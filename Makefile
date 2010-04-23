
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

DATE_STRING   = `date '+%Y%m%d-%H%M%S'`

TARLIST  = Makefile
TARLIST += *.csh
TARLIST += *.sh
TARLIST += *.py
TARLIST += *.txt
TARLIST += *.xsl

archive backup tar ::
	tar czf archive/${DATE_STRING}.tar.gz $(TARLIST)

clean :: $(TARLIST)
	./manage.csh stop
	/bin/echo "`/bin/date`: restarted usaxs livedata ..." > log.txt
	./manage.csh start

start :: $(TARLIST)
	./manage.csh start

stop :: $(TARLIST)
	./manage.csh stop

restart :: $(TARLIST)
	./manage.csh restart

all :: tar clean
