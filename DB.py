import json

db_string = r""" 
{
	"products": {
        "watches": 1,
        "jewelry": 1,
        "watch band": 1,
        "collection": 1
}

"""

data = json.loads(db_string)