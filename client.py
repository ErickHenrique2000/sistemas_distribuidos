import base64
import socket
import json
import os
import sys

def find_file(name_part):
    print(os.listdir('.'))
    for file_name in os.listdir('.'):
        if name_part in file_name:
            return file_name
    return None


def connect_to_server():
    host = 'localhost'
    port = 8765

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        while True:
            file_select = input("""
DIGITE O NOME DO ARQUIVO OU -1 PARA SAIR
""")
            if(file_select != '-1'):
                file_path = find_file(file_select)
                if file_path:
                    image_file= open(file_path, "rb")
                    image_data_binary = image_file.read()
                    image_data = (base64.b64encode(image_data_binary)).decode('ascii')
                    fileName = file_path
                    print(image_data)
                    mensagem = {
                        "body": {
                            "file": image_data,
                            "file_name": fileName
                        },
                        "channel": "enviar-arquivo"
                    }
                    mensagem_json = json.dumps(mensagem)
                    s.send(json.dumps({"channel": "set-lenght", "body": {"req_size": ((sys.getsizeof(mensagem_json.encode()) + 1024))}}).encode())
                    data = s.recv(1024)
                    s.sendall(mensagem_json.encode())
                    
                    data = s.recv(1024)
                else:
                    print('Arquivo não encontrado, por favor tente novamente')
            else:
                break
            print('O seu arquvio foi salvo com sucesso')

        s.close()

        

if __name__ == "__main__":
    connect_to_server()