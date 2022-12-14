import tensorflow as tf
from tensorflow_serving.apis import predict_pb2, prediction_service_pb2_grpc
import grpc
import os
from keras_image_helper import create_preprocessor

from flask import Flask, request, jsonify

from proto import np_to_protobuf


host = os.getenv('TF_SERVING_HOST', 'localhost:8500')

channel = grpc.insecure_channel(host)
stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)


preprocessor = create_preprocessor('xception', target_size=(150, 150))


def prepare_request(X):
    pb_request = predict_pb2.PredictRequest()
    pb_request.model_spec.name = 'santa-class-v1'
    pb_request.model_spec.signature_name = 'serving_default'
    pb_request.inputs['input_2'].CopyFrom(np_to_protobuf(X))

    return pb_request

def prepare_response(pb_response):
    preds = pb_response.outputs['dense_1'].float_val
    return preds[0]


def predict(url):
    X = preprocessor.from_url(url)

    pb_request = prepare_request(X)
    pb_response = stub.Predict(pb_request, timeout=20.0)
    response = prepare_response(pb_response)
    return response
    

app = Flask('gateway')

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    data = request.get_json()
    url = data['url']
    return jsonify(predict(url))


if __name__ == '__main__':
    # url = 'https://www.surreynowleader.com/wp-content/uploads/2022/02/28111564_web1_220217-SUL-BrettKellyFamilyLaw-main_1.jpg'
    # response = predict(url)
    # print(f'This is Santa with probability {response:.2f}')
    app.run(debug=True, host='0.0.0.0', port=9696)
