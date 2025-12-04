import zmq

def get_reducer(word: str) -> int:
  return hash(word) % 2

def execute_mapper():
  context = zmq.Context()
  # create PULL socket
  # connect to splitter
  receiver = context.socket(zmq.PULL)
  receiver.connect("tcp://localhost:5555")
  print("Mapper connected to splitter on port 5555")

  # create PUSH sockets for first reducer
  reducer1 = context.socket(zmq.PUSH)
  reducer1.connect("tcp://localhost:5556")
  print("Mapper connected to reducer 1 on port 5556")

  # create PUSH sockets for second reducer
  reducer2 = context.socket(zmq.PUSH)
  reducer2.connect("tcp://localhost:5557")
  print("Mapper connected to reducer 2 on port 5557")

  while True:
    sentence = receiver.recv_string()
    # split sentence into words
    words = sentence.split()

    # send words to reducers
    for word in words:
      word = word.lower()
      reducer = get_reducer(word)
      if reducer == 0:
        reducer1.send_string(word)
        print(f"Mapper sent word '{word}' to reducer 1")
      else:
        reducer2.send_string(word)
        print(f"Mapper sent word '{word}' to reducer 2")
      
def main():
  execute_mapper()

if __name__ == "__main__":
  main()
