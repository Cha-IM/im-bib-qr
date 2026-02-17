# Endpoint, bruker inventory_service for å lage gui
from inventory_service import print_all_new, create_new_categories_from_csv, add_to_category,fetch_all_items,show_all_items,show_all_new,fetch_all_categories, fetch_all_storages,create_new_category_with_items, show_all_categories

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


    def handle_request(self, request):
        '''Behandle forespørselen og be gui om å vise resultatet'''
        """ hvordan sortere? 
            Vis alle kategorier  - CHECK
            Vis enkelt-rom : 
            Vis alle rom, alle nye, alle items etc. 
                Behøver egentlig hente hele db og så filtrere?
                Alle items er en veldig dårlig ide... 
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
        if request == 'show_all_cats':
            data=fetch_all_categories()
            self.gui.display_table(data)
        elif request == "show_storages":
            pass


    def run(self):
        '''Start hendelsessløyfen og hold vinduet åpent'''
        self.gui.mainloop()

class Gui(tk.Tk):
    def __init__(self,app):
        '''opprett GUI-vindu med kontroll- og visningsområder'''
        super().__init__()
        # Lagre en referanse til app-instansen
        self.app = app
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
        self.setup_controls()

        # Visnngsområde
        self.display_frame = tk.Frame(self)
        self.display_frame.pack(side=tk.RIGHT, fill='both', expand=True)
        # Meny
        self.meny_frame = tk.Frame(self, relief="solid")
        self.meny_frame.pack(side=tk.LEFT)

    def setup_controls(self):
        '''Opprett kontroller for valg av visning'''
        tk.Button(self.controls_frame, text='Vis alle \n kategorier',
                  command=self.show_cats_request).grid(
            row=0, column=0, padx=10, pady=10)
        tk.Button(self.controls_frame, text='Vis alle \n lagerrom',
                  command=self.show_rooms_request).grid(
            row=0, column=1, padx=10, pady=10)

    def show_cats_request(self):
        '''
        Be app om å behandle forespørselen,
        som deretter ber gui om å vise resultatet i en tabell
        '''
        self.app.handle_request('show_all_cats')

    def show_rooms_request(self):
        '''
        Be app om å behandle forespørselen,
        som deretter ber gui om å vise resultatet i en graf
        '''
        self.app.handle_request('show_storages')

    
    def display_table(self, data:list):
        '''Vis tekst i visningsområdet'''
        self.clear_display_frame()
        vals = [0]*len(data[0])
        room_index = None
        for i,j in enumerate(data[0]):
            if j == "Storage":
                room_index = i

        # Find len of rows:
        for row in data:
            for i, info in enumerate(row):
                vals[i] = max( vals[i], len(str(info)) )
       

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

        # Menyfelt
        meny:dict[str,tk.BooleanVar] = {}
        # Updating the meny text with this internal function
        def update_meny_text(): 
           
            for i,j in meny.items():
                print(i,j.get())
            
            text = ""
            # Header
            for i,info in enumerate(data[0]):
                text += f"{info:<{vals[i]}} "
            text += "\n"
            # If rooms filter
            if room_index:
                for row in data[1:]:
                    room:str = row[room_index]
                    if meny[room].get():
                        for i,info in enumerate(row):
                            text += f"{info:<{vals[i]}} "
                        text += "\n"

            else:
            # Prepp text
                text = ""
                for row in data:
                    for i,info in enumerate(row):
                        text += f"{info:<{vals[i]}} "
                    text += "\n"

       
            output['state'] = 'normal'
            output.delete("1.0",tk.END)
            output.insert('1.0', text, "marg")
            output.tag_add("fet", "1.0", "1.end")
            output['state'] = 'disabled'

        if room_index:
            rooms = fetch_all_storages() 
            for i,storage in enumerate( rooms):
                meny[storage] = tk.BooleanVar()
                btn= tk.Checkbutton(self.meny_frame,text=storage,onvalue=True, offvalue=False,variable=meny[storage], command=update_meny_text)
                btn.select()
                btn.grid(row=i , column=0, sticky = "w")    
            # tk.Button(meny_frame,text="test",).pack(side='left', fill="y",ipadx=10)

        update_meny_text()

       

    def display_graph(self, data, title):
        '''Vis graf i visningsområdet'''
        pass
        # self.clear_display_frame()
        # sns.set_theme()
        # fig, ax = plt.subplots(figsize=(6, 4))
        # sns.barplot(data=data, x='Navn', y='Alder', ax=ax)
        # ax.set_title(title)
        # plt.tight_layout()
        # canvas = FigureCanvasTkAgg(fig, master=self.display_frame)
        # canvas.draw()
        # canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def clear_display_frame(self) -> None:
        '''Fjern alle widgeter fra visningsområdet (før ny visning)'''
        for widget in self.display_frame.winfo_children():
            widget.destroy()

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
