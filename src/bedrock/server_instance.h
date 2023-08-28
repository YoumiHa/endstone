//
// Created by Vincent on 02/08/2023.
//

#ifndef ENDSTONE_SERVER_INSTANCE_H
#define ENDSTONE_SERVER_INSTANCE_H

class ServerInstance {
public:
    void startServerThread();
};

class ServerInstanceEventCoordinator {
public:
    void sendServerThreadStarted(ServerInstance *instance);
    void sendServerThreadStopped(ServerInstance *instance);
    void sendServerUpdateEnd(ServerInstance *instance);
};

#endif // ENDSTONE_SERVER_INSTANCE_H
