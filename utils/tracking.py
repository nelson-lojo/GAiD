import os
from datetime import timedelta
from datetime import datetime
import sqlite3
from sqlite3.dbapi2 import OperationalError
from typing import Any, Callable
from utils.result import Result

class Tracker:
    
    _db = sqlite3.connect('GAiD-dev.sqlite3')
        #DBWrapper(f"GAiD-{os.getenv('GAID_ENV')}.db")
    init = False
    limits = {}

    @classmethod
    def initialize(cls):
        # make the table
        with cls._db:
            cur = cls._db.cursor()
            cur.execute("""
                CREATE TABLE queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    label TEXT,
                    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        pass

    @classmethod
    def limit(cls, **kwargs) -> Callable:
        """
        Returns a decorator that limits the execution of <Query>._request methods 
            to `count: int` times per `age: timedelta` under `label: str`
        """

        if not cls.init:
            try:
                cls.initialize()
            except OperationalError:
                cls.init = True

        def limitUse(method: Callable[[Any], Result]) -> Callable[[Any], Result]:
            """
            Decorator made to limit the execution of <Query>._request methods
            """

            # update the label's `count` and `age` if provided
            #   and if there is no already set values, assume 1 execution per day
            label = kwargs.get('label', method.__name__)
            cls.limits.update({
                label: {
                    'count' : 
                        kwargs.get('count', False) or \
                            cls.limits.get(
                                label, 
                                { 'count' : 1 }
                            )['count'],
                    'age' : 
                        kwargs.get('age', False) or \
                            cls.limits.get(
                                label, 
                                { 'age' : timedelta(days=1) }
                            )['age'] 
                }
            })

            def control(*a, **kw):

                maxAge = cls.limits[label]['age']
                count = cls.limits[label]['count']
                runs = cls.getCountedRuns(label, maxAge)

                if runs >= count:
                    raise Exception(f"Maximum execution count {count} reached within {maxAge}")
                
                cls.addRun(label, a, kw)
                
                result: Result =  method(*a, **kw)

                for page in result.pages:
                    page.title = page.title.format(count=f"{runs + 1}/{count}")
                
                return result
            

            return control
    

        return limitUse

    @classmethod
    def getCountedRuns(cls, name: str, age: timedelta) -> int:
        # raise NotImplementedError
        with cls._db:
            cur = cls._db.cursor()
            
            count = cur.execute(
                "SELECT COUNT(time) FROM queries " + \
                    "WHERE label = :name AND time > :oldest",
                {
                    'name' : name,
                    'oldest' : datetime.now() - age
                }
            ).fetchall()[0][0]

        return count
        

    @classmethod
    def addRun(cls, label, arguments, kwarguments) -> None:
        with cls._db:
            cur = cls._db.cursor()
            cur.execute(
                "INSERT INTO queries (label, time) VALUES (:name, :time)",#, :args, :kwargs)",
                {
                    'name' : label,
                    'time' : datetime.now(),
                    # 'args' : arguments,
                    # 'kwargs' : kwarguments
                }
            )
            cur.close()
        return


# class DBWrapper:

#     def __init__(self, dbName) -> None:
#         pass