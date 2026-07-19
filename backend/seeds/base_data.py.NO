class BaseDataProvider:
    name = "base_data"
    order = 10

    def run(self, session):
        # seed idempotente dei dati base applicativi
        # (logica presa/modernizzata da add_new_tables.py)
        pass


provider = BaseDataProvider()