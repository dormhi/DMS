class I18n:
    def __init__(self):
        self.locales = {}
        self.default_locale = "en"
        self._load_locales()

    def _load_locales(self):
        # Basic translations for backend messages
        self.locales = {
            "en": {
                "job_started": "Job has been started.",
                "job_not_found": "Job not found."
            },
            "tr": {
                "job_started": "İş başlatıldı.",
                "job_not_found": "İş bulunamadı."
            }
        }

    def t(self, key: str, locale: str = None) -> str:
        loc = locale or self.default_locale
        return self.locales.get(loc, self.locales[self.default_locale]).get(key, key)

i18n = I18n()
