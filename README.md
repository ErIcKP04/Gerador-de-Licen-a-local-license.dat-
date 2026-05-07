# License Generator

Gerador offline de arquivos `license.dat` para o produto *******.

O programa possui uma interface gráfica simples para gerar uma licença a partir de:

- Nome do cliente
- HWID do cliente
- Chave privada `.pem`
- Pasta de saída

A licença gerada é salva como `license.dat`.

## Funcionalidades

- Interface gráfica com Tkinter
- Geração offline de licença
- Assinatura digital usando chave privada
- Produto fixo: *******
- Validade fixa: vitalícia
- Salvamento automático das últimas configurações locais

## Estrutura recomendada

```text
projeto/
├─ src/
│  └─ main.py
├─ config/
├─ keys/
├─ licenses/
├─ README.md
├─ requirements.txt
└─ .gitignore
```

## Requisitos

- Python 3.9 ou superior
- Dependências listadas em `requirements.txt`

O projeto usa a biblioteca `cryptography` para assinar a licença digitalmente.

## Instalação

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

Depois instale as dependências:

```bash
pip install -r requirements.txt
```

## Como executar

Se o arquivo principal estiver dentro da pasta `src`, rode:

```bash
python src/main.py
```

Se o arquivo principal estiver na raiz do projeto, rode:

```bash
python main.py
```

## Como usar

1. Abra o programa.
2. Selecione a chave privada `.pem`.
3. Escolha a pasta onde o arquivo `license.dat` será salvo.
4. Informe o nome do cliente.
5. Informe o HWID do cliente.
6. Clique em **Gerar license.dat**.

O arquivo será criado na pasta escolhida.

## Segurança

Não envie para o GitHub arquivos sensíveis ou gerados localmente, como:

```text
keys/
*.pem
*.key
license.dat
licenses/
app_settings.json
.env
```

A chave privada deve ficar somente no computador autorizado a gerar licenças.

## Arquivos ignorados pelo Git

Confirme que o `.gitignore` está configurado para ignorar:

```gitignore
.venv/
.vscode/
dist/
build/
keys/
licenses/
*.pem
*.key
license.dat
app_settings.json
.env
```

Antes de fazer commit, sempre confira:

```bash
git status
```

Não devem aparecer chaves privadas, licenças geradas, ambiente virtual ou arquivos de configuração local.

## Build

Caso use PyInstaller ou outra ferramenta para gerar executável, os arquivos da pasta `dist/` não precisam ser enviados ao GitHub.

O executável deve ser gerado localmente quando necessário.

## Observação

Este projeto é um gerador de licença local. Ele não valida a licença no aplicativo final; ele apenas cria o arquivo `license.dat`.

A validação da licença deve existir no software que irá consumir esse arquivo.
