# Holds the tags position and lock mechanism to prevent race condition
import threading

lock =threading.Lock()
positions = {}