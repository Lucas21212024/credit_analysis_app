from models import Base, engine

# Criar todas as tabelas no banco de dados
Base.metadata.create_all(engine)
print("Migrações realizadas com sucesso.")
