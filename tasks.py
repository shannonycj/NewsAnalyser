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
