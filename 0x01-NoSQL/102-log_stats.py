#!/usr/bin/env python3

from pymongo import MongoClient

if __name__ == "__main__":
    """Prints the log stats in nginx collection"""
    client = MongoClient('mongodb://localhost:27017')
    logs_collection = client.logs.nginx

    print(f"{logs_collection.estimated_document_count()} logs")

    methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
    print("Methods:")

    for method in methods:
        print("\tmethods {}: {}".format(method, logs_collection.count_documents({"method": method})))

    print("{} status check".format(logs_collection.count_documents({"method": "GET", "path": "/status"})))

    print("IPs:")
    sorted_ips = logs_collection.aggregate(
            [{"$group": {"_id": "$ip", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}, {"$limit": 10}])

    for ip in sorted_ips:
        print(f"\t{ip.get('_id')}: {ip.get('count')}")
