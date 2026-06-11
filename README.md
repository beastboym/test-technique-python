# Notes techniques

### Dépendances choisi

- `requirements.txt`: Liste les lib à installer. Un `pip install -r requirements.txt` installe tout d'un coup.

`fastapi`
`uvicorn[standard]`
`sqlalchemy[asyncio]`
`asyncpg`
`alembic`
`pydantic`
`pydantic-settings`
`python-dotenv`
`httpx`
`pytest`
`pytest-asyncio`
`anyio`

- `.env.example`: Stockent les variables de configuration sensibles (URL de la base, clé API)

#### core: add config and database
# test-technique-python
