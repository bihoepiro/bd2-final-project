# Variables globales para almacenar el índice y otros datos necesarios
def index_and_search(csv_file, block_size=1000):
    global global_index, global_idf

    df = pd.read_csv(csv_file)

    documents = {}
    for index, row in df.iterrows():
        row_text = ' '.join(row.astype(str).tolist())
        terms = nltk.word_tokenize(row_text)
        terms = [term.lower() for term in terms if term.isalnum()]
        documents[index] = terms

    document_frequency = df(documents)
    N = len(documents)
    idf = idf(document_frequency, N)

    spimi_invert_block(documents, block_size)

    block_count = len([name for name in os.listdir() if name.startswith('block_') and name.endswith('.json')])
    top_k_documentos = top_k_documentos(block_count)

    # Guardar el índice consolidado como archivos JSON
    with open('merged_index.json', 'w') as f:
        json.dump(top_k_documentos, f)

    # Guardar en variables globales
    global_index = 'merged_index.json'
    global_idf = idf

    return global_index, global_idf
