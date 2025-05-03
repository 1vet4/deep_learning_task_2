from tools.vector_index import VectorIndex

if __name__ == '__main__':
    vector_index = VectorIndex()
    file_path = r"C:\Users\Iveta\Desktop\test.txt"

    vector_index.add_additional_document_to_vector_index(file_path)
