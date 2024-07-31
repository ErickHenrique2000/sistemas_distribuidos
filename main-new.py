import socket
import threading
import json
import uuid
import time

socketsServer = []
tasks = []

def calcServerValue(serverSocket):
    return (serverSocket['uso'] + serverSocket['arquivos']) / serverSocket['capacidade']

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

def my_periodic_task():
    while True:
        print("Executando tarefa periódica...")
        print(len(socketsServer))
        print(socketsServer)
        for socket in socketsServer:
            mensagem = {'channel': 'teste', "body": "ola"}
            socket['connection'].send(json.dumps(mensagem).encode())
        time.sleep(15)

def handle_connection(conn, addr):
    print(f"Conexão estabelecida com {addr}")
    connection = {'connection': conn, 'uso': 0, 'capacidade': 0}

    try:
        while True:
            data = conn.recv(1024 * 1024 * 10)
            if not data:
                print('cai no break')
                break
            message = data.decode()
            data = json.loads(message)
            print("Mensagem recebida como objeto:", data)
            if data['channel'] == 'inscrever-servidor':
                capacidade = data['body']['capacidade']
                connection['capacidade'] = capacidade
                connection['arquivos'] = 0
                socketsServer.append(connection)
            if data['channel'] == 'enviar-arquivo':
                body = data['body']
                taskSize = len(body['file'])
                findedSockets = findServer()
                if findedSockets:
                    findedSockets[0]['uso'] = findedSockets[0]['uso'] + taskSize
                    findedSockets[0]['arquivos'] = findedSockets[0]['arquivos'] + 1
                    findedSockets[1]['uso'] = findedSockets[1]['uso'] + taskSize
                    findedSockets[1]['arquivos'] = findedSockets[1]['arquivos'] + 1
                    myuuid = uuid.uuid4()
                    taskId = str(myuuid)
                    body['id'] = taskId
                    print('Enviando 1')
                    body['backup'] = False
                    findedSockets[0]['connection'].send(json.dumps({"channel": "upload", "body": body}).encode())
                    body['id'] = body['id']
                    body['backup'] = True
                    print('Enviando 2')
                    findedSockets[1]['connection'].send(json.dumps({"channel": "upload", "body": body}).encode())
                    tasks.append({'task': taskId, 'socket': conn, 'pendentes': 2, 'size': taskSize})
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
                        sender['uso'] -= objeto_encontrado['size']
                        break
                if objeto_encontrado['pendentes'] == 1:
                    print('removendo task')
                    tasks.remove(objeto_encontrado)
                    print('task removida')
                else:
                    print('Enviando 3')
                    objeto_encontrado['socket'].send(json.dumps({'channel': 'arquivo-enviado', 'body': ''}).encode())
                    objeto_encontrado['pendentes'] = 1
                    print('Enviado 3')
    except Exception as e:
        for server in socketsServer:
            if(server['connection'] == conn):
                socketsServer.remove(server)
        print(f"Conexão fechada: {e}")
    finally:
        conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 8765))
    server.listen(5)
    print("Servidor socket iniciado na porta 8765")

    threading.Thread(target=my_periodic_task, daemon=True).start()

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_connection, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
