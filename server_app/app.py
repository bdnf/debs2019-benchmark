from flask import Flask
from flask_restful import Api

from resources import Benchmark, BenchmarkSummary, BenchmarkResults

app = Flask(__name__)
api = Api(app)

api.add_resource(BenchmarkSummary, '/scenes/')
api.add_resource(Benchmark, '/scene/')
api.add_resource(BenchmarkResults, '/compute_result/')
# api.add_resource(Prediction, '/prediction/scene/<string:number>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
