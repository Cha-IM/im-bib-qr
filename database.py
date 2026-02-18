# Datalayer, works on the db directly. CRUD.
import sqlite3

from pathlib import Path
from utils import now, NotFoundError, ValidationError

DB_PATH = Path("inventory.db")
DB_TEST = Path("test.db")
MIN_LEN = 8



class Logg_data:
    def __init__(self, name:str, description:str) -> None:
        self.name = name
        self.description = description
        self.items = []
    
    def add(self,item):
        self.items.append(item)

    def __str__(self) -> str:
        padding = "*"*10
        string = ""
        string += f"{padding}{self.name}{padding} \n"
        string += f"{self.description} \n"
        if self.items:
            for i in self.items:
                string += f"{i}\n"
        else:
            return ""
        return string
class Logger:
    def __init__(self) -> None:
        self.logs:dict[str,Logg_data] = {}    
    def add(self,name:str, e:str, item):
        if name not in self.logs:
            self.logs[name] = Logg_data(name, e)
        self.logs[name].add(item)
    
    def write_log(self):
        for i in self.logs.values():
            print(i)

        log = Path("logs")
        log.mkdir(exist_ok=True,parents=True)

        with open(log/"log.txt", "a") as f:
            if not self.logs:
                f.writelines(now()+" - No logs \n")
            else:
                f.writelines([now()+'\n',*[str(x)for x in self.logs.values()], '\n'])
        if "Existing" in self.logs:
            with open(log/"existing.txt", "a") as f:
                f.writelines([now()+'\n',str(self.logs["Existing"]), '\n'])
        if "Errors" in self.logs:
            with open(log/"errors.txt", "a") as f:
                f.writelines([now()+'\n',str(self.logs["Errors"]), '\n'])

class DB:
    def __init__(self, path=DB_PATH) -> None:
        self.path = path
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS storage_rooms (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                fg TEXT NOT NULL ,
                bg TEXT NOT NULL
            )
        """
        )

        

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                prefix TEXT NOT NULL UNIQUE CHECK(length(prefix) >= 3),
                storage_room_id INTEGER NOT NULL,
                FOREIGN KEY(storage_room_id) REFERENCES storage_rooms(id)
            )
        """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                category_id INTEGER NOT NULL,
                number INTEGER NOT NULL CHECK(number >= 1),
                item_code TEXT NOT NULL,
                qr_print_count INTEGER NOT NULL DEFAULT 0,
                qr_print_at TEXT,
                UNIQUE(category_id, number),
                FOREIGN KEY(category_id) REFERENCES categories(id)
            )
        """
        )

        self.conn.commit()
        self._storage_to_ID()

    def __enter__(self):
            self.logs = Logger()
            return self
        
    def __exit__(self, exc_type, exc_value, traceback):

        try:
            if exc_type is None:
                self.conn.commit() # Commiter endringer kun om ingen feilmeldinger
            else:
                self.conn.rollback() # Om feilmeldinger reverter vi alle  endringer så kan vi prøve på nytt senere.
        finally:
            self.logs.write_log()
            self.conn.close()

    def _storage_to_ID(self):
        self.cursor.execute(
            """
            SELECT id,name
            FROM storage_rooms
                            """
        )
        result = self.cursor.fetchall()

        storage: dict[str, int] = {}
        for room in result:
            storage[room[1]] = room[0]

        self.STORAGE = storage

    def validate_storage(self,storage:str):
           if not storage in self.STORAGE:
               raise NotFoundError(f"{storage} not in the Database")
               
    def add_storage(self, name: str, foreground_color:str, background_color:str):
        try:
            self.cursor.execute("INSERT INTO storage_rooms (name, fg, bg) VALUES (?,?,?)", (name,foreground_color,background_color))
            
            self._storage_to_ID()
            res = self.cursor.lastrowid
            if res:
                return res
            else:
                raise ValidationError("Storage not added")
        except sqlite3.IntegrityError as e:
            e.add_note(f"{name} already exists")
            raise e

    def add_category(self, name: str, prefix: str, storage_room_name: str):
        self.validate_storage(storage_room_name)
        storage_room_id = self.STORAGE.get(storage_room_name)
        if not prefix.startswith("CHA"):
            prefix = "CHA"+prefix
        try:
            self.cursor.execute(
                "INSERT INTO categories (name, prefix, storage_room_id) VALUES (?, ?, ?)",
                (name, prefix, storage_room_id),
            )
        except sqlite3.IntegrityError as e:
            e.add_note(f"{name,prefix,storage_room_name}")
            raise e

        if self.cursor.lastrowid:
            return self.cursor.lastrowid
        else:
            raise ValidationError("Category not added")
       
    def find_cat_id(self,prefix:str)->int:
        self.cursor.execute(
            "SELECT id FROM categories WHERE prefix = ?", (prefix,)
        )
        row = self.cursor.fetchone()
        if not row:
            raise NotFoundError("Category not found")

        return row[0]


    def find_cat_prefix(self, category_id: int):
        self.cursor.execute(
            "SELECT prefix FROM categories WHERE id = ?", (category_id,)
        )
        row = self.cursor.fetchone()
        if not row:
            raise NotFoundError("Category not found")

        return row[0]

    def compute_item_code(self, prefix: str, number: int) -> str:
        # Compute item_code: prefix + zero-padded number so total length >= MIN_LEN
        if len(prefix) < MIN_LEN:
            item_code = prefix + str(number).zfill(MIN_LEN - len(prefix))
        else:
            item_code = prefix + str(number)
        return item_code

    def id_to_item_code(self, item_id: int) -> str:

        self.cursor.execute(
            """
                    SELECT item_code
                    FROM items
                    WHERE id = ?
                    """,
            (item_id,),
        )
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            raise NotFoundError(f"{item_id}")
        

    def item_code_to_id(self, item_code: str) -> int:

        self.cursor.execute(
            """
                    SELECT id
                    FROM items
                    WHERE item_code = ?
                    """,
            (item_code,),
        )
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            raise NotFoundError(f"{item_code}")

    def _add_item(self, category_id: int, number: int)-> tuple[int,str]:

        prefix = self.find_cat_prefix(category_id)
        item_code = self.compute_item_code(prefix, number)
        self.cursor.execute(
            "INSERT INTO items (category_id, number, item_code) VALUES (?, ?, ?)",
            (category_id, number, item_code),
        )
        
        if not self.cursor.lastrowid:
            raise ValidationError(f"{category_id}{item_code} not added to Database")
        return self.cursor.lastrowid, item_code
    
    def _add_items(self, category_id:int, start:int, count:int, prefix:str)-> None:
        """ Adds count items to an existing category from itemcode = prefix+start """
        items = []
        for number in range(start, count + start):
            items.append([category_id, number, self.compute_item_code(prefix, number)])
        self.cursor.executemany(
            "INSERT INTO items (category_id, number, item_code) VALUES (?, ?, ?)", items
        )
       
        self.logs.add("Added","Added the following to the DB", [category_id, start, count, prefix])

    def add_items(self, category_id: int, count: int)-> None:
        """ Adds items to an existing category, will add to the maximum in the category"""
        #TODO add option to "fill" category if empty spaces in the cat. c0 c1 c3 add_items(2) gives c0 c1 C2 c3 C4 instead of c0 c1 c3 C4 C5
        prefix = self.find_cat_prefix(category_id)
        self.cursor.execute(
            """
                    SELECT MAX(number)
                    FROM items 
                    WHERE category_id = ? 
                    """,
            (category_id,),
        )
        start = self.cursor.fetchone()[0]
        start = start + 1 if isinstance(start, int) else 1
        self._add_items(category_id, start, count, prefix)

    def fetch_not_printed(self):
        """ Returns all items not yet printed"""
        self.cursor.execute(
            """
                    SELECT i.id, i.item_code, s.fg, s.bg
                    FROM ITEMS as i
                    JOIN categories c ON i.category_id = c.id
                    JOIN storage_rooms s ON c.storage_room_id = s.id
                    WHERE qr_print_count = 0
                    """
        )
        return self.cursor.fetchall()

    def mark_qr_printed(self, item_id: int):
        """ Updates item_id print values """
        self.cursor.execute(
            """
                    UPDATE items
                    SET qr_print_count = qr_print_count + 1,
                    qr_print_at = ? 
                    WHERE id = ?
                    """,
            (now(), item_id),
        )
       

    def mark_multiple_qr_printed(self, item_ids:list[int]):
        """ Takes a list of item_id's and updates print values"""
        items = []
        time = now()
        for i in item_ids:
            items.append((time,i))
        self.cursor.executemany(
            """
                    UPDATE items
                    SET qr_print_count = qr_print_count + 1,
                    qr_print_at = ? 
                    WHERE id = ?
                    """,
            (items),
        )
        

    def fetch_items(self):

        self.cursor.execute(
            """
            SELECT i.item_code, s.name AS storage_room , i.qr_print_count, i.qr_print_at,  i.number, c.name AS category_name
            FROM items i
            JOIN categories c ON i.category_id = c.id
            JOIN storage_rooms s ON c.storage_room_id = s.id
            ORDER BY i.item_code
        """
        )
        return self.cursor.fetchall()



    def fetch_categories(self):
        self.cursor.execute(
            """
            SELECT c.prefix, s.name AS storage_room, COALESCE(COUNT(i.id), 0), c.name
            FROM categories c 
            JOIN storage_rooms s on c.storage_room_id = s.id
            LEFT JOIN items i on i.category_id = c.id
            GROUP BY c.prefix
            ORDER BY s.name
            """
        )
        return self.cursor.fetchall()

            

    def remove_item_id(self, item_id: int):

        try:
            self.cursor.execute(
                """
                        DELETE FROM items
                        WHERE id = ?
                        """,
                (item_id,),
            )
           
        except:
            raise NotFoundError(f"{item_id}")

    def remove_item_code(self, itemcode:str):
        id = self.item_code_to_id(itemcode)
        self.remove_item_id(id)

  
    def fetch_categories_prefixes(self):

        self.cursor.execute(
            """
            SELECT prefix
            FROM categories
        """
        )
        # print("test",self.cursor.fetchall())
        categories = []
        for res in self.cursor.fetchall():
            categories.append(*res)
        return categories



def demo():

    # Demo usage
    if DB_TEST.exists():
        DB_TEST.unlink()
    with DB(DB_TEST) as db:
      


        # # Add storage rooms
        db.add_storage("Video", "Orange", "Cyan")
        db.add_storage("IM", "Yellow", "Orange")

        # # Add categories
        cam_id = db.add_category("CAMERA", "CAM", "Video")
        com_id = db.add_category("COMPUTER", "COM", "IM")
        print(cam_id)
        # Add items
        db._add_item(cam_id, 1)
        db._add_item(cam_id, 2)
        db._add_item(com_id, 1)
        db._add_item(com_id, 2)

        # Add multiple items with an item_group
        db.add_items(cam_id, 5)

        db.mark_qr_printed(2)

        # removing an obj from id:
        db.remove_item_id(1)

        # removing an obj from a prefix:
        db.remove_item_code("CAM00002")

        # db.remove_items_from_cat("CAM",[4,5,6])
        for item in db.fetch_items():
            print(item)
        for item in db.fetch_not_printed():
            print(item)
        for item in db.fetch_categories():
            print(item)
        
        

if __name__ == "__main__":
    demo()
