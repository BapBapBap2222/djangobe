from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        import accounts.signals
        from utils.supabase_storage import configure_supabase_model_storages

        configure_supabase_model_storages()
