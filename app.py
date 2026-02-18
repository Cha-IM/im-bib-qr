# Endpoint, bruker inventory_service for å lage gui
from inventory_service import print_all_new, create_new_categories_from_csv, add_to_category,show_all_items,show_all_new,create_new_category_with_items, show_all_categories
from inventory_service import fetch_all_new,fetch_all_categories, fetch_all_storages, fetch_all_items
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
        '''Opprett en Gui-instans og hent data'''
        self.gui = Gui(self)
        
        self.gui.show_cats_request()


    def handle_request(self, request):
        '''Behandle forespørselen og be gui om å vise resultatet'''
        """ hvordan sortere? 
            Vis alle kategorier  - CHECK
            Vise utvalg av kategorier - CHECK.
            Vise alle items - Check
            Vise alle nye items - Check
            Vise utvalg av items fra ulike rom - Check

            Søk på kategorier fra navn - ?
            

            Så velg enkelt rader -> checkboxbtn's 
            Enten skriv ut på nytt
            Legg til/fyll på items i en kategori
            Legg til kategori
            Legg til fra csv
            eller Fjern 
            Enklere med flere faner. 
            - Vise / Skrive ut
            - Legge til 
            - Fjerne 

            Ha noen standard filter øverst? Ja, som persister over ulike faner. 

            """
      
        self.gui.setup_controls()
        if request == 'show_all_cats':
            data=fetch_all_categories()
            self.gui.set_menu(self.gui.update_table_text)
            self.gui.display_table(data)
        elif request == "show_storages":
            data=fetch_all_items()
            self.gui.set_menu(self.gui.update_table_text,False)
            self.gui.display_table(data)
        elif request == "show_prints":
            data = fetch_all_new()
            self.gui.set_menu(self.gui.update_table_text)
            self.gui.display_table(data)


    def run(self):
        '''Start hendelsessløyfen og hold vinduet åpent'''
        self.gui.mainloop()
        

class Gui(tk.Tk):
    def __init__(self,app):
        '''opprett GUI-vindu med kontroll- og visningsområder'''
        super().__init__()
        # Lagre en referanse til app-instansen
        self.app:App = app
        # Vindustittel, størrelse og sentrering
        self.title("IM BIBQR SYS")
        self.FONT_SIZE = 18
        b, h = 900, 800
        bs, hs = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{b}x{h}+{bs//2-b//2}+{hs//2-h//2}')
        self.resizable(False, False)

        

        if platform.system() == "Windows":
            font = ('Consolas', self.FONT_SIZE)
        elif platform.system() == "Darwin":  # macOS
            font = ('Menlo', self.FONT_SIZE)
        else:                                # Linux
            font = ('Monospace', self.FONT_SIZE)
        self.option_add('*Font', font)
        self.max_text_len = b//self.FONT_SIZE
        # Kontrollområde for valg av visning
        self.controls_frame = tk.Frame(self, relief='raised', bd=1)
        self.controls_frame.pack(side=tk.TOP, fill='x')
        self.controls = {
            'Vis alle \n kategorier':self.show_cats_request,
            'Vis \n lagerrom':self.show_rooms_request,
            'Vis nye \n ting':self.show_prints_request,
        }
        self.current  = None

        # Visnngsområde
        self.display_frame = tk.Frame(self)
        self.display_frame.pack(side=tk.RIGHT, fill='both', expand=True)
        # Meny
        self.meny_frame = tk.Frame(self, relief="solid")
        self.meny_frame.pack(side=tk.LEFT)
        self.meny_vals:dict[str,tk.BooleanVar] = {}
        
        
        

        
    def setup_controls(self):
        '''Opprett kontroller for valg av visning'''
        for widget in self.controls_frame.winfo_children():
            widget.destroy()    
        col = 0
       
        for text,function in self.controls.items():
            if self.current == function:
                
                btn = tk.Button(self.controls_frame, text=text,
                    command=function, border=0, borderwidth=5)
            else:
                btn = tk.Button(self.controls_frame, text=text,
                    command=function)
            btn.grid(
                row=0, column=col, padx=10, pady=10)
            col += 1
        # tk.Button(self.controls_frame, text='Vis \n lagerrom',
        #           command=self.show_rooms_request, ).grid(
        #     row=0, column=1, padx=10, pady=10)
        # tk.Button(self.controls_frame, text='Vis nye \n',
        #           command=self.show_prints_request).grid(
        #     row=0, column=2, padx=10, pady=10)

    def show_cats_request(self):
        '''
        Be app om å behandle forespørselen,
        som deretter ber gui om å vise resultatet i en tabell
        '''
        self.current = self.show_cats_request
        self.app.handle_request('show_all_cats')

    def show_rooms_request(self):
        self.current = self.show_rooms_request
        self.app.handle_request('show_storages')

    def show_prints_request(self):
        self.current = self.show_prints_request
        self.app.handle_request('show_prints')

   
        
            
        
    def set_menu(self, onclick, inital_val = True, ):
        # Menyfelt
        rooms = fetch_all_storages()
        for i,storage in enumerate(rooms):
            self.meny_vals[storage] = tk.BooleanVar()
            # self.meny_vals[storage].set(inital_val)
         
            btn= tk.Checkbutton(self.meny_frame,text=storage,onvalue=True, offvalue=False,variable=self.meny_vals[storage], command=onclick)
            
            if inital_val:
                btn.select()

            btn.grid(row=i , column=0, sticky = "w")    
        
           
    def set_room_index(self)->None:
        for i,j in enumerate(self.data[0]):
            if j.lower() == "storage":
                self.room_index = i

    def display_table(self, data:list):
        '''Vis tekst i visningsområdet'''
        self.clear_display()
        self.vals = [0]*len(data[0])
        self.data = data
        self.set_room_index()

        

        # Find len of rows:
        for row in data:
            for i, info in enumerate(row):
                self.vals[i] = max( self.vals[i], len(str(info)) )
       

        # Tekstfelt
        output = tk.Text(self.display_frame, wrap='none')
        output.pack(padx=10, pady=10, fill='both', expand=True)
        # Rullefelt
        scroll = ttk.Scrollbar(output, orient='vertical',
                            command=output.yview)
        scroll.pack(side='right', fill='y')
        output['yscrollcommand'] = scroll.set
        # Tag for marger
        output.tag_configure(
            "marg", lmargin1=10, lmargin2=10, rmargin=10)
        # Tag for fet skrift
        font = Font(output, output.cget("font"))
        font.config(weight="bold")
        output.tag_configure('fet', font=font)
        
        output.configure(cursor="arrow", takefocus=0, exportselection=False)
        for seq in ("<Key>", "<<Paste>>", "<<Cut>>", "<Control-v>", "<Control-x>", "<Control-Shift-V>"):
            output.bind(seq, lambda e: "break")
        for seq in ("<Button-1>", "<B1-Motion>", "<Shift-Button-1>",
                    "<Double-Button-1>", "<Triple-Button-1>", "<Control-a>"):
            output.bind(seq, lambda e: "break")
        self.output = output

        self.update_table_text()


    def update_table_text(self): 
        text = ""
        # Header
        for i,info in enumerate(self.data[0]):
            text += f"{info:<{self.vals[i]}} "
        text += "\n"
        # If rooms filter
        if self.room_index:
            for row in self.data[1:]:
                room:str = row[self.room_index]
                if self.meny_vals[room].get():
                    for i,info in enumerate(row):
                        text += f"{info:<{self.vals[i]}} "
                    text += "\n"

        else:
        # Prepp text
            text = ""
            for row in self.data:
                for i,info in enumerate(row):
                    text += f"{info:<{self.vals[i]}} "
                text += "\n"


        
        self.output.delete("1.0",tk.END)
        self.output.insert('1.0', text, "marg")
        self.output.tag_add("fet", "1.0", "1.end")
           


        

    def clear_display(self) -> None:
        '''Fjern alle widgeter fra visningsområdet (før ny visning)'''
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        # for widget in self.meny_frame.winfo_children():
        #     widget.destroy()

    def destroy(self) -> None:
        '''
        Lukk alle matplotlib-figurer og avslutt vinduet.
        Nødvendig når vi bruker matplotlib i tkinter.
        '''
        # plt.close('all')
        super().destroy()


if __name__ == "__main__":
    '''
    Start applikasjonen hvis filen kjøres som et skript.
    Kjøres ikke hvis denne filen importeres som modul.
    '''

    app = App()
    app.run()
