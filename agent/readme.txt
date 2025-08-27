game && compressed agent
game: decompress agent and stored it in the fs and run it in background

AGENT:

```
module connection(host,port):
         while not server ping(host):
                  sleep(2)
                  server ping(host)

module authentication(host,port):
         return bool


mudule keylogger(keys):
         return dict(password_correct:bool)

module create_backdoor_as_root(file):
         return bool

module collector():
         return data

module sender(host, port)
         return bool

module checker(host, port):
         return bool

module bypass(bool)
         return bool, data
```




