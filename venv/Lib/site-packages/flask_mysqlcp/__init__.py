import mysqlcp
class Pool:
    def __init__(self):
        self.config=mysqlcp.infos()
    def create(self):
        return mysqlcp.pool(self.config)
    def destroy(self,pool):
        pool.destroy()
