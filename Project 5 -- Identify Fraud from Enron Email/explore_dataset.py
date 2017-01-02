# -*- coding: utf-8 -*-

def explore_dataset(data_dict):
    """ 
        prints out some general informaiton / insights about the Enron 
            financial and email dataset
            
        data_dict = This is the Enron financial and email dataset
    """
    import pprint
    
    ### Print out the data dictionary
    pprint.pprint(data_dict)
    
    num_pois = 0
    persons = {}
    features = {}
    
    ### Interates through each data point (person) in the data dictionary
    for person in data_dict:
        ### Skip if this is the TOTAL datapoint which is an outlier
        if person != "TOTAL":
            if person not in persons:
                persons[person] = {"poi": False}

            ### Determine the total number of POIs in the dataset
            if data_dict[person]["poi"] == True:
                persons[person]["poi"] = True
                num_pois += 1
                
            ### Determine the number of missing values for each feature
            for feature in data_dict[person]:
                if feature not in features:
                    features[feature] = {"num_nan": 0, 
                                         "perc_nan": 0, 
                                         "num_poi_nan": 0, 
                                         "perc_poi_nan": 0}

                if data_dict[person][feature] == "NaN":
                    features[feature]["num_nan"] += 1
                    if data_dict[person]["poi"] == True:
                        features[feature]["num_poi_nan"] += 1
    
    print "There are", len(persons), \
          "people (datapoints) in dataset (note: not including Total datapoint)."

    print "There are", num_pois, "POIs in the dataset."
    
    print (float(num_pois)/float(len(persons))*100), "percent of the people are POIS."
    
    print "Here is the full list of people in the dataset and if they're a POI."
    pprint.pprint(persons)

    features_high_nan = []

    print "There are", len(features), "features in the dataset."
    
    print "Here is the full list of features in the dataset:"
    for feature in features:
        print "-", feature
        features[feature]["perc_nan"] = int((features[feature]["num_nan"] / 
                                        float(len(persons)))*100)
        features[feature]["perc_poi_nan"] = int((features[feature]["num_poi_nan"] / 
                                            float(num_pois))*100)
        
        if features[feature]["perc_nan"] > 50:
            features_high_nan.append(feature)
    
    print "Here are the features that have many missing values."
    for feature in features:
        if feature in features_high_nan:
            print "-", feature, "percentage NaN: ", features[feature]["perc_nan"], \
                  ", percentage POI NaN: ", features[feature]["perc_poi_nan"]
    

    ### Investigate how POIs interact with eachother vs. other non-POIs
    poi_to_messages = 0
    poi_from_messages = 0
    poi_from_poi_to_this_person = 0
    poi_from_this_person_to_poi = 0
    
    nonpoi_to_messages = 0
    nonpoi_from_messages = 0
    nonpoi_from_poi_to_this_person = 0
    nonpoi_from_this_person_to_poi = 0
    
    ### Interates through each data point (person) in the data dictionary
    for person in data_dict:
        ### Skip if this is the TOTAL datapoint which is an outlier
        if person != "TOTAL":
            ### If none of these features ['to_messages', 'from_messages', 
            ### 'from_poi_to_this_person', 'from_this_person_to_poi'] are equal to 
            ### "NaN", then continue
            if data_dict[person]["to_messages"] != "NaN" and \
                data_dict[person]["from_messages"] != "NaN" and \
                data_dict[person]["from_poi_to_this_person"] != "NaN" and \
                data_dict[person]["from_this_person_to_poi"] != "NaN":
                    ### IF person is a poi, then add their message counts to 
                    ### the POI totals. ELSE add their message counts to the 
                    ### Non-POI totals.
                    if data_dict[person]["poi"] == True:                
                        poi_to_messages += data_dict[person]["to_messages"]
                        poi_from_messages += data_dict[person]["from_messages"]
                        poi_from_poi_to_this_person += data_dict[person]["from_poi_to_this_person"]  
                        poi_from_this_person_to_poi += data_dict[person]["from_this_person_to_poi"]
                    else:
                        nonpoi_to_messages += data_dict[person]["to_messages"]
                        nonpoi_from_messages += data_dict[person]["from_messages"]
                        nonpoi_from_poi_to_this_person += data_dict[person]["from_poi_to_this_person"]  
                        nonpoi_from_this_person_to_poi += data_dict[person]["from_this_person_to_poi"]

    print "Do POIs talk to each other more frequently than non-POIs?"
    print "POI percent of TO messages from POI:", (float(poi_from_poi_to_this_person)/poi_to_messages)
    print "POI percent of FROM messages from POI:", (float(poi_from_this_person_to_poi)/poi_from_messages)
    print "NON-POI percent of TO messages from POI:", (float(nonpoi_from_poi_to_this_person)/nonpoi_to_messages)
    print "NON-POI percent of FROM messages from POI:", (float(nonpoi_from_this_person_to_poi)/nonpoi_from_messages)
