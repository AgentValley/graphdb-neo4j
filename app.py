from flask import Flask, jsonify

from graphdb.connect import connect_to_neo4j_driver
from logger import setup_logger
from routes.upload import upload_bp
from routes.query import query_bp


setup_logger('logs/neo4jdb.logs')

app = Flask(__name__)

driver = connect_to_neo4j_driver()
if driver is None:
    raise IOError('Failed to connet to neo4j.')

@app.route('/', methods=['GET'])
def hello():
    return jsonify('ok'), 200


app.register_blueprint(upload_bp, url_prefix='/upload')
app.register_blueprint(query_bp, url_prefix='/query')


if __name__ == '__main__':
    app.run(port=5020, load_dotenv=True)
