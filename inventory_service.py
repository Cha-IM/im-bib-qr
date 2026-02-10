### Funksjonalitet:
from pathlib import Path
import csv
from database import DB,DB_TEST
from QR_writing import qr_pdf_generator, MAX_PAGE_QR
from utils import now, check_path, ValidationError, NotFoundError
from sqlite3 import IntegrityError
from QR_writing import MAX_PAGE_QR

PAGE_PRINT_TRESHOLD = 0.75 # Andel av siden som må være fylt før den ordinært skal printes. 
"""
Behov:
1. OK
Legge flere nye kategorier av ting fra csv som er formatert på følgende måte:
    Kategori_prefix, Navn, Lager_rom, Antall_i_kategori
Legger til kun nye kategorier, slik at om man kjører samme csv.fil flere ganger legges kun nye elementer til. 

F.eks
CAM, Kamera, Video, 11 -> Legger til 11 kamera til Video_lageret med koder: CAM0001 til CAM0011

Trenger:
2. OK
Legge til Lager_rom
Oversikt over Lagerrom navn til ID, lage en dict/funksjon.  


3. OK
Genererer QR-koder
Skriv ut QR kode til alle uten QR_kode. 

4. 
Oppdatere innhold, legge til og fjerne enkelt ting. 
Legge til flere ting. 

5. Skrive ut ny QR-kode til enkelt items.

6. Oversikter over hva som er i DB. 
OK-Alle items

7. Resultater av csv importeringer, med logger. OK, ish. Kan ikke bruke disse til noe senere. 
En csv logg for items som allerede var i DB - Ok.
En csv logg med ny opprettede lager og Items.  - Nei, legger aldri til Lager med .csv, må gjøres eksplisitt.

Farger koblet til rom? 

"""

"""
Ønsker: 
Grafisk med tkinter, ikke kun script?

"""
HEADERS = ["Prefix", "Name", "Storage", "Number"]

def create_new_category_with_items(name: str, prefix: str, storage: str, count: int):
        name = name.strip().capitalize()
        prefix =prefix.strip().upper()
        storage = storage.strip().capitalize()
        count = int(count)
        if count < 1:
            raise ValidationError("count must be >= 1")
        with DB() as db:
            db.validate_storage(storage)
            try:
                category_id = db.add_category(name,prefix,storage)
                db._add_items(category_id, 1, count, prefix)
            except IntegrityError as e:
                db.logs.add("Error", str(e), (name,prefix, storage, count)) 
                
            
def add_to_category(prefix:str, count:int):
    prefix =prefix.strip().upper()
    if not prefix.startswith("CHA"):
        prefix = "CHA"+prefix
    if count < 1:
            raise ValidationError("count must be >= 1")   
             
    with DB() as db:
        cat_id = db.find_category_id(prefix)
        db.add_items(cat_id, count)
    

def create_new_categories_from_csv(filename: str, add_new_storages=False):
    """Takes inn a csv with the following headers:
        Prefix,Name,Storage,Number
        It will only generate new categories, so existing categories will not be changed.
        Example:
    CAM, Kamera, Video, 11 -> Adds 11 kamera to Video_lageret with codes: CAM0001 til CAM0011
        OBS:
        If storage is not in the database a new storage room will be added for the category.

    """
    inn_path = check_path(filename)
    with open(inn_path, encoding="UTF-8-sig") as f:
        reader = csv.DictReader(f)

        data = [row for row in reader]
        expexted = [x.lower().strip() for x in HEADERS]
        actual = [x.lower().strip() for x in reader.fieldnames or []]
        if expexted != actual:
            raise (
                ValueError(
                    f"Ukjent formatering av headers i {filename}, {actual} forventet {expexted}"
                )
            )
        
        for row in data:
            number = int(row["Number"])
            prefix = "CHA"+row["Prefix"]
            name = row["Name"]
            storage = row["Storage"]
            
            create_new_category_with_items(name, prefix, storage, number)
            
def show_all_new():
     with DB() as db:
        to_print = db.fetch_not_printed()
        a = ["ID", "CODE", "FG","BG"]
        for row in [a,*to_print]:
            for i in row:
                print(f"{i:<11}",end="|")
            print()
        print(f"Antall: {len(to_print)}, printer {MAX_PAGE_QR} per side")
        
def print_all_new():
    """Generate pdf's for all items in the database yet to be printed.
    When QR_codes are printed it will update the items last printed values
    """
    with DB() as db:
        to_print = db.fetch_not_printed()
        if not to_print:
            return False
        items_list = []
        id_list = []
        for id, prefix,fg,bg in to_print:
            items_list.append({"prefix":prefix, "fg":fg, "bg":bg})
            id_list.append(id)

        # Fill-check
        if (len(id_list) % MAX_PAGE_QR)/MAX_PAGE_QR < PAGE_PRINT_TRESHOLD: 
            excess = len(id_list) % MAX_PAGE_QR
            id_list = id_list[:len(id_list)-excess] #Hopper over de n - første elementene.
            items_list = items_list[:len(id_list)-excess]

        
        qr_pdf_generator(items_list, name="new")
        db.mark_multiple_qr_printed(id_list)
        return True


def add_storage(name:str, fg:str, bg:str):
    try:
        with DB() as db:
            db.add_storage(name.strip().capitalize(), fg, bg)
    except IntegrityError:
        pass




def show_all_items():
    with DB() as db:
        a = ["ID", "CODE", "number", "name", "storage" ,"qr_count", "qr_print_at"]
        for row in [a,*db.fetch_items()]:
            for i in row:
                if i == None:
                    i = "Never"
                print(f"{i:<11}",end="|")
            print()


def show_all_categories():
    for i in ["Name", "Prefix", "Storage_Name", "Count"]:
        print(f"{i:13}", end="")
    print()
    with DB() as db:
        for row in db.fetch_categories():
            print(f"{row[0].title():13}", end="")
            for i in row[1:-1]:
                print(f"{i:13}", end="")
            print(f"Antall: {row[-1]:5}")

def add_storages():
    # add_storage("TVstudio","173.216.230", "0.0.0.0")
    # add_storage("Verksted","80.200.120", "0.0.0.0")
    # add_storage("2IT","255.197.211", "0.0.0.0")
    # add_storage("Videolager", "255. 170. 130", "0.0.0.0")
    # add_storage("Fotolager",   "255. 220. 95",  "0.0.0.0") 
    # add_storage("Spesialager", "200. 170. 220", "0.0.0.0")
    # add_storage("IMlager",     "170. 220. 210", "0.0.0.0")
    pass

def demo():
    # Testing
 
    
    # add_storages()
    # create_new_categories_from_csv("test_2")
    show_all_categories()
    # show_all_items()
    # if print_all_new():
    #     print("All new QR's printed")
    # else:
    #     print("No new QR's to print")
    # show_all_items()



if __name__ == "__main__":
    demo()
    # add_storages()
    