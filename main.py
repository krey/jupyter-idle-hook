import time
import notebook.notebookapp

from core import get_sessions, test_running, test_active
import config

def main():
    jupyter_servers = list(notebook.notebookapp.list_running_servers())
    assert(len(jupyter_servers) == 1)
    server = jupyter_servers[0]
    idle = False
    while True:
        sessions = get_sessions(server['url'], server['token'])
        #  pipe "or" is necessary here for eager execution
        idle = not (test_running(sessions, server['url']) | test_active(sessions, server['url'], config.timeout))
        if idle:
            break
        time.sleep(config.polling_interval.total_seconds())
    config.idle_hook()


if __name__ == '__main__':
    main()
