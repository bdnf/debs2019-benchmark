from flask import request
from flask_restful import Resource
import sqlite3
import datetime
import pandas as pd
import numpy
import csv
import sys
import os.path
import subprocess
import metrics

in_file = "../dataset/in.csv"
out_file = "../dataset/out.csv"
current_scene = 0

if not os.path.isfile(in_file):
    print("in.csv file not found. Please put datafiles in /dataset folder")
    #raise FileNotFoundError()
    exit(1)

TOTAL_SCENES = int(subprocess.check_output(["tail", "-1", in_file]).decode('ascii').split(",")[0].split('.')[0]) + 1
try:
    out_scenes = int(subprocess.check_output(["tail", "-1", out_file]).decode('ascii').split(",")[0].split('.')[0]) + 1
except FileNotFoundError:
    out_scenes = 500

#if (TOTAL_SCENES != out_scenes) raise ValueError("Mismatch of scenes in in.csv and out.csv files. Check if amount of total scenes equal")
if current_scene != 0:
    num_rows_to_skip = current_scene*72000
    print("to skip: ", num_rows_to_skip)
    df = pd.read_csv(in_file, sep=',', header = None, names=['time', 'laser_id', 'X', 'Y', 'Z'], iterator=True, skiprows=num_rows_to_skip)
    #print(df.get_chunk(5))
    # all_rows = int(subprocess.check_output(["cat " + in_file + " | wc -l"]))
    # assert(num_rows_to_skip < all_rows)
else:
    df = pd.read_csv(in_file, sep=',', header = None, names=['time', 'laser_id', 'X', 'Y', 'Z'], iterator=True)
#TODO improve global state


class Benchmark(Resource):

    total_time_score = 0

    def get(self):
        global current_scene, TOTAL_SCENES, df

        if current_scene >= TOTAL_SCENES:
                return {'message': 'Last scene reached. No more scenes left. Please, check you detailed results now',
                        'results:': BenchmarkResults.results()}, 404

        current_scene +=1
        print("Requested scene %s" % current_scene)
        sys.stdout.flush()

        try:
            self.get_timestamp(current_scene)
        except sqlite3.IntegrityError:
            return {"Benchmark error": "Please restart your benchmark-server to be able to submit new results"}, 404

        result = []
        sc = df.get_chunk(72000)
        if (int(sc["time"].iloc[0]) != int(sc["time"].iloc[-1])):
            #TODO add fail-over case
            raise ValueError("scene probably has incorrect number of rows", len(sc.index))
        #print(sc.tail(5))
        result = sc.to_json(orient='records')

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
        if not correct_dict:
            return {'message': "There is no reuslt dataexist for scene {}.".format(current_scene)}, 400
        your_dict = request.get_json()
        submission_time = datetime.datetime.now()
        print(' Correct prediction', correct_dict)
        your_dict = {str(k):int(v) for k,v in your_dict.items()}
        print(' Your prediction', your_dict)
        sys.stdout.flush()
        score = 0
        score2 = 0
        score3 = 0
        if your_dict:
            #score = Benchmark.diff_dicts(correct_dict, your_dict)
            score = metrics.accuracy(correct_dict,your_dict)
            score2 = metrics.precision(correct_dict,your_dict)
            score3 = metrics.recall(correct_dict,your_dict)
            print("scene accuracy", score)
            print("scene precision", score2)
            print("scene recall", score3)

        submission_result = {'scene': current_scene, 'accuracy': score, 'precision': score2, 'recall':score3}
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
        query = "UPDATE predictions SET accuracy=?, precision=?, recall=?, prediction_speed =?, submitted_at=? WHERE scene=?"

        cursor.execute(query, (result['accuracy'], result['precision'], result['recall'], time_diff, stop_time, result['scene']))
        conn.commit()
        conn.close()

    @classmethod
    def fetch_correct_result(cls):
        a = Benchmark.read_csv(out_file, current_scene-1)
        return Benchmark.list_to_dict(a)

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
            return False

    @classmethod
    def read_csv(cls, out_file, scene):
            with open(out_file, 'r') as f:
                reader = csv.reader(f)
                for line in reader:
                    scene_index = float(line[0])
                    if scene_index == scene:
                        return line[1:]

    @classmethod
    def list_to_dict(cls,a):

        my_dict = {}
        if not a:
            return my_dict
        for index, item in enumerate(a):
            if index % 2 == 0:
                my_dict[item] = a[index+1]
        return my_dict


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
    @classmethod
    def results(cls):
        conn = sqlite3.connect('debs.db')
        cursor = conn.cursor()

        query = "SELECT AVG(accuracy), AVG(precision), AVG(recall), SUM(prediction_speed) FROM predictions"
        cursor.execute(query)
        result = cursor.fetchone()

        conn.close()
        print('FINAL_RESULT average accuracy %s' % result[0])
        print('FINAL_RESULT average precision %s' % result[1])
        print('FINAL_RESULT average recall %s' % result[2])
        print('FINAL_RESULT total db runtime %s' % result[3])

        return {'average accuracy': result[0],
                'average precision': result[1],
                'average recall': result[2],
                'total runtime from db': result[3],
                'total runtime': Benchmark.total_time_score}

    def get(self):
        self.results()
