import openai
from security import key, endpoint, connectionstring
from openai import AzureOpenAI
from azure.storage.blob import BlobServiceClient

class ChatHistory:
    def __init__(self):
        self.history = []

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})

    def get_history(self):
        return self.history

def load_system_prompt(filename):
    with open(filename, 'r') as file:
        return file.read().strip()
    
system_prompt = load_system_prompt("systemprompt.txt")

connection_string = connectionstring
container_name = "embeddings"

# Blob depolama servisine bağlanma
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)

# Blob depolama içindeki dosyaları listeleyin
blob_list = container_client.list_blobs()
for blob in blob_list:
    # Her bir blob için işlem yapın
    blob_client = container_client.get_blob_client(blob)
    # Blob'u indirin
    downloaded_blob = blob_client.download_blob()
    # İndirilen blob'un içeriğini alın
    content = downloaded_blob.readall()
    # Dosyayı GPT'ye veri olarak sağlayın
    chat_history = ChatHistory()
    client = AzureOpenAI(
        api_key=key,  
        azure_endpoint=endpoint, 
        api_version="2023-05-15"
    )

    def generate_answer(prompt):
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=chat_history.get_history() + [
                {"role": "system", 
                 "content": system_prompt},
                {"role": "user",
                 "content": prompt}],
            temperature=0.7,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=['END']
        )
        return (response.choices[0].message.content).strip()

    def print_chat_history():
        print("Önceki Konuşmalar:")
        for message in chat_history.get_history():
            role = message["role"]
            content = message["content"]
            print(f"{role}: {content}")

    def main():
        chat_history.add_message("system", system_prompt)
        chat_history.add_message("user", content.decode("utf-8"))
        while True:
            user_input = input("Sorunuzu girin (Çıkmak için 'exit' yazın): ")
            if user_input.lower() == "exit":
                print("Programdan çıkılıyor...")
                break
            elif user_input.lower() == "history":
                print_chat_history()
            else:
                chat_history.add_message("user", user_input)
                prompt = user_input + "\n"
                answer = generate_answer(prompt)
                chat_history.add_message("system", answer)
                print("Cevap:", answer)

    if __name__ == "__main__":
        main()
