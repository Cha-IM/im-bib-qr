import datetime
from pathlib import Path

def now():
    """Returns a string representing now in iso-format"""
    return (
        datetime.datetime.now(datetime.UTC)
        .isoformat(timespec="minutes")
        .split("+")[0]
        .replace(":", "-")
    )

class ValidationError(Exception):
    """ Validation failed for database"""

class NotFoundError(Exception):
    """ Item was not Found in database"""
        
def check_path(path:str,sufix=".csv"):
    inn_path = Path(path).with_suffix(".csv")
    if not inn_path.exists():
        raise FileNotFoundError(f"{path}.csv not found")
    return inn_path
if __name__ == "__main__":
    print(now())


            