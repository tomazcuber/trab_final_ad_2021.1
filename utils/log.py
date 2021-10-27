import pandas as pd
from datetime import datetime

class Log:
    def __init__(self, title="default", print_on_console=False):
        self.title = title
        self.log = pd.DataFrame()
        self.print_on_console = print_on_console
    
    def write(self, level, content):
        self.log = self.log.append({
            'datetime': datetime.now(),
            'level':level,
            'content':content
        }, ignore_index=True)
        if self.print_on_console:
            print(datetime.now(), level, content)
    
    def info(self, content):
        self.write(1, content)

    def debug(self, content):
        self.write(0, content)
    
    def get(self, minimum_level=0):
        return self.log[self.log.level >= minimum_level]
    
    def save(self):
        self.log['content'].to_csv("logs/{title}_{datetime}.csv".format(
            title = self.title,
            datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        ), header=True, index=False)