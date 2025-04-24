import time
#TODO: Use Redis or Hazelcast

class Cache:
    def __init__(self):
        self.cache = {}

    def set(self, key, value, ttl=None):
        if ttl is None:
            ttl = 3600
        
        expire_time = time.time() + ttl
        self.cache[key] = (value, expire_time)
        
    def get(self, key):
        if key not in self.cache:
            return None
        
        value, expire_time = self.cache[key]
        if time.time() > expire_time:
            del self.cache[key]
            return None
        
        return value
    
    def delete(self, key):
        if key in self.cache:
            del self.cache[key]
            return True
        return False
            
    def clear(self):
        self.cache.clear()
        
    def __len__(self):
        return len(self.cache)
    
c = Cache()
c.set("test", "value", 2)
assert c.get("test") == "value"
time.sleep(3)
assert c.get("test") is None

c.delete("test")
assert c.get("test") is None

print("All tests passed")