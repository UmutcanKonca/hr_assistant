from azure_openai import AzureOpenAI
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError
from security import key, endpoint, connectionstring
import json

# Azure OpenAI istemcisini oluştur
client = AzureOpenAI(
    api_key=key,  
    azure_endpoint=endpoint, 
    api_version="2023-05-15"
)

def generate_embeddings(text, model="text-embedding-ada-002"):
    return client.embeddings.create(input=[text], model=model).data[0].embedding

# Azure Blob Storage bağlantı dizesini ve container adını belirtin
connection_string = connectionstring
source_container_name = "cv-text-files"
destination_container_name = "embeddings"

# BlobServiceClient oluşturun
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Source ContainerClient oluşturun
source_container_client = blob_service_client.get_container_client(source_container_name)
if not source_container_client.exists():
    print(f"Kaynak konteyner '{source_container_name}' bulunamadı.")
    exit()

# Destination ContainerClient oluşturun veya varsa alın
destination_container_client = blob_service_client.get_container_client(destination_container_name)
if not destination_container_client.exists():
    destination_container_client.create_container()

# CV dosyalarını işle ve embeddinglerini oluştur
for blob in source_container_client.list_blobs():
    if blob.name.endswith(".txt"):
        # Blob'daki içeriği indir
        blob_client = source_container_client.get_blob_client(blob.name)
        blob_data = blob_client.download_blob()
        cv_text = blob_data.readall().decode("utf-8")
        
        # Text embedding oluştur
        embedding = generate_embeddings(cv_text, model="text-embedding-ada-002")

        # Embedding'i JSON formatına dönüştür
        embedding_json = json.dumps(embedding)

        # Blob adı belirtin
        destination_blob_name = f"{blob.name}.json"

        # Destination BlobClient oluşturun
        destination_blob_client = destination_container_client.get_blob_client(destination_blob_name)

        # Embedding'i Destination Blob Storage'e yükleyin
        destination_blob_client.upload_blob(embedding_json, overwrite=True)

print("İşlem tamamlandı: CV dosyalarının embeddingleri başarıyla aktarıldı.")