import os
from azure.storage.blob import BlobServiceClient
from pdfminer.high_level import extract_text, LAParams
from io import BytesIO
from security import connectionstring

def convert_pdf_to_text_from_blob(blob_client):
    laparams = LAParams(all_texts=True, detect_vertical=True)
    blob_data = blob_client.download_blob()
    # BytesIO ile blob verisini dosya nesnesine çevir
    with BytesIO(blob_data.readall()) as file:
        text = extract_text(file, laparams=laparams, codec='utf-8')
    return text

def save_texts_to_blob_container(source_container_name, target_container_name):
    connection_string = connectionstring
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    source_container_client = blob_service_client.get_container_client(source_container_name)
    target_container_client = blob_service_client.get_container_client(target_container_name)

    for blob in source_container_client.list_blobs():
        blob_client = source_container_client.get_blob_client(blob)
        if blob.name.endswith('.pdf'):
            # PDF dosyasını metne dönüştür
            text = convert_pdf_to_text_from_blob(blob_client)
            # Hedef container'a metni kaydet
            target_blob_client = target_container_client.get_blob_client(blob.name.replace('.pdf', '.txt'))
            target_blob_client.upload_blob(text, overwrite=True)

    print("CV files converted to text and saved to the target container!")

if __name__ == "__main__":
    save_texts_to_blob_container("cv-pdf-files", "cv-text-files")
