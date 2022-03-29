from os import environ
keys = {
    "walpha" : environ.get( "GAiD_WALPHA_KEY", None),
    "kgraph" : environ.get( "GAiD_KGRAPH_KEY", None),
    "cse"    : environ.get( "GAiD_GOOGLE_KEY", None),
}