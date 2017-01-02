# -*- coding: utf-8 -*-

def create_variables(data_dict):
    """ 
        creates / adds three new variables to the data dictionary
        
        data_dict = This is the Enron financial and email dataset
    """
    ### Interates through each data point (person) in the data dictionary
    for person in data_dict:
        ### If none of these features ['to_messages', 'from_messages', 
        ### 'from_poi_to_this_person', 'from_this_person_to_poi'] are equal to 
        ### "NaN", then create the three variables below
        ### total_message = to_messages + from_messages
        ### total_poi = from_poi_to_this_person + from_this_person_to_poi
        ### percent_poi = total_poi / total_messages
        if data_dict[person]["to_messages"] != "NaN" and \
            data_dict[person]["from_messages"] != "NaN" and \
            data_dict[person]["from_poi_to_this_person"] != "NaN" and \
            data_dict[person]["from_this_person_to_poi"] != "NaN":
                data_dict[person]["total_messages"] = \
                    data_dict[person]["to_messages"] + \
                    data_dict[person]["from_messages"]
                data_dict[person]["total_poi"] = \
                    data_dict[person]["from_poi_to_this_person"] + \
                    data_dict[person]["from_this_person_to_poi"]
                data_dict[person]["percent_poi"] = \
                    float(data_dict[person]["total_poi"]) / \
                    float(data_dict[person]["total_messages"])
        ### Else create the three new variable with value equal to "NaN"
        else:
            data_dict[person]["total_messages"] = "NaN"
            data_dict[person]["total_poi"] = "NaN"
            data_dict[person]["percent_poi"] = "NaN"
        
    return data_dict # return udpated data dictionary