from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
import pandas as pd

app = Flask(__name__)
api = Api(app)

predictions = []
armIn = pd.read_csv("./armchair/in.csv", header=None, names=['time', 'index', 'X', 'Y', 'Z'])


class AllScenes(Resource):

    def get(self):
        return {'scene': predictions}


class Scene(Resource):


    def get(self, number):
        result = []
        for ix, row in armIn[armIn.time < int(number)].head(10).iterrows():
            result.append(row.values.tolist())
        return {'scene': result}


class Prediction(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('object_id',
                        type=int,
                        required=True,
                        help='This field better not be blank!'
                        )

    def get(self, number):
        res = next((x for x in predictions if x['scene'] == number), None)
        return {'scene': res}, 200 if res else 404

    def post(self, number):
        if next((x for x in predictions if x['scene'] == number), None):
            return {'message': '''A scene {} already exist.
                    If you want to update your value try to use PUT request'''
                    .format(number)}, 400
        data = request.get_json()
        data = Prediction.parser.parse_args()
        result = {'scene': number, 'object_id': data['object_id']}
        predictions.append(result)
        return result, 202

    def put(self, number):
        data = Prediction.parser.parse_args() # request.get_json()
        res = next(filter(lambda x: x['scene'] == number, predictions), None)
        if res is None:
            result = {'scene': number, 'object_id': data['object_id']}
            predictions.append(result)
        else:
            predictions.update(res)
        return res


api.add_resource(AllScenes, '/scenes/')
api.add_resource(Scene, '/scene/<string:number>')
api.add_resource(Prediction, '/prediction/scene/<string:number>')

app.run(port=5000, debug=True)

#df = pd.read_csv("./armchair/in.csv")
#df.describe
