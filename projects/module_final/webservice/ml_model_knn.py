import pandas as pd
import random
import pickle
from collections import defaultdict
from surprise import accuracy


# Загрузка модели и данных
with open('data/model_knn.pickle', 'rb') as file:
    model_knn = pickle.load(file)

with open('data/testset.pickle', 'rb') as file:
    # для вычисления метрики
    testset = pickle.load(file)

# Получить список всех известных товаров
items_all = [model_knn.trainset.to_raw_iid(x) for x in model_knn.trainset.all_items()]
# Получить список всех известных пользователей
user_all = [model_knn.trainset.to_raw_uid(x) for x in model_knn.trainset.all_users()]


def precision_recall_at_k(predictions, k=3, threshold=2):
    """Return precision and recall at k metrics for each user"""

    # First map the predictions to each user.
    user_est_true = defaultdict(list)
    for uid, _, true_r, est, _ in predictions:
        user_est_true[uid].append((est, true_r))

    precisions = dict()
    recalls = dict()
    for uid, user_ratings in user_est_true.items():

        # Sort user ratings by estimated value
        user_ratings.sort(key=lambda x: x[0], reverse=True)

        # Number of relevant items
        n_rel = sum((true_r >= threshold) for (_, true_r) in user_ratings)

        # Number of recommended items in top k
        n_rec_k = sum((est >= threshold) for (est, _) in user_ratings[:k])

        # Number of relevant and recommended items in top k
        n_rel_and_rec_k = sum(
            ((true_r >= threshold) and (est >= threshold))
            for (est, true_r) in user_ratings[:k]
        )

        # Precision@K: Proportion of recommended items that are relevant
        # When n_rec_k is 0, Precision is undefined. We here set it to 0.

        precisions[uid] = n_rel_and_rec_k / n_rec_k if n_rec_k != 0 else 0

        # Recall@K: Proportion of relevant items that are recommended
        # When n_rel is 0, Recall is undefined. We here set it to 0.

        recalls[uid] = n_rel_and_rec_k / n_rel if n_rel != 0 else 0

    return precisions, recalls


def precision_recall_at_k_mean(predictions):
    precisions, recalls = precision_recall_at_k(predictions, k=3, threshold=2)

    # Precision and recall can then be averaged over all users
    prec = round(sum(prec for prec in precisions.values()) / len(precisions), 5)
    recall = round(sum(rec for rec in recalls.values()) / len(recalls), 5)
    return prec, recall


def ml_recommendations(user_id):
    ''' Рекомендации, Top 3 '''
    try:
        if int(user_id) not in user_all:
            return {'Status': 'Error',
            'Result': f'Unknown visitor. Hint: you can use these ids (random 5): {random.sample(user_all, 5)}'}
        # Выполнить прогнозирование для uid по всем товарам и показать top 3
        recommendations = pd.DataFrame([model_knn.predict(user_id, iid) for iid in items_all]).sort_values('est', ascending=False)[:3].iid.to_list()
        return {'Status': 'Success',
                'Result': {
                    f'Recommendations for user {user_id}': recommendations
                }
        }
    except Exception as err:
        print(err)
        return {'Status': 'Error',
                'Result': 'Something is wrong! Please enter the correct data.'}


def ml_metrics():
    ''' Функция возвращает метрики '''
    predictions = model_knn.test(testset)
    rmse = round(accuracy.rmse(predictions, verbose=True), 4)
    precision_recall = precision_recall_at_k_mean(predictions)
    return {'Status': 'Success',
            'Result': {
                'Precision at 3': precision_recall[0],
                'Recall at 3': precision_recall[1],
                'Rmse': rmse
            }
    }
