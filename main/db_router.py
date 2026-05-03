class DatabaseRouter:
    """
    A router to control all database operations on models for different databases.
    """

    def db_for_read(self, model, **hints):
        """
        Suggest the database to read from.
        """
        # Route RawatInap model to database2 (rs_rekom)
        if model._meta.db_table == 'rawat_inap':
            return 'database2'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Suggest the database to write to.
        """
        # Route RawatInap model to database2 (rs_rekom)
        if model._meta.db_table == 'rawat_inap':
            return 'database2'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if models are in the same database.
        """
        db_set = {'default', 'database2'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, database, app_label, model_name=None, **hints):
        """
        Ensure that the following apps' models are only created in the appropriate database.
        """
        if database == 'database2':
            # Route RawatInap model to database2 (rs_rekom)
            if model_name and model_name.lower() == 'rawatinap':
                return True
            return False
        elif database == 'default':
            # All other models go to default database (rs_pku)
            if model_name and model_name.lower() == 'rawatinap':
                return False
            return True
        return None
