from duplicateDetector import ROOT_PATH
import logging
import flask


def deploy_graph(ip, port):
		app = flask.Flask(__name__, static_folder=ROOT_PATH + "force")
		app.logger.disabled = True
		log = logging.getLogger('werkzeug')
		log.disabled = True

		@app.after_request
		def add_header(r):
			"""
			Add headers to both force latest IE rendering engine or Chrome Frame,
			and also to cache the rendered page for 10 minutes.
			"""
			r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
			r.headers["Pragma"] = "no-cache"
			r.headers["Expires"] = "0"
			r.headers['Cache-Control'] = 'public, max-age=0'
			return r

		@app.route('/')
		def static_proxy():
			# return "hello"
			return app.send_static_file('force.html')

		app.run(ip, port=port)
