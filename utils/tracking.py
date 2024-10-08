import sqlalchemy as sa
from utils.keys import keys
from datetime import timedelta
from datetime import datetime
from typing import Any, Callable
from utils.result import Result

class Tracker:
    
    _db = sa.create_engine(keys['db'])
    limits = {}

    @classmethod
    def initialize(cls):
        # make the table
        cls.metaData = sa.MetaData()
        cls.metaData.bind = cls._db
        cls.table = sa.Table(
            'queries', cls.metaData,
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
        
        count = cls.table.select(). \
            where(
                sa.and_(
                    cls.table.c.label == name,
                    cls.table.c.time > (datetime.now() - age)
                )
            ).rowcount

        return count

    @classmethod
    def addRun(cls, label, arguments, kwarguments) -> None:
        # consider storing search words
        cls.table.insert().values(label=label, time=datetime.now()).execute()

        return
