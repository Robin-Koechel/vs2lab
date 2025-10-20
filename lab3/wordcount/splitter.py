import logging
import zmq
import argparse

# 3. python lab3/wordcount/splitter.py --bind tcp://127.0.0.1:7000 --file lab3/wordcount/text.txt

class Splitter:
    def __init__(self, bind_endpoint: str, text_file_path: str):
        self.bind_endpoint = bind_endpoint
        self.text_file_path = text_file_path
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.bind(self.bind_endpoint)
        logging.info("Splitter bound PUSH socket to %s", self.bind_endpoint)

    def send_all(self) -> None:
        with open(self.text_file_path, 'r') as f:
            count = 0
            for line in f:
                line = line.rstrip('\n')
                if line:
                    self.socket.send_string(line)
                    count += 1
                    logging.debug("Splitter sent line: %s", line)
            logging.info("Splitter finished sending %d lines", count)
        # done sending; close socket
        self.socket.close()
        self.context.term()
        logging.info("Splitter sockets closed and context terminated")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--bind', '-b', required=True, help='bind endpoint, e.g. tcp://127.0.0.1:7000')
    p.add_argument('--file', '-f', required=True, help='text file to split into lines')
    return p.parse_args()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    args = parse_args()
    s = Splitter(args.bind, args.file)
    s.send_all()