from flask import current_app
from lib.logger import logger
from elasticsearch import Elasticsearch


def query_index(index, query, page, per_page):
    search = current_app.elasticsearch.search(
        index=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
              'from': (page - 1) * per_page, 'size': per_page})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']


def find_all_with_work_id(scan_id):
    try:
        res = current_app.elasticsearch.search(index="distscanner-result", scroll='5m', size='10000',
                                               body={"query": {"filter": {'scan_id': scan_id}}})

        hit_count = res['hits']['total']['value']
        return res['hits']['hits'], hit_count
    except Exception as e:
        logger.error('Exception in find_all_with_work_id', e)
        return None, None


def find_scan_details_on_elastics(scan_id):
    res = current_app.elasticsearch.search(index="distscanner-result",
                         body={
                             "query": {
                                 "bool": {
                                     "must": [
                                         {"match": {"scan_id": scan_id}},
                                         {"exists": {"field": "open_ports"}}
                                     ]
                                 },
                             },
                             "size": 0,
                             "aggs": {
                                 "top_ports": {
                                     "terms": {
                                         "field": "open_ports.port",
                                         "order": {"_count": "desc"},
                                         "size": 10,
                                     },
                                 }
                             }
                         })

    top_ports = res['aggregations']['top_ports']['buckets']

    host_up = current_app.elasticsearch.count(index="distscanner-result",
                            body={"query": {"bool": {"must": [{"match": {"scan_id": scan_id}},
                                                              {"exists": {"field": "open_ports"}}]}}})

    host_total = current_app.elasticsearch.count(index="distscanner-result",
                               body={"query": {"match": {'scan_id': scan_id}}})

    return {'top_ports': top_ports, 'host_count': {'up': host_up['count'], 'total': host_total['count']}}


# scan_id = '9666b652-d082-4d72-b26b-2c98fd696499'
# find_scan_details_on_elastics(scan_id)
