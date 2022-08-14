from tkinter import *
from tkinter import messagebox
import math
from random import randint
import time


root = Tk()

boardRows = 7
maxHexID = boardRows ** 2

hexSideLength = boardRows * 2

hexHeight = 2 * hexSideLength
hexWidth = int(round(math.sqrt(3) * hexSideLength))
rowDis = int(1.5 * hexSideLength)

canWid = 22 * hexWidth / rowDis * hexSideLength
canHei = 22 * hexSideLength - 2 * rowDis
lastWid = canWid
lastHei= canHei
canRatio = canWid / canHei

aiDiffVal = 0
aiSetting = 0
evalVar = 0
gameWon = 0
playerWon = ""
turnTreeList = []
playDic2 = {}
uglyCommunicationVariable = 0

dictField = {}

fieldWidth = 16 * hexSideLength
fieldHeight = 2 * hexSideLength + 10 * 1.5 * hexSideLength
fieldRatio = fieldWidth / fieldHeight

colDef = StringVar()
colPl1 = StringVar()
colPl2 = StringVar()
colBG = StringVar()

colDef.set("#F7B733")
colPl1.set("#FC4A1A")
colPl2.set("#4ABDAC")
colBG.set("#336699")

counterTurn = 0
counterUndo = 0
start = 0
redraws = 0
borderDraws = 0
maxID = 0
notRunFunctionsAtStartup = 0
listTurn = []
listLeftoverTurns = list(range(1, (boardRows ** 2) + 1))

DEBUGFirstGame = 0

canvas = Canvas(root, width=canWid, height=canHei, borderwidth=0, highlightthickness=0, bg=colBG.get(), highlightcolor=colBG.get())
canvas.pack(side="bottom", fill=BOTH, expand=YES)


def motion(event):
    if len(canvas.find_overlapping(event.x, event.y, event.x, event.y)) == 1:
        canvas.tag_raise(event.widget.find_withtag("current"))
    for i in canvas.find_withtag("border"):
        canvas.tag_raise(i)


def undo(event = NONE):
    global counterTurn
    global counterUndo
    global gameWon
    global playerWon
    global listLeftoverTurns
    global aiSetting

    if counterTurn > 0:

        gameWon = 0
        playerWon = ""

        listLeftoverTurns.insert(listTurn[-1] - 1, listTurn[-1])
        del dictField[listTurn[-1]][3]
        del dictField[listTurn[-1]][-1]
        del dictField[listTurn[-1]][-1]
        dictField[listTurn[-1]].insert(3, [])
        del listTurn[-1]
        counterTurn = counterTurn - 1

        if evalVar == 0:
            draw()
        if aiSetting == 2:
            aiSetting = 0
            undo()
            aiSetting = 2


def draw(event = None):
    global polNum
    global canvas
    global start
    global redraws
    global counterTurn
    global borderDraws
    global maxID
    global boardRows
    global borderDraws
    global currentDrawMaxID

    canvas.delete("all")

    hexHeight = 2 * hexSideLength
    hexWidth = int(round(math.sqrt(3) * hexSideLength))
    rowDis = int(1.5 * hexSideLength)
    currentDrawMaxID = 0

    polNum = 1

    for row in range(rowDis, (boardRows + 1) * rowDis, rowDis):
        for column in range(hexWidth, (boardRows + 1) * hexWidth, hexWidth):
            xN = column + (row / rowDis * hexWidth / 2)
            yN = row

            xNE = xN + 0.5 * hexWidth
            yNE = yN + 0.5 * hexSideLength

            xSE = xNE
            ySE = yN + hexSideLength * 1.5

            xS = xN
            yS = yN + hexHeight

            xNW = xN - 0.5 * hexWidth
            yNW = yN + 0.5 * hexSideLength

            xSW = xNW
            ySW = ySE

            xMid = xN
            yMid = yN + 0.5 * hexWidth

            #erst Zeichnen, dann if-checks durchführen und updaten.
            if counterTurn % 2 == 0:
                canvas.create_polygon(xSW, ySW, xNW, yNW, xN, yN, xNE, yNE, xSE, ySE, xS, yS, fill=colDef.get(),
                                              activeoutline=colPl1.get(), outline=colBG.get(), tags="field")
            else:
                canvas.create_polygon(xSW, ySW, xNW, yNW, xN, yN, xNE, yNE, xSE, ySE, xS, yS, fill=colDef.get(),
                                              activeoutline=colPl2.get(), outline=colBG.get(), tags="field")
            if counterTurn > 0:
                if "Pl1" in dictField[polNum][-1]:
                    canvas.itemconfig(canvas.find_overlapping(xMid, yMid, xMid, yMid), fill=colPl1.get(), tags=("Pl1"))
                elif "Pl2" in dictField[polNum][-1]:
                    canvas.itemconfig(canvas.find_overlapping(xMid, yMid, xMid, yMid), fill=colPl2.get(), tags=("Pl2"))

            fieldStr = "Row = " + str(row / rowDis) + "\nColumn =" + str(column / hexWidth)
            if start == 0:
                 # the list after the dictionary is for IDs of neighbouring Hexes. The one after that is for connected Hexes,
                 #the next list is for all hexes that have 2 same neighbours.
                dictField[polNum] = [fieldStr, {"Row": row / rowDis, "Column": column / hexWidth}, [], [], []]

                #this list can only be done for Hexes with a smaller ID, as ones with a higher don't exist yet, so this
                #adds the current Hex itself to the list of its neighbours.
                #while -1, -10 and -11 are for the direct neighbours and the list at index 2, -21, -12 and -9 are for
                #hexes that have 2 neighbours in common and go into the list at index 4.
                if polNum > 1:
                 if not column / hexWidth == 1:
                     dictField[(polNum - 1)][2].append(polNum)
                     dictField[polNum][2].append(polNum - 1)
                 #the if before is to keep KeyErrors from happening. This if is also to make sure that the Hexes in
                 #the first row wont have any neighbours above, hence this if checks for polNum > 11 rather than
                 #polNum > 10, as the latter wouldn't work with the 11th Hex being in the first row, as it is.
                 #This can also be done with try;except, but would probably be even less readable.
                 if polNum > boardRows:
                     dictField[(polNum - boardRows)][2].append(polNum)
                     dictField[polNum][2].append(polNum - boardRows)
                     if not column / hexWidth == boardRows:
                         dictField[(polNum - (boardRows - 1))][2].append(polNum)
                         dictField[polNum][2].append(polNum - (boardRows - 1))

                if row / rowDis == 1:
                    dictField[polNum].append("atBorderTop")
                if row / rowDis == boardRows:
                    dictField[polNum].append("atBorderBot")
                if column / hexWidth == 1:
                    dictField[polNum].append("atBorderLef")
                if column / hexWidth == boardRows:
                    dictField[polNum].append("atBorderRig")



            maxID += 1
            currentDrawMaxID += 1
            polNum = polNum + 1
    #seperate for statements for border and hexes as borders would mess up the canvas objects' IDs.
    for row in range(rowDis, (boardRows + 1) * rowDis, rowDis):
        for column in range(hexWidth, (boardRows + 1) * hexWidth, hexWidth):
            xN = column + (row / rowDis * hexWidth / 2)
            yN = row

            xNE = xN + 0.5 * hexWidth
            yNE = yN + 0.5 * hexSideLength

            xSE = xNE
            ySE = yN + hexSideLength * 1.5

            xS = xN
            yS = yN + hexHeight

            xNW = xN - 0.5 * hexWidth
            yNW = yN + 0.5 * hexSideLength

            xSW = xNW
            ySW = ySE

            if row == rowDis:
                canvas.create_line(xNW, yNW, xN, yN, xNE, yNE, fill=colPl1.get(), width="2", tags="border")
                borderDraws += 1
                maxID += 1
                currentDrawMaxID += 1
            elif row == boardRows * rowDis:
                canvas.create_line(xSW, ySW, xS, yS, xSE, ySE, fill=colPl1.get(), width="2", tags="border")
                borderDraws += 1
                maxID += 1
                currentDrawMaxID += 1
            if column == hexWidth:
                canvas.create_line(xNW, yNW, xSW, ySW, xS, yS, fill=colPl2.get(), width="2", tags="border")
                borderDraws += 1
                maxID += 1
                currentDrawMaxID += 1
            elif column == boardRows * hexWidth:
                canvas.create_line(xN, yN, xNE, yNE, xSE, ySE, fill=colPl2.get(), width="2", tags="border")
                borderDraws += 1
                maxID += 1
                currentDrawMaxID += 1

    redraws += 1
    start = 1

def click_AI(ID):
    global counterTurn
    global counterUndo
    global dictField
    global aiSetting
    global gameWon
    global playerWon
    global listLeftoverTurns

    border1 = 0
    border2 = 0
    currentHex = (maxID - currentDrawMaxID) + ID

    if "taken" not in dictField[ID][-2]:
        listLeftoverTurns.remove(ID)
        if counterTurn % 2 == 0:
            canvas.itemconfig(currentHex,
                              fill=colPl1.get())
            dictField[ID].append("taken")
            dictField[ID].append("Pl1")
            for i in dictField[ID][2]:
                #if this if statement gives unexpected results (for example because of the playernumber not being last)
                #another way to write this would be " if "Pl1" in dictField[i]:  ", although one would have to check
                # if it would return true on hexes with "atBorderPl1" in them.
                if "Pl1" == dictField[i][-1]:
                    #hexes DO count as being connected to themselves
                    dictField[i][3].append(ID)
                    dictField[ID][3].append(i)
                    dictField[i][3] = list(set((dictField[ID][3]) + dictField[i][3]))
                    dictField[ID][3] = list(set((dictField[ID][3]) + dictField[i][3]))

            for i in dictField[ID][3]:
                dictField[i][3] = dictField[ID][3]

            for i in dictField[ID][3]:
                if "atBorderTop" in dictField[i]:
                    border1 = 1
                elif "atBorderBot" in dictField[i]:
                    border2 = 1

            if (border1 == 1 and border2 == 1):# or counterTurn == 24:

                gameWon = 1
                playerWon = "Pl1"

                if evalVar == 0:
                    messagebox.showinfo("Player 2 loses.", "Player 1 wins!")


        else:
            canvas.itemconfig(currentHex,
                              fill=colPl2.get())
            dictField[ID].append("taken")
            dictField[ID].append("Pl2")
            for i in dictField[ID][2]:
                if "Pl2" == dictField[i][-1]:
                    dictField[i][3].append(ID)
                    dictField[ID][3].append(i)
                    dictField[i][3] = list(set((dictField[ID][3]) + dictField[i][3]))
                    dictField[ID][3] = list(set((dictField[ID][3]) + dictField[i][3]))

            for i in dictField[ID][3]:
                dictField[i][3] = dictField[ID][3]

            for i in dictField[ID][3]:
                if "atBorderLef" in dictField[i]:
                    border1 = 1
                elif "atBorderRig" in dictField[i]:
                    border2 = 1

            if border1 == 1 and border2 == 1:

                gameWon = 1
                playerWon = "Pl2"

                if evalVar == 0:
                    messagebox.showinfo("Player 1 loses.", "Player 2 wins!")

        counterTurn += 1

        listTurn.append(ID)

        counterUndo = counterTurn + 1

    if aiSetting == 1 and evalVar == 0:
        time.sleep(0.2)
        root.update()

def click(event = None):

    global counterTurn
    global counterUndo
    global dictField
    global aiSetting
    global gameWon
    global playerWon
    global listLeftoverTurns

    border1 = 0
    border2 = 0

    try:
        currentHex = canvas.find_overlapping(event.x, event.y, event.x, event.y)
        currentHexID = currentHex[0] - (maxID - currentDrawMaxID)
        if len(currentHex) == 1 and \
            "taken" not in dictField[currentHexID][-2] and \
            currentHex[0] not in canvas.find_withtag("border"):

            listLeftoverTurns.remove(currentHexID)
            if counterTurn % 2 == 0:
                canvas.itemconfig(currentHex[0],
                                  fill=colPl1.get())
                dictField[currentHexID].append("taken")
                dictField[currentHexID].append("Pl1")
                for i in dictField[currentHexID][2]:
                    #if this if statement gives unexpected results (for example because of the playernumber not being last)
                    #another way to write this would be " if "Pl1" in dictField[i]:  ", although one would have to check
                    # if it would return true on hexes with "atBorderPl1" in them.
                    if "Pl1" == dictField[i][-1]:
                        #hexes DO count as being connected to themselves
                        dictField[i][3].append(currentHexID)
                        dictField[currentHexID][3].append(i)
                        dictField[i][3] = list(set((dictField[currentHexID][3]) + dictField[i][3]))
                        dictField[currentHexID][3] = list(set((dictField[currentHexID][3]) + dictField[i][3]))

                for i in dictField[currentHexID][3]:
                    dictField[i][3] = dictField[currentHexID][3]

                for i in dictField[currentHexID][3]:
                    if "atBorderTop" in dictField[i]:
                        border1 = 1
                    if "atBorderBot" in dictField[i]:
                        border2 = 1

                if (border1 == 1 and border2 == 1):

                    gameWon = 1
                    playerWon = "Pl1"

                    if evalVar == 0:
                        messagebox.showinfo("Player 2 loses.", "Player 1 wins!")


            else:
                canvas.itemconfig(currentHex[0],
                                  fill=colPl2.get())
                dictField[currentHexID].append("taken")
                dictField[currentHexID].append("Pl2")
                for i in dictField[currentHexID][2]:
                    if "Pl2" == dictField[i][-1]:
                        dictField[i][3].append(currentHexID)
                        dictField[currentHexID][3].append(i)
                        dictField[i][3] = list(set((dictField[currentHexID][3]) + dictField[i][3]))
                        dictField[currentHexID][3] = list(set((dictField[currentHexID][3]) + dictField[i][3]))

                for i in dictField[currentHexID][3]:
                    dictField[i][3] = dictField[currentHexID][3]

                for i in dictField[currentHexID][3]:
                    if "atBorderLef" in dictField[i]:
                        border1 = 1
                    if "atBorderRig" in dictField[i]:
                        border2 = 1

                if border1 == 1 and border2 == 1:

                    gameWon = 1
                    playerWon = "Pl2"

                    if evalVar == 0:
                        messagebox.showinfo("Player 1 loses.", "Player 2 wins!")

            counterTurn += 1
            listTurn.append(currentHexID)
            counterUndo = counterTurn + 1
            if aiSetting == 2:
                aiSetting = 0
                root.event_generate("<a>")
                aiSetting = 2
                draw()

        if aiSetting == 1:
            root.update()
        elif aiSetting == 0:
            draw()
    except IndexError:
        pass




def on_resize(event = None):
    global canWid
    global canHei
    global canRatio
    global lastWid
    global lastHei
    global hexSideLength
    global notRunFunctionsAtStartup
    global hexWidth

    if canvas.winfo_width() >= canvas.winfo_height() * hexWidth / rowDis:
        hexSideLength = canvas.winfo_height() * hexWidth / rowDis / (2.9 * boardRows)
        draw()

    if canvas.winfo_width() < canvas.winfo_height() * hexWidth / rowDis:
        hexSideLength = canvas.winfo_width() / (2.9 * boardRows)
        draw()


def idToRowAndCol(ID = 0):
    row = math.ceil(ID / boardRows)
    column = (ID - boardRows * row) + boardRows
    return (row, column)

def idToCoords(ID = 0):
    global hexWidth
    global rowDis

    hexWidth = int(round(math.sqrt(3) * hexSideLength))
    rowDis = int(1.5 * hexSideLength)

    row = idToRowAndCol(ID)[0] + 1
    column = idToRowAndCol(ID)[1]

    return (column * hexWidth + (row * hexWidth / 2) - 0.5 * hexSideLength, row * rowDis - 0.5 * hexSideLength)


def idToClick(event):
    temp1 = idToCoords(uglyCommunicationVariable)
    event.x = temp1[0]
    event.y = temp1[1]
    click(event)

def hex_eval(ID):
    global dictField
    global aiSetting
    global uglyCommunicationVariable
    global DEBUGFirstGame

    gamesWon = 0
    if aiDiffVal == 1:
        gamesplayed = 75
    elif aiDiffVal == 2:
        gamesplayed = 100
    elif aiDiffVal == 3:
        gamesplayed = 200
    elif aiDiffVal == 4:
        gamesplayed = 500

    temp1 = listTurn[:]

    for i in range (1, gamesplayed + 1):
        RanAIvsRanAI()
        if playerWon == "Pl2":
            gamesWon += 1

        if i == 51:
            try:
                if gamesWon / i < max(turnTreeList) - 0.1:
                    new_game()
                    for j in temp1:
                        click_AI(j)
                    return gamesWon / i
            except ValueError:
                p = 0
            except TypeError:
                p = 0



        new_game()

        #DEBUGFirstGame = 0
        for j in temp1:
            # uglyCommunicationVariable = j
            # root.focus_force()
            # root.event_generate("<Control-Home>") #idToClick
            click_AI(j)
    return gamesWon / gamesplayed

def RanAIvsRanAI():
    while gameWon == 0:
        aiRan()

def tree(event = None):
    global dictField
    global evalVar
    global turnTreeList
    global playDic2
    global uglyCommunicationVariable

    tempEvalBefore = evalVar
    evalVar = 1

    del turnTreeList
    turnTreeList = []

    for i in range(1, boardRows ** 2 + 1):

        #up until the next if is for the visual effect
        if "taken" not in dictField[i][-2]:
            click_AI(i)

            turnTreeList.append(hex_eval(i))
            draw()
            root.update()
            undo()

        else:
            turnTreeList.append(0)

    evalVar = tempEvalBefore
    draw()
    root.update()
    return(turnTreeList)



def aiRan(event = None):
    global uglyCommunicationVariable
    click_AI(listLeftoverTurns[randint(0, len(listLeftoverTurns) - 1)])


def ai(event = None):
    global uglyCommunicationVariable
    global aiDiffVal

    root.focus_force()
    if aiDiffVal > 0:
        tree()
        click_AI((turnTreeList.index(max(turnTreeList)) + 1))
    elif aiDiffVal == 0:
        root.focus_force()
        root.event_generate("<Alt-BackSpace>")

def regeln():
    top = Toplevel()
    top.title("Rules")

    msg = Message(top, text="Players alternate placing markers on unoccupied spaces in an attempt to link their opposite sides of the board in an unbroken chain. One player must win; there are no draws.  The game has deep strategy, sharp tactics and a profound mathematical underpinning related to the Brouwer fixed-point theorem.")
    msg.pack()

    button = Button(top, text="Close", command=top.destroy)
    button.pack()

def aiMode(i = 0):
    global aiSetting

    #0 Pl vs Pl, 1 AI vs AI, 2 Pl vs AI
    new_game()
    aiSetting = i
    if i == 1:
        while gameWon == 0:
            aiRan()

def aiDiffChange(diff = 1):
    global aiDiffVal

    new_game()
    aiDiffVal = diff


def feldGroesse(a = boardRows):
    global boardRows
    #new_game()

    try:
        a = int(a)
        if isinstance(a, int) and a in range(5, 20):
            boardRows = a
            new_game()
            draw()
            on_resize()
        else:
            messagebox.showerror("Alarrrm!", "Das Feld muss zwischen 5 und 19 Reihen groß sein!")
    except ValueError:
        messagebox.showerror("Alarm!", "Bitte geben Sie eine ganze Zahl ein!")

def colourChange(i = 1):
    if i == 1:
        colDef.set("#F7B733")
        colPl1.set("#FC4A1A")
        colPl2.set("#4ABDAC")
        colBG.set("#336699")
        canvas.configure(bg=colBG.get())
    elif i == 2:
        colDef.set("#E7DFDD")
        colPl1.set("#A239CA")
        colPl2.set("#4717F6")
        colBG.set("forest green")
        canvas.configure(bg=colBG.get())
    elif i == 3:
        colDef.set("#e6e6fa")
        colPl1.set("green")
        colPl2.set("#E42D9F")
        colBG.set("#b2b2ee")
        canvas.configure(bg=colBG.get())

    draw()


def feld(event = None):
    global boardRows


    top1 = Toplevel()
    inp = Entry(top1)

    but = Button(top1, command= lambda: feldGroesse(inp.get()), text="Feld zeichnen")
    msg = Message(top1, text="Geben Sie hier die gewünschte Reihenanzahl zwischen 5 und 19 ein.")
    msg.grid(row=1,column=1)
    inp.grid(row=2,column=1)
    but.grid(row=3,column=1)

def new_game():
    global counterTurn
    global counterUndo
    global gameWon
    global start
    global playerWon
    global dictField
    global listTurn
    global listLeftoverTurns

    # gameWon = 0
    # playerWon = ""
    #
    #
    # while counterTurn > 0:
    #     undo()
    #
    # draw()


    listTurn = []
    start = 0
    gameWon = 0
    playerWon = ""
    counterTurn = 0
    counterUndo = 0
    listLeftoverTurns = list(range(1, (boardRows ** 2) + 1))

    dictField.clear()
    # del dictField
    # dictField = {}

    draw()


menuBar = Menu(root)
colDefMenu = Menu(menuBar, tearoff=0)
colPl1Menu = Menu(menuBar, tearoff=0)
colPl2Menu = Menu(menuBar, tearoff=0)
colourMenu = Menu(menuBar, tearoff=0)
optionsMenu = Menu(menuBar, tearoff=0)
helpMenu = Menu(menuBar, tearoff=0)
activeColMenu = Menu(optionsMenu, tearoff=0)
aiOptMenu = Menu(menuBar, tearoff=0)
testMenu = Menu(menuBar, tearoff=0)
feldMenu= Menu(menuBar, tearoff=0)

colourMenu.add_cascade(label="Board", menu=colDefMenu)
colourMenu.add_cascade(label="Player 1", menu=colPl1Menu)
colourMenu.add_cascade(label="Player 2", menu=colPl2Menu)



aiOptMenu.add_command(label="RanvRan", command=lambda: aiMode(1))
aiOptMenu.add_command(label="PvE", command=lambda: aiMode(2))
aiOptMenu.add_command(label="PvP", command=lambda: aiMode(0))
aiOptMenu.add_separator()
aiOptMenu.add_command(label="Level 0", command= lambda: aiDiffChange(0))
aiOptMenu.add_command(label="Level 1", command= lambda: aiDiffChange(1))
aiOptMenu.add_command(label="Level 2", command= lambda: aiDiffChange(2))
aiOptMenu.add_command(label="Level 3", command= lambda: aiDiffChange(3))
aiOptMenu.add_command(label="Level 4", command= lambda: aiDiffChange(4))



optionsMenu.add_command(label="Undo", command=undo)
optionsMenu.add_cascade(label="Boardoptions", menu=feldMenu)
feldMenu.add_command(label="Boardsize", command=lambda: feld())
feldMenu.add_command(label="Colourscheme 1", command=lambda: colourChange(1))
feldMenu.add_command(label="Colourscheme 2", command=lambda: colourChange(2))
feldMenu.add_command(label="Colourscheme 3", command=lambda: colourChange(3))


menuBar.add_cascade(label="Options", menu=optionsMenu)
menuBar.add_cascade(label="AI options", menu=aiOptMenu)
menuBar.add_command(label="Rules", command=regeln)
menuBar.add_command(label="Restart", command=new_game)
menuBar.add_command(label="Close", command=root.quit)


root.config(menu=menuBar)
root.minsize(300, 300)
root.bind("<Button-1>", click)
root.bind("<Control-z>", undo)
root.bind("<a>", ai)
root.bind("<b>", tree)
root.bind("<Alt-BackSpace>", aiRan)
root.bind("<d>", feld)
root.bind("<Control-Home>", idToClick)
canvas.bind("<Configure>", on_resize)
canvas.bind("<Motion>", motion)

# canvas.bind("<Button-1>", draw)
# draw()

root.mainloop()
