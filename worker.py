import asyncio
import websockets
import json

async def process_message(websocket, message):
    # Função para processar a mensagem recebida do servidor
    print(f"Processando mensagem: {message}")
    data = json.loads(message)
    if data['channel'] == 'teste':
        print(data['body'])
    if data['channel'] == 'upload':
        body = data['body']
        task_id = body['id']
        file_name = body['file_name']
        file_data_base64 = body['file']
        
        # Decodificar e salvar o arquivo
        file_data = base64.b64decode(file_data_base64)
        dir_path = os.path.join('.', str(task_id))
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        print(f"Arquivo salvo em: {file_path}")
        
        # Enviar mensagem de confirmação
        confirmation_message = json.dumps({
            'channel': 'arquivo-enviado',
            'body': {'id': task_id}
        })
        await websocket.send(confirmation_message)

    # Adicione aqui o processamento que você deseja fazer com a mensagem


async def connect_to_server():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        mensagem = {"body": {"capacidade": 5}, "channel": "inscrever-servidor"}
        await websocket.send(json.dumps(mensagem))
        # response = await websocket.recv()
        # print(f"Resposta do servidor: {response}")
        while True:
            response = await websocket.recv()
            await process_message(websocket, response)
        # await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(connect_to_server())
