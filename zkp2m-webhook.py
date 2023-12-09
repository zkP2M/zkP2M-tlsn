import logging
import json
import re
import os
import os.path
import subprocess
import tornado.escape
import tornado.ioloop
import tornado.process
import tornado.options
import tornado.websocket
import tornado.concurrent
import tornado.process
import tornado.gen
from tornado.queues import Queue
from tornado.options import define, options
from dotenv import load_dotenv
import utils.contract_utils

define("port", default=3030, help="run on the given port", type=int)
q = Queue()

load_dotenv()
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/ws", SocketHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
        )
        super(Application, self).__init__(handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        logging.info(json.loads(self.request.body))
        user_data = json.loads(self.request.body)
        os.environ["PAYMENT_ID"] = user_data["razorpay_payment_id"]
        self.set_status(200)
        self.finish()
        futures = self.prove()
        try:
            results = yield futures 
            res = results.find("success")
            print("finished ", results)
            verifyfut = self.verify()
            valid = yield verifyfut
            match_api_json = re.search('{\"id".*}}', valid)
            if match_api_json:            
                api_json = match_api_json.group(0)
                print("matched: ", api_json)
                api_data = json.loads(api_json)
                print("approving usdc withdrawal")
                #tmp values until sourabh and sachin get in gear
                #user_data = {'intent_hash': 'intentHash'}
                #api_data =  {'amount': 100,  'created_at': 1702052754, 'email': 'success@razorpay'}
                print("using %s as the intent hash",api_data["notes"]["id"])
                utils.contract_utils.call_onramp(api_data["notes"]["id"], api_data["created_at"], api_data["amount"], api_data["email"])
        except subprocess.CalledProcessError as e:
            logging.info("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    @tornado.gen.coroutine
    def prove(self):
        bstring = subprocess.check_output(
        "whoami; exit 0",
        stderr=subprocess.STDOUT,
        shell=True)
        username=str(bstring,  encoding='utf-8').strip()
        workdir = '/home/' + username + '/zkP2M-tlsn'
        bashCommand = ['cargo','run','--release','--example','razorpay_payment_prover']
        logging.info("creating for: %s", workdir)
        proc = tornado.process.Subprocess(bashCommand, stdout=tornado.process.subprocess.PIPE, stderr=tornado.process.subprocess.STDOUT, universal_newlines=True, cwd=workdir)

        yield proc.wait_for_exit() # `wait_for_exit` returns a future 
                               # which you can yield. Basically, it means
                               # you can wait for the process to complete
                               # without blocking the server

        return proc.stdout.read() # return the result of the process

    @tornado.gen.coroutine
    def verify(self):
        bstring = subprocess.check_output(
        "whoami; exit 0",
        stderr=subprocess.STDOUT,
        shell=True)
        username=str(bstring,  encoding='utf-8').strip()
        workdir = '/home/' + username + '/zkP2M-tlsn'
        bashCommand = ['cargo','run','--release','--example','razorpay_payment_verifier']
        proc = tornado.process.Subprocess(bashCommand, stdout=tornado.process.subprocess.PIPE, stderr=tornado.process.subprocess.STDOUT, universal_newlines=True, cwd=workdir)

        yield proc.wait_for_exit() # `wait_for_exit` returns a future
                               # which you can yield. Basically, it means
                               # you can wait for the process to complete
                               # without blocking the server

        return proc.stdout.read() # return the result of the process

    @tornado.gen.coroutine
    def on_connection_close(self):
        self.msg_future.set_result(None)

class SocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()

    def check_origin(self, origin):
        return True

    def open(self):
        SocketHandler.waiters.add(self)
        logging.info(
            'New WebSocket Connection: %d total',
            len(SocketHandler.waiters)
        )

    def select_subprotocol(self, subprotocol):
        if len(subprotocol):
            return subprotocol[0]
        return super().select_subprotocol(subprotocol)

    async def on_message(self, message):
        logging.info('new message: %s', message)
        await q.put(message)


    def on_close(self):
        SocketHandler.waiters.remove(self)
        logging.info(
            'Disconnected WebSocket (%d total)',
            len(SocketHandler.waiters)
        )

    @classmethod
    def broadcast(cls, data):
        for waiter in cls.waiters:
            try:
                waiter.write_message(data, binary=True)
            except tornado.websocket.WebSocketClosedError:
                logging.error("Error sending message", exc_info=True)


def relay():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()




if __name__ == "__main__":

    relay()

