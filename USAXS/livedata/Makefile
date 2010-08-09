
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

DATE_STRING   = `date '+%Y%m%d-%H%M%S'`

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

all :: clean
