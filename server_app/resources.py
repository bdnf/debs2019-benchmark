from flask import request
from flask_restful import Resource
import sqlite3
import datetime
import pandas as pd
import numpy
import csv
import sys

in_file = "../dataset/in.csv"
out_file = "../dataset/out.csv"
correct = pd.read_csv("../dataset/out.csv", header=None, names=['object_id', 'quantity'])
current_scene = 0
TOTAL_SCENES = 50


class Benchmark(Resource):
    PENALTY_FOR_INCORRECT_OBJECT_PREDICTION = 10
    PENALTY_FOR_INCORRECT_VALUE_PREDICTION = 5

    total_time_score = 0

    def get(self):
        global current_scene
        current_scene +=1
        print("Requested scene %s" % current_scene)
        sys.stdout.flush()

        if current_scene >= TOTAL_SCENES:
            if Benchmark.total_time_score == 0:
                return {'message': 'Last scene reached. No more scenes left. Please, check you detailed results now',
                        'total runtime': 'An error occured when computing total runtime. Please rebuild the Benchmark server'}, 404
            else:
                return {'message': 'Last scene reached. No more scenes left. Please, check you detailed results now',
                        'total runtime': Benchmark.total_time_score}, 404

        self.get_timestamp(current_scene)
        result = []
        # with loading into memory
        # scene = dataset[(dataset.time > int(current_scene) -1) & (dataset.time < int(current_scene))].head(5)
        # result = scene.to_json(orient='records')

        # csv reader way
        # with open("../dataset/in.csv", 'r') as f:
        #     reader = csv.reader(f)
        #     for line in reader:
        #         scene_index = float(line[0])
        #         if scene_index > current_scene-1 and scene_index < current_scene:
        #              data = {
        #                 'timestamp': line[0],
        #                 'laser_id': line[1],
        #                 'X': line[2],
        #                 'Y': line[3],
        #                 'Z': line[4]
        #              }
        #              result.append(data)

        # fastest way with Pandas
        df = pd.read_csv(in_file, sep=',', header = None, names=['time', 'laser_id', 'X', 'Y', 'Z'], skiprows= (current_scene-1)*72000, nrows=72000)
        result = df.head(5).to_json(orient='records')

        return {'scene': result}

    @classmethod
    def get_timestamp(self, number):

        conn = sqlite3.connect('debs.db')
        cursor = conn.cursor()

        query = "INSERT INTO predictions (scene, requested_at) VALUES(?,?)"
        start_time = datetime.datetime.now()
        cursor.execute(query, (number, start_time))
        conn.commit()
        conn.close()

    def post(self):
        global current_scene
        score = 0

        print('Submitted scene %s' % current_scene)
        if self.scene_exists(current_scene):
            return {'message': "Scene {} already exist.".format(current_scene)}, 400
        correct_dict = self.fetch_correct_result()
        your_dict = request.get_json()
        submission_time = datetime.datetime.now()
        print(' Correct prediction', correct_dict)
        your_dict = {str(k):int(v) for k,v in your_dict.items()}
        print(' Your prediction', your_dict)
        sys.stdout.flush()

        if your_dict:
            score = Benchmark.diff_dicts(correct_dict, your_dict)

        # data = Prediction.parser.parse_args()
        # result = {'scene': number, 'object_id': self.check_objects(data['object_id']), 'quantity': self.check_object(data['quantity'])}
        submission_result = {'scene': current_scene, 'accuracy': score}
        try:
            self.insert(submission_result, submission_time)
        except:
            return {'message': 'An error occured while inserting the item'}, 500

        return {'Your score for this scene is ': submission_result['accuracy']}, 201

    @classmethod
    def insert(cls, result, stop_time):
        conn = sqlite3.connect('debs.db')
        cursor = conn.cursor()

        select = "SELECT requested_at FROM predictions WHERE scene=?"
        cursor.execute(select, (result['scene'],))
        start_time = cursor.fetchone()

        unix_start_time = (datetime.datetime.strptime(str(start_time[0]), "%Y-%m-%d %H:%M:%S.%f")).strftime("%s")
        unix_stop_time = stop_time.strftime("%s")
        time_diff = int(unix_stop_time) - int(unix_start_time)
        Benchmark.total_time_score += time_diff
        print('Your prediction time for this scene was %s seconds' % time_diff)

        cursor = conn.cursor()
        query = "UPDATE predictions SET accuracy=?, prediction_speed =?, submitted_at=? WHERE scene=?"

        cursor.execute(query, (result['accuracy'], time_diff, stop_time, result['scene']))
        conn.commit()
        conn.close()

    @classmethod
    def fetch_correct_result(cls):
        correct_object = correct['object_id'].iloc[0].split(',')
        correct_quantity = correct['quantity'].iloc[0]
        if (isinstance(correct_quantity, int)) or (isinstance(correct_quantity, numpy.int64)):
            correct_quantity = [correct_quantity]
        else:
            correct_quantity = correct_quantity.split(',')
        res = dict(zip(correct_object, correct_quantity))
        return res

    @classmethod
    def diff_dicts(cls, a, b):
        # print(a.keys() & b.keys())
        total = 0
        for key in a.keys():
            if key in b.keys():
                total += abs(int(a[key]) - int(b[key]))
            else:
                total += Benchmark.PENALTY_FOR_INCORRECT_OBJECT_PREDICTION

        for key in b.keys():
            if key in a.keys():
                total += abs(int(a[key]) - int(b[key]))
            else:
                total += Benchmark.PENALTY_FOR_INCORRECT_OBJECT_PREDICTION

        i = [k for k in b if k in a if b[k] != a[k]]
        if i:
            for k in i:
                print("""Your prediction is not correct:
                         your predicted [%s] = %s but was expected [%s] = %s""" % (k, b[k], k, a[k]) )
                total += Benchmark.PENALTY_FOR_INCORRECT_VALUE_PREDICTION

        else:
            i = [k for k in b if k in a if a[k] != b[k]]
            if i:
                for k in i:
                    print("""Your prediction is not correct:
                            your predicted [%s] = %s but was expected [%s] = %s""" % (k, b[k], k, a[k]) )
                    total += Benchmark.PENALTY_FOR_INCORRECT_VALUE_PREDICTION

        print("Difference score %s" % total)
        return total

    @classmethod
    def scene_exists(cls, number):
        conn = sqlite3.connect('debs.db')
        cursor = conn.cursor()

        query = "SELECT prediction_speed FROM predictions WHERE scene=?"
        cursor.execute(query, (number,))
        row = cursor.fetchone()
        conn.close()
        try:
            if row[0]:
                return True
        except:
            return True


class BenchmarkSummary(Resource):

    def get(self):
        conn = sqlite3.connect('debs.db')
        cursor = conn.cursor()

        query = "SELECT * FROM predictions"
        result = cursor.execute(query)
        items = []
        for row in result:
            items.append({'scene': row[0],
                          'accuracy': row[1],
                          'prediction_speed': row[2],
                          'requested_at': row[3],
                          'submitted_at': row[4]})
        conn.close()
        return {'Submitted scenes': items,
                'total runtime': Benchmark.total_time_score}


class BenchmarkResults(Resource):
    def get(self):
        conn = sqlite3.connect('debs.db')
        cursor = conn.cursor()

        query = "SELECT SUM(accuracy), SUM(prediction_speed) FROM predictions"
        cursor.execute(query)
        result = cursor.fetchone()

        conn.close()
        return {'total accuracy': result[0],
                'total runtime from db': result[1],
                'total runtime': Benchmark.total_time_score}
