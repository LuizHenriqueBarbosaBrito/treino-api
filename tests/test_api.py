from .conftest import novo_exercicio


# ---------- Autenticação ----------
def test_registro_e_login(client):
    r = client.post("/auth/register", json={"username": "ana_01", "password": "senha12345"})
    assert r.status_code == 201
    assert "senha" not in r.text  # nunca expõe hash/senha
    r = client.post("/auth/login", data={"username": "ana_01", "password": "senha12345"})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"


def test_registro_duplicado_409(client):
    dados = {"username": "ana_01", "password": "senha12345"}
    client.post("/auth/register", json=dados)
    assert client.post("/auth/register", json=dados).status_code == 409


def test_login_senha_errada_401(client):
    client.post("/auth/register", json={"username": "ana_01", "password": "senha12345"})
    r = client.post("/auth/login", data={"username": "ana_01", "password": "errada123"})
    assert r.status_code == 401


def test_endpoint_protegido_sem_token_401(client):
    assert client.get("/auth/me").status_code == 401


def test_endpoint_protegido_token_invalido_401(client):
    r = client.get("/auth/me", headers={"Authorization": "Bearer lixo"})
    assert r.status_code == 401


def test_endpoint_protegido_com_token_200(client, auth):
    r = client.get("/auth/me", headers=auth)
    assert r.status_code == 200
    assert r.json()["username"] == "luiz"


def test_escrita_exige_token(client, grupo):
    assert client.post("/exercicios", json=novo_exercicio(grupo["id"])).status_code == 401
    assert client.patch("/exercicios/1", json={"nivel": "avancado"}).status_code == 401
    assert client.delete("/exercicios/1").status_code == 401


# ---------- CRUD de exercícios ----------
def test_criar_exercicio_201(client, auth, grupo):
    r = client.post("/exercicios", json=novo_exercicio(grupo["id"]), headers=auth)
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["nome"] == "Supino reto"
    assert corpo["nivel"] == "iniciante"  # valor padrão
    assert corpo["grupo"]["nome"] == "Peitoral"


def test_criar_exercicio_invalido_400(client, auth, grupo):
    r = client.post(
        "/exercicios",
        json=novo_exercicio(grupo["id"], series_padrao=99, nivel="deus"),
        headers=auth,
    )
    assert r.status_code == 400
    campos = {d["campo"] for d in r.json()["detalhes"]}
    assert {"series_padrao", "nivel"} <= campos


def test_criar_exercicio_grupo_inexistente_400(client, auth):
    r = client.post("/exercicios", json=novo_exercicio(999), headers=auth)
    assert r.status_code == 400


def test_criar_exercicio_nome_duplicado_409(client, auth, grupo):
    client.post("/exercicios", json=novo_exercicio(grupo["id"]), headers=auth)
    r = client.post("/exercicios", json=novo_exercicio(grupo["id"]), headers=auth)
    assert r.status_code == 409


def test_listar_e_filtrar(client, auth, grupo):
    costas = client.post("/grupos", json={"nome": "Costas"}, headers=auth).json()
    client.post("/exercicios", json=novo_exercicio(grupo["id"]), headers=auth)
    client.post(
        "/exercicios",
        json={"nome": "Remada curvada", "grupo_muscular_id": costas["id"], "nivel": "avancado"},
        headers=auth,
    )
    assert len(client.get("/exercicios").json()) == 2
    assert len(client.get("/exercicios", params={"grupo_id": costas["id"]}).json()) == 1
    assert client.get("/exercicios", params={"nivel": "avancado"}).json()[0]["nome"] == "Remada curvada"
    assert len(client.get("/exercicios", params={"busca": "supino"}).json()) == 1
    assert client.get("/exercicios", params={"nivel": "invalido"}).status_code == 400
    assert len(client.get("/exercicios", params={"limit": 1}).json()) == 1


def test_consultar_por_id_e_404(client, auth, grupo):
    criado = client.post("/exercicios", json=novo_exercicio(grupo["id"]), headers=auth).json()
    assert client.get(f"/exercicios/{criado['id']}").status_code == 200
    r = client.get("/exercicios/999")
    assert r.status_code == 404
    assert "erro" in r.json()


def test_patch_atualiza_parcialmente(client, auth, grupo):
    criado = client.post("/exercicios", json=novo_exercicio(grupo["id"]), headers=auth).json()
    r = client.patch(f"/exercicios/{criado['id']}", json={"nivel": "avancado"}, headers=auth)
    assert r.status_code == 200
    assert r.json()["nivel"] == "avancado"
    assert r.json()["nome"] == "Supino reto"  # não enviado -> não muda


def test_patch_erros(client, auth, grupo):
    criado = client.post("/exercicios", json=novo_exercicio(grupo["id"]), headers=auth).json()
    url = f"/exercicios/{criado['id']}"
    assert client.patch(url, json={}, headers=auth).status_code == 400
    assert client.patch(url, json={"nome": None}, headers=auth).status_code == 400
    assert client.patch(url, json={"series_padrao": 0}, headers=auth).status_code == 400
    assert client.patch("/exercicios/999", json={"nivel": "avancado"}, headers=auth).status_code == 404


def test_delete_204_depois_404(client, auth, grupo):
    criado = client.post("/exercicios", json=novo_exercicio(grupo["id"]), headers=auth).json()
    url = f"/exercicios/{criado['id']}"
    r = client.delete(url, headers=auth)
    assert r.status_code == 204
    assert r.content == b""
    assert client.get(url).status_code == 404
    assert client.delete(url, headers=auth).status_code == 404


# ---------- Grupos ----------
def test_grupo_com_exercicios_nao_pode_ser_excluido(client, auth, grupo):
    client.post("/exercicios", json=novo_exercicio(grupo["id"]), headers=auth)
    assert client.delete(f"/grupos/{grupo['id']}", headers=auth).status_code == 409


def test_grupo_vazio_pode_ser_excluido(client, auth, grupo):
    assert client.delete(f"/grupos/{grupo['id']}", headers=auth).status_code == 204


# ---------- CORS ----------
def test_cors_origem_permitida(client):
    r = client.options(
        "/exercicios",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"},
    )
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_origem_nao_permitida(client):
    r = client.options(
        "/exercicios",
        headers={"Origin": "http://site-malicioso.com", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in r.headers
