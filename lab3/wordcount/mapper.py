import logging
import zmq
import string
from typing import List


#2 python lab3/wordcount/mapper.py --splitter tcp://127.0.0.1:7000 --reducers tcp://127.0.0.1:6001 tcp://127.0.0.1:6002
#  python lab3/wordcount/mapper.py --splitter tcp://127.0.0.1:7000 --reducers tcp://127.0.0.1:6001 tcp://127.0.0.1:6002
#  python lab3/wordcount/mapper.py --splitter tcp://127.0.0.1:7000 --reducers tcp://127.0.0.1:6001 tcp://127.0.0.1:6002

class Mapper:
    def __init__(self, splitter: str, reducers: List[str]):
        if not reducers:
            raise ValueError("reducers list must contain at least one endpoint")

        self.context = zmq.Context()
        # PULL socket to receive lines from the splitter
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.connect(splitter)
        logging.info("Mapper connected to splitter %s", splitter)

        # create one PUSH socket per reducer so we can target reducers directly
        self.reducers = list(reducers)
        self.push_sockets = []
        for endpoint in self.reducers:
            s = self.context.socket(zmq.PUSH)
            s.connect(endpoint)
            self.push_sockets.append(s)
            logging.info("Mapper connected PUSH to reducer %s", endpoint)

        # build char -> reducer index mapping dynamically
        self._build_char_map()

    def _build_char_map(self) -> None:
        """Build a mapping from a-z characters to reducer indices.

        The 26 letters are divided into len(reducers) contiguous buckets.
        """
        letters = string.ascii_lowercase
        n = len(self.reducers)
        self.char_to_reducer = {}
        for i, ch in enumerate(letters):
            # integer division to map 0..25 into 0..n-1
            idx = (i * n) // 26
            if idx >= n:
                idx = n - 1
            self.char_to_reducer[ch] = idx

    def _reducer_index_for_word(self, word: str) -> int:
        """Return reducer index for a given word based on its first character."""
        if not word:
            return 0
        first = word[0].lower()
        if first in self.char_to_reducer:
            return self.char_to_reducer[first]
        # fallback: distribute non-alpha characters by hash
        return abs(hash(first)) % len(self.push_sockets)

    def map_line(self, line: str) -> None:
        """Split a line into words and send each word to its reducer."""
        # simple whitespace split; callers may pre-process punctuation if needed
        words = line.split()
        logging.debug("Mapper received line with %d words", len(words))
        for w in words:
            idx = self._reducer_index_for_word(w)
            # include the word as a string payload; reducers can parse as needed
            self.push_sockets[idx].send_string(w)
            logging.debug("Mapper sent word '%s' to reducer index %d", w, idx)

    def run(self) -> None:
        """Main loop: receive lines from splitter and map them to reducers."""
        logging.info("Mapper running main loop")
        try:
            while True:
                # use recv_string so we get a decoded python str
                line = self.receiver.recv_string()
                self.map_line(line)
        except KeyboardInterrupt:
            # graceful shutdown
            logging.info("Mapper interrupted, shutting down")
            return

    def close(self) -> None:
        for s in self.push_sockets:
            s.close()
        self.receiver.close()
        self.context.term()
        logging.info("Mapper sockets closed and context terminated")


def parse_args():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--splitter', '-s', required=True, help='splitter endpoint, e.g. tcp://127.0.0.1:7000')
    p.add_argument('--reducers', '-r', required=True, nargs='+', help='one or more reducer endpoints')
    return p.parse_args()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    args = parse_args()
    m = Mapper(args.splitter, args.reducers)
    try:
        m.run()
    finally:
        m.close()