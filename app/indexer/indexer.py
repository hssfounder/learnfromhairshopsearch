import app.config
from pyelasticsearch import ElasticSearch
from ..helpers import JSONEncoder
from .mappings import MAPPINGS
from ..core import es

# need mappings storage
es.json_encoder = JSONEncoder

def index_one(entity, id):
    """ Create a document in the HSS index of the type 'provider'
    :param entity: subset of model's attributes indexed as doc
    :param id: persisted id of entity
    :type id: int
    """
    # doc = JSONEncoder().encode(entity)
    doc_type = 'provider'
    index = 'hairshopsearch'
    resp = es.index(index, doc_type, entity, id=id)
    return resp

def index_many():
    # bulk_index()
    pass

def update_doc(entity):
    doc = {'location': entity.location }
    resp = es.update('hairshopsearch',
            'provider',
            id=entity.id,
            doc=doc)
    return resp

def create_index(doc_type):
    resp = es.create_index('hairshopsearch', settings=None)
    print resp

    resp1 = es.put_mapping('hairshopsearch',
            doc_type=doc_type,
            mapping=MAPPINGS['PROVIDER'])
    print resp1

def reset_index(doc_type):
    resp = es.delete_index('hairshopsearch')
    print resp

    create_index(doc_type)

