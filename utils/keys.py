from os import environ, getcwd
keys = {
    "walpha" : environ.get( "GAiD_WALPHA_KEY", None),
    "kgraph" : environ.get( "GAiD_KGRAPH_KEY", None),
    "cse"    : environ.get( "GAiD_GOOGLE_KEY", None),
    "db"     : environ.get("DATABASE_URL", 
                           f"sqlite:///{getcwd()}/GAiD-dev.sqlite3").
                           replace("postgres://", "postgresql://", 1),
    "prefix" : 'g ' if environ.get("GAiD_ENV", None) in ("prod", "production") else 'm '
}
