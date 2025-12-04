import sys
import zmq

def execute_reducer():
  id = sys.argv[1]  # get reducer ID from command line argument
  if id == "1":
    port = "5556"
  elif id == "2":
    port = "5557"
  else:
    print("Invalid reducer ID. Use '1' or '2'.")

  # create PULL socket and bind to appropriate port
  context = zmq.Context()
  receiver = context.socket(zmq.PULL)
  receiver.bind(f"tcp://*:{port}")
  print(f"Reducer {id} listening on port {port}")

  word_count: dict[str, int] = {}
  while True:
    word = receiver.recv_string()
    print(f"Reducer {id} received word: {word}")

    # count occurrences of the word
    if word in word_count:
      word_count[word] += 1
    else:
      word_count[word] = 1

    print(f"Reducer {id} current count for '{word}': {word_count[word]}")

def main():
  execute_reducer()

if __name__ == "__main__":
  main()
  