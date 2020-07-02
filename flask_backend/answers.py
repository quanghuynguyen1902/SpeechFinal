from flask_restful import Resource, Api
from flask import Flask, request
from module import get_answer
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['PROPAGATE_EXCEPTIONS'] = True 
app.secret_key = 'jose'
api = Api(app)

question = None

class Answer(Resource):
    def get(self):
        global question
        if question is None:
            return {'message': 'Not found question'}, 400
        answer = get_answer(question)
        if answer:
            return {'answer': answer}, 200
        return {'message': 'Hien tai chung toi chua the tra loi cau hoi nay. Vui long len he voi nhan vien de biet them chi tiet'}, 400
    def post(self):
        global question
        json = request.get_json()
        question = json['question']
        print(question)
        if question is None:
            return {'message ': 'Please send my questions'}, 400
        return {'message': 'Question adlready send'}, 201

api.add_resource(Answer, '/answer')

if __name__ == '__main__':
    app.run(debug=True)  # important to mention debug=True