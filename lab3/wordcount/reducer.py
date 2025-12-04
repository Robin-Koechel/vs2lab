import logging
import zmq
import argparse
from typing import Dict

#   python lab3/wordcount/reducer.py --bind tcp://127.0.0.1:6001
#   python lab3/wordcount/reducer.py --bind tcp://127.0.0.1:6002
class Reducer:
	"""Reducer receives words on a PULL socket and maintains word counts.

	Each time a word's count changes the reducer prints a line:
		UPDATED <word> <new_count>
	"""

	def __init__(self, bind_endpoint: str):
		self.bind_endpoint = bind_endpoint
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.PULL)
		# bind to the endpoint so mappers can connect
		self.socket.bind(self.bind_endpoint)
		logging.info("Reducer bound PULL socket to %s", self.bind_endpoint)
		self.counts: Dict[str, int] = {}

	def handle_word(self, word: str) -> None:
		old = self.counts.get(word, 0)
		new = old + 1
		self.counts[word] = new
		# Print change to terminal as requested
		print(f"UPDATED {word} {new}")
		logging.debug("Reducer updated word '%s' to %d", word, new)

	def run(self) -> None:
		try:
			while True:
				# receive a word as a string
				word = self.socket.recv_string()
				logging.debug("Reducer received word: %s", word)
				self.handle_word(word)
		except KeyboardInterrupt:
			return

	def close(self) -> None:
		self.socket.close()
		self.context.term()
		logging.info("Reducer sockets closed and context terminated")


def parse_args():
	p = argparse.ArgumentParser()
	p.add_argument('--bind', '-b', required=True, help='bind endpoint, e.g. tcp://127.0.0.1:5001')
	return p.parse_args()


if __name__ == '__main__':
	args = parse_args()
	r = Reducer(args.bind)
	try:
		r.run()
	finally:
		r.close()

