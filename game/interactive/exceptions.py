import json


class ClientError(Exception):

    def __int__(self, err):
        super.__init__(err)
        self.err = err

    def send_to(self, channel):

        channel.send({
            "text": json.dumps({
                'error', self.err,
            }),

        })
