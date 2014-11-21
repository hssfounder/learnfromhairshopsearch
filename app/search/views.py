from flask import Blueprint, render_template, current_app, flash, redirect, url_for, request
from .forms import SearchForm
from ..provider.models import Provider, Address
from ..core import es

import math

search = Blueprint('search', __name__, template_folder='templates',
    url_prefix='/search')

def searched_out_objects(ids):
    objects = []
    for _id in ids:
        p = Provider.query.get(_id)
        if p:
            objects.append(p)

    return objects

@search.route('/test', defaults={'page': 1})
@search.route('/test/page/<int:page>')
def test(page):
    # 10 per page
    paged_providers = Provider.query.paginate(page, 10)
    return render_template('search/serp.jade', providers=paged_providers)

@search.route('/', defaults={'page': 1}, methods=['POST', 'GET'])
@search.route('/page/<int:page>', methods=['POST', 'GET'])
def _search(page):
    # send the same query to the api on repeat with qstring
    # build links 
    # hit the engine with the query
    # get the result total
    # figure out how many pages from count
    # build set of links based on pages

    # 
    # count
    # es_from
    # size
    zip_code = request.args['zip_code']
    menu_type = request.args['menu_type']
    
    a = Address(zip_code=zip_code)

    # TODO lat_lon expects an address object. this is perhaps silly
    lat, lon = a.geocode()[0]

    current_app.logger.info('** Searching for {} in {} @ {} by {}'.format(
            menu_type,
            zip_code,
            str(lat), str(lon)
            ))

    query = {
        "query": {
            "filtered": {
                "query": {
                    "nested": {
                        "path": "menus",
                        "query": {
                            "bool": {
                                "must": {
                                    "term": { "menus.menu_type": menu_type }
                                },
                            }
                        }
                    }
                }, # /query
                "filter": {
                    "geo_distance": {
                        "distance": "100mi",
                        "location": {
                            "lat": lat,
                            "lon": lon
                        }
                    }
                } # /filter
            }
        },
    }

    # TODO hard coded index name
    per_page = 10
    inter = page * per_page
    ifrom = inter - 10
    results = es.search(query, index='hairshopsearch', doc_type='provider', size=per_page, es_from=ifrom)
    current_app.logger.info(results)

    ids = []
     
    if results['hits']['total'] > 0:
        # calc number of pages based on per_page config and result count
        pages = math.ceil(float(results['hits']['total'])/per_page)

        pagination_links = []

        for num in xrange(1, int(pages) + 1):
            link = '/search/page/{}?zip_code={}&menu_type={}'.format(num, zip_code, menu_type)
            pagination_links.append(dict(url=link, page_number=num))

        for result in results['hits']['hits']:
            ids.append(result['_id'])

        current_app.logger.info('hits: %s' % results['hits']['total'])
        current_app.logger.info(ids)

        providers = searched_out_objects(ids)

        return render_template('search/serp.jade', providers=providers, pagination_links=pagination_links)

    else:
        current_app.logger.info('No results found!')
        flash('No results found!', 'error')
        current_app.logger.info('2nd')
        return render_template('search/serp.jade')

    # TODO flash errors and get them rendered
    current_app.logger.info('last')
    return render_template('search/serp.jade')
