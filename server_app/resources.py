from flask import request
from flask_restful import Resource
import sqlite3
import datetime
import pandas as pd
import numpy

dataset = pd.read_csv("../dataset/in.csv", header=None, names=['time', 'laser_id', 'X', 'Y', 'Z'])
correct = pd.read_csv("../dataset/out.csv", header=None, names=['object_id', 'quantity'])


class AllScenes(Resource):

    def get(self):
        conn = sqlite3.connect('debs.db')
        cursor = conn.cursor()

        query = "SELECT * FROM predictions"
        result = cursor.execute(query)
        items = []
        for row in result:
            items.append({'scene': row[0], 'similarity_score': row[1], 'client_timestamp': row[2]})
        conn.close()
        return {'Submitted scenes': items}


class Scene(Resource):

    @classmethod
    def get_timestamp(self, number):

        conn = sqlite3.connect('debs.db')
        cursor = conn.cursor()
        query = "SELECT * FROM measurements WHERE scene=?"
        result = cursor.execute(query, (number,))
        row = result.fetchone()
        if row:
            cursor.execute("DELETE FROM measurements WHERE scene=?", (number,))

        query = "INSERT INTO measurements VALUES(?,?,?)"
        cursor.execute(query, (number, 0, datetime.datetime.now()))
        conn.commit()
        conn.close()

    def get(self, number):
        self.get_timestamp(number)
        result = []

        #1) return {'scene': armIn[(armIn.time > int(number) -1) & (armIn.time < int(number))].to_dict(orient='list')}
        #2)
        # for ix, row in armIn[(armIn.time > int(number) -1) & (armIn.time < int(number))].iterrows(): # TODO
        #     result.append(row.values.tolist())
        # return {'scene': result}
        # [list(x) for x in dt.T.itertuples()]
        scene = dataset[(dataset.time > int(number) -1) & (dataset.time < int(number))]
        #3) result.append([list(x) for x in scene.itertuples()])
        #4) result.append(list(scene.itertuples()))
        #5) result = scene.values.tolist()
        #6) result = scene.to_dict('list')
        # result = scene.to_dict('records')
        # result = scene.to_dict(orient="index")
        # result = scene.to_json()
        result = scene.to_json(orient='records')
        return {'scene': result}


class Prediction(Resource):

    # parser = reqparse.RequestParser()
    # parser.add_argument('object_id',
    #                     type=int,
    #                     required=True,
    #                     help='This field better not be blank!'
    #                     )
    # parser.add_argument('object_id',
    #                     type=str,
    #                     required=True,
    #                     help='This field better not be blank!',
    #                     action='append'
    #                     )
    # parser.add_argument('quantity',
    #                     type=str,
    #                     required=True,
    #                     help='This field better not be blank!',
    #                     action='append'
    #                     )

    def get(self, number):
        scene = self.find_scene(number)
        if scene:
            return scene

        return {'message': 'Predictions on these scene are not found'}, 404

    @classmethod
    def find_scene(cls, number):
        conn = sqlite3.connect('debs.db')
        cursor = conn.cursor()

        query = "SELECT * FROM predictions WHERE scene=?"
        result = cursor.execute(query, (number,))
        row = result.fetchone()
        conn.close()
        if row:
            return {'scene': {'scene': row[0], 'similarity_score': row[1]}}

    def post(self, number):
        if self.find_scene(number):
            return {'message': "A scene {} already exist.".format(number)}, 400
        score = 0
        correct_dict = self.fetch_correct_result()
        your_dict = request.get_json()
        print(' Correct prediction', correct_dict)
        print(' Your prediction', your_dict)
        if your_dict:
            score = self.diff_dicts(correct_dict, your_dict)

        # data = Prediction.parser.parse_args()
        # result = {'scene': number, 'object_id': self.check_objects(data['object_id']), 'quantity': self.check_object(data['quantity'])}
        result = {'scene': number, 'similarity_score': score}
        print(result)

        try:
            self.insert(result)
        except:
            return {'message': 'An error occured while inserting the item'}, 500

        return {'Your score for this scene is ': result['similarity_score']}, 201

    @classmethod
    def check_objects(cls, result):
        return ','.join(result)

    @classmethod
    def fetch_correct_result(cls):
        correct_object = correct['object_id'].iloc[0].split(',')
        correct_quantity = correct['quantity'].iloc[0]
        if (isinstance(correct_quantity, int)) or (isinstance(correct_quantity, numpy.int64)):
            correct_quantity = [correct_quantity]
        else:
            correct_quantity = correct_quantity.split(',')
        res = dict(zip(correct_object, correct_quantity))
        print(res)
        return res

    @classmethod
    def diff_dicts(cls, a, b):
        # print(a.keys() & b.keys())
        total = 0
        for key in a.keys():
            if key in b.keys():
                total += abs(int(a[key]) - int(b[key]))
            else:
                total += 10

        for key in b.keys():
            if key in a.keys():
                total += abs(int(a[key]) - int(b[key]))
            else:
                total += 10

        i = [k for k in b if k in a if b[k] != a[k]]
        if i:
            for k in i:
                print('Your predictions are not correct: your predicted [%s] = %s but was expected [%s] = %s' % (k, b[k], k, a[k]) )

        else:
            i = [k for k in b if k in a if a[k] != b[k]]
            if i:
                for k in i:
                    print('Else Your predictions are not correct: your predicted [%s] = %s but was expected [%s] = %s' % (k, b[k], k, a[k]) )
        print("Difference ", total)
        return total

    @classmethod
    def insert(cls, result):
        conn = sqlite3.connect('debs.db')
        cursor = conn.cursor()

        query = "INSERT INTO predictions VALUES(?,?,?)"
        print(result['scene'])
        cursor.execute(query, (result['scene'], result['similarity_score'], datetime.datetime.now()))
        conn.commit()
        conn.close()


""" This additional functionality may be added later.

    def put(self, number):

        correct_dict = self.fetch_correct_result()
        your_dict = request.get_json()
        print(your_dict)
        self.diff_dicts(correct_dict, your_dict)
        try:
            data = Prediction.parser.parse_args()  # request.get_json()
            res = self.find_scene(number)

        except:
            return {'message': 'Probably and invalid JSON object was passed'}, 400

        updated_result = {'scene': number, 'object_id': self.check_objects(data['object_id']), 'quantity': self.check_objects(data['quantity'])}
        print("Updated result", updated_result)

        if res is None:
            try:
                self.insert(updated_result)
            except:
                return {'message': 'An error occured while inserting the item'}, 500
        else:
            try:
                self.update(updated_result)
            except:
                return {'message': 'An error occured while updating the predicition'}, 500
        return updated_result

    @classmethod
    def update(cls, result):
        conn = sqlite3.connect('debs.db')
        cursor = conn.cursor()

        query = "UPDATE predictions SET score=?, submitted_at=? WHERE scene=?"
        cursor.execute(query, (result['similarity_score'], datetime.datetime.now(), result['scene']))
        conn.commit()
        conn.close() """
