import random
import sys
import time
import os
import zmq

# vocabulary for sentence generation
vocab = [
  "never", "gonna", "give", "you", "up", "let", "down", "run", "around",
  "desert", "make", "cry", "say", "goodbye", "tell", "lie", "hurt", "annie", "are", "you", "ok",
  "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit", "sed", "do", "eiusmod",
  "tempor", "incididunt", "ut", "labore", "et", "dolore", "magna", "aliqua", "ut", "enim", "ad", "minim",
  "veniam", "quis", "nostrud", "exercitation", "ullamco", "laboris", "nisi", "ut", "aliquip", "ex", "ea",
  "commodo", "consequat", "duis", "aute", "irure", "dolor", "in", "reprehenderit", "in", "voluptate", "velit",
  "esse", "cillum", "dolore", "eu", "fugiat", "nulla", "pariatur", "excepteur", "sint", "occaecat", "cupidatat",
  "non", "proident", "sunt", "in", "culpa", "qui", "officia", "deserunt", "mollit", "anim", "id", "est", "laborum"
  "aurum", "bella", "casa", "domus", "equus", "ferrum", "gladius", "hortus", "insula", "jus", "luna"
]

def generate_sentences(vocab : list[str]) -> list[str]:
  # list to hold generated sentences
  sentences = []

  # generate 100 sentences
  for i in range(100):
    length = random.randint(5, 15)  # random sentence length between 5 and 15 words
    words = random.choices(vocab, k=length)  # randomly select words from vocab
    sentence = " ".join(words)  # join words to form a sentence
    sentences.append(sentence)  # add sentence to list
  
  return sentences

def send_from_vocab(sender: zmq.Socket, sentences: list[str]):
  for sentence in sentences:
    # send sentence as string
    sender.send_string(sentence)

    print(f"Sent sentence: {sentence}")
    
    # slight delay to be observe what is happening
    time.sleep(0.1)

def send_from_file(sender: zmq.Socket):
  filename = sys.argv[1]
  with open(filename, 'r') as file:
    for line in file:
      # remove leading/trailing whitespace and newline characters
      sentence = line.strip()
      if sentence:  # ensure the line is not empty
        sender.send_string(sentence)
        print(f"Sent sentence from file: {sentence}")
        time.sleep(0.1)  # slight delay to observe what is happening

def textfile_exists():
  if len(sys.argv) > 1:
    filename = sys.argv[1]
    if os.path.exists(filename):
      print(f"File {filename} exists.")
      print(f"Reading from file: {filename}")
      return True
    else:
      print(f"File {filename} does not exist.")
      print("Exiting...")
      return False

def execute_splitter():
  # create PUSH socket
  # bind to port 5555 like in https://zguide.zeromq.org/docs/chapter1/#Divide-and-Conquer
  context = zmq.Context()
  sender = context.socket(zmq.PUSH)
  sender.bind("tcp://*:5555")

  if textfile_exists():
    send_from_file(sender)
  else:
    # generate sentences from vocab
    sentences = generate_sentences(vocab)
    send_from_vocab(sender, sentences)

def main():
  execute_splitter()

if __name__ == "__main__":
  main()