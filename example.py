#!/usr/bin/env python3

from pirc import Client


q = Client('irc.freenode.net', 6667)


@q.event
def on_message(message):
	print(message.raw)


try:
	q.run()

except KeyboardInterrupt:
	q.stop()
