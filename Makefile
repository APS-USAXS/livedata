
DATE_STRING   = `date '+%Y%m%d-%H%M%S'`

TARLIST  = Makefile
TARLIST += *.csh
TARLIST += *.tcl
TARLIST += *.txt

archive backup tar ::
	tar czf archive/${DATE_STRING}.tar.gz $(TARLIST)

burt ::
	burtrb -sdds -f burt.req -l burt.log -o burt.sdds

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
