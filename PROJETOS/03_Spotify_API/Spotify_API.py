import time, base64, json, pandas as pd, pyxlsb
from requests import post, get

CLIENT_ID = '441b9d1721fb449593ca75a62a196408'
CLIENT_SECRET = '4fd5823aaf0b4da2858b75ffddaaaa2f'
CAMINHO = 'C:\\Users\\paulo\\OneDrive\\Videos\\Projeto Tocar\\Geração 4 - 2024\\Planilha\\'

def get_token():
    hora_ini = time.time()
    print('Autenticando token Spotify...')
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url,headers=headers, data = data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    print('Autenticado em {:.2f} segundos.'.format(time.time() - hora_ini))
    return token
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}
def search_for_artist(token, artist_name):
        hora_ini = time.time()
        print('Procurando dados do artista {}...'.format(BUSCA))
        url = "https://api.spotify.com/v1/search"
        headers = get_auth_header(token)
        query = f"q={artist_name}&type=artist&limit=10"
        query_url = url + "?" + query
        result = get(query_url, headers=headers)
        json_result = json.loads(result.content) ["artists"]["items"]
        if len(json_result) == 0:
            print("Não localizado...")
            return None
        print('Código de resposta API: {} em {:.2f} segundos.'.format(result, time.time() - hora_ini))
        return json_result
def get_songs_by_artist(token, artist_id):
    hora_ini = time.time()
    print('Procurando top 10 do artista {} no país BR...'.format(BUSCA))
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=BR"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    print('Código de resposta API: {} em {:.2f} segundos.'.format(result, time.time() - hora_ini))
    return json_result

# Inicio Execucao
tempo_ini = time.time()
token = get_token()
df_fonte = pd.read_excel(CAMINHO + 'ADM 2DAY New.xlsb', sheet_name="Brainstorm")
df_fonte

# Inicio Repeticao
for i in range(0,len(df_fonte.index)):
    BUSCA = df_fonte.iloc[i]['Banda']
    result = search_for_artist(token, str(BUSCA))
    df_artistas = pd.json_normalize(result)

    id = 10
    while id < 0 or id >= 9:
        if df_artistas.iloc[0]['name'].upper() == BUSCA.upper():
            artist_id = df_artistas.iloc[0]['id']
            id = 0
        else:
            print('Foram localizados mais de um registro pertinentes à sua busca.')
            print(df_artistas[['name','popularity','genres','followers.total']])
            id = int(input('Digite a escolha de 0 a 9?'))
            artist_id = df_artistas.iloc[id]['id']
            break


    # DataFrames iniciais
    songs = get_songs_by_artist(token,artist_id)
    df_songs = pd.json_normalize(songs)
    df_artista = df_artistas.iloc[id]
    df_artista

    # Padroniza cabeçalho das tracks
    keys_songs = {k: f'track_{k}' for k in df_songs.keys()[:len(df_songs.columns)]}
    df_songs_final = df_songs.rename(columns=keys_songs)

    # Padroniza cabeçalho do artista
    df_arts_final = pd.DataFrame(df_artista).T
    keys_arts = {i: f'artist_{col}' for i, col in enumerate(df_arts_final.columns)}
    df_arts_final.columns = keys_arts.values()

    # Concatena
    df_arts_replicado = pd.concat([df_arts_final]*len(df_songs_final), ignore_index=True)
    df_unificado = pd.concat([df_songs_final, df_arts_replicado], axis=1)
    if i == 0:
        df_final = df_unificado
    else:
        df_final = pd.concat([df_final,df_unificado])

# Exportação Final
df_final.to_csv(CAMINHO + '\SpotifyDataBase.csv')
print('Arquivos exportados com sucesso para:', CAMINHO)
print('Tempo total de execução foi de {:.2f} segundos'.format(time.time()-tempo_ini))