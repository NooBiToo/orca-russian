"""Белый список защищённого plugin*-хрома, разрешённого к переводу.

Точная копия TRANSLATABLE_PLUGIN_CHROME из Orca
(src/shared/plugins/plugin-translatable-chrome.ts). Общий источник для
build.py и chunk.py — при обновлении апстрима правится только здесь.
"""

PROTECTED_ROOT = "auto.components.settings."

# Точный белый список из Orca (src/shared/plugins/plugin-translatable-chrome.ts):
# защищённые plugin*-пути, которые языковому паку переводить РАЗРЕШЕНЫ.
TRANSLATABLE_PLUGIN_CHROME = {
    "auto.components.settings.PluginsSettingsSection.title",
    "auto.components.settings.PluginsSettingsSection.systemLabel",
    "auto.components.settings.PluginsSettingsSection.install",
    "auto.components.settings.PluginsSettingsSection.loading",
    "auto.components.settings.PluginsSettingsSection.empty",
    "auto.components.settings.PluginsSettingsSection.emptyTitle",
    "auto.components.settings.PluginsSettingsSection.noInstalledResults",
    "auto.components.settings.PluginsSettingsSection.noInstalledResultsTitle",
    "auto.components.settings.PluginMarketplaceBrowser.manageSources",
    "auto.components.settings.PluginMarketplaceBrowser.addSource",
    "auto.components.settings.PluginMarketplaceBrowser.refresh",
    "auto.components.settings.PluginMarketplaceBrowser.refreshing",
    "auto.components.settings.PluginMarketplaceBrowser.loading",
    "auto.components.settings.PluginMarketplaceBrowser.tryAgain",
    "auto.components.settings.PluginMarketplaceBrowser.clearSearch",
    "auto.components.settings.PluginMarketplaceBrowser.empty",
    "auto.components.settings.PluginMarketplaceBrowser.emptyTitle",
    "auto.components.settings.PluginMarketplaceBrowser.noInstalled",
    "auto.components.settings.PluginMarketplaceBrowser.noInstalledTitle",
    "auto.components.settings.PluginMarketplaceBrowser.noResults",
    "auto.components.settings.PluginMarketplaceBrowser.noResultsTitle",
    "auto.components.settings.PluginMarketplaceBrowser.noSourcesTitle",
    "auto.components.settings.PluginDevelopmentSection.title",
    "auto.components.settings.PluginDevelopmentSection.add",
    "auto.components.settings.PluginDevelopmentSection.remove",
    "auto.components.settings.PluginDevelopmentSection.pathLabel",
    "auto.components.settings.PluginDevelopmentSection.pathRequired",
    "auto.components.settings.PluginDevelopmentSection.placeholder",
    "auto.components.settings.plugins.search.title",
    "auto.components.settings.plugins.search.description",
    "auto.components.settings.plugins.search.install",
    "auto.components.settings.plugins.search.permissions",
    "auto.components.settings.plugins.search.logs",
    "auto.components.settings.plugins.search.development",
}


def protected_translation(path: str) -> bool:
    """Путь в защищённом пространстве и не в белом списке — переводить нельзя
    (replicates protectedTranslation: prefix auto.components.settings.plugin*)."""
    if not path.startswith(PROTECTED_ROOT):
        return False
    if path in TRANSLATABLE_PLUGIN_CHROME:
        return False
    return path[len(PROTECTED_ROOT):].split(".", 1)[0].lower().startswith("plugin")


def translatable_plugin_chrome_container(path: str) -> bool:
    """Защищённый контейнер проходим, если ниже него лежит разрешённый лист
    (replicates translatablePluginChromeContainer из Orca); каждое конечное
    значение всё равно проверяется по своему полному пути."""
    prefix = f"{path}."
    return any(w.startswith(prefix) for w in TRANSLATABLE_PLUGIN_CHROME)
