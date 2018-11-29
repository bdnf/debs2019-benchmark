from flask import Flask
from flask_restful import Api

from resources import AllScenes, Scene, Prediction
from measurements import Measurements

app = Flask(__name__)
api = Api(app)

api.add_resource(Measurements, '/measurements/')
api.add_resource(AllScenes, '/scenes/')
api.add_resource(Scene, '/scene/<string:number>')
api.add_resource(Prediction, '/prediction/scene/<string:number>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
