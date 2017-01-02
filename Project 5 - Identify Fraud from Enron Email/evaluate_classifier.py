# -*- coding: utf-8 -*-

def evaluate_classifier(clf, features, labels):
    """ 
        Evaluates the classifier using StratifiedKFold cross validation. The 
            precision and recall scores are used to evaluate the algorithm's 
            performance.
        
        clf = classifier
        features = features list as returned by the targetFeatureSplit script
        labels = target list as returned by the targetFeatureSplit script
    """
    from sklearn.metrics import precision_score
    from sklearn.metrics import recall_score
    from sklearn.model_selection import StratifiedKFold
    
    ### Use StratifiedKFold cross validation with 10 folds
    skf = StratifiedKFold(n_splits = 10, random_state = 42)
    
    precision = []
    recall = []
    count = 0

    ### Split the features and labels into training and testing sets.
    for train_index, test_index in skf.split(features, labels):
        features_train = []
        features_test = []
        labels_train = []
        labels_test = []

        for i in train_index:
            features_train.append(features[i])
            labels_train.append(labels[i])
                
        for j in test_index:
            features_test.append(features[j])
            labels_test.append(labels[j])
    
        clf.fit(features_train, labels_train)
        pred = clf.predict(features_test)
        
        precision.append(precision_score(labels_test, pred))
        recall.append(recall_score(labels_test, pred))
        
        count += 1
    
    print clf
    print "Folds:", count
    print "Average Precision:", sum(precision) / count
    print "Average Recall:", sum(recall) / count
    print ""