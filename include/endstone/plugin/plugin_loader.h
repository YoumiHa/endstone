//
// Created by Vincent on 17/08/2023.
//

#ifndef ENDSTONE_PLUGIN_LOADER_H
#define ENDSTONE_PLUGIN_LOADER_H

#include "plugin.h"

class PluginLoader : public std::enable_shared_from_this<PluginLoader> {
public:
    virtual ~PluginLoader() = default;
    virtual std::unique_ptr<Plugin> loadPlugin(const std::string &file) = 0;
    virtual std::vector<std::string> getPluginFileFilters() const noexcept = 0;
    virtual void enablePlugin(Plugin &plugin) const noexcept
    {
        if (!plugin.isEnabled()) {
            plugin.getLogger()->info("Enabling {}", plugin.getDescription().getFullName());
            plugin.setEnabled(true);
        }
    }
    virtual void disablePlugin(Plugin &plugin) const noexcept
    {
        if (plugin.isEnabled()) {
            plugin.getLogger()->info("Disabling {}", plugin.getDescription().getFullName());
            plugin.setEnabled(false);
        }
    }

protected:
    virtual void initPlugin(Plugin &plugin, const std::shared_ptr<Logger> &logger) noexcept
    {
        plugin.loader_ = shared_from_this();
        plugin.logger_ = logger;
    }
};

#endif // ENDSTONE_PLUGIN_LOADER_H
