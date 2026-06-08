# FinTrack — Gerenciamento Financeiro Pessoal

Sistema web para controle de finanças pessoais, desenvolvido com Python, Flask e SQLite.

## Tecnologias

- **Backend:** Python 3 + Flask
- **Banco de dados:** SQLite (via Flask-SQLAlchemy)
- **Autenticação:** Flask-Login
- **Frontend:** HTML5, CSS3, JavaScript
- **Gráficos:** Chart.js
- **Ícones:** Lucide Icons

## Funcionalidades

- Cadastro e login de usuários (senha criptografada)
- Cadastro de receitas e despesas com categorias
- Dashboard com gráficos (evolução mensal + pizza por categoria)
- Listagem de transações com filtros (tipo, categoria, mês, ano, busca)
- Gerenciamento de categorias personalizadas
- Interface responsiva (desktop e mobile)

## Como rodar

### 1. Pré-requisitos

- Python 3.10 ou superior instalado
- pip (vem com o Python)

### 2. Clonar / extrair o projeto

```
cd fintrack
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Rodar o servidor

```bash
python app.py
```

### 5. Acessar no navegador

```
http://localhost:5000
```

## Estrutura de pastas

```
fintrack/
├── app.py              ← ponto de entrada
├── requirements.txt
├── fintrack.db         ← criado automaticamente
├── models/
│   └── models.py       ← User, Category, Transaction
├── routes/
│   ├── auth.py         ← login, registro, logout
│   └── main.py         ← dashboard, transações, categorias
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── transactions.html
│   ├── transaction_form.html
│   └── categories.html
└── static/
    └── css/
        └── style.css
```

## Conta de demonstração

Ao criar uma conta nova, 12 categorias padrão são criadas automaticamente
(Salário, Alimentação, Transporte, etc.).

---

> "Educação financeira começa com organização, e tecnologia pode tornar isso mais simples para todos."
