# import asyncio
# import websockets
# import json
# import base64
# import os

# async def process_message(websocket, message):
#     print(f"Processando mensagem: {message}")
#     data = json.loads(message)
#     if data['channel'] == 'teste':
#         print(data['body'])
#     if data['channel'] == 'upload':
#         body = data['body']
#         task_id = body['id']
#         file_name = body['file_name']
#         file_data_base64 = body['file']
        
#         file_data = base64.b64decode(file_data_base64)
#         dir_path = os.path.join('.', str(task_id))
#         os.makedirs(dir_path, exist_ok=True)
#         file_path = os.path.join(dir_path, file_name)
#         with open(file_path, 'wb') as f:
#             f.write(file_data)
        
#         print(f"Arquivo salvo em: {file_path}")
        
#         confirmation_message = json.dumps({
#             'channel': 'arquivo-enviado',
#             'body': {'id': task_id}
#         })
#         await websocket.send(confirmation_message)

# async def connect_to_server():
#     uri = "ws://localhost:8765"
#     async with websockets.connect(uri) as websocket:
#         mensagem = {"body": {"capacidade": 5}, "channel": "inscrever-servidor"}
#         await websocket.send(json.dumps(mensagem))
#         while True:
#             response = await websocket.recv()
#             await process_message(websocket, response)

# if __name__ == "__main__":
#     asyncio.run(connect_to_server())
import asyncio
import json
import base64
import os
import socket

async def process_message(client_socket, message):
    if not message:
        return
    print(f"Processando mensagem: {message}")
    data = json.loads(message)
    if data['channel'] == 'teste':
        print(data['body'])
    if data['channel'] == 'upload':
        body = data['body']
        task_id = body['id']
        file_name = body['file_name']
        file_data_base64 = body['file']
        
        file_data = base64.b64decode(file_data_base64)
        dir_path = os.path.join('.', str(task_id + ('-B' if body['backup'] else '')))
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        print(f"Arquivo salvo em: {file_path}")
        
        confirmation_message = json.dumps({
            'channel': 'arquivo-enviado',
            'body': {'id': task_id}
        })
        client_socket.send(confirmation_message.encode('utf-8'))

async def connect_to_server():
    host = 'localhost'
    port = 8765
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    mensagem = {"body": {"capacidade": 5}, "channel": "inscrever-servidor"}
    client_socket.send(json.dumps(mensagem).encode('utf-8'))
    
    while True:
        response = client_socket.recv(1024 * 1024 * 10).decode('utf-8')
        if not response:
            client_socket.close()
        await process_message(client_socket, response)

if __name__ == "__main__":
    asyncio.run(connect_to_server())
