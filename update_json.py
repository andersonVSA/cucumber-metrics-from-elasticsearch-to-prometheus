import json
import os
import datetime
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from pprint import pprint
import jsonpickle

#Project and jenkins build identifiers
project_name = os.environ["PROJECT_NAME"]
version = os.environ["VERSION"]
revision = os.environ["REVISION"]
build_number = os.environ["BUILD_NUMBER"]
build_tag = os.environ["BUILD_TAG"]
executor_name = os.environ["EXECUTOR_NUMBER"]
timestamp = datetime.datetime.now()

current_dir = os.getcwd()
filename = current_dir+'/'+project_name+'.json'
mapping = current_dir+'/utils/regressive_tests/mapping.json'
index_name = 'regression-tests-'+project_name

def setup_elasticsearch():
    if os.environ.get("ELASTICSEARCH_URL_WITH_PORT") == None:
        os.environ["ELASTICSEARCH_URL_WITH_PORT"]='http://127.0.0.1:9200'
    es = Elasticsearch( [ os.environ["ELASTICSEARCH_URL_WITH_PORT"] ], timeout=200 )
    return es

#This read the .json file, and return list of dict(array of jsons)
def read_json(filename):
    with open(filename, 'r+') as f:
        result_json = json.load(f)
        f.close()
        return result_json

def remove_file(filename):
    os.remove(filename)

def save_new_file(new_filename, content):
    with open(new_filename, 'w') as f:
        f.write(json.dumps(content, sort_keys=True))

#For each dict/json, append new identifiers data before index.
def add_identifiers_to_json(content):
    for myjson in content:
        myjson['project_name'] = project_name
        myjson['version'] = version
        myjson['revision'] = revision
        myjson['build_number'] = build_number
        myjson['build_tag'] = build_tag
        myjson['executor_name'] = executor_name
        myjson['finished_at'] = timestamp
    return content

#Do a bulk index, each test/json will be a document, and the project will be the index_name
def index_content(content):
    es = setup_elasticsearch()

    #Bulk API Need do a single API call: https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html
    for myjson in content:
        actions = [
            {
              "_index": index_name,
              "_type": 'doc',
              "_source": myjson
            }
        ]
        helpers.bulk(es, actions)

def update_index_mapping(mapping):
    #After indexing, we need to UPDATE mapping, Enabling fielddata in fields that es_prometheus_exporter do aggregations queries
    es = setup_elasticsearch()
    with open(mapping) as f:
        mapping_json = json.load(f)
    
    es.indices.put_mapping(
        index = index_name,
        doc_type = 'doc',
        body = mapping_json
    )
   

if __name__ == '__main__':
    try:
        result_json = read_json(filename)
        modified_json = add_identifiers_to_json(result_json)
        index_content(modified_json)
        update_index_mapping(mapping)
    except Exception as e:
        print("Error sending regression test output to elasticsearch")
        print("An exception occurred [" + jsonpickle.encode(e) + " ]")
        pass