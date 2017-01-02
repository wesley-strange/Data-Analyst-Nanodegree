feature_format.py contains:
-- featureFormat script used to convert dictionary to numpy array of features
-- targetFeatureSplit script used to splits out the POI feature into its own list and returns targets and features as separate lists.

remove_outliers.py contains:
-- remove_outliers script used to remove outliers from the data dictionary and returns the updated dictionary.

create_variables.py contains:
-- create_variables script which creates / adds three new variables to the data dictionary.

explore_dataset.py contains:
-- explore_dataset script that prints out some general informaiton / insights about the Enron financial and email dataset.

feature_selection.py contains:
-- k_best_feature_selection script which identifies the best features using SelectKBest feature selection.
-- feature_importances script that prints the feature importances for the features used in the Decision Tree algorithm.

classifiers.py contains:
-- run_guassianNB script used to create and return the Guassian Naive Bayes classifier.
-- run_decision_tree script use to create and return a Decision Tree classifier. Run the tune_parameters script to use GridSearchCV to identify the best parameters to use for the algorithm.
-- tune_parameters script which uses GridSearchCV to identify and return the best parameters to use for the Decision Tree algorithm.
-- calculate_scores script which calculates the precision, recall, and average of precision/recall using the labels and prediction input values.
-- custom_scorer script that returns the average of the precision and recall scores from the calculate_scores function.

evaluate_classifier.py contains:
-- evaluate_classifier script that evaluates the classifier using StratifiedKFold cross validation. The precision and recall scores are used to evaluate the algorithm's performance.

tester.py contains:
-- a basic script for importing student's POI identifier, and checking the results that they get from it.