# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from ml_model_knn import *

app = Flask(__name__)


@app.route('/')
def home():
    return('Connected')


@app.route('/api/healthz')
def healthz():
    return jsonify({
                    'Result': 'Ok',
                    "Status": "Success"
                   }
)


@app.route('/api/get_recommendations/<user_id>')
def get_recommendations(user_id):
    ''' Вычисление рекомендаций '''
    return jsonify(ml_recommendations(user_id))


@app.route('/api/get_metrics')
def get_metrics():
    ''' Функция рассчитывает и возвращает метрики '''
    return jsonify(ml_metrics())


if __name__ == '__main__':
    # Run command line: waitress-serve --host 0.0.0.0 app:app
    app.run(host='0.0.0.0', port=5000, debug=True)
