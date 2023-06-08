from sentence_transformers import SentenceTransformer, util

EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
KEYWORDS = "Medicine, Symptoms, Remedies, Health, Disease, Illness, Cure, Medication, Prescription, Diagnosis, Dying, Surgery, Mental Illness, Suicide, Injury, Hurting, Blood, Germs"
KEYWORDS_EMBEDDING = EMBEDDING_MODEL.encode(KEYWORDS)

def get_relevance(query):
    return util.cos_sim(EMBEDDING_MODEL.encode(query), KEYWORDS_EMBEDDING)[0][0]
