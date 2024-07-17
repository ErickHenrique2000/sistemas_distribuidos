# import asyncio
# import websockets
# import json
# import uuid

# socketsServer = []
# tasks = []

# def calcServerValue(serverSocket):
#     return serverSocket['uso'] / serverSocket['capacidade']

# def findServer():
#     serverValues = map(calcServerValue, socketsServer)
#     serverValuesList = list(serverValues)
#     menor1_idx, menor2_idx = None, None
    
#     for i in range(len(serverValuesList)):
#         if menor1_idx is None or serverValuesList[i] < serverValuesList[menor1_idx]:
#             menor2_idx = menor1_idx
#             menor1_idx = i
#         elif menor2_idx is None or serverValuesList[i] < serverValuesList[menor2_idx]:
#             menor2_idx = i
    
#     return [socketsServer[menor1_idx], socketsServer[menor2_idx]]

# async def my_periodic_task():
#     while True:
#         print("Executando tarefa periódica...")
#         print(len(socketsServer))
#         for socket in socketsServer:
#             mensagem = {'channel': 'teste', "body": "ola"}
#             await socket['websocket'].send(json.dumps(mensagem))
#         # Coloque aqui o código que você deseja executar a cada X segundos
#         await asyncio.sleep(15)


# async def handle_connection(websocket, path):
#     print(f"Conexão estabelecida com {websocket.remote_address}")
#     try:
#         async for message in websocket:
#             data = json.loads(message)
#             print("Mensagem recebida como objeto:", data)
#             if data['channel'] == 'inscrever-servidor':
#                 capacidade = data['body']['capacidade']
#                 socketsServer.append({'capacidade': capacidade , 'websocket': websocket, 'uso': 0})
#             if data['channel'] == 'enviar-arquivo':
#                 body = data['body']
#                 taskSize = len(body['file'])
#                 findedSockets = findServer()
#                 if findedSockets:
#                     findedSockets[0]['uso'] = findedSockets[0]['uso'] + taskSize
#                     findedSockets[1]['uso'] = findedSockets[1]['uso'] + taskSize
#                     myuuid = uuid.uuid4()
#                     taskId = str(myuuid)
#                     body['id'] = taskId
#                     await findedSockets[0]['websocket'].send(json.dumps({"channel": "upload", "body": body}))
#                     body['id'] = body['id'] + '-B'
#                     await findedSockets[1]['websocket'].send(json.dumps({"channel": "upload", "body": body}))
#                     tasks.append({'task': taskId, 'socket': websocket, 'pendentes': 2, 'size': taskSize})
#             if data['channel'] == 'arquivo-enviado':
#                 body = data['body']
#                 taskId = body['id']
#                 objeto_encontrado = None
#                 for task in tasks:
#                     if task['task'] == taskId:
#                         objeto_encontrado = task
#                         break
#                 for sender in socketsServer:
#                     if sender['websocket'] == websocket:
#                         sender['uso'] -= task['size']
#                         break
#                 if task['pendentes'] == 1:
#                     tasks.remove(task)
#                 else:
#                     task['socket'].send(json.dumps({'channel': 'arquivo-enviado', 'body': ''}))
#     except websockets.ConnectionClosed as e:
#         socketsServer[:] = [s for s in socketsServer if s['websocket'] != websocket]
#         print(f"Conexão fechada: {e}")

# async def main():
#     asyncio.create_task(my_periodic_task())
#     async with websockets.serve(handle_connection, "localhost", 8765):
#         print("Servidor WebSocket iniciado na porta 8765")
#         await asyncio.Future()  # Para manter o servidor rodando

# if __name__ == "__main__":
#     asyncio.run(main())

import asyncio
import json
import uuid
from socket import *
import thread

socketsServer = []
tasks = []

def calcServerValue(serverSocket):
    return serverSocket['uso'] / serverSocket['capacidade']

def findServer():
    serverValues = map(calcServerValue, socketsServer)
    serverValuesList = list(serverValues)
    menor1_idx, menor2_idx = None, None
    
    for i in range(len(serverValuesList)):
        if menor1_idx is None or serverValuesList[i] < serverValuesList[menor1_idx]:
            menor2_idx = menor1_idx
            menor1_idx = i
        elif menor2_idx is None or serverValuesList[i] < serverValuesList[menor2_idx]:
            menor2_idx = i
    
    return [socketsServer[menor1_idx], socketsServer[menor2_idx]]

async def my_periodic_task():
    while True:
        print("Executando tarefa periódica...")
        print(len(socketsServer))
        for socket in socketsServer:
            mensagem = {'channel': 'teste', "body": "ola"}
            socket['socket'].send(json.dumps(mensagem).encode())
        await asyncio.sleep(15)

async def handle_connection(conn, addr):
    print('Dados recebidos')
    print(data)
    while True:
        data = conn.recv(1024)
        if not data: break
        await handle_connection(data, conn)
        try:
            message = data.decode()
            data = json.loads(message)
            print("Mensagem recebida como objeto:", data)
            if data['channel'] == 'inscrever-servidor':
                capacidade = data['body']['capacidade']
                # connection['capacidade'] = capacidade
                socketsServer.append({'capacidade': capacidade, 'socket': conn, 'uso': 0})
            if data['channel'] == 'enviar-arquivo':
                body = data['body']
                taskSize = len(body['file'])
                findedSockets = findServer()
                if findedSockets:
                    findedSockets[0]['uso'] = findedSockets[0]['uso'] + taskSize
                    findedSockets[1]['uso'] = findedSockets[1]['uso'] + taskSize
                    myuuid = uuid.uuid4()
                    taskId = str(myuuid)
                    body['id'] = taskId
                    findedSockets[0]['connection']['writer'].write(json.dumps({"channel": "upload", "body": body}).encode())
                    await findedSockets[0]['connection']['writer'].drain()
                    body['id'] = body['id'] + '-B'
                    findedSockets[1]['connection']['writer'].write(json.dumps({"channel": "upload", "body": body}).encode())
                    await findedSockets[1]['connection']['writer'].drain()
                    tasks.append({'task': taskId, 'socket': connection, 'pendentes': 2, 'size': taskSize})
            if data['channel'] == 'arquivo-enviado':
                body = data['body']
                taskId = body['id']
                objeto_encontrado = None
                for task in tasks:
                    if task['task'] == taskId:
                        objeto_encontrado = task
                        break
                for sender in socketsServer:
                    if sender == connection:
                        sender['uso'] -= task['size']
                        break
                if task['pendentes'] == 1:
                    tasks.remove(task)
                else:
                    connection['writer'].write(json.dumps({'channel': 'arquivo-enviado', 'body': ''}).encode())
                    await connection['writer'].drain()
        except Exception as e:
            print(f"Conexão fechada: {e}")
            # socketsServer[:] = [s for s in socketsServer if s != connection]
        # finally:
            # writer.close()
            # await writer.wait_closed()

async def main():
    asyncio.create_task(my_periodic_task())
    # server = await asyncio.start_server(handle_connection, "localhost", 8765)
    # print("Servidor socket iniciado na porta 8765")
    # async with server:
        # await server.serve_forever()
    HOST = ''                 # Symbolic name meaning all available interfaces
    PORT = 8765              # Arbitrary non-privileged port
    with socket(AF_INET, SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        # s.setblocking(False)
        while True:
            conn, addr = s.accept()
            print('Connected by', addr)
            # asyncio.create_task(handle_connection,(conn, socketsServer))
            thread.Thread(target=handle_connection,args=(conn, socketsServer), daemon=True).start()
        # with conn:
        #     while True:
        #         data = conn.recv(1024)
        #         if not data: break
        #         await handle_connection(data, conn)

if __name__ == "__main__":
    asyncio.run(main())

