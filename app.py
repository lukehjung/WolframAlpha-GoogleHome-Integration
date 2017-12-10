#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "calculator":
        return {}
    baseurl = "http://api.wolframalpha.com/v2/query?appid=7EJ2E7-ULT25HHJUR&input="
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urlencode({'q': yql_query}) + "&output=json"
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res



def makeYqlQuery(req):
    result = req.get("result")
    return result.get("resolvedQuery")

def makeWebhookResult(data):
    query = data.get('queryresult')
    if query is None:
    	return {}
    pods = query.get('pods')
    if pods is None:
    	return {}

    podin = pods[0]
    subpodsin = podin.get('subpods')
    if subpodsin is None:
    	return {}
    subpodin = subpodsin[0]

    podresult = pods[1]
    subpods = podresult.get('subpods')
    if subpods is None:
    	return {}
    subpodresult = subpods[0]

    start = subpodin.get('plaintext').replace("q = ","")
    
    if start.startswith(' integral') is True:
    	return {
        "speech": subpodin.get('plaintext').replace("q = ",""),
        "displayText": subpodin.get('plaintext').replace("q = ",""),
        # "data": data,
        # "contextOut": [],
        "source": "Luke Wolfram Buddy"
    }

    speech = subpodin.get('plaintext').replace("q = ","") + " = " 
    + subpodresult.get('plaintext').replace("q = ","")
    # udata = subpodresult.get('plaintext').decode('utf-8')
    # speech = udata.encode("ascii","ignore")

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "Luke Wolfram Buddy"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
