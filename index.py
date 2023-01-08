from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import mysql.connector
from mysql.connector import errorcode


try:
   conn = mysql.connector.connect(user="bau", password="roof1234.", host="aiwebsite.mysql.database.azure.com", port=3306, database="demodb")
   print("Connection established")
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with the user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
    def do_OPTIONS(self):
        self.send_response(200)
        self.set_cors_headers()
        self.end_headers()
    def do_PUT(self):
        if self.path == '/deleteDocument':
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            data = data.decode('utf-8')

            # JSON verisini Python dict'ine dönüştür
            data = json.loads(data)
            user_id = data['user_id']
            document_id = data['document_id']
            print(data)
            cursor = conn.cursor()

            # Silme işlemi
            cursor.execute("DELETE FROM texts WHERE id=%s AND user_id=%s", (document_id, user_id))
            conn.commit()
            cursor.close()
         

            # Silme işleminin başarılı olduğunu client'a bildir
            self.send_response(200)
            self.set_cors_headers()
            self.end_headers()
    def do_POST(self):
        if self.path == '/newDocument':
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            data = data.decode('utf-8')


            data = json.loads(data)

         
            document = data['document']


            summary =sample_extractive_summarization(document)
            keys = sample_extract_key_phrases(document) 
            print(summary)

            self.send_response(200)
            self.set_cors_headers()
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()


            response = {'summary': summary,
                        'keys':keys }
            data = json.dumps(response)
            self.wfile.write(data.encode('utf-8'))
        if self.path == "/newUser":
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            data = data.decode('utf-8')

            data = json.loads(data)
            cursor = conn.cursor()

            username = data["username"]
            password = data["password"]
            cursor.execute("CREATE TABLE IF NOT EXISTS users (username VARCHAR(255), password VARCHAR(255))")
            
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, PASSWORD(%s))", (username, password))


            conn.commit()
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=PASSWORD(%s)", (username, password))


            result = cursor.fetchone()


            if result:
                    print(result)
                    user_info = {
                        "username": result[0],
                        "user_id": result[2],
                    }
                    user_info = json.dumps(user_info)
                    self.send_response(200)
                    self.set_cors_headers()
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(user_info.encode("utf-8"))

        if self.path =="/user":
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            data = data.decode('utf-8')


            data = json.loads(data)

            cursor =conn.cursor(buffered=True)
        

            username = data["username"]
            password = data["password"]

            cursor.execute("SELECT * FROM users WHERE username=%s AND password=PASSWORD(%s)", (username, password))


            result = cursor.fetchone()

            if result:
                    print(result)
                    user_info = {
                        "username": result[0],
                        "user_id": result[2],
                    }
                    user_info = json.dumps(user_info)
                    print("we found you")
                    cursor.reset()
                    self.send_response(200)
                    self.set_cors_headers()
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(user_info.encode("utf-8"))

            else:
                print("HATA")
                error_message = {
                "error": "Kullanıcı bulunamadı"
                }
                error_message = json.dumps(error_message)
                self.send_response(400)
                self.set_cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(error_message.encode("utf-8"))


        if self.path =="/saveNewDocument":
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            data = data.decode('utf-8')
            data = json.loads(data)
            print(data)
            cursor = conn.cursor()

            cursor.execute("CREATE TABLE IF NOT EXISTS texts (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, text LONGTEXT )")

            text = data["document"]
            user_id = data["user_id"]
            print(text)
            cursor.execute("INSERT INTO texts (user_id, text) VALUES (%s, %s)", (user_id, text))
            text_id = cursor.lastrowid



            conn.commit()

            response = {
                "user_id": user_id,
                "text_id": text_id,

            }
            response = json.dumps(response)
            self.send_response(200)
            self.set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response.encode("utf-8"))

        if self.path == "/getDocuments":
            print("###################333")
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            data = data.decode('utf-8')
            data = json.loads(data)


            user_id = data["user_id"]
            print(user_id)       
            cursor = conn.cursor(buffered=True)

            cursor.execute("SELECT * FROM texts WHERE user_id=%s", (user_id,))
            texts = cursor.fetchall()


            print(texts)
            texts = [(text[0], text[2]) for text in texts]
            print(texts)

            response = {
            "user_id": user_id,
            "texts": texts
            }
            response = json.dumps(response)
            self.send_response(200)
            self.set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response.encode("utf-8"))



def sample_extractive_summarization(document):
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import (
        TextAnalyticsClient,
        ExtractSummaryAction
    )

    endpoint ="https://myai1.cognitiveservices.azure.com/"
    key = "463ff8058da5469eab2f41cb1e19bb46"

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )
    max_count=0;
    if len(document[0]) < 1200:
        max_count = 4
    elif len(document[0]) < 1400:
        max_count = 5
    elif len(document[0]) < 1600:
        max_count = 6
    elif len(document[0]) < 2000:
        max_count = 8
    elif len(document[0]) < 2200:
        max_count = 10
    else:
        max_count = 11

    poller = text_analytics_client.begin_analyze_actions(
        document,
        actions=[
            ExtractSummaryAction( max_sentence_count=max_count ),
        ],
    )

    document_results = poller.result()
    summary = []
    for extract_summary_results in document_results:
        for result in extract_summary_results:
            if result.kind == "ExtractiveSummarization":
                summary.extend([sentence.text for sentence in result.sentences])
            elif result.is_error is True:
                print("...Is an error with code '{}' and message '{}'".format(
                    result.code, result.message
                ))
    return summary


def sample_extract_key_phrases(articles):
    print(
        "In this sample, we want to find the articles that mention Microsoft to read."
    )
    articles_that_mention_microsoft = []
    # [START extract_key_phrases]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import TextAnalyticsClient

    endpoint ="https://myai1.cognitiveservices.azure.com/"
    key = "463ff8058da5469eab2f41cb1e19bb46"


    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    result = text_analytics_client.extract_key_phrases(articles)
    print("$$$$$$$$$$$$$$4")
    key_phrases = []
    for doc in result:
        if not doc.is_error:
            key_phrases.extend(doc.key_phrases)
    print("Key phrases:", key_phrases)
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$44")
    return key_phrases



if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

