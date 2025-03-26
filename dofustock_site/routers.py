class DofusItemRouter:
    """
    A router to control all database operations on models in the
    dofustock_site application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read dofus items models from dofus_items.sqlite3
        """
        if model.__name__ in ['Item', 'Effect', 'Recipe']:
            return 'dofus_items'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write only website-specific models to default database
        """
        if model.__name__ not in ['Item', 'Effect', 'Recipe']:
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model from default database is involved
        """
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure only default database gets migrations
        """
        return db == 'default'