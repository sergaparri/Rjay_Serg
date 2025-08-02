from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Timer
from typing import Callable, Optional, List

class FolderMonitor:
    def __init__(self):
        self.observer = None
        self._running = False

    def start(self, path: str, event_handler: FileSystemEventHandler) -> bool:
        if self._running:
            return False
        self.observer = Observer()
        self.observer.schedule(event_handler, path, recursive=True)
        self.observer.start()
        self._running = True
        return True

    def stop(self) -> None:
        if self.observer and self._running:
            self.observer.stop()
            self.observer.join()
            self._running = False

    def is_running(self) -> bool:
        return self._running

class DebouncedEventHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable, debounce_sec: float = 1.0):
        self.callback = callback
        self.debounce_sec = debounce_sec
        self._timer: Optional[Timer] = None
        self._pending_events = set()

    def _trigger(self):
        self._timer = None
        if self._pending_events:
            self.callback(list(self._pending_events))
            self._pending_events.clear()

    def on_any_event(self, event):
        if not event.is_directory:
            if self._timer:
                self._timer.cancel()
            self._pending_events.add(event.src_path)
            self._timer = Timer(self.debounce_sec, self._trigger)
            self._timer.start() 