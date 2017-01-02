# -*- coding: utf-8 -*-

def k_best_feature_selection(labels, features, features_list):
    """ 
        Identifies the best features using SelectKBest feature selection
    
        labels = target list as returned by the targetFeatureSplit script
        features = features list as returned by the targetFeatureSplit script
        features_list = list of the features to be assessed
    """
    from sklearn.feature_selection import SelectKBest
    
    k_best = SelectKBest(k = 10)
    k_best.fit(features, labels)
    scores = k_best.scores_
    
    features_list = features_list[1:]
    feature_scores = zip(features_list, scores)
    feature_scores = sorted(feature_scores, key = lambda x: x[1])
    feature_scores = feature_scores[::-1]

    print feature_scores
    
    print "Top 10 features identifed using SelectKBest:"
    i = 1
    while i < 11:
        print "  ", i, "-", feature_scores[i-1]
        i += 1
        
        
        
def feature_importances(features, clf):
    """ 
        Prints the feature importances for the features used in the Decision
            Tree algorithm.
            
        features = features list input into the algorithm
        clf = Decision Tree Classifier
    """
    i = 1
    imp = clf.feature_importances_
    while i < len(features):
        print features[i], imp[i-1]
        i += 1