# -*- coding: utf-8 -*-

def remove_outliers(data_dict):
    """ 
        Removes outliers from the data dictionary and returns the updated
            dictionary
            
        data_dict = This is the Enron financial and email dataset
    """
    ### Remove the TOTAL and THE TRAVEL AGENCY IN THE PARK data points
    ### TOTAL is a spreadsheet summary line
    ### THE TRAVEL AGENCY IN THE PARK is not a person
    outliers = ['TOTAL', 'THE TRAVEL AGENCY IN THE PARK']
    for feature in outliers:
        data_dict.pop(feature, 0)
    return data_dict # return the updated data dictionary