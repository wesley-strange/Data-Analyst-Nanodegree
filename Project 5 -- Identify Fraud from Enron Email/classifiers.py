# -*- coding: utf-8 -*-

def run_guassianNB():
    """ 
        Create and return a Guassian Naive Bayes classifier.
    """
    from sklearn.naive_bayes import GaussianNB
    clf = GaussianNB()
    return clf
    
    
    
def run_decision_tree(features, labels):
    """ 
        Create and return a Decision Tree classifier. Run the
            tune_parameters script to use GridSearchCV to identify the best 
            parameters to use for the algorithm.
        
        features = features list as returned by the targetFeatureSplit script
        labels = target list as returned by the targetFeatureSplit script
    """
    from sklearn import tree
    
#==============================================================================
#     best_parameters = tune_parameters(features, labels)
#     
#     clf = tree.DecisionTreeClassifier(
#             criterion = best_parameters["criterion"], 
#             min_samples_split = best_parameters["min_samples_split"], 
#             random_state = best_parameters["random_state"], 
#             splitter = best_parameters["splitter"],
#             presort = best_parameters["presort"],
#             min_impurity_split = best_parameters["min_impurity_split"],
#             min_samples_leaf = best_parameters["min_samples_leaf"])
#==============================================================================
    
    clf = tree.DecisionTreeClassifier(
            criterion = "gini", 
            min_samples_split = 2, 
            random_state = 42, 
            splitter = "best",
            presort = True,
            min_impurity_split = 1e-09,
            min_samples_leaf = 1)
    
    return clf
    
    
    
def tune_parameters(features, labels):
    """ 
        Use GridSearchCV to identify and return the best parameters to use 
            for the Decision Tree algorithm.
        
        features = features list as returned by the targetFeatureSplit script
        labels = target list as returned by the targetFeatureSplit script
    """
    from sklearn import tree
    from sklearn.model_selection import GridSearchCV
    from sklearn.metrics import make_scorer
    
    # Make scorer for the GridSearchCV function
    scorer = make_scorer(custom_scorer, greater_is_better = True)
    
    # Parameters names and settings to be used by GridSearchCV
    parameters = [{"criterion": ["gini", "entropy"], 
                   "splitter": ["best", "random"], 
                   "min_samples_split": [2, 3, 4, 5, 6, 7, 8, 9, 10], 
                   "min_samples_leaf": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 
                   "min_impurity_split": [1e-9, 1e-8, 1e-7, 1e-6, 1e-5], 
                   "presort": [True, False], 
                   "random_state": [42]}]
    
    # Use GridSearchCV to identify the best parameters
    # K-fold cross-validation is used (100 folds)
    # F1 score from custom_scorer function is used as the evaluator
    clf = GridSearchCV(tree.DecisionTreeClassifier(), parameters, cv = 100, scoring = scorer)
    
    clf.fit(features, labels)
    
    best_parameters = clf.best_params_
    
    return best_parameters
    
    
    
def calculate_scores(labels, predictions):
    """ 
        Calculates the precision, recall, and average of precision/recall 
            using the labels and prediction input values.
        
        labels = target list as returned by the targetFeatureSplit script
        predictions = predicted values from the classifier
    """
    # Calculate the true / false positives and negatives
    true_positives = [i for i in range(0, len(labels)) if (predictions[i] == 1) & (labels[i] == 1)]
    false_positives = [i for i in range(0, len(labels)) if ((predictions[i]==1) & (labels[i] == 0))]
    false_negatives = [i for i in range(0, len(labels)) if ((predictions[i]==0) & (labels[i] == 1))]
    #true_negatives = [i for i in range(0, len(labels)) if ((predictions[i]==0) & (labels[i] == 0))]
    
    precision = 0
    recall = 0
    avg_precision_recall = 0        
    
    # Calculate precision (true positives / true positives + false positives)
    if float( len(true_positives) + len(false_positives)) != 0:
        precision = float(len(true_positives)) / float( len(true_positives) + len(false_positives))
    
    # Calculate recall (true positives / true positives + false positives)
    if float( len(true_positives) + len(false_negatives))!=0:
        recall = float(len(true_positives)) / float( len(true_positives) + len(false_negatives))
    
    # Calculate F1 score (mean of precision and recall)
    avg_precision_recall = (precision + recall) / 2.0

    # return scores
    return precision, recall, avg_precision_recall
    
   
    
def custom_scorer(labels, predictions):
    """ 
        Returns the average of the precision and recall scores from the 
            calculate_scores function.
        
        labels = target list as returned by the targetFeatureSplit script
        predictions = predicted values from the classifier
    """
    # Calculate the true / false positives and negatives
    _, _, avg = calculate_scores(labels, predictions)

    # return F1 score
    return avg