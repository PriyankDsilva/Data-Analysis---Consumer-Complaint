from tkinter import *
from tkinter import ttk

#Global Variables
#Fonts
LARGE_FONT= ("Verdana", 12)
NORM_FONT = ("Helvetica", 10)
SMALL_FONT = ("Helvetica", 8)

#Program Info
ABOUT_INFO="In Progress !!!"

def SignUpFrame(root,photo):
    # Set Title for the Sign Up Frame
    root.title('Consumer Complaint Analysis - Login')
    root.iconbitmap(default='ConsumerComplaintIcon.ico')
    # Menu Window for SignUp
    menu = Menu(root)
    root.config(menu=menu)
    subMenu = Menu(menu)
    menu.add_cascade(label='Menu', menu=subMenu)
    subMenu.add_command(label='About...', command=lambda : popupmsg(ABOUT_INFO))
    subMenu.add_separator()
    subMenu.add_command(label='Exit', command=root.quit)

    # BackGround Image for SignUp
    ImageLabel = Label(root, image=photo)
    ImageLabel.pack(fill=BOTH)

    # User and Password Frame
    UserPassFrame = Frame(root)
    UserPassFrame.pack()

    #Create Label and Entry
    UserLable = Label(UserPassFrame, text='User:')
    PassLabel = Label(UserPassFrame, text='Password:')
    UserEntry = Entry(UserPassFrame)
    PassEntry = Entry(UserPassFrame,show='*')

    #Display
    UserLable.grid(row=1, sticky=E)
    PassLabel.grid(row=2, sticky=E)
    UserEntry.grid(row=1, column=1)
    PassEntry.grid(row=2, column=1)

    #Login Button
    LoginButton = ttk.Button(UserPassFrame, text='Login',command=lambda : Login(UserEntry.get(),PassEntry.get(),menu,UserPassFrame,ImageLabel,status))
    LoginButton.grid(row=4, column=1)

    # Status Bar
    status = Label(root, text='Consumer Complaint Analysis...', bd=1, relief=SUNKEN, anchor=E)
    status.pack(side=BOTTOM, fill=X)

#Authenticate User and Login
def Login(User,Password,menu,frame,image,lable):
    if User=='admin' and Password=='admin':
        #Clear All Contents
        menu.destroy()
        frame.destroy()
        lable.destroy()
        image.destroy()
    else:
        popupmsg("Invalid User/Password !!!")

#Pop UP
def popupmsg(msg):
    popup = Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()

def main():
    root = Tk()
    #Image for SignUp Background
    photo = PhotoImage(file='ConsumerComplaint.png')
    SignUpFrame(root,photo)
    root.mainloop()


main()


'''
def doNothing():
    print('Do Nothing !!!')

root = Tk()
root.title('Consumer Complaint Analysis - Login')
#Main Menu
menu=Menu(root)
root.config(menu=menu)
subMenu=Menu(menu)
menu.add_cascade(label='Menu',menu=subMenu)
subMenu.add_command(label='About...',command=doNothing)
subMenu.add_separator()
subMenu.add_command(label='Exit',command=root.quit)

#BackGround Image
photo = PhotoImage(file='ConsumerComplaint.png')
label = Label(root,image=photo)
label.pack(fill=BOTH)

#Username and Password

UserPassFrame=Frame(root)
UserPassFrame.pack()

UserLable=Label(UserPassFrame,text='User:')
PassLabel=Label(UserPassFrame,text='Password:')
UserEntry=Entry(UserPassFrame)
PassEntry=Entry(UserPassFrame)

UserLable.grid(row=0,sticky=E)
PassLabel.grid(row=1,sticky=E)

UserEntry.grid(row=0,column=1)
PassEntry.grid(row=1,column=1)

LoginButton=Button(UserPassFrame,text='Login',bg='blue',fg='red')
LoginButton.grid(columnspan=2)

#Status Bar
status=Label(root,text='Preparing !!!',bd=1,relief=SUNKEN,anchor=W)
status.pack(side=BOTTOM,fill=X)

root.mainloop()
'''
