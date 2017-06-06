#!python.exe
import site
import json
import requests
requests.packages.urllib3.disable_warnings()
from flask import Flask

# Declare web application instace as 'app'
app = Flask(__name__)

# Cath all messages
@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'], defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return "This CMX resoruce has been moved to https://cmxlocationsandbox.cisco.com. Find more information here: https://communities.cisco.com/docs/DOC-72621"

def authorize():
    sess = requests.Session()
    ticket = ''
    url = 'https://10.10.10.190/api/v1/ticket'
    sess.headers = {
        'Content-Type': 'application/json',
	 }
    params = {
        'username' : 'devnetuser',
        'password': 'Cisco123!',
    }
    try:
        resp = sess.post(url, data=json.dumps(params), verify=False)
        js = json.loads(resp.text)
    except Exception, e:
        err = e
    if resp.status_code == 401:
        err = 'Not authorized, password maybe changed'
    elif resp.status_code == 200:
        err = 'OK'
        ticket = js["response"]["serviceTicket"]
    elif resp.status_code == 500:
        err = 'Interal server error'
    else:
        err = 'Error:'+str(resp.status_code)
    return (err,ticket)

@app.route('/healthcheck')
def HealthCheck():
    err,ticket = authorize()
    return err

@app.route('/topology')
def TopologyCheck():
    #authozie to get token
    err,ticket = authorize()
    if err!='OK':
        return err
    #check topo
    sess = requests.Session()
    url = 'https://10.10.10.190/api/v1/network-device/'
    sess.headers = {
        'X-Auth-Token' : ticket
    }
    try:
        resp = sess.get(url, verify=False)
        js = json.loads(resp.text)
    except Exception, e:
	 js = json.loads(resp.text)
    except Exception, e:
        err = e
    #print resp.text
    if resp.status_code == 401:
        err = 'Not authorized, password maybe changed'
    elif resp.status_code == 200:
        err = 'OK'
    elif resp.status_code == 400 or resp.status_code == 503:
        err = 'topology is broken, to be fixed!!!'
    else:
        err = 'Status:'+str(resp.status_code)
    return err


# Runs the web application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)
