from time import time
import requests
import json
import pandas as pd
# unirest fo Java


def host_url(path):
    return "http://127.0.0.1:5000" + path


# def get_scenes():
#     response = requests.get(host_url('/scenes/'))
#     if (response.ok):
#         data = json.loads(response.content)
#         print(data)
#         return data
    # return requests.get(host_url('/scenes/'))


def get_scene(number):
    response = requests.get(host_url('/scene/'+str(number)))
    if (response.ok):
        data = json.loads(response.content)
        print(data)
        return data
    #else: return response


def post_answer(scene, object_id):
    headers = {'Content-type': 'application/json'}
    # list of objects with quantities
    #TODO
    response = requests.post(host_url('/prediction/scene/'+str(scene)), json={'object_id': object_id}, headers=headers)
    print(response.status_code)
    if (response.status_code == 201):
        return {'status': 'success', 'message': 'updated'}
    if (response.status_code == 400):
        # NOT needed
        # data already exists try post request
        print ({'message': '''A scene {} already exist.
                If you want to update your value try to use PUT request'''
                .format(scene)})
                # PUT?


if __name__ == "__main__":
    print('Getting the scenes for predictions...')

    start_time = time()

    data = get_scene(10)
    # result = json.dumps(data['scene'])
    # print(result)

    # print(pd.DataFrame(result))
    print("Getting scene done in --- %s seconds ---" % (time() - start_time))

    # reconstructing json to DataFrame
    print(pd.read_json(data['scene'], orient='records'))

    # 3.853092908859253 seconds for .to_dict(orient='list') !columnwise
    # 9.07844591140747 seconds --- for row append methods
    # 4.220257997512817 seconds --- for itertuples with list comprehention
    # 4.997031211853027 seconds --- for itertuples append
    # 3.337400197982788 seconds --- for append ( df.values.tolist() )
    # 3.583112955093384 seconds best --- for result =
    # 2.7062032222747803 seconds --- scene.to_dict('list') !columnwise
    # 11.396817922592163 seconds --- scene.to_dict('records') !rowwise as pure json
    # 9.465748071670532 seconds --- orient="index" !rowwise as pure json
    # 1.2855260372161865 seconds --- df.to_json()
    # 1.021428108215332 seconds --- scene.to_json(orient='records') !rowwise

    # {do complex prediction}
    # post_answer(scene=12, object_id=1)
