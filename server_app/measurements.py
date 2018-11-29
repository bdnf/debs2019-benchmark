from flask_restful import Resource
import sqlite3
import datetime
# from difflib import SequenceMatcher


class Measurements(Resource):
    @classmethod
    def compute_score(self, row):
        import _strptime # solves some sudden crashes "Failed to import _strptime because the import lockis held by"
        # test1 = int(datetime.datetime.strptime("2018-11-26 16:20:04.485056", "%Y-%m-%d %H:%M:%S.%f").strftime("%s"))
        # test2 = int(datetime.datetime.strptime("2018-11-26 16:21:04.485056", "%Y-%m-%d %H:%M:%S.%f").strftime("%s"))
        # print("test ", test1-test2)

        # date1 = datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%f").strftime("%Y-%m-%d %H:%M:%f")
        # date2 = datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%f").strftime("%Y-%m-%d %H:%M:%f")
        date1 = int(datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S.%f").strftime("%s"))
        date2 = int(datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S.%f").strftime("%s"))
        time_result = date2-date1
        # print(date1)
        # print(date2)
        print('Your time for predictions was %s seconds' % time_result) # or / by 60 to get value
        return time_result

        """
        correct_object = correct['object_id'].iloc[0]
        correct_quantity = correct['quantity'].iloc[0]

        predicted_result = row[1].lower()
        predicted_quantity = row[2]
        print("predicted_quantity is: ", len([predicted_quantity]) )

        keys =  correct_object.split(',')
        values = str(correct_quantity).split(',')
        import itertools
        d = dict(zip(keys,itertools.repeat(values,len(keys))))
        pred_keys =  predicted_result.split(',')

        if len([predicted_quantity]) == 1:
            pred_values = [predicted_quantity]
        else:
            pred_values = predicted_quantity.split(',')
        assert(len(pred_keys) == len(pred_values))
        #pred_d = dict(zip(pred_keys,pred_values))
        pred_dict = {str(k): int(v) for k, v in zip(pred_keys, pred_values)}
        """

        # print("Sequence matcher score: ", SequenceMatcher(
        #             None,
        #             correct['object_id'].iloc[0],
        #             row[1].lower()
        #             ).ratio() )
        #
        # if correct['object_id'].iloc[0] in row[1].lower():
        #     print('You result is correct')


    @classmethod
    def join(self):
        conn = sqlite3.connect('debs.db')
        cursor = conn.cursor()

        query = '''
        SELECT
            predictions.scene,
            predictions.similarity_score,
            measurements.started_at,
            predictions.submitted_at

        FROM predictions
        INNER JOIN measurements
            ON measurements.scene = predictions.scene
        '''
        result = cursor.execute(query)

        items = []
        scenes_predicted = 0
        overall_time_score = 0
        for row in result:
            scenes_predicted +=1
            print('Row: ', row)
            if row[0] > 51:
                break
            time_score = self.compute_score(row)
            overall_time_score += time_score
            items.append({'scene':row[0], 'similarity_score': row[1], 'started_at': row[2], 'submitted_at': row[3]})

            # the result might be updated fror each scene individually or for all of the scenes once at the end
            cursor = conn.cursor()
            query = "UPDATE measurements SET time_result=? WHERE scene=?"
            cursor.execute(query, (time_score, row[0]))
            conn.commit()

        conn.close()
        unpredicted_scenes = 50 - scenes_predicted
        if unpredicted_scenes != 0:
            overall_time_score += (unpredicted_scenes * 100)

        return {'Results': items,
                'Overall time_score is': overall_time_score,
                'Predicted scenes': scenes_predicted,
                'Penalty for not predicted scenes is ': unpredicted_scenes * 100}

    def get(self):
        result = self.join()
        return result
