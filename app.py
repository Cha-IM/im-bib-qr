# Endpoint, bruker inventory_service for å lage gui
from inventory_service import (
    print_all_new,
    create_new_categories_from_csv,
    show_all_items,
    show_all_new,
    show_all_categories,
)
from inventory_service import (
    fetch_all_new,
    fetch_all_categories,
    fetch_all_storages,
    fetch_all_items,
    is_existing_category,
    create_new_category_with_items,
    add_to_category,
)
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import platform

# create_new_categories_from_csv("input_1.csv")
# create_new_categories_from_csv("input_2.csv")
# create_new_categories_from_csv("input_4.csv")
# create_new_categories_from_csv("input_6.csv")
# add_to_category("SDL",1)
# add_to_category("VIL",4)
# create_new_category_with_items("Lysmåler","Lysmaal","Fotolager",1)
# create_new_categories_from_csv()
# show_all_items()

# show_all_new()
# show_all_categories()
# print_all_new()


class App:
    def __init__(self):
        """Opprett en Gui-instans og hent data"""
        self.gui = Gui(self)

        self.gui.show_cats_request()

    def handle_request(self, request):
        """Behandle forespørselen og be gui om å vise resultatet"""
        """ hvordan sortere? ¨
        Prioritering --> 
            1. Legge til nye kategorier - #DONE
            2. Skrive ut mer av eksisterende
                Skrive ut av ting. 

            Vis alle kategorier  - CHECK
            Vise utvalg av kategorier - CHECK.
            Vise alle items - Check
            Vise alle nye items - Check
            Vise utvalg av items fra ulike rom - Check

            Søk på kategorier fra navn - ?
            
            Legge til:
                Helt nye kategorier 
                Fra csv-fil. 
                Fylle på enkelt-items

            Fjerne:
                Hele kategorier
                Enkelt-ting

            Utskrift:
                Skrive ut alle nye
                Velge enkelt-kategorier/ting til utskrift. 


            Ha noen standard filter øverst? Ja, som persister over ulike faner. 

            TODO menyen husker valgt fra mellom fjerning. Kanskje legge til active/inactive - states. 
            """

        self.gui.setup_controls()
        if request == "show_all_cats":
            data = fetch_all_categories()
            self.gui.display_single_table(data)
        elif request == "show_storages":
            data = fetch_all_items()
            # self.gui.set_menu(self.gui.update_table_text)
            self.gui.display_single_table(data)
        elif request == "show_prints":
            new = fetch_all_new()
            selected = ["TEST"]
            self.gui.display_prints(new,selected)
            # self.gui.set_menu(self.gui.update_table_text)


        elif request == "add_cats":
            self.changed = []
            self.gui.display_add_cats()

    def run(self):
        """Start hendelsessløyfen og hold vinduet åpent"""
        self.gui.mainloop()

    def add_to_db(self,prefix,name,storage,count):
        if not prefix:
            raise ValueError("Prefix can't be empty")
        
        # Verifisering av innhold. 
        # 1 unikt
        if is_existing_category(prefix):
            add_to_category(prefix,count)
            return f"Adding {count} to exsisting category CHA{prefix} \n name and storage is ignored"
        else:
            if not name:
                raise ValueError("Name can't be empty")
            if not storage:
                raise ValueError("Storage can't be empty")
            

            create_new_category_with_items(name,prefix,storage,count)
            return f"Successfully added {count} to the database \n CHA{prefix} \n {name} to {storage}"


class Gui(tk.Tk):
    def __init__(self, app):
        """opprett GUI-vindu med kontroll- og visningsområder"""
        super().__init__()
        # Lagre en referanse til app-instansen
        self.app: App = app
        # Vindustittel, størrelse og sentrering
        self.title("IM BIBQR SYS")
        self.FONT_SIZE = 18
        b, h = 900, 800
        bs, hs = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{b}x{h}+{bs//2-b//2}+{hs//2-h//2}")
        # self.resizable(False, False)

        if platform.system() == "Windows":
            font = ("Consolas", self.FONT_SIZE)
        elif platform.system() == "Darwin":  # macOS
            font = ("Menlo", self.FONT_SIZE)
        else:  # Linux
            font = ("Monospace", self.FONT_SIZE)
        self.option_add("*Font", font)
        self.max_text_len = b // self.FONT_SIZE
        # Kontrollområde for valg av visning
        self.controls_frame = tk.Frame(self, relief="raised", bd=1)
        self.controls_frame.pack(side=tk.TOP, fill="x")
        self.controls = {
            "Vis \n kategorier": self.show_cats_request,
            "\n Vis ting": self.show_rooms_request,
            "\n Utskrift ": self.show_prints_request,
            "\n Legg til ": self.add_cats_request,
            "Fjern\n innhold": lambda: print("Not implemented"),
        }
        self.current = None

        # Visnngsområde
        self.display_frame = tk.Frame(self)
        self.display_frame.pack(side=tk.RIGHT, fill="both", expand=True)
        # Meny
        self.meny_frame = tk.Frame(self, relief="solid")
        self.meny_frame.pack(side=tk.LEFT)
        self.meny_vals: dict[str, tk.BooleanVar] = {}

    def setup_controls(self):
        """Opprett kontroller for valg av visning"""
        # TODO passe på størrelsen til disse knappene
        for widget in self.controls_frame.winfo_children():
            widget.destroy()
        col = 0

        for text, function in self.controls.items():
            if self.current == function:

                btn = tk.Button(
                    self.controls_frame,
                    text=text,
                    command=function,
                    border=0,
                    borderwidth=5,
                )
            else:
                btn = tk.Button(self.controls_frame, text=text, command=function)

            btn.grid(row=0, column=col, padx=10, pady=10)
            col += 1
        # tk.Button(self.controls_frame, text='Vis \n lagerrom',
        #           command=self.show_rooms_request, ).grid(
        #     row=0, column=1, padx=10, pady=10)
        # tk.Button(self.controls_frame, text='Vis nye \n',
        #           command=self.show_prints_request).grid(
        #     row=0, column=2, padx=10, pady=10)

    def show_cats_request(self):
        """
        Be app om å behandle forespørselen,
        som deretter ber gui om å vise resultatet i en tabell
        """
        self.current = self.show_cats_request
        self.app.handle_request("show_all_cats")

    def show_rooms_request(self):
        self.current = self.show_rooms_request
        self.app.handle_request("show_storages")

    def show_prints_request(self):
        self.current = self.show_prints_request
        self.app.handle_request("show_prints")

    def add_cats_request(self):
        self.current = self.add_cats_request
        self.app.handle_request("add_cats")

    def set_room_index(self) -> None:
        for i, j in enumerate(self.data[0]):
            if j.lower() == "storage":
                self.room_index = i
                return
        else:
            self.room_index = None
    def display_single_table(self, data:list[str]):
        self.clear_display()
        self.set_menu(self.update_table_text)
        self.display_table(data, self.display_frame)

    def display_table(self, data: list[str], frame:tk.Frame):
        """Vis tekst i visningsområdet"""
        self.vals = [0] * len(data[0])
        self.data = data
        self.set_room_index()

        # Find len of rows:
        for row in data:
            for i, info in enumerate(row):
                self.vals[i] = max(self.vals[i], len(str(info)),1)

        # Tekstfelt
        output = tk.Text(frame, wrap="none")
        output.pack(padx=10, pady=10, fill="both", expand=True)
        # Rullefelt
        scroll = ttk.Scrollbar(output, orient="vertical", command=output.yview)
        scroll.pack(side="right", fill="y")
        output["yscrollcommand"] = scroll.set
        # Tag for marger
        output.tag_configure("marg", lmargin1=10, lmargin2=10, rmargin=10)
        # Tag for fet skrift
        font = Font(output, output.cget("font"))
        font.config(weight="bold")
        output.tag_configure("fet", font=font)

        output.configure(cursor="arrow", takefocus=0, exportselection=False)
        for seq in (
            "<Key>",
            "<<Paste>>",
            "<<Cut>>",
            "<Control-v>",
            "<Control-x>",
            "<Control-Shift-V>",
        ):
            output.bind(seq, lambda e: "break")
        for seq in (
            "<Button-1>",
            "<B1-Motion>",
            "<Shift-Button-1>",
            "<Double-Button-1>",
            "<Triple-Button-1>",
            "<Control-a>",
        ):
            output.bind(seq, lambda e: "break")
        self.output = output

        self.update_table_text()

    def update_table_text(self):
        text = ""
        # Header
        for i, info in enumerate(self.data[0]):
            text += f"{info:<{self.vals[i]}} "
        text += "\n"
        # If rooms filter
        if self.room_index != None:
            for row in self.data[1:]:
                room: str = row[self.room_index]

                if self.meny_vals[room].get():
                    for i, info in enumerate(row):
                        text += f"{info:<{self.vals[i]}} "
                    text += "\n"
        
        else:
            # Prepp text
            text = ""
            for row in self.data:
                for i, info in enumerate(row):
                    text += f"{info:<{self.vals[i]}} "
                text += "\n"

        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", text, "marg")
        self.output.tag_add("fet", "1.0", "1.end")

    def display_add_cats(self) -> None:
        self.clear_display()
        self.clear_menu()
        # Hva trengs her:
        # Prefix;Name;Storage;Number
        # Prefix er ok. --> Sjekk at ikke starter på CHA
        # Navn er ok
        # Storage velges fra eksisterende
        # Number >= 1
        prefixVar = tk.StringVar()
        nameVar = tk.StringVar()
        storageVar = tk.StringVar()
        numbVar = tk.IntVar()

        col_1 = []
        col_2 = []
        prefix_text = tk.Label(self.display_frame, text="Prefix")
        
        prefix_input = tk.Entry(self.display_frame, textvariable=prefixVar)
        col_1.append(prefix_text)
        col_2.append(prefix_input)

        name_text = tk.Label(self.display_frame, text="Navn")
        name_input = tk.Entry(self.display_frame, textvariable=nameVar)

        col_1.append(name_text)
        col_2.append(name_input)

        storage_text = tk.Label(self.display_frame, text="Lager")

        storage_frame = tk.Frame(self.display_frame)
        scrollbar = tk.Scrollbar(storage_frame, orient="vertical")
        storage_input = tk.Listbox(
            storage_frame, height=5,
            yscrollcommand=scrollbar.set,
            selectmode="single",
            
        )

        
        storages = fetch_all_storages()
        for storage in storages:
            storage_input.insert("end", storage)

        scrollbar.configure(command=storage_input.yview)
        scrollbar.pack(side="right", fill="y")
        storage_input.pack()

        def update(_):
            selection = storage_input.curselection()
            if selection:
                index = selection[0]
                # Get actual value
                selected_text = storage_input.get(index)
                # Update StringVar
                storageVar.set(selected_text)

        storage_input.bind("<<ListboxSelect>>", update)

        col_1.append(storage_text)
        col_2.append(storage_frame)

        number_text = tk.Label(self.display_frame, text="Antall")
        number_input = tk.Spinbox(self.display_frame, from_=1, to=99, increment=1, textvariable=numbVar)
        col_1.append(number_text)
        col_2.append(number_input)

        
        for i, item in enumerate(col_1):
            item.grid(row=i, column=0, pady=10, ipadx=5)
            # storage_frame.grid(st)
        for i, item in enumerate(col_2):
            item.grid(row=i, column=1, pady=10)
        i = len(col_1)
        err = tk.StringVar()
        feedback_label = tk.Label(self.display_frame,textvariable=err, fg="red")
        feedback_label.grid(row=i,column=0,columnspan=2)
        
        
        def add_cat():
            
            try:
                prefix  = prefixVar.get().strip().upper()
                name    = nameVar.get().strip().capitalize()
                storage = storageVar.get().strip()
                count  = numbVar.get()
                res = app.add_to_db(
                    prefix,
                    name,
                    storage,
                    count
                )
                err.set(res)  #HACK should have a unified prefix method, and unified way to display Repeating Skriv ut. 
            except ValueError as e:
                err.set(str(e))


        self.display_frame.columnconfigure(3,weight=3)
        make_button = tk.Button(self.display_frame, text="", command=add_cat)
        make_button.grid(row=0, column=3, rowspan=i, pady=10, padx=10, sticky="NSEW")

        def btn_text(*args):

            prefix  = prefixVar.get().strip().upper()
            name    = nameVar.get().strip().capitalize()
            storage = storageVar.get().strip()
            number  = numbVar.get()

            txt = "Trykk for å lage følgende: \n"
            if prefix:  txt += f"\n CHA{prefix}"
            if number:  txt += f" {number}"
            if storage: txt += f"\n{storage}"
            if name:    txt += f"\n{name}"
            make_button.config(text=txt)
            
        btn_text([])
        vars = [prefixVar, nameVar, storageVar, numbVar]
        for var in vars:
            var.trace_add("write", btn_text)
        

        
      
    def display_prints(self, new_prints, selected) -> None:
        self.clear_display()
        self.clear_menu()
        # IDEA: Menu show color
        # # And show storage colors
        # How to make selected possible ... 
        # App needs two attributes, slc_item, slc_cats
        # Need to update display_table alot, so that all have a checkbox to select or not, also able to preselect some/all/none.
        # Display print needs to remove from selected. And give option to clear. 
        new_frame = tk.Frame(self.display_frame,relief="raised",)
        selected_frame = tk.Frame(self.display_frame,relief="raised")

        tk.Label(self.display_frame, text="New ").pack(anchor="w")
        new_frame.pack(fill="both",expand=True)
        tk.Label(self.display_frame, text="Selected").pack(anchor="w")
        selected_frame.pack(fill="both",expand=True)
        # self.set_menu(self.update_table_text)
        tk.Label(self.display_frame, text=f"Total items to print {len(new_prints)+len(selected)}").pack(anchor="w")

        self.display_table(new_prints, new_frame)
        self.display_table(selected,selected_frame)

        # Samt muligheter for å velge egne data til utskrift.
        # Enten fra å velge fra de andre fanene 1-2, eller i denne?

        # For alle disse kan man velge å ikke printe...
        # 1 Info om valgte prints, av hel side.
        # 2 Widget med alle nye prints
        # 3 Widget med alle valgte kategorier for prints
        # 4 Widget med alle valgte items for prints

        pass

    def set_menu(
            
        self,
        onclick,
        inital_val=True,
    ):
        """ Controls menu behavior

        Args:
            onclick (Functoin): What funtion the menu should call
            inital_val (bool, optional): Defaults to True.
        """
        if self.meny_frame.winfo_children():
            return
        # Menyfelt
        rooms = fetch_all_storages()
        for i, storage in enumerate(rooms):
            self.meny_vals[storage] = tk.BooleanVar()
            # self.meny_vals[storage].set(inital_val)

            btn = tk.Checkbutton(
                self.meny_frame,
                text=storage,
                onvalue=True,
                offvalue=False,
                variable=self.meny_vals[storage],
                command=onclick,
            )

            if inital_val:
                btn.select()

            btn.grid(row=i, column=0, sticky="w")

    def clear_menu(self) -> None:
        for widget in self.meny_frame.winfo_children():
            widget.destroy()

    def clear_display(self) -> None:
        """Fjern alle widgeter fra visningsområdet (før ny visning)"""
        for widget in self.display_frame.winfo_children():
            widget.destroy()

    def destroy(self) -> None:
        """
        Lukk alle matplotlib-figurer og avslutt vinduet.
        Nødvendig når vi bruker matplotlib i tkinter.
        """
        # plt.close('all')
        super().destroy()


if __name__ == "__main__":
    """
    Start applikasjonen hvis filen kjøres som et skript.
    Kjøres ikke hvis denne filen importeres som modul.
    """

    app = App()
    app.run()
