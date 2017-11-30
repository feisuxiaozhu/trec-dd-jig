ES_HOST = 'localhost'
ES_PORT = 9200
BULK_MAX_OPS_CNT = 5000

DIMENSION = 75

INDEX_NAME = 'dd'
INDEX_SETTINGS_FP = "properties/default_dd.json"

DATA_DIR = 'real_doc/nyt_corpus/nyt_trectext'
QUERIES_FP = 'real_run/truth_data_nyt_2017_v2.3.xml'

BASE_RESULT_FP='base_search_doc.txt'
TRAINED_RESULT_FP='trained_search_doc.txt'
JIG_FP = 'jig/jig.py'
CUBE_TEST_FP ='scorer/cubetest.py'
PARAM_FP = 'real_run/params'
HIEARCHY_MAP_FP = 'lda/hiearchy_map.txt'

JIG_LOG_FP = 'initialization.txt'
TOPIC_FP='topics.txt'

SUBTOPIC_FP = '/Users/shuchenzhu/Desktop/es_dd/trec-dd-jig/subtopics'

DICTIONARY_PATH = "lda/models/dictionary.dict"
LDA_MODEL_PATH = "lda/models/lda_model_50_topics.loggingda"
SUBTOPICS_PATH = 'subtopics'