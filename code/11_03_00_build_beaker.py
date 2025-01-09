from lightgbm import LGBMClassifier
import lightgbm as lgb
import pandas as pd
from sklearn.metrics import average_precision_score
from sklearn.base import clone
from datetime import datetime
import optuna
import joblib
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm


def lgb_metric_ap(y, y_hat):
    is_higher_better = True
    return "avg_precision", average_precision_score(y, y_hat), is_higher_better


def lgbm_train_iteration(train_X_train, train_y_train,
                         train_X_val, train_y_val, 
                         val_X, val_y, base_model):
    model = clone(base_model)
    model.fit(train_X_train, train_y_train, 
              eval_set=(train_X_val, train_y_val), 
              eval_metric=lgb_metric_ap, 
              callbacks=[lgb.early_stopping(50), 
                         lgb.log_evaluation(50)])
    val_predictions = model.predict_proba(val_X, 
                                          num_iteration=model.best_iteration_)[:, 1]
    score = average_precision_score(val_y, val_predictions)
    return score


def get_lgbm_objective(train_X_train, train_y_train,
                       train_X_val, train_y_val,
                       val_X, val_y):
    """Get objective function for training a lgbm model
    :param train_df: DataFrame
    :return: obejctive function
    """
    def objective(trial):
        """For training set, get optimal hyperparameters for lgbm
        :param trial: optuna.trial
        :return: int, pearson correlation with held out test data
        """
        num_leaves = trial.suggest_int('num_leaves', 4, 256)
        min_child_samples = trial.suggest_int('min_child_samples', 32, 1024)
        model = LGBMClassifier(random_state=7, n_jobs=48, learning_rate=0.1, 
                               n_estimators=10_000, 
                               num_leaves=num_leaves, 
                               min_child_samples=min_child_samples, 
                               metric='None') # don't evaluate binary log-loss
        performance = lgbm_train_iteration(train_X_train, train_y_train,
                                           train_X_val, train_y_val,
                                           val_X, val_y, model)
        return performance
    return objective


class SaveStudyCallback:
    def __init__(self, file_name):
        self.file_name = file_name

    def __call__(self, study, trial):
        print('saving study')
        joblib.dump(study, self.file_name)


if __name__ == '__main__':
    train_X = pd.read_parquet('../data/interim/train_X.pq')
    train_y = pd.read_parquet('../data/interim/train_y.pq')
    val_X = pd.read_parquet('../data/interim/val_X.pq')
    val_y = pd.read_parquet('../data/interim/val_y.pq')
    assert (train_X.columns == val_X.columns).all()
    assert (train_X.index == train_y.index).all()
    assert (val_X.index == val_y.index).all()
    print('validation set size')
    print(val_y['defense'].value_counts())
    cluster_df = pd.read_table('../data/interim/refseqs_clusters_mode1.tsv', 
                               names=['cluster_id', 'seq_id'])
    train_cluster_df = (cluster_df[cluster_df['seq_id'].isin(train_X.index)]
                    .reset_index(drop=True))
    del cluster_df
    all_train_clusters = train_cluster_df['cluster_id'].unique()
    train_train_clusters, train_val_clusters = train_test_split(all_train_clusters, 
                                                                test_size=0.1)
    train_train_ids = train_cluster_df.loc[train_cluster_df['cluster_id']
                                           .isin(train_train_clusters), 
                                           'seq_id']
    train_val_ids = train_cluster_df.loc[train_cluster_df['cluster_id']
                                           .isin(train_val_clusters), 
                                           'seq_id']
    train_X_train = train_X.loc[train_train_ids, :]
    train_y_train = train_y.loc[train_train_ids, :]
    train_X_val = train_X.loc[train_val_ids, :]
    train_y_val = train_y.loc[train_val_ids, :]
    assert (train_X_train.index == train_y_train.index).all()
    assert (train_X_val.index == train_y_val.index).all()
    assert (train_X_val.index.isin(train_X_train.index).sum() == 0)
    print('Train validation stats')
    print(train_y_val.value_counts())
    print('Train train stats')
    train_y_train.value_counts()
    n_trials = 20
    if n_trials:
        study = optuna.create_study(direction='maximize',
                                    sampler=optuna.samplers.TPESampler(seed=8)) # maximize average precision
        objective = get_lgbm_objective(train_X_train.to_numpy(), train_y_train.squeeze(),
                                       train_X_val.to_numpy(), train_y_val.squeeze(),
                                       val_X.to_numpy(), val_y.squeeze())
        start_time = datetime.now()
        study.optimize(objective, n_trials=n_trials, 
                       callbacks=[SaveStudyCallback('../data/interim/optuna_study.joblib')])
        end_time = datetime.now()
        difference = end_time - start_time
        print("Number of finished trials: {}".format(len(study.trials)))
        print("Training Time: " + str(difference))
    else:
        study = joblib.load('../data/interim/optuna_study.joblib')
    print("Best trial:")
    trial = study.best_trial
    print("  Value: {}".format(trial.value))
    print("  Params: ")
    for key, value in trial.params.items():
        print("    {}: {}".format(key, value))
    del train_X_train, train_y_train, train_X_val, train_y_val 
    beaker = LGBMClassifier(random_state=7, n_jobs=48, learning_rate=0.01,
                            n_estimators=100_000, 
                            num_leaves=study.best_params['num_leaves'],
                            min_child_samples=study.best_params['min_child_samples'], 
                            metric='None')
    beaker.fit(train_X.to_numpy(), train_y.squeeze(), 
          eval_set=(val_X.to_numpy(), val_y.squeeze()), 
          eval_metric=lgb_metric_ap, 
          callbacks=[lgb.early_stopping(200), 
                     lgb.log_evaluation(50)])
    joblib.dump(beaker, '../models/beaker_v3.pkl')
    