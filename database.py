import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import config

logger = logging.getLogger("discord_bot.database")

class Database:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None

    async def connect(self):
        """Inicializa a conexão assíncrona com o MongoDB Atlas."""
        if not config.MONGO_URI or "usuario:senha" in config.MONGO_URI:
            logger.warning("URI do MongoDB não configurada ou usando placeholder padrão no .env.")
            return False

        try:
            logger.info("Conectando ao MongoDB Atlas...")
            # Define tempo limite de seleção de servidor para evitar travamentos longos
            self.client = AsyncIOMotorClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
            
            # Sanitiza o nome do banco para evitar caracteres inválidos como '.' ou '/'
            raw_db_name = config.DB_NAME.strip().strip('"').strip("'")
            clean_db_name = raw_db_name if raw_db_name and '.' not in raw_db_name and '/' not in raw_db_name else "discord_bot_db"
            
            try:
                # Tenta pegar o banco padrão definido na própria URI (se houver), ou usa o nome sanitizado
                self.db = self.client.get_default_database(default=clean_db_name)
            except Exception:
                self.db = self.client[clean_db_name]
            
            # Testa a conexão fazendo um ping no banco
            await self.client.admin.command('ping')
            logger.info(f"✅ Conectado com sucesso ao MongoDB Atlas! Banco de Dados: '{self.db.name}'")
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ Falha ao conectar ao MongoDB: {e}")
            self.client = None
            self.db = None
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado na conexão do MongoDB: {e}")
            self.client = None
            self.db = None
            return False

    def close(self):
        """Fecha o cliente do MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Conexão com MongoDB encerrada.")

    def get_collection(self, collection_name: str):
        """Retorna uma coleção do banco de dados."""
        if self.db is None:
            return None
        return self.db[collection_name]

# Instância global da base de dados
db_manager = Database()
