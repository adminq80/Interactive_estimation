import json
from decimal import Decimal
import datetime


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        if isinstance(o, datetime.timedelta):
            return o.seconds
        return super(DecimalEncoder, self).default(o)
