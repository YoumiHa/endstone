//
// Created by Vincent on 22/08/2023.
//

#ifndef ENDSTONE_LOGGER_FACTORY_H
#define ENDSTONE_LOGGER_FACTORY_H

#include "endstone/logger.h"

class AbstractLogger : public Logger {
public:
    explicit AbstractLogger(std::string name);

    void setLevel(LogLevel level) override;
    bool isEnabledFor(LogLevel level) const noexcept override;
    std::string_view getName() const override;

    void log(LogLevel level, const std::string &message) const override = 0;

private:
    LogLevel level_;
    std::string name_;
};

class BedrockLoggerAdapter : public AbstractLogger {

public:
    using AbstractLogger::AbstractLogger;

    void log(LogLevel level, const std::string &message) const override;
};

class LoggerFactory {
public:
    static std::shared_ptr<Logger> getLogger(const std::string &name);
};

#endif // ENDSTONE_LOGGER_FACTORY_H