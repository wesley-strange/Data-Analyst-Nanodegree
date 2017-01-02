#!/usr/bin/env python

# pipeline to identify top user
top_users_pipe = [
        {"$group": {"_id": "$created.user", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}]
        
# top 10 amenities
top_amenities_pipe = [
        {"$match": {"amenity": {"$exists": 1}}},
        {"$group": {"_id": "$amenity", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}]
        
# top religions
top_religions_pipe = [
        {"$match": {"amenity": {"$exists":1}, "amenity": "place_of_worship"}},
        {"$group": {"_id": "$religion", "count": {"$sum": 1}}},
        {"$sort": {"count":-1}},
        {"$limit": 10}]

# top cuisines
top_cuisines_pipe = [
        {"$match": {"amenity": {"$exists":1}, "amenity": "restaurant"}},
        {"$group": {"_id": "$cuisine", "count": {"$sum": 1}}},
        {"$sort": {"count":-1}},
        {"$limit": 10}] 

def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db
    
def counts(db):
    count = db.chicagoIL.find().count()
    nodes = db.chicagoIL.find({"type":"node"}).count()
    ways = db.chicagoIL.find({"type":"way"}).count()
    return count, nodes, ways

def aggregate(db, pipeline):
    result = db.chicagoIL.aggregate(pipeline)
    return result

if __name__ == '__main__':
    db = get_db('project3')
    #db.drop_collection('chicago')
    count, nodes, ways = counts(db)
    top_users = aggregate(db, top_users_pipe)
    top_amenities = aggregate(db, top_amenities_pipe)
    top_religions = aggregate(db, top_religions_pipe)
    top_cuisines = aggregate(db, top_cuisines_pipe)
    print "Total Nodes and Ways:\n", count
    print "Total Nodes:\n", nodes
    print "Total Ways:\n", ways
    print "Top Users:\n", (list(top_users))
    print "Top Amenities:\n", (list(top_amenities))
    print "Top Religions:\n", (list(top_religions))
    print "Top Cuisines:\n", (list(top_cuisines))