from flask import current_app


def query_index(index, query, page, per_page):
    search = current_app.elasticsearch.search(
        index=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
              'from': (page - 1) * per_page, 'size': per_page})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']


def find_all_with_work_id(work_id):
    res = current_app.elasticsearch.search(index="distscanner-result", scroll='5m', size='10000',
                                           body={"query": {"match": {'work_id': work_id}}})

    hit_count = res['hits']['total']['value']
    return res['hits']['hits'], hit_count


def find_host_with_open_ports(work_id):
    return []
