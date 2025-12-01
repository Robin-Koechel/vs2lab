import constRPC
import threading
import time

from context import lab_channel


class DBList:
    def __init__(self, basic_list):
        self.value = list(basic_list)

    def append(self, data):
        self.value = self.value + [data]
        return self


class Client:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.client = self.chan.join('client')
        self.server = None

    def run(self):
        self.chan.bind(self.client)
        self.server = self.chan.subgroup('server')

    def stop(self):
        self.chan.leave('client')

    def append(self, data, db_list):
        assert isinstance(db_list, DBList)
        msglst = (constRPC.APPEND, data, db_list)  # message payload
        self.chan.send_to(self.server, msglst)  # send msg to server

        while True:
            msgrcv = self.chan.receive_from(self.server)  # wait for ACK
            msg_type = msgrcv[1][0]
            msg_payload = msgrcv[1][1]

            if msg_type == constRPC.ACK:
                print('ACK received from server: {}'.format(msg_payload)) # ACK received
                continue
            elif msg_type == constRPC.APPEND:
                return msg_payload # actual response


    def runner(self, function: callable, cb: callable, **kwargs):
        def run_and_callback():
            result = function(**kwargs)
            cb(result)
        thread = threading.Thread(target=run_and_callback)
        thread.start()
        return thread

class Server:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.server = self.chan.join('server')
        self.timeout = 3

    @staticmethod
    def append(data, db_list):
        assert isinstance(db_list, DBList)  # - Make sure we have a list
        return db_list.append(data)

    def run(self):
        self.chan.bind(self.server)
        while True:
            msgreq = self.chan.receive_from_any(self.timeout)  # wait for any request
            if msgreq is not None:
                client = msgreq[0]  # see who is the caller
                msgrpc = msgreq[1]  # fetch call & parameters
                if constRPC.APPEND == msgrpc[0]:  # check what is being requested
                    self.chan.send_to({client}, (constRPC.ACK, 'received ACK request'))  # send ACK                    
                    result = self.append(msgrpc[1], msgrpc[2])  # do local call
                    time.sleep(10)  # simulate processing time
                    self.chan.send_to({client}, (constRPC.APPEND, result))  # return response
                else:
                    pass  # unsupported request, simply ignore
