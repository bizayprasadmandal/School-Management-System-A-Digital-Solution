"""
Database router — directs read queries to the replica, writes to primary.
"""


class ReadReplicaRouter:
    READ_APPS = {
        "services.students", "services.academics",
        "services.attendance", "services.gradebook",
        "services.communication", "services.reporting",
    }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.READ_APPS:
            return "replica"
        return "default"

    def db_for_write(self, model, **hints):
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == "default"
