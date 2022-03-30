from operator import truediv
import os
import sqlalchemy as sa
from datetime import timedelta
from datetime import datetime
from typing import Any, Callable
from utils.result import Result

class Tracker:
    
    _dbURL = os.environ.get("DATABASE_URL", f"sqlite://{os.getcwd()}/GAiD-dev.sqlite3")
    _db = sa.create_engine(_dbURL.replace("postgres://", "postgresql://", 1))

    init = False
    limits = {}

    @classmethod
    def initialize(cls):
        # make the table
        cls.table = sa.Table(
            'queries', sa.MetaData(), 
            sa.Column('id', sa.INTEGER, primary_key=True, autoincrement=True), 
            sa.Column('label', sa.TEXT), 
            sa.Column('time', sa.TIMESTAMP, default=sa.func.now())
        )
        cls.table.create(cls._db, checkfirst=True)

    @classmethod
    def limit(cls, **kwargs) -> Callable:
        """
        Returns a decorator that limits the execution of <Query>._request methods 
            to `count: int` times per `age: timedelta` under `label: str`
        """

        if not cls.init:
            cls.initialize()

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
        countStmt = ( sa.select(sa.func.count('*')). \
            select_from(cls.table). \
            where(
                sa.and_(
                    cls.table.c.label == name,
                    cls.table.c.time > (datetime.now() - age)
                )
            ).scalar()
        )

        with cls._db.begin() as conn:
            count = conn.execute(countStmt)

        return count
        

    @classmethod
    def addRun(cls, label, arguments, kwarguments) -> None:
        # consider storing search words
        stmt = ( sa.insert(cls.table).values(label=label, time=datetime.now()) )

        with cls._db.begin() as conn:
            conn.execute(stmt)

        return
