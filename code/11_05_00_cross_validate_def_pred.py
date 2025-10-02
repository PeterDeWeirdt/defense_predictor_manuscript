#!/usr/bin/env python
# coding: utf-8

# In[21]:


from lightgbm import LGBMClassifier
import lightgbm as lgb
import pandas as pd
from sklearn import model_selection as ms
from sklearn import metrics as me
from sklearn.base import clone
import optuna
import joblib
from datetime import datetime


# In[23]:


def lgb_metric_ap(y, y_hat):
    is_higher_better = True
    return "avg_precision", me.average_precision_score(y, y_hat), is_higher_better


# In[24]:


def lgbm_train_iteration(train_X, train_y,
                         val_X, val_y, base_model):
    model = clone(base_model)
    model.fit(train_X, train_y, 
              eval_set=(val_X, val_y), 
              eval_metric=lgb_metric_ap, 
              callbacks=[lgb.early_stopping(50), 
                         lgb.log_evaluation(50)])
    val_predictions = model.predict_proba(val_X, 
                                          num_iteration=model.best_iteration_)[:, 1]
    score = me.average_precision_score(val_y, val_predictions)
    return score


# In[4]:


def get_lgbm_objective(train_X, train_y,
                       val_X, val_y):
    """Get objective function for training a lgbm model
    :param train_df: DataFrame
    :return: obejctive function
    """
    def objective(trial):
        """For training set, get optimal hyperparameters for lgbm
        :param trial: optuna.trial
        :return: int, avg precision with held out test data
        """
        num_leaves = trial.suggest_int('num_leaves', 4, 256)
        min_child_samples = trial.suggest_int('min_child_samples', 32, 1024)
        model = LGBMClassifier(random_state=7, n_jobs=48, learning_rate=0.1, 
                               n_estimators=5_000, 
                               num_leaves=num_leaves, 
                               min_child_samples=min_child_samples, 
                               metric='None') # don't evaluate binary log-loss
        performance = lgbm_train_iteration(train_X, train_y,
                                           val_X, val_y, model)
        return performance
    return objective


# In[5]:


model_seq_info = pd.read_parquet('../data3/interim/model_seq_info.pq')
model_mat = pd.read_parquet('../data3/interim/defense_predictor_full_ft_mat.pq')


# In[8]:


out_list = list()
for fold, fold_df in model_seq_info.groupby('test_fold'):
    print(fold)
    test_y = fold_df[['seq_id', 'defensive']].set_index('seq_id')
    test_X = (test_y.merge(model_mat, left_index=True, right_index=True, how='inner')
              .drop(columns='defensive'))
    assert (test_y.index == test_X.index).all()
    train_val_info = (model_seq_info[model_seq_info['test_fold'] != fold]
                      .reset_index(drop=True))
    # Get validation data
    defense_cluster_info = (train_val_info.query('defensive')
                        [['defense_cluster', 'cluster']]
                        .drop_duplicates()
                        .sample(frac=1, random_state=7)
                        .reset_index(drop=True))
    gkf = ms.GroupKFold(n_splits=10)
    defense_splitter = gkf.split(defense_cluster_info, groups=defense_cluster_info['cluster'])
    _ = next(defense_splitter)
    _ = next(defense_splitter)
    train_index, val_index = next(defense_splitter)
    defense_train_cluster_info = (defense_cluster_info.loc[train_index, :])
    defense_val_cluster_info = (defense_cluster_info.loc[val_index, :])
    control_cluster_info = (train_val_info.query('~defensive')
                        [['functional_group', 'cluster']]
                        .drop_duplicates()
                        .sample(frac=1, random_state=7)
                        .reset_index(drop=True))
    gkf = ms.GroupKFold(n_splits=10)
    control_splitter = gkf.split(control_cluster_info, groups=control_cluster_info['cluster'])
    _ = next(control_splitter)
    _ = next(control_splitter)
    train_index, val_index = next(control_splitter)
    control_train_cluster_info = (control_cluster_info.loc[train_index, :])
    control_val_cluster_info = (control_cluster_info.loc[val_index, :])
    train_info = (train_val_info[train_val_info['cluster'].isin(defense_train_cluster_info['cluster']) | 
                             train_val_info['cluster'].isin(control_train_cluster_info['cluster'])]
              .reset_index(drop=True))
    train_y = (train_info[['seq_id', 'defensive']]
               .set_index('seq_id'))
    train_X = (train_y.merge(model_mat, left_index=True, right_index=True, how='inner')
              .drop(columns='defensive'))
    assert (train_y.index == train_X.index).all()
    val_info = (train_val_info[train_val_info['cluster'].isin(defense_val_cluster_info['cluster']) | 
                                 train_val_info['cluster'].isin(control_val_cluster_info['cluster'])]
                  .reset_index(drop=True))
    val_y = (val_info[['seq_id', 'defensive']]
               .set_index('seq_id'))
    val_X = (val_y.merge(model_mat, left_index=True, right_index=True, how='inner')
              .drop(columns='defensive'))
    assert (val_y.index == val_X.index).all() 
    print('Train size:', len(train_X))
    print('Train defense:', train_y.mean().item())
    print('Val size:', len(val_X))
    print('Val defense:', val_y.mean().item())
    print('Test size:', len(test_X))
    print('Test defense:', test_y.mean().item())
    n_trials = 15
    study = optuna.create_study(direction='maximize',
                                sampler=optuna.samplers.TPESampler(seed=8)) # maximize average precision
    objective = get_lgbm_objective(train_X.to_numpy(), train_y.squeeze(),
                                   val_X.to_numpy(), val_y.squeeze())
    start_time = datetime.now()
    study.optimize(objective, n_trials=n_trials)
    end_time = datetime.now()
    difference = end_time - start_time
    print("Number of finished trials: {}".format(len(study.trials)))
    print("Training Time: " + str(difference))
    print("Best trial:")
    trial = study.best_trial
    print("  Value: {}".format(trial.value))
    print("  Params: ")
    for key, value in trial.params.items():
        print("    {}: {}".format(key, value))
    beaker = LGBMClassifier(random_state=7, n_jobs=48, learning_rate=0.01,
                                n_estimators=30_000, 
                                num_leaves=study.best_params['num_leaves'],
                                min_child_samples=study.best_params['min_child_samples'], 
                                metric='None')
    beaker.fit(train_X.to_numpy(), train_y.squeeze(), 
               eval_set=(val_X.to_numpy(), val_y.squeeze()), 
               eval_metric=lgb_metric_ap, 
               callbacks=[lgb.early_stopping(200), 
                          lgb.log_evaluation(100)])
    joblib.dump(beaker, '../models3/beaker_fold_' + str(fold) + '.pkl')
    test_predictions = (beaker.predict_proba(test_X)[:, 1])
    fold_df['prediction'] = test_predictions
    fold_out_df = fold_df[['seq_id', 'prediction']]
    out_list.append(fold_out_df)


# In[32]:


out_df = pd.concat(out_list)
out_df['method'] = 'DefensePredictor'
out_df.to_parquet('../data3/interim/cv_predictions_defense_predictor.pq', index=False)

