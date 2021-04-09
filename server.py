from twisted.internet import protocol, reactor
import names
import argparse
import logging
from datetime import datetime

from models import Message


TRANSPORTS = set()
NAMES = set()


# 아래 ChatProtocol 을 async 로 만들면,
# 현재 서버에서 처리하고 있는 동기적 처리를 비동기로 바꿀 수 있고,
# dataReceived 및 connectionMade 를 동시적으로 처리할 수 있을듯
class ChatProtocol(protocol.Protocol):
    def connectionMade(self):
        self.log = None
        self.name = names.get_first_name()
        TRANSPORTS.add(self.transport)

        if self.name in NAMES:
            self.log = f"Connection aborted: name {self.name!r} is not unique"
            self.transport.abortConnection()
        else:
            msg = Message(user='initializer', value=self.name).string().encode()
            self.transport.write(msg)
            NAMES.add(self.name)

            print(f"{self.transport} (connection made for user {self.name!r})")

    def connectionLost(self, reason):
        print(f"{reason.getErrorMessage()} ({self.log})")
        print(f"{self.transport} (connection lost for user {self.name!r})")

        TRANSPORTS.remove(self.transport)
        self.transport.loseConnection()

    def dataReceived(self, message):
        print(f"[{datetime.now()}] {message.decode()}")

        # 메시지를 send한 transport를 제외한 나머지 transport들에게 들어온 메시지를 전달함
        for t in TRANSPORTS:
            if self.transport is not t:
                t.write(message)


# 지정된 port로 커넥션하면 아래 팩토리가 각 클라이언트에 프로토콜을 하나씩 만들어 제공
class ChatFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return ChatProtocol()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', action='store', type=int, required=True)
    args = parser.parse_args()
    return args


def main(args):
    print('Server running...')
    reactor.listenTCP(args.port, ChatFactory())
    reactor.run()


if __name__ == '__main__':
    args = parse_args()
    main(args)
