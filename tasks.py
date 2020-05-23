import invoke
import json


@invoke.task
def crawl(c):
    entity = input('Enter entity of interest: ')
    print(f'Received entity name: {entity}.')
    with open('./config.json', 'r') as f:
        __config = json.load(f)
    __config['reuters_search_entity'] = entity
    with open('./config.json', 'w') as f:
        json.dump(__config, f)
    print('\tStart Crawling...')
    c.run('scrapy crawl reuters')
    print('Task complete.')


@invoke.task
def refresh_tfidf(c, topk=5):
    from data_pipeline import query_interface as dqi
    dqi.get_tfidf(topk)


@invoke.task
def refresh_lda(c, num_topics=10, chunksize=2000, iterations=400, passes=20):
    from data_pipeline import query_interface as dqi
    dqi.get_lda_topics(num_topics, chunksize, iterations, passes)


@invoke.task
def clean(c):
    c.run("rm ./data/corpora/*.txt")
    c.run("rm ./data/*.db")
