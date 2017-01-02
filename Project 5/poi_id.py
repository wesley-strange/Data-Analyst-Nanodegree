#!/usr/bin/python

import pickle
from feature_format import featureFormat, targetFeatureSplit
from remove_outliers import remove_outliers
from create_variables import create_variables
from explore_dataset import explore_dataset
from feature_selection import k_best_feature_selection, feature_importances
from classifiers import run_guassianNB, run_decision_tree
from evaluate_classifier import evaluate_classifier
from tester import test_classifier, dump_classifier_and_data


### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)
    
    
### Run explore_dataset script to print out some important information about 
### the dateset. Note: this script is commented out since it was initially 
### created to gain insight about the data, but is not being used as part of 
### the algorithm. 
#explore_dataset(data_dict)

    
### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
### This is the feature list used for the GuassianNB classifier
### The next line is intentionally commented out since the features_list
### for the Decision Tree classifier is being used.

#features_list = ['poi', 'deferred_income', 'exercised_stock_options', \
#                 'total_stock_value', 'shared_receipt_with_poi']

### This is the feature list used for the Decision Tree classifier
features_list = ['poi', 'exercised_stock_options', 'total_stock_value', \
                 'bonus', 'shared_receipt_with_poi']

    
### Task 2: Remove outliers
### Run remove_outliers script to remove the outliers from the dataset
data_dict = remove_outliers(data_dict)
    
    
### Task 3: Create new feature(s)
### Run create_variables script to create the new variables for the dataset
data_dict = create_variables(data_dict)


### Store to my_dataset for easy export below.
my_dataset = data_dict


### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)


### Run k_best_feature selection to identify the best features using 
### SelectKBest. The next line is intentionally commented out, since 
### SelectKBest was already performed to determine the best features.
#k_best_feature_selection(labels, features, features_list)
    

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.

### Classifier 1: GuassianNB
### Run run_guassianNB script to create the Naive Bayes classifier
#clf = run_guassianNB()

### Classifier 2: Decision Tree
### Run run_decision_tree script to create the Decision Tree classifier
clf = run_decision_tree(features, labels)


### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. 

### Run evaluate_classifier script to perform StratifiedKFold cross-validation
print "***** My evaluation results *****"
evaluate_classifier(clf, features, labels)


### Run feature_importances script to identify the feature importances for
### each of the features used in the Decision Tree Classifier algorithm
feature_importances(features_list, clf)


### Run tester.py script to evaluate performance
### Note: precision and recall must be greater than 0.3
print "***** tester.py code results *****"
test_classifier(clf, my_dataset, features_list)


### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.
dump_classifier_and_data(clf, my_dataset, features_list)