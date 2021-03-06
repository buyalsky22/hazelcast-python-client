import logging
import uuid

from hazelcast.util import create_git_info

LIFECYCLE_STATE_STARTING = "STARTING"
LIFECYCLE_STATE_CONNECTED = "CONNECTED"
LIFECYCLE_STATE_DISCONNECTED = "DISCONNECTED"
LIFECYCLE_STATE_SHUTTING_DOWN = "SHUTTING_DOWN"
LIFECYCLE_STATE_SHUTDOWN = "SHUTDOWN"


class LifecycleService(object):
    """
    LifecycleService allows you to shutdown, terminate, and listen to LifecycleEvent's on HazelcastInstances.
    """
    logger = logging.getLogger("HazelcastClient.LifecycleService")
    state = None

    def __init__(self, config, logger_extras=None):
        self._listeners = {}
        self._logger_extras = logger_extras

        for listener in config.lifecycle_listeners:
            self.add_listener(listener)

        self._git_info = create_git_info()
        self.is_live = True
        self.fire_lifecycle_event(LIFECYCLE_STATE_STARTING)

    def add_listener(self, on_lifecycle_change):
        """
        Add a listener object to listen for lifecycle events.

        :param on_lifecycle_change: (Function), function to be called when LifeCycle state is changed.
        :return: (str), id of the listener.
        """
        id = str(uuid.uuid4())
        self._listeners[id] = on_lifecycle_change
        return id

    def remove_listener(self, registration_id):
        """
        Removes a lifecycle listener.

        :param registration_id: (str), the id of the listener to be removed.
        :return: (bool), ``true`` if the listener is removed successfully, ``false`` otherwise.
        """
        try:
            self._listeners.pop(registration_id)
            return True
        except KeyError:
            return False

    def fire_lifecycle_event(self, new_state):
        """
        Called when instance's state changes.

        :param new_state: (Lifecycle State), the new state of the instance.
        """
        if new_state == LIFECYCLE_STATE_SHUTTING_DOWN:
            self.is_live = False

        self.state = new_state
        self.logger.info(self._git_info + "HazelcastClient is %s", new_state, extra=self._logger_extras)
        for listener in list(self._listeners.values()):
            try:
                listener(new_state)
            except:
                self.logger.exception("Exception in lifecycle listener", extra=self._logger_extras)
