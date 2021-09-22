import requests


def is_elastic_running():
    try:
        res = requests.get("http://elasticsearch:9200/_cluster/health")
        if res.status_code == 200:
            if res.json()['number_of_nodes'] > 0:
                return True
        return False
    except Exception as e:
        # print(e)
        return False

