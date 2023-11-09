"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)
Ethan Robb
"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config
import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()

###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')

@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404

###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############

@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)

    # Brevet distance & start date
    start_date = request.args.get('start_date', type = str)
    brev_distance = request.args.get('brev_dist', 200, type=int) 
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))
    begin_arrow = arrow.get(start_date) # Arrow variable from the beginning time
    
    try:
        open_time = acp_times.open_time(km, brev_distance, begin_arrow).format('YYYY-MM-DDTHH:mm')
        close_time = acp_times.close_time(km, brev_distance, begin_arrow).format('YYYY-MM-DDTHH:mm')
        rslt = {"open": open_time, "close": close_time, "ecode": 0}
        return flask.jsonify(result=rslt)
    
    except OverflowError:
        rslt = {"open": "mm/dd/yyyy --:-- --", "close": "mm/dd/yyyy --:-- --", "ecode": 1}
        return flask.jsonify(result=rslt)
    except ArithmeticError:
        rslt = {"open": "mm/dd/yyyy --:-- --", "close": "mm/dd/yyyy --:-- --", "ecode": 2}
        return flask.jsonify(result=rslt)

#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
